class INA3221:
    """A basic driver for the INA3221 Voltage and Current Sensor."""

    # Register addresses from the datasheet
    REG_CONFIG = 0x00
    REG_SHUNT_VOLTAGE = [0x01, 0x03, 0x05] # Channels 1, 2, 3
    REG_BUS_VOLTAGE = [0x02, 0x04, 0x06]   # Channels 1, 2, 3

    def __init__(self, bus, device_address=0x40):
        """
        Initializes the driver.
        Note: Takes an existing smbus2 bus object.
        """
        self.bus = bus
        self.address = device_address
        
        # A common configuration: enable all 3 channels, 1.1ms conversion time, 16 averages
        # You can change this based on your needs.
        config = 0b0111000100100111 
        self.bus.write_word_data(self.address, self.REG_CONFIG, config)

    def _read_register(self, register):
        """Reads a 16-bit value from a register (handling byte order)."""
        raw_word = self.bus.read_word_data(self.address, register)
        # The INA3221 is big-endian, but read_word_data might be little-endian.
        # We swap the bytes to ensure correct interpretation.
        swapped_word = ((raw_word << 8) & 0xFF00) | ((raw_word >> 8) & 0x00FF)
        
        # Convert from two's complement signed value if necessary
        if swapped_word & (1 << 15): # Check if the sign bit is set
            return swapped_word - (1 << 16)
        return swapped_word
    
    def get_bus_voltage(self, channel):
        """
        Gets the bus voltage for one of the INA's channels (1-3).
        Returns the voltage in Volts.
        """
        if not 1 <= channel <= 3:
            raise ValueError("INA3221 channel must be 1, 2, or 3.")
        
        register = self.REG_BUS_VOLTAGE[channel - 1]
        raw_value = self._read_register(register)
        
        # The value is shifted left by 3 bits in the register.
        # The LSB resolution is 8mV.
        voltage_mv = (raw_value >> 3) * 8
        return voltage_mv / 1000.0 # Convert to Volts

    def get_shunt_voltage(self, channel):
        """
        Gets the shunt voltage for one of the INA's channels (1-3).
        The shunt is the small resistor used to measure current.
        Returns the voltage in millivolts.
        """
        if not 1 <= channel <= 3:
            raise ValueError("INA3221 channel must be 1, 2, or 3.")
            
        register = self.REG_SHUNT_VOLTAGE[channel - 1]
        raw_value = self._read_register(register)
        
        # The LSB resolution is 40µV.
        shunt_voltage_uv = raw_value * 40
        return shunt_voltage_uv / 1000.0 # Convert to millivolts

    def get_current(self, channel, shunt_resistance_ohms):
        """
        Calculates the current for one of the INA's channels (1-3).
        You MUST provide the resistance of the shunt resistor on your board.
        Returns the current in milliamps (mA).
        """
        shunt_voltage_mv = self.get_shunt_voltage(channel)
        # Ohm's Law: I = V / R
        # I (mA) = (V (mV)) / R (Ohms)
        return shunt_voltage_mv / shunt_resistance_ohms

import smbus2

class MCP23017:
    """A class to control an MCP23017 I/O expander using smbus2."""

    # All register addresses, straight from the datasheet
    IODIRA = 0x00
    IODIRB = 0x01
    IPOLA = 0x02
    IPOLB = 0x03
    GPINTENA = 0x04
    GPINTENB = 0x05
    DEFVALA = 0x06
    DEFVALB = 0x07
    INTCONA = 0x08
    INTCONB = 0x09
    IOCONA = 0x0A
    IOCONB = 0x0B
    GPPUA = 0x0C
    GPPUB = 0x0D
    INTFA = 0x0E
    INTFB = 0x0F
    INTCAPA = 0x10
    INTCAPB = 0x11
    GPIOA = 0x12
    GPIOB = 0x13
    OLATA = 0x14
    OLATB = 0x15

    def __init__(self, bus_number, device_address=0x20):
        """Initializes the I2C bus and device."""
        self.bus = smbus2.SMBus(bus_number)
        self.address = device_address
        
        # In a production class, you might configure IOCON registers here
        # For now, we'll stick to the defaults.

    def _get_register_pair(self, pin):
        """Helper function to determine if a pin is on Port A or B."""
        if 0 <= pin <= 7:
            # Port A
            return self.IODIRA, self.GPPUB, self.GPIOA, self.OLATA
        elif 8 <= pin <= 15:
            # Port B
            return self.IODIRB, self.GPPUB, self.GPIOB, self.OLATB
        else:
            raise ValueError("Pin number must be between 0 and 15.")

    def setup(self, pin, mode):
        """
        Configures a single pin as an input or output.
        :param pin: Pin number (0-15)
        :param mode: "OUTPUT", "INPUT", or "INPUT_PULLUP"
        """
        iodir_reg, gppu_reg, _, _ = self._get_register_pair(pin)
        pin_bit = pin % 8  # Bit position (0-7) within the port

        # Read the current direction and pull-up configurations
        current_iodir = self.bus.read_byte_data(self.address, iodir_reg)
        current_gppu = self.bus.read_byte_data(self.address, gppu_reg)

        if mode == "OUTPUT":
            new_iodir = current_iodir & ~(1 << pin_bit) # Set bit to 0 for output
            self.bus.write_byte_data(self.address, iodir_reg, new_iodir)
        elif mode == "INPUT" or mode == "INPUT_PULLUP":
            new_iodir = current_iodir | (1 << pin_bit) # Set bit to 1 for input
            self.bus.write_byte_data(self.address, iodir_reg, new_iodir)
            
            if mode == "INPUT_PULLUP":
                new_gppu = current_gppu | (1 << pin_bit) # Set bit to 1 to enable pull-up
                self.bus.write_byte_data(self.address, gppu_reg, new_gppu)
            else: # mode == "INPUT"
                new_gppu = current_gppu & ~(1 << pin_bit) # Set bit to 0 to disable pull-up
                self.bus.write_byte_data(self.address, gppu_reg, new_gppu)
        else:
            raise ValueError("Mode must be 'OUTPUT', 'INPUT', or 'INPUT_PULLUP'.")

    def output(self, pin, value):
        """
        Sets the state of an output pin.
        :param pin: Pin number (0-15)
        :param value: True/1 for HIGH, False/0 for LOW
        """
        _, _, _, olat_reg = self._get_register_pair(pin)
        pin_bit = pin % 8

        # "Read-Modify-Write" - read the current output state, change one bit, write it back
        current_olat = self.bus.read_byte_data(self.address, olat_reg)
        if value: # True, 1, HIGH
            new_olat = current_olat | (1 << pin_bit)
        else: # False, 0, LOW
            new_olat = current_olat & ~(1 << pin_bit)
        self.bus.write_byte_data(self.address, olat_reg, new_olat)
        
    def input(self, pin):
        """
        Reads the state of an input pin.
        :param pin: Pin number (0-15)
        :return: True if the pin is HIGH, False if LOW.
        """
        _, _, gpio_reg, _ = self._get_register_pair(pin)
        pin_bit = pin % 8
        
        port_state = self.bus.read_byte_data(self.address, gpio_reg)
        # Check if the specific bit is set and return True or False
        return (port_state & (1 << pin_bit)) != 0

    def close(self):
        """Closes the I2C bus connection."""
        self.bus.close()

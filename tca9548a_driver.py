import smbus2

class TCA9548A:
    """Driver for the TCA9548A I2C multiplexer."""
    def __init__(self, bus_number, address=0x77):
        """Initialize the TCA9548A multiplexer."""
        self.bus = smbus2.SMBus(bus_number)
        self.address = address

    def select_channel(self, channel):
        """Selects one of the 8 channels of the TCA9548A. (0-7)"""
        if not 0 <= channel <= 7:
            raise ValueError("Channel must be between 0 and 7.")
        
        # The command to send is a single byte with the bit corresponding to the channel set to 1
        # Example: To select channel 3, we send 0b00001000
        channel_byte = 1 << channel

        try:
            self.bus.write_byte(self.address, channel_byte)
        except OSError as e:
            print(f"Error selecting channel {channel}. Is the multiplexer at address {hex(self.address)}?")
            raise e
    
    def close(self):
        """Close the I2C bus."""
        self.bus.close()

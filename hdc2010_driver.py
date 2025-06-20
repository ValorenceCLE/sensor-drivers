import time
import smbus2

class HDC2010:
    DEFAULT_ADDR = 0x41

    TEMP_LOW = 0x00
    TEMP_HIGH = 0x01
    HUMID_LOW = 0x02
    HUMID_HIGH = 0x03
    CONFIG = 0x0E
    MEASUREMENT_CONFIG = 0x0F

    def __init__(self, bus_number, address=DEFAULT_ADDR):
        self.bus = smbus2.SMBus(bus_number)
        self.addr = address
        self._configure_sensor()

    def _configure_sensor(self):
        # Reset config to defaults (14-bit resolution)
        self.bus.write_byte_data(self.addr, self.CONFIG, 0x00)
        time.sleep(0.01)
        # Trigger measurement
        self.bus.write_byte_data(self.addr, self.MEASUREMENT_CONFIG, 0x01)
        time.sleep(0.01)

    def _read_data(self, low_reg, high_reg):
        low = self.bus.read_byte_data(self.addr, low_reg)
        high = self.bus.read_byte_data(self.addr, high_reg)
        return (high << 8) | low

    def read_temperature_c(self):
        raw = self._read_data(self.TEMP_LOW, self.TEMP_HIGH)
        temp_c = (raw / 65536.0) * 165.0 - 40.0
        return temp_c

    def read_temperature_f(self):
        return self.read_temperature_c() * 9.0 / 5.0 + 32.0

    def read_humidity(self):
        raw = self._read_data(self.HUMID_LOW, self.HUMID_HIGH)
        humidity = (raw / 65536.0) * 100.0
        return humidity

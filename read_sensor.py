import time
from tca9548a_driver import TCA9548A
from ina3221_driver import INA3221

# --- 1. Hardware Configuration ---
I2C_BUS = 3 # The bus your TCA9548A is on
TCA_ADDRESS = 0x77
INA_ADDRESS = 0x40 # The default address for most INA3221 boards

# The channel on the TCA9548A that the INA3221 is connected to.
# Let's assume it's on channel 0 for this example.
INA_MUX_CHANNEL = 0

# CRITICAL: The value of the shunt resistor on your INA3221 board.
# This is usually 0.1 Ohm. It might be marked "R100" on the board.
SHUNT_RESISTANCE = 0.1 


# --- 2. Main Program ---
mux = None # Initialize to ensure it's available in the 'finally' block
try:
    # Initialize the multiplexer
    mux = TCA9548A(I2C_BUS, TCA_ADDRESS)
    print(f"TCA9548A Multiplexer initialized at {hex(TCA_ADDRESS)}.")

    # Select the channel where the INA3221 resides.
    # THIS IS THE KEY STEP.
    mux.select_channel(INA_MUX_CHANNEL)
    print(f"Mux channel {INA_MUX_CHANNEL} selected.")

    # Now, initialize the INA3221 driver.
    # IMPORTANT: We pass it the *same bus object* from the mux driver.
    sensor = INA3221(bus=mux.bus, device_address=INA_ADDRESS)
    print(f"INA3221 Sensor initialized at {hex(INA_ADDRESS)}.")

    print("\nReading sensor data... Press Ctrl+C to stop.")
    
    # --- 3. Reading Loop ---
    while True:
        # We'll read from Channel 1 of the INA3221 itself
        ina_sensor_channel = 1
        
        bus_voltage = sensor.get_bus_voltage(ina_sensor_channel)
        shunt_voltage = sensor.get_shunt_voltage(ina_sensor_channel)
        current = sensor.get_current(ina_sensor_channel, SHUNT_RESISTANCE)

        print(f"--- INA3221 Channel {ina_sensor_channel} ---")
        print(f"Time:          {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Bus Voltage:    {bus_voltage:.3f} V")
        print(f"Shunt Voltage:  {shunt_voltage:.3f} mV")
        print(f"Current:        {current:.1f} mA")
        print("-" * 25)
        
        time.sleep(2)

except KeyboardInterrupt:
    print("\nProgram stopped.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if mux:
        # It's good practice to close the bus connection.
        mux.close()
        print("I2C bus closed.")

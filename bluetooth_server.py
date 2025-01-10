import dbus
import struct
import random
from utils.advertisement import Advertisement
from utils.service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 1000  

class SensorAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("NeuraLoad")
        self.include_tx_power = True

class SensorService(Service):
    SENSOR_SVC_UUID = "00000001-736c-4645-b520-7127aadf8c47"

    def __init__(self, index):
        Service.__init__(self, index, self.SENSOR_SVC_UUID, True)
        self.add_characteristic(IMUCharacteristic(self))
        self.add_characteristic(LaserCharacteristic(self))

class IMUCharacteristic(Characteristic):
    IMU_CHARACTERISTIC_UUID = "00000002-736c-4645-b520-7127aadf8c47"

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
            self, self.IMU_CHARACTERISTIC_UUID, ["notify", "read"], service
        )
        self.add_descriptor(SensorDescriptor(self, "IMU Sensor Data"))

    def get_imu_data(self):
        # Randomized IMU data for 4 sensors (AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ)
        imu_data = [
            [random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(9.5, 9.8),
             random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)]
            for _ in range(4)
        ]
        flat_data = [item for sublist in imu_data for item in sublist]  # Flatten list
        return struct.pack(f"{len(flat_data)}f", *flat_data)

    def set_imu_callback(self):
        if self.notifying:
            value = self.get_imu_data()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": dbus.Array(value)}, [])
        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        value = self.get_imu_data()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": dbus.Array(value)}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_imu_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        return dbus.Array(self.get_imu_data())

class LaserCharacteristic(Characteristic):
    LASER_CHARACTERISTIC_UUID = "00000003-736c-4645-b520-7127aadf8c47"

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
            self, self.LASER_CHARACTERISTIC_UUID, ["notify", "read"], service
        )
        self.add_descriptor(SensorDescriptor(self, "Laser Sensor Data"))

    def get_laser_data(self):
        # Randomized Laser sensor data for 4 sensors (distances in meters)
        laser_data = [random.uniform(0.5, 5.0) for _ in range(4)]
        return struct.pack(f"{len(laser_data)}f", *laser_data)

    def set_laser_callback(self):
        if self.notifying:
            value = self.get_laser_data()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": dbus.Array(value)}, [])
        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return

        self.notifying = True
        value = self.get_laser_data()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": dbus.Array(value)}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_laser_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        return dbus.Array(self.get_laser_data())

class SensorDescriptor(Descriptor):
    DESCRIPTOR_UUID = "2901"

    def __init__(self, characteristic, description):
        Descriptor.__init__(self, self.DESCRIPTOR_UUID, ["read"], characteristic)
        self.description = description

    def ReadValue(self, options):
        value = []
        for c in self.description:
            value.append(dbus.Byte(c.encode()))
        return value

app = Application()
app.add_service(SensorService(0))
app.register()

adv = SensorAdvertisement(0)
adv.register()

try:
    app.run()
except KeyboardInterrupt:
    app.quit()

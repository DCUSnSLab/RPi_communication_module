# ble_server.py
import dbus
import struct
from utils.advertisement import Advertisement
from utils.service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
NOTIFY_TIMEOUT = 1000  # ms

class SensorAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("NeuraLoad")
        self.include_tx_power = True

class SensorService(Service):
    SENSOR_SVC_UUID = "00000001-736c-4645-b520-7127aadf8c47"

    def __init__(self, index, sensor_data):
        super().__init__(index, self.SENSOR_SVC_UUID, True)
        self.sensor_data = sensor_data  # 다른 Characteristic에서도 접근

        self.add_characteristic(IMUCharacteristic(self))
        self.add_characteristic(LaserCharacteristic(self))
        self.add_characteristic(WeightCharacteristic(self))

class IMUCharacteristic(Characteristic):
    IMU_CHARACTERISTIC_UUID = "00000002-736c-4645-b520-7127aadf8c47"

    def __init__(self, service):
        super().__init__(
            self.IMU_CHARACTERISTIC_UUID,
            ["notify", "read"],
            service
        )
        self.notifying = False
        self.add_descriptor(SensorDescriptor(self, "IMU Sensor Data"))

    def get_imu_data(self):
        imu_data = self.service.sensor_data.get_imu_data()
        flat_data = [val for row in imu_data for val in row]
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
        super().__init__(
            self.LASER_CHARACTERISTIC_UUID,
            ["notify", "read"],
            service
        )
        self.notifying = False
        self.add_descriptor(SensorDescriptor(self, "Laser Sensor Data"))

    def get_laser_data(self):
        laser_data = self.service.sensor_data.get_laser_data()
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

class WeightCharacteristic(Characteristic):
    WEIGHT_CHARACTERISTIC_UUID = "00000004-736c-4645-b520-7127aadf8c47"

    def __init__(self, service):
        super().__init__(
            self.WEIGHT_CHARACTERISTIC_UUID,
            ["notify", "read"],
            service
        )
        self.notifying = False
        self.add_descriptor(SensorDescriptor(self, "Estimated Weight"))

    def get_weight_data(self):
        weight = self.service.sensor_data.get_weight_data()
        return struct.pack("f", weight)

    def set_weight_callback(self):
        if self.notifying:
            value = self.get_weight_data()
            self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": dbus.Array(value)}, [])
        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        value = self.get_weight_data()
        self.PropertiesChanged(GATT_CHRC_IFACE, {"Value": dbus.Array(value)}, [])
        self.add_timeout(NOTIFY_TIMEOUT, self.set_weight_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        return dbus.Array(self.get_weight_data())

class SensorDescriptor(Descriptor):
    DESCRIPTOR_UUID = "2901"

    def __init__(self, characteristic, description):
        super().__init__(self.DESCRIPTOR_UUID, ["read"], characteristic)
        self.description = description

    def ReadValue(self, options):
        value = []
        for c in self.description:
            value.append(dbus.Byte(c.encode()))
        return value

def start_ble_server(sensor_data):
    """
    BLE 서버를 실행하는 함수.
    """
    app = Application()

    sensor_service = SensorService(0, sensor_data)
    app.add_service(sensor_service)
    app.register()

    adv = SensorAdvertisement(0)
    adv.register()

    print("BLE Server is running. Press Ctrl+C to stop.")
    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()

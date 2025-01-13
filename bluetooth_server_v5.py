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
        self.add_characteristic(DeviceIDCharacteristic(self))

#
# IMU
#
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
        """
        IMU 데이터를 [4 x 9 floats] = 36 floats 라고 가정.
        예) [[a1,a2,...,a9], [b1,b2,...,b9], ...] 형태
        """
        imu_data = self.service.sensor_data.get_imu_data()  # 2차원 리스트
        flat_data = [val for row in imu_data for val in row]
        return struct.pack(f"{len(flat_data)}f", *flat_data)  # bytes

    def set_imu_callback(self):
        if self.notifying:
            value = self.get_imu_data()
            # 바이트 배열을 제대로 넘기기 위해 dbus.ByteArray(...) 사용
            self.PropertiesChanged(
                GATT_CHRC_IFACE,
                {"Value": dbus.ByteArray(value)},
                []
            )
        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        value = self.get_imu_data()
        self.PropertiesChanged(
            GATT_CHRC_IFACE,
            {"Value": dbus.ByteArray(value)},
            []
        )
        self.add_timeout(NOTIFY_TIMEOUT, self.set_imu_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_imu_data()
        return dbus.ByteArray(value)

#
# Laser
#
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
        laser_data = self.service.sensor_data.get_laser_data()  # 예) 4 floats
        return struct.pack(f"{len(laser_data)}f", *laser_data)

    def set_laser_callback(self):
        if self.notifying:
            value = self.get_laser_data()
            self.PropertiesChanged(
                GATT_CHRC_IFACE,
                {"Value": dbus.ByteArray(value)},
                []
            )
        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        value = self.get_laser_data()
        self.PropertiesChanged(
            GATT_CHRC_IFACE,
            {"Value": dbus.ByteArray(value)},
            []
        )
        self.add_timeout(NOTIFY_TIMEOUT, self.set_laser_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_laser_data()
        return dbus.ByteArray(value)

#
# Weight
#
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
        weight = self.service.sensor_data.get_weight_data()  # float 1개
        return struct.pack("f", weight)

    def set_weight_callback(self):
        if self.notifying:
            value = self.get_weight_data()
            self.PropertiesChanged(
                GATT_CHRC_IFACE,
                {"Value": dbus.ByteArray(value)},
                []
            )
        return self.notifying

    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
        value = self.get_weight_data()
        self.PropertiesChanged(
            GATT_CHRC_IFACE,
            {"Value": dbus.ByteArray(value)},
            []
        )
        self.add_timeout(NOTIFY_TIMEOUT, self.set_weight_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        value = self.get_weight_data()
        return dbus.ByteArray(value)

#
# Device ID Characteristic (문자열)
#
class DeviceIDCharacteristic(Characteristic):
    DEVICE_ID_CHARACTERISTIC_UUID = "00000005-736c-4645-b520-7127aadf8c47"

    def __init__(self, service):
        super().__init__(
            self.DEVICE_ID_CHARACTERISTIC_UUID,
            ["read"],  # 필요에 따라 ["read", "notify"] 가능
            service
        )
        self.add_descriptor(SensorDescriptor(self, "Device ID"))

    def get_device_id_bytes(self):
        # 문자열 -> utf-8 인코딩 -> bytes
        device_id_str = self.service.sensor_data.get_device_id()
        return device_id_str.encode('utf-8')

    def ReadValue(self, options):
        device_id_bytes = self.get_device_id_bytes()
        # 문자열도 ByteArray로 전달
        return dbus.ByteArray(device_id_bytes)

#
# Descriptor
#
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

#
# 메인 함수
#
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

import dbus
import struct
import random
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
    # 기존 SensorService UUID
    SENSOR_SVC_UUID = "00000001-736c-4645-b520-7127aadf8c47"

    def __init__(self, index):
        Service.__init__(self, index, self.SENSOR_SVC_UUID, True)
        self.add_characteristic(IMUCharacteristic(self))
        self.add_characteristic(LaserCharacteristic(self))
        # 새로 추가된 WeightCharacteristic 등록
        self.add_characteristic(WeightCharacteristic(self))


class IMUCharacteristic(Characteristic):
    # IMU Characteristic UUID
    IMU_CHARACTERISTIC_UUID = "00000002-736c-4645-b520-7127aadf8c47"

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
            self,
            self.IMU_CHARACTERISTIC_UUID,
            ["notify", "read"],
            service
        )
        self.add_descriptor(SensorDescriptor(self, "IMU Sensor Data"))

    def get_imu_data(self):
        """
        예시:
        - 가속도 (AccelX, AccelY, AccelZ)
        - 자이로  (GyroX, GyroY, GyroZ)
        - 자기계  (MagX, MagY, MagZ)  <-- 추가됨
        총 9개 값 * 4개의 센서 = 36개 float
        """
        imu_data = []
        for _ in range(4):  # 4개의 센서
            accel_x = random.uniform(-1.0, 1.0)
            accel_y = random.uniform(-1.0, 1.0)
            accel_z = random.uniform(9.5, 9.8)  # 중력가속도 근사값
            gyro_x = random.uniform(-0.1, 0.1)
            gyro_y = random.uniform(-0.1, 0.1)
            gyro_z = random.uniform(-0.1, 0.1)
            mag_x = random.uniform(-50.0, 50.0)  # 예시 범위
            mag_y = random.uniform(-50.0, 50.0)
            mag_z = random.uniform(-50.0, 50.0)

            imu_data.append([
                accel_x, accel_y, accel_z,
                gyro_x, gyro_y, gyro_z,
                mag_x, mag_y, mag_z
            ])
        # 2차원 리스트 -> 1차원으로 평탄화
        flat_data = [item for sublist in imu_data for item in sublist]
        # float 개수만큼 packing
        return struct.pack(f"{len(flat_data)}f", *flat_data)

    def set_imu_callback(self):
        if self.notifying:
            value = self.get_imu_data()
            self.PropertiesChanged(
                GATT_CHRC_IFACE,
                {"Value": dbus.Array(value)},
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
            {"Value": dbus.Array(value)},
            []
        )
        self.add_timeout(NOTIFY_TIMEOUT, self.set_imu_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        return dbus.Array(self.get_imu_data())


class LaserCharacteristic(Characteristic):
    # Laser Characteristic UUID
    LASER_CHARACTERISTIC_UUID = "00000003-736c-4645-b520-7127aadf8c47"

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
            self,
            self.LASER_CHARACTERISTIC_UUID,
            ["notify", "read"],
            service
        )
        self.add_descriptor(SensorDescriptor(self, "Laser Sensor Data"))

    def get_laser_data(self):
        # 랜덤 Laser sensor 데이터 (4개 센서, 거리값)
        laser_data = [random.uniform(0.5, 5.0) for _ in range(4)]
        return struct.pack(f"{len(laser_data)}f", *laser_data)

    def set_laser_callback(self):
        if self.notifying:
            value = self.get_laser_data()
            self.PropertiesChanged(
                GATT_CHRC_IFACE,
                {"Value": dbus.Array(value)},
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
            {"Value": dbus.Array(value)},
            []
        )
        self.add_timeout(NOTIFY_TIMEOUT, self.set_laser_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        return dbus.Array(self.get_laser_data())


class WeightCharacteristic(Characteristic):
    """
    추정 무게 데이터를 전송하기 위한 새로운 특성.
    원하시는 방식대로 여러 개 데이터를 보낼 수도 있고,
    여기서는 단일 float 값으로 예시를 들었습니다.
    """
    WEIGHT_CHARACTERISTIC_UUID = "00000004-736c-4645-b520-7127aadf8c47"

    def __init__(self, service):
        self.notifying = False
        Characteristic.__init__(
            self,
            self.WEIGHT_CHARACTERISTIC_UUID,
            ["notify", "read"],
            service
        )
        self.add_descriptor(SensorDescriptor(self, "Estimated Weight"))

    def get_weight_data(self):
        # 예: 50 ~ 100 kg 범위를 랜덤으로 추정
        weight = random.uniform(50.0, 100.0)
        return struct.pack("f", weight)

    def set_weight_callback(self):
        if self.notifying:
            value = self.get_weight_data()
            self.PropertiesChanged(
                GATT_CHRC_IFACE,
                {"Value": dbus.Array(value)},
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
            {"Value": dbus.Array(value)},
            []
        )
        self.add_timeout(NOTIFY_TIMEOUT, self.set_weight_callback)

    def StopNotify(self):
        self.notifying = False

    def ReadValue(self, options):
        return dbus.Array(self.get_weight_data())


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


# 애플리케이션/광고 등록
app = Application()
app.add_service(SensorService(0))
app.register()

adv = SensorAdvertisement(0)
adv.register()

try:
    app.run()
except KeyboardInterrupt:
    app.quit()

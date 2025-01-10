# sensor_data.py

class SensorData:
    """
    실제 센서에서 얻은 데이터를 임시로 저장해 두고,
    BLE 서버가 필요 시 가져갈 수 있도록 관리하는 클래스.
    아래 예시에서는 IMU, Laser, Weight 데이터를
    각각 set/get 메서드로 업데이트할 수 있게 했습니다.
    """

    def __init__(self):
        # IMU: 4개의 센서 * 9개 float (AccelX,Y,Z + GyroX,Y,Z + MagX,Y,Z) 
        # 기본값(0.0)으로 초기화
        self._imu_data = [[0.0]*9 for _ in range(4)]

        # Laser: 4개 센서 (거리값) 
        self._laser_data = [0.0]*4

        # Weight: 단일 float
        self._weight_data = 0.0

    # -----------------------
    # IMU
    # -----------------------
    def set_imu_data(self, new_data):
        """
        new_data 형식 예시 (4x9 형태):
        [
          [aX, aY, aZ, gX, gY, gZ, mX, mY, mZ],  # 센서1
          [ ... ],                             # 센서2
          ...
        ]
        """
        self._imu_data = new_data

    def get_imu_data(self):
        return self._imu_data

    # -----------------------
    # Laser
    # -----------------------
    def set_laser_data(self, new_data):
        """
        new_data 형식 예시(길이 4 리스트): [값1, 값2, 값3, 값4]
        """
        self._laser_data = new_data

    def get_laser_data(self):
        return self._laser_data

    # -----------------------
    # Weight
    # -----------------------
    def set_weight_data(self, weight):
        """ weight는 단일 float """
        self._weight_data = weight

    def get_weight_data(self):
        return self._weight_data

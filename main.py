import threading
import time
import random

from utils.sensor_data import SensorData
from bluetooth_server_v3 import start_ble_server

def update_loop(sensor_data):
    while True:
        '''
        # 예시 IMU 데이터 (센서4개, 각 9개 값)
        new_imu = [
            [1.0, 0.5, 9.8, 0.01, 0.0, -0.02, 10.0,  5.0,  -8.0],  # 센서1
            [0.9, 0.2, 9.7, 0.02, 0.1,  0.01,  15.0, -3.2,  12.0], # 센서2
            [ ... ],  # 센서3
            [ ... ],  # 센서4
        ]
        sensor_data.set_imu_data(new_imu)

        new_laser = [2.1, 3.2, 4.5, 5.0]
        sensor_data.set_laser_data(new_laser)

        new_weight = 73.2
        sensor_data.set_weight_data(new_weight)
        '''
        # 랜덤 IMU 데이터 (센서4개, 각 9개 값: AccelX, AccelY, AccelZ, GyroX, GyroY, GyroZ, MagX, MagY, MagZ)
        new_imu = [
            [
                random.uniform(-1.0, 1.0),  # AccelX
                random.uniform(-1.0, 1.0),  # AccelY
                random.uniform(9.5, 9.8),  # AccelZ (중력가속도 근사값)
                random.uniform(-0.1, 0.1),  # GyroX
                random.uniform(-0.1, 0.1),  # GyroY
                random.uniform(-0.1, 0.1),  # GyroZ
                random.uniform(-50.0, 50.0),  # MagX
                random.uniform(-50.0, 50.0),  # MagY
                random.uniform(-50.0, 50.0),  # MagZ
            ]
            for _ in range(4)  # 센서4개
        ]
        sensor_data.set_imu_data(new_imu)

        # 랜덤 Laser 데이터 (센서4개, 거리값 0.5~5.0m)
        new_laser = [random.uniform(0.5, 5.0) for _ in range(4)]
        sensor_data.set_laser_data(new_laser)

        # 랜덤 Weight 데이터 (무게 50~100kg)
        new_weight = random.uniform(50.0, 100.0)
        sensor_data.set_weight_data(new_weight)

        # 1초마다 업데이트
        time.sleep(1.0)

def main():
    # 공용 SensorData 객체 생성
    sensor_data = SensorData()

    # update_loop를 스레드로 동작시킴 (데몬 스레드로 설정도 가능)
    updater_thread = threading.Thread(target=update_loop, args=(sensor_data,))
    updater_thread.daemon = True
    updater_thread.start()

    # BLE 서버 실행 (메인 스레드에서)
    start_ble_server(sensor_data)

if __name__ == "__main__":
    main()

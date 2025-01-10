# Raspberry pi BLE communication module


## 사용법

라즈베리파이 BLE 설정 필요

### BLE 서버 실행

1. **서버 시작**
   ```bash
   python main.py
   ```

2. **BLE 서버 동작**
   - "NeuraLoad"라는 이름으로 BLE 광고를 시작합니다.
   - IMU, Laser, Weight 데이터를 BLE Characteristic으로 제공합니다.
   - 데이터는 1초마다 갱신됩니다.


3. **데이터 예시**
   BLE 서버는 다음과 같은 형식의 데이터를 주기적으로 전송합니다:
   ```python
       # 예시 IMU 데이터 (센서4개, 각 9개 값)
       new_imu = [
           [1.0, 0.5, 9.8, 0.01, 0.0, -0.02, 10.0,  5.0,  -8.0],  # 센서1
           [0.9, 0.2, 9.7, 0.02, 0.1,  0.01,  15.0, -3.2,  12.0], # 센서2
           [0.3, -0.1, 9.6, 0.03, -0.05, 0.02, -5.0, 8.0, -11.0],  # 센서3
           [0.7, 0.4, 9.5, -0.02, 0.03, 0.00, 20.0, -2.0,  7.0],  # 센서4
       ]
       sensor_data.set_imu_data(new_imu)

       new_laser = [2.1, 3.2, 4.5, 5.0]
       sensor_data.set_laser_data(new_laser)

       new_weight = 73.2
       sensor_data.set_weight_data(new_weight)
   ```

4. **서버 시작**
   ```bash
   python main.py
   ```

5. **BLE 서버 동작**
   - "NeuraLoad"라는 이름으로 BLE 광고를 시작합니다.
   - IMU, Laser, Weight 데이터를 BLE Characteristic으로 제공합니다.
   - 데이터는 1초마다 갱신됩니다.

6. 실행 중 로그를 통해 BLE 상태 및 센서 데이터 갱신 상황을 확인할 수 있습니다.

---



### BLE 클라이언트로 테스트

BLE 서버를 테스트하려면 아래 클라이언트를 사용할 수 있습니다:

- **Android**: [nRF Connect](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp)

- **iOS**: [LightBlue](https://apps.apple.com/us/app/lightblue-explorer/id557428110)

- **커스텀 앱**: [NeuraLoadAPP](https://github.com/DCUSnSLab/NeuraLoadAPP)

1. BLE 클라이언트 앱을 실행합니다.
2. "NeuraLoad" 장치를 검색하여 연결합니다.
3. IMU, Laser, Weight Characteristics를 탐색합니다.
4. Notifications를 구독하여 실시간 데이터를 수신합니다.

---

## 코드 구조

```
root/
├── script/
│   ├── utils/
│   │   ├── advertisement.py   # BLE 광고 관련 기능
│   │   ├── bletools.py        # BLE 도구 및 유틸리티
│   │   ├── sensor_data.py     # 센서 데이터 관리
│   │   ├── service.py         # BLE 서비스 정의
│   ├── bluetooth_server.py    # BLE 서버 버전 1 (단독 사용 가능)
│   ├── bluetooth_server_v2.py # BLE 서버 버전 2 (단독 사용 가능)
│   ├── bluetooth_server_v3.py # BLE 서버 메인 파일
│   ├── main.py                # 프로젝트 진입점
├── .gitignore                 
├── README.md                  
├── requirements.txt           # 의존성 패키지 목록
```



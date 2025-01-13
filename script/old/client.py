"""
다른 장치에서 테스트용으로 실행할 것
"""

import asyncio
from bleak import BleakScanner, BleakClient

IMU_CHARACTERISTIC_UUID = "00000002-736c-4645-b520-7127aadf8c47"
LASER_CHARACTERISTIC_UUID = "00000003-736c-4645-b520-7127aadf8c47"
WEIGHT_CHARACTERISTIC_UUID = "00000004-736c-4645-b520-7127aadf8c47"
DEVICE_ID_CHARACTERISTIC_UUID = "00000005-736c-4645-b520-7127aadf8c47"

async def main():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()

    for i, device in enumerate(devices):
        print(f"[{i}] {device.name} ({device.address})")

    device_index = int(input("Select the device index: "))
    target_device = devices[device_index]

    print(f"Connecting to {target_device.name} ({target_device.address})...")
    async with BleakClient(target_device.address) as client:
        print("Connected.")

        # Read IMU Data
        imu_data = await client.read_gatt_char(IMU_CHARACTERISTIC_UUID)
        imu_values = struct.unpack(f"{len(imu_data)//4}f", imu_data)
        print(f"IMU Data: {imu_values}")

        # Read Laser Data
        laser_data = await client.read_gatt_char(LASER_CHARACTERISTIC_UUID)
        laser_values = struct.unpack(f"{len(laser_data)//4}f", laser_data)
        print(f"Laser Data: {laser_values}")

        # Read Weight Data
        weight_data = await client.read_gatt_char(WEIGHT_CHARACTERISTIC_UUID)
        weight_value = struct.unpack("f", weight_data)[0]
        print(f"Weight Data: {weight_value}")

        # Read Device ID
        device_id_data = await client.read_gatt_char(DEVICE_ID_CHARACTERISTIC_UUID)
        device_id = device_id_data.decode('utf-8')
        print(f"Device ID: {device_id}")

if __name__ == "__main__":
    asyncio.run(main())

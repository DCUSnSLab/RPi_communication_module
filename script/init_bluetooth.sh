#!/bin/bash

# 쉘 스크립트 시작
set -e  # 에러 발생 시 스크립트 중단

# Bluetooth 서비스 파일 경로
SERVICE_FILE="/lib/systemd/system/bluetooth.service"

# Experimental 모드 옵션 추가
EXPERIMENTAL_FLAG="--experimental"

# Experimental 옵션 추가 확인 및 수정
if grep -q "$EXPERIMENTAL_FLAG" "$SERVICE_FILE"; then
    echo "Experimental mode is already enabled in $SERVICE_FILE"
else
    echo "Enabling Experimental mode in $SERVICE_FILE..."
    sudo sed -i "s|ExecStart=.*|& $EXPERIMENTAL_FLAG|" "$SERVICE_FILE"
    echo "Experimental mode added to $SERVICE_FILE"
fi

# systemd 데몬 재로드 및 Bluetooth 데몬 재시작
echo "Reloading systemd daemon and restarting bluetooth service..."
sudo systemctl daemon-reload
sudo systemctl restart bluetooth

# Bluetooth 서비스 상태 확인
sudo systemctl status bluetooth --no-pager

echo "Bluetooth Experimental mode is now enabled."


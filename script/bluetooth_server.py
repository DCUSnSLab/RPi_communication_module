class SensorCharacteristic(dbus.service.Object):
    def __init__(self, bus, index, uuid, service):
        self.path = service.get_path() + '/char' + str(index)
        self.bus = bus
        self.uuid = uuid
        self.service = service
        self.value = []
        self.notifying = False
        dbus.service.Object.__init__(self, bus, self.path)

    def _update_value_loop(self):
        """Notify를 통해 주기적으로 데이터 전송"""
        def run():
            while self.notifying:
                # 센서 데이터 생성 (여기서는 단순 예제)
                sensor_data = "Hello from Raspberry Pi"
                self.value = [dbus.Byte(c) for c in sensor_data.encode('utf-8')]

                # Notify 활성화된 클라이언트로 데이터 전송
                self.PropertiesChanged(
                    GATT_CHRC_IFACE,
                    {'Value': self.value},
                    []
                )
                print(f"Sent: {sensor_data}")

                # 전송 주기 (1초)
                time.sleep(1)

        t = threading.Thread(target=run)
        t.start()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='a{sv}')
    def StartNotify(self, options):
        if self.notifying:
            print("Already notifying")
            return
        self.notifying = True
        self._update_value_loop()

    @dbus.service.method(GATT_CHRC_IFACE, in_signature='a{sv}')
    def StopNotify(self, options):
        if not self.notifying:
            print("Not notifying")
            return
        self.notifying = False

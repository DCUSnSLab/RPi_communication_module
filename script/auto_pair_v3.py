import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

# BlueZ Agent Path 및 설정
AGENT_PATH = "/test/agent"
CAPABILITY = "NoInputNoOutput"  # Just Works 방식

class Agent(dbus.service.Object):
    def __init__(self):
        super().__init__(bus, AGENT_PATH)

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Release(self):
        print("Agent Released")

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print(f"RequestAuthorization for {device}")
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print(f"RequestPinCode for {device}")
        return "0000"  # 고정된 PIN 코드

    @dbus.service.method("org.bluez.Agent1", in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print(f"RequestConfirmation for {device}, Passkey: {passkey}")
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print(f"RequestPasskey for {device}")
        return dbus.UInt32(123456)

def register_agent():
    agent = Agent()
    manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"), "org.bluez.AgentManager1")
    manager.RegisterAgent(AGENT_PATH, CAPABILITY)
    manager.RequestDefaultAgent(AGENT_PATH)
    print("Agent registered and set as default")

if __name__ == "__main__":
    try:
        register_agent()
        print("자동 페어링 에이전트 실행 중...")
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        print("종료 중...")

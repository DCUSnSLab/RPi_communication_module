import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import subprocess

BUS_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
ADAPTER_ROOT = '/org/bluez/hci'
AGENT_IFACE = 'org.bluez.Agent1'
AGNT_MNGR_IFACE = 'org.bluez.AgentManager1'
AGENT_PATH = '/my/app/agent'
AGNT_MNGR_PATH = '/org/bluez'
CAPABILITY = 'KeyboardDisplay'
DEVICE_IFACE = 'org.bluez.Device1'
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

def set_trusted(path):
    props = dbus.Interface(bus.get_object(BUS_NAME, path), dbus.PROPERTIES_IFACE)
    props.Set(DEVICE_IFACE, "Trusted", True)

class Agent(dbus.service.Object):

    @dbus.service.method(AGENT_IFACE,
                         in_signature="", out_signature="")
    def Release(self):
        print("Release")

    @dbus.service.method(AGENT_IFACE,
                         in_signature='o', out_signature='s')
    def RequestPinCode(self, device):
        print(f'RequestPinCode {device}')
        return '0000'

    @dbus.service.method(AGENT_IFACE,
                         in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        set_trusted(device)
        return

    @dbus.service.method(AGENT_IFACE,
                         in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization (%s)" % (device))
        auth = input("Authorize? (yes/no): ")
        if (auth == "yes"):
            return
        raise Rejected("Pairing rejected")

    @dbus.service.method(AGENT_IFACE,
                         in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        print("RequestPasskey (%s)" % (device))
        set_trusted(device)
        passkey = input("Enter passkey: ")
        return dbus.UInt32(passkey)

    @dbus.service.method(AGENT_IFACE,
                         in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey (%s, %06u entered %u)" %
              (device, passkey, entered))

    @dbus.service.method(AGENT_IFACE,
                         in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))


class Adapter:
    def __init__(self, idx=0):
        bus = dbus.SystemBus()
        self.path = f'{ADAPTER_ROOT}{idx}'
        self.adapter_object = bus.get_object(BUS_NAME, self.path)
        self.adapter_props = dbus.Interface(self.adapter_object,
                                            dbus.PROPERTIES_IFACE)
        self.adapter_props.Set(ADAPTER_IFACE, 'DiscoverableTimeout', dbus.UInt32(0))
        self.adapter_props.Set(ADAPTER_IFACE, 'Discoverable', True)
        self.adapter_props.Set(ADAPTER_IFACE, 'PairableTimeout', dbus.UInt32(0))
        self.adapter_props.Set(ADAPTER_IFACE, 'Pairable', True)
        
        # BLE Advertising 모드 활성화
        self.enable_ble_advertising()

    def enable_ble_advertising(self):
        try:
            # Bluetooth 장치 활성화
            subprocess.run(["sudo", "hciconfig", "hci0", "up"], check=True)
            # BLE Advertising 모드 활성화
            subprocess.run(["sudo", "hciconfig", "hci0", "leadv", "3"], check=True)
            print("BLE Advertising 모드가 활성화되었습니다.")
        except subprocess.CalledProcessError as e:
            print("BLE Advertising 설정에 실패했습니다:", e)


if __name__ == '__main__':
    agent = Agent(bus, AGENT_PATH)
    agnt_mngr = dbus.Interface(bus.get_object(BUS_NAME, AGNT_MNGR_PATH),
                               AGNT_MNGR_IFACE)
    agnt_mngr.RegisterAgent(AGENT_PATH, CAPABILITY)
    agnt_mngr.RequestDefaultAgent(AGENT_PATH)

    adapter = Adapter()
    mainloop = GLib.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        agnt_mngr.UnregisterAgent(AGENT_PATH)
        mainloop.quit()


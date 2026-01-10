import dbus.service

AGENT_PATH = "/bluetooth/agent"

class AutoAcceptAgent(dbus.service.Object):
    def __init__(self, bus):
        super().__init__(bus, AGENT_PATH)

    @dbus.service.method("org.bluez.Agent1")
    def Release(self):
        pass

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        return "0000"

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        return 0

    @dbus.service.method("org.bluez.Agent1", in_signature="ou")
    def DisplayPasskey(self, device, passkey):
        pass

    @dbus.service.method("org.bluez.Agent1", in_signature="os")
    def DisplayPinCode(self, device, pincode):
        pass

    @dbus.service.method("org.bluez.Agent1", in_signature="ou")
    def RequestConfirmation(self, device, passkey):
        # AUTO-ACCEPT
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="o")
    def AuthorizeService(self, device, uuid):
        # AUTO-AUTHORIZE A2DP / AVRCP
        return

    @dbus.service.method("org.bluez.Agent1")
    def Cancel(self):
        pass

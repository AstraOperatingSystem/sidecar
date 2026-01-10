from dataclasses import dataclass
from asyncio import sleep

import dbus

@dataclass
class WifiNetwork:
    ssid: str
    strength: float

class WiFiManager:
    def __init__(self) -> None:
        self.bus = dbus.SystemBus()
        self.nm = self.bus.get_object(
            "org.freedesktop.NetworkManager",
            "/org/freedesktop/NetworkManager"
        )
        self.nm_iface = dbus.Interface(
            self.nm, "org.freedesktop.NetworkManager"
        )
        self.wifi_device = None
        self._select_device()

    def _select_device(self) -> None:
        devices = self.nm_iface.GetDevices()
        wifi_device = None
        for dev_path in devices:
            dev = self.bus.get_object("org.freedesktop.NetworkManager", dev_path)
            dev_props = dbus.Interface(dev, "org.freedesktop.DBus.Properties")
            dev_type = dev_props.Get("org.freedesktop.NetworkManager.Device", "DeviceType")

            if dev_type == 2: # WiFi
                wifi_device = dev
                print(dev_path)
                break

        if not wifi_device:
            raise RuntimeError("No WiFi device found")

        self.wifi_device = wifi_device
        self.wifi_iface = dbus.Interface(
            wifi_device,
            "org.freedesktop.NetworkManager.Device.Wireless"
        )

    async def scan(self) -> list[WifiNetwork]:
        networks: list[WifiNetwork] = []

        self.wifi_iface.RequestScan({})
        await sleep(3)
        aps = self.wifi_iface.GetAccessPoints()

        for ap_path in aps:
            ap = self.bus.get_object("org.freedesktop.NetworkManager", ap_path)
            ap_props = dbus.Interface(ap, "org.freedesktop.DBus.Properties")
            
            strength = int(ap_props.Get(
                "org.freedesktop.NetworkManager.AccessPoint",
                "Strength"
            ))
            
            if strength < 50: continue

            ssid = ap_props.Get(
                "org.freedesktop.NetworkManager.AccessPoint",
                "Ssid"
            )
            
            ssid_str = bytes(ssid).decode(errors="ignore")
            networks.append(WifiNetwork(ssid_str, strength))

        return networks
    


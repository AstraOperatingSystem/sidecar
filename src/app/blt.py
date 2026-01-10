from dataclasses import dataclass
from asyncio import sleep

import dbus
from dbus.mainloop.glib import DBusGMainLoop

from .blt_agent import AGENT_PATH, AutoAcceptAgent

class BltManager:
	def __init__(self) -> None:
		self.bus = dbus.SystemBus()
		self.bluez = self.bus.get_object(
			"org.bluez",
			"/"
		)
		self.adapter = self.bus.get_object(
			"org.bluez", "/org/bluez/hci0"
		)
		self.adapter_props = dbus.Interface(
			self.adapter, "org.freedesktop.DBus.Properties"
		)
		self._setup_agent()

	def _setup_agent(self) -> None:
		agent = AutoAcceptAgent(self.bus)
		self.manager = dbus.Interface(
			self.bus.get_object("org.bluez", "/org/bluez"),
			"org.bluez.AgentManager1"
		)
		self.manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
		self.manager.RequestDefaultAgent(AGENT_PATH)
		self.bus.add_signal_receiver(
			self._interfaces_added,
			dbus_interface="org.freedesktop.DBus.ObjectManager",
			signal_name="InterfacesAdded"
		)

	def _interfaces_added(self, path, interfaces):
		if "org.bluez.Device1" not in interfaces:
			return

		device = self.bus.get_object("org.bluez", path)
		props = dbus.Interface(device, "org.freedesktop.DBus.Properties")
		props.Set("org.bluez.Device1", "Trusted", True)

	@property
	def powered(self) -> bool:
		return self.adapter_props.Get("org.bluez.Adapter1", "Powered")

	@powered.setter
	def powered(self, value: bool):
		self.adapter_props.Set("org.bluez.Adapter1", "Powered", value)

	@property
	def discoverable(self) -> bool:
		return self.adapter_props.Get("org.bluez.Adapter1", "Discoverable")
	
	@discoverable.setter
	def discoverable(self, value: bool):
		self.adapter_props.Set("org.bluez.Adapter1", "Discoverable", value)

	@property
	def pairable(self) -> bool:
		return self.adapter_props.Get("org.bluez.Adapter1", "Pairable")
	
	@pairable.setter
	def pairable(self, value: bool):
		self.adapter_props.Set("org.bluez.Adapter1", "Pairable", value)

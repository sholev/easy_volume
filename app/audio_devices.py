from ctypes import POINTER, cast

import pycaw.utils
from comtypes import (CoCreateInstance, CLSCTX_ALL, CLSCTX_INPROC_SERVER,
                      COMError)
from pycaw.constants import CLSID_MMDeviceEnumerator
from pycaw.pycaw import (AudioUtilities, IAudioEndpointVolume,
                         IMMDeviceEnumerator, EDataFlow, IMMEndpoint,
                         AudioDeviceState)


class AudioDevice:
    def __init__(self, audio_device: pycaw.utils.AudioDevice):
        self.audio_device: pycaw.utils.AudioDevice = audio_device
        self.volume_control_endpoint = None

    def __str__(self):
        return (f"id: {self.audio_device.id}"
                f", state: {self.get_state().name}"  # pycaw.pycaw DEVICE_STATE
                f", mute: {self.get_mute()}"
                f", volume_level: {self.get_volume_level()}"
                f", flow: {self.get_data_flow()}"
                f", friendly_name: {self.get_friendly_name()}")

    def get_property(self, key):
        return self.audio_device.properties.get(key)

    def get_friendly_name(self) -> str:
        return self.audio_device.FriendlyName

    def get_device_name(self) -> str:
        key = '{026E516E-B814-414B-83CD-856D6FEF4822} 2'
        return self.get_property(key)

    def get_device_type(self) -> str:
        key = '{A45C254E-DF1C-4EFD-8020-67D146A850E0} 2'
        return self.get_property(key)

    def get_state(self):
        return self.audio_device.state

    def get_data_flow(self) -> str:
        try:
            device_enumerator = CoCreateInstance(
                CLSID_MMDeviceEnumerator,
                IMMDeviceEnumerator,
                CLSCTX_INPROC_SERVER
            )

            device_pointer = device_enumerator.GetDevice(self.audio_device.id)
            endpoint_pointer = device_pointer.QueryInterface(IMMEndpoint)
            data_flow = endpoint_pointer.GetDataFlow()

            if data_flow == EDataFlow.eRender.value:
                return "Output"
            if data_flow == EDataFlow.eCapture.value:
                return "Input"
            if data_flow == EDataFlow.eAll.value:
                return "All"
            return "Unknown"
        except COMError:
            return "Unknown"

    def try_get_volume_control(self) -> POINTER(IAudioEndpointVolume):
        if self.volume_control_endpoint is not None:
            return self.volume_control_endpoint

        try:
            device_enumerator = CoCreateInstance(
                CLSID_MMDeviceEnumerator,
                IMMDeviceEnumerator,
                CLSCTX_INPROC_SERVER
            )

            device_pointer = device_enumerator.GetDevice(self.audio_device.id)
            interface = device_pointer.Activate(
                getattr(IAudioEndpointVolume, '_iid_'),
                CLSCTX_ALL,
                None
            )
            self.volume_control_endpoint = cast(
                interface,
                POINTER(IAudioEndpointVolume)
            )
            return self.volume_control_endpoint
        except COMError:
            return None

    def get_mute(self):
        volume = self.try_get_volume_control()
        return volume.GetMute() if volume is not None else None

    def set_mute(self, is_muted: bool):
        volume = self.try_get_volume_control()
        if volume is not None:
            volume.SetMute(1 if is_muted else 0, None)

    def get_volume_level(self):
        volume = self.try_get_volume_control()
        if volume is None:
            return None

        return int(0.5 + 100.0 * volume.GetMasterVolumeLevelScalar())

    def set_volume_level(self, volume_level):
        volume = self.try_get_volume_control()
        if volume is not None:
            volume_level = max(min(100.0, volume_level), 0.0)
            volume.SetMasterVolumeLevelScalar(volume_level / 100.0, None)


class AudioDevices:
    @staticmethod
    def get_all_devices() -> list[AudioDevice]:
        devices_list = AudioUtilities.GetAllDevices()

        return [AudioDevice(d) for d in devices_list]

    @staticmethod
    def get_device_states_list():
        return [s.name for s in AudioDeviceState]


if __name__ == "__main__":
    devices = AudioDevices.get_all_devices()
    for i, device in enumerate(devices):
        print(i, device)

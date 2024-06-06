import customtkinter as ctk
import customtkinter_extensions as ctk_e

from audio_devices import AudioDevices, AudioDevice
from config import config

TXT_MUTE = {
    True: "🔈",
    False: "🔊"
}


class AudioDevicesWindow(ctk_e.CTkToplevel):
    def __init__(self, *args, title='Audio Devices', **kwargs):
        super().__init__(*args, **kwargs)
        self.title_txt = title
        self.title(title)

        self.grid_rowconfigure((0, 2), weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.audio_devices = self.get_audio_devices_grouped()
        self.audio_devices = self.sort_audio_devices(self.audio_devices)
        self.label = None
        self.scroll_frame = None
        self.visibility_label = None
        self.states_combo_box = None
        self.build_widgets()

    @staticmethod
    def sort_audio_devices(audio_devices: dict[str, list[AudioDevice]]):
        if config.get('audio_devices_order') is None:
            config.set('audio_devices_order', list(audio_devices.keys()))

        order = config.get('audio_devices_order')
        for k in audio_devices:
            if k not in order:
                order.append(k)

        return {k: audio_devices[k] for k in order if k in audio_devices}

    @staticmethod
    def get_audio_devices_grouped() -> dict[str, list[AudioDevice]]:
        audio_devices = AudioDevices.get_all_devices()
        devices_per_type = {}
        for device in audio_devices:
            device_name = device.get_device_name()
            devices_per_type.setdefault(device_name, []).append(device)

        return devices_per_type

    def build_widgets(self):
        self.label = ctk.CTkLabel(
            self, text="Audio Devices", anchor="center",
            font=('TkDefaultFont', 18))
        self.label.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.scroll_frame = self.create_scroll_frame(self.audio_devices)

        self.visibility_label = ctk.CTkLabel(self, text="Show:")
        self.visibility_label.grid(row=0, column=1, pady=0, padx=5)

        device_states = AudioDevices.get_device_states_list()
        self.states_combo_box = ctk.CTkComboBox(
            self, values=device_states, command=self.on_state_selected)
        self.states_combo_box.grid(row=0, column=2, pady=0, padx=5)
        self.states_combo_box.set(device_states[0])
        self.states_combo_box.bind('<Return>', self.on_state_selected)
        if config.get('selected_device_state') is not None:
            self.states_combo_box.set(config.get('selected_device_state'))
        self.on_state_selected(self.states_combo_box.get())

    def destroy_widgets(self):
        self.scroll_frame.destroy()
        self.states_combo_box.destroy()
        self.visibility_label.destroy()
        self.label.destroy()

    def on_state_selected(self, _: str):
        value = self.states_combo_box.get()
        self.scroll_frame.on_state_selected(value)
        self.focus_set()
        config.set('selected_device_state', value)

    def create_scroll_frame(self, audio_devices):
        frame = AudioDevicesFrame(self, audio_devices=audio_devices)
        frame.grid(row=1, column=0, columnspan=3, sticky='nsew')

        return frame

    def reload(self):
        self.after(0, self._reload)

    def _reload(self):
        self.withdraw()
        self.destroy_widgets()
        self.build_widgets()
        self.deiconify()


class AudioDevicesFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, audio_devices: dict[AudioDevice], **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color=('gray72', 'gray22'))
        self.grid_columnconfigure(0, weight=1)

        self.audio_devices = audio_devices
        self.audio_device_frames = self.create_frames()

        self.draw_frames_grid()

    def create_frames(self):
        frames = []
        for name, devices in self.audio_devices.items():
            frame = DeviceFrame(
                self, title=name, devices=devices, on_move=self.on_move_frame
            )
            frames.append(frame)

        return frames

    def draw_frames_grid(self, start_row=1):
        for i, frame in enumerate(self.audio_device_frames):
            frame.grid(
                row=start_row + i, column=0, padx=10, pady=10, sticky="nsew"
            )

    def on_state_selected(self, event: str):
        for frame in self.audio_device_frames:
            frame.on_state_selected(event)

    def sort_and_draw_frames_grid(self):
        devices_order = config.get('audio_devices_order')
        self.audio_device_frames = sorted(
            self.audio_device_frames,
            key=lambda f: devices_order.index(f.title)
        )

        self.draw_frames_grid()

    def on_move_frame(self, option: str, title: str):
        if option == 'Top':
            devices_order = config.get('audio_devices_order')
            devices_order.remove(title)
            devices_order.insert(0, title)
        elif option == 'Bottom':
            devices_order = config.get('audio_devices_order')
            devices_order.remove(title)
            devices_order.append(title)

        self.sort_and_draw_frames_grid()
        self.on_state_selected(config.get('selected_device_state'))


class DeviceFrame(ctk_e.CTkVisibilityGridFrame):
    def __init__(self, master, title: str, devices: list[AudioDevice], on_move,
                 **kwargs):
        super().__init__(master, **kwargs)

        self.devices = devices

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.title = title
        self.title_label = ctk.CTkLabel(self, text=title)
        self.title_label.grid(row=0, column=0, padx=10, pady=1, sticky='w')

        self.move_option_menu = ctk.CTkOptionMenu(
            self, width=80, values=['Top', 'Bottom'],
            command=lambda option: on_move(option, self.title)
        )
        self.move_option_menu.grid(row=0, column=1, padx=10, pady=1,
                                   sticky='e')
        self.move_option_menu.set('Move')

        sliders_per_flow = {}
        for device in devices:
            flow = device.get_data_flow()
            sliders_per_flow.setdefault(flow, []).append(device)

        self.flow_frames = []
        for flow, flow_devices in sliders_per_flow.items():
            count = len(self.flow_frames)
            frame = FlowFrame(self, title=flow, devices=flow_devices)
            frame.grid(row=1 + count, column=0, columnspan=2, padx=0, pady=1,
                       sticky="ew")
            self.flow_frames.append(frame)

    def on_state_selected(self, event: str):
        self.is_visible = False
        for frame in self.flow_frames:
            frame.on_state_selected(event)
            if frame.is_visible:
                self.is_visible = True

        self.set_visibility(self.is_visible)


class FlowFrame(ctk_e.CTkVisibilityGridFrame):
    def __init__(self, master, title: str, devices: list[AudioDevice],
                 **kwargs):
        super().__init__(master, **kwargs)

        self.devices = devices

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text=title)
        self.label.grid(row=0, column=0, padx=10, pady=0, sticky='ew')

        self.sliders = []
        for i, d in enumerate(devices):
            slider = SliderFrame(self, device=d)
            slider.grid(row=i + 1, column=0, pady=1, sticky='ew')
            self.sliders.append(slider)

    def on_state_selected(self, event: str):
        self.is_visible = False
        for slider in self.sliders:
            slider.on_state_selected(event)
            if slider.is_visible:
                self.is_visible = True

        self.set_visibility(self.is_visible)


class SliderFrame(ctk_e.CTkVisibilityGridFrame):
    def __init__(self, master, device: AudioDevice, **kwargs):
        super().__init__(master, **kwargs)

        self.device = device

        self.configure(fg_color=('gray78', 'gray28'))

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=device.get_friendly_name())
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=1,
                        sticky='e')

        self.btn_mute = None
        self.slider = None
        self.level = self.device.get_volume_level()
        if self.level is not None:
            self.level = int(self.level)
            self.btn_mute = ctk.CTkButton(
                self, text=self.get_btn_text(), width=32, height=32,
                command=self.on_mute, font=('TkDefaultFont', 16))
            self.btn_mute.grid(row=1, column=0, padx=3, pady=3)

            self.slider = ctk.CTkSlider(
                self, from_=0, to=100, command=self.on_slide)
            self.slider.grid(row=1, column=1, padx=(0, 3), pady=3, sticky='ew')
            self.slider.set(self.level)

            self.vol_label = ctk.CTkLabel(
                self, width=45, height=32,
                fg_color=('gray68', 'gray38'),
                corner_radius=6
            )
            self.vol_label.grid(row=1, column=2, padx=3, pady=3)
            self.vol_label.configure(text=self.level)

    def on_slide(self, val):
        if self.level == int(val):
            return

        self.level = int(val)
        self.device.set_volume_level(self.level)
        self.vol_label.configure(text=self.level)
        print(self.level, self.device.get_friendly_name())

    def on_mute(self):
        is_muted = self.device.get_mute()
        self.device.set_mute(not is_muted)
        self.btn_mute.configure(text=self.get_btn_text())
        print(not is_muted, self.device.get_friendly_name())

    def get_btn_text(self):
        return TXT_MUTE[self.device.get_mute()]

    def on_state_selected(self, event: str):
        if self.device.get_state().name in event:
            self.set_visibility(True)
        else:
            self.set_visibility(False)


if __name__ == '__main__':
    window = AudioDevicesWindow()
    window.mainloop()

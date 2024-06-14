import customtkinter as ctk
import customtkinter_extensions as ctk_e

from audio_devices import AudioDevices, AudioDevice
from config import config
from utils import emoji_to_ctk_img
from logger import logger

TXT_MUTE = {
    True: "🔈",
    False: "🔊"
}

FONT = 'TkDefaultFont'


class AudioDevicesWindow(ctk_e.CTkToplevel):
    def __init__(self, *args, title='Audio Devices', **kwargs):
        super().__init__(*args, **kwargs)
        self.title_txt = title
        self.title(title)

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure((1, 2, 3, 4), weight=0)

        self.audio_devices = self.get_audio_devices_grouped()
        self.audio_devices = self.sort_audio_devices(self.audio_devices)
        self.label = None
        self.scroll_frame = None
        self.label_visibility = None
        self.states_combo_box = None
        self.label_reload = None
        self.build_widgets(title)

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

    def build_widgets(self, label_text):
        self.label = ctk.CTkLabel(
            self, text=label_text, anchor="center", font=(FONT, 18))
        self.label.grid(row=0, column=0, sticky="w", padx=25, pady=5)

        self.scroll_frame = self.create_scroll_frame(self.audio_devices)

        self.label_visibility = ctk.CTkLabel(self, text="Show:")
        self.label_visibility.grid(row=0, column=2, pady=0, padx=5)

        device_states = AudioDevices.get_device_states_list()
        self.states_combo_box = ctk.CTkComboBox(
            self, values=device_states, command=self.on_state_selected)
        self.states_combo_box.grid(row=0, column=3, pady=0, padx=5)
        self.states_combo_box.set(device_states[0])
        self.states_combo_box.bind('<Return>', self.on_state_selected)
        if config.get('selected_device_state') is not None:
            self.states_combo_box.set(config.get('selected_device_state'))
        self.on_state_selected(self.states_combo_box.get())

        self.label_reload = ctk.CTkLabel(
            self, text='🔄', anchor="center", font=(FONT, 24))
        self.label_reload.bind(
            "<Button-1>", lambda _: self._reload(hide=False))
        self.label_reload.grid(row=0, column=4, pady=0, padx=5)

    def destroy_widgets(self):
        # Are contained widgets destroyed and the memory freed?
        self.scroll_frame.destroy()
        self.states_combo_box.destroy()
        self.label_visibility.destroy()
        self.label.destroy()
        self.label_reload.destroy()

    def on_state_selected(self, _: str):
        value = self.states_combo_box.get()
        self.scroll_frame.refresh_state_visibility(value)
        self.focus_set()
        config.set('selected_device_state', value)

    def create_scroll_frame(self, audio_devices):
        frame = AudioDevicesFrame(self, audio_devices=audio_devices)
        frame.grid(row=1, column=0, columnspan=5, sticky='nsew')

        return frame

    def refresh(self):
        for audio_device_frame in self.scroll_frame.audio_device_frames:
            for flow_frame in audio_device_frame.flow_frames:
                for slider in flow_frame.sliders:
                    slider.refresh()

    def reload(self, update_devices=True):
        if update_devices:
            self.audio_devices = self.get_audio_devices_grouped()
            self.audio_devices = self.sort_audio_devices(self.audio_devices)

        self.after(0, self._reload)

    def _reload(self, hide=True):
        if hide:
            self.withdraw()
        self.destroy_widgets()
        self.build_widgets(self.title_txt)
        if hide:
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

    def refresh_state_visibility(self, event: str):
        for frame in self.audio_device_frames:
            frame.refresh_state_visibility(event)

    def sort_and_draw_frames_grid(self):
        devices_order = config.get('audio_devices_order')
        self.audio_device_frames = sorted(
            self.audio_device_frames,
            key=lambda f: devices_order.index(f.title)
        )

        self.draw_frames_grid()

    def on_move_frame(self, option: str, title: str):
        devices_order = config.get('audio_devices_order')
        devices_order.remove(title)
        if option == 'Top':
            devices_order.insert(0, title)
        elif option == 'Bottom':
            devices_order.append(title)
        config.set('audio_devices_order', devices_order)

        self.sort_and_draw_frames_grid()
        self.refresh_state_visibility(config.get('selected_device_state'))


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

        self.move_option_menu = ctk_e.CustomDropdown(
            self, width=80, values=['Top', 'Bottom'],
            command=lambda option: on_move(option, self.title)
        )
        self.move_option_menu.grid(row=0, column=1, padx=1, pady=1, sticky='e')

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

    def refresh_state_visibility(self, event: str):
        self.is_visible = False
        for frame in self.flow_frames:
            frame.refresh_state_visibility(event)
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

    def refresh_state_visibility(self, event: str):
        self.is_visible = False
        for slider in self.sliders:
            slider.refresh_state_visibility(event)
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
        self.label.grid(row=0, column=0, columnspan=3, padx=10, pady=1,
                        sticky='e')

        self.btn_mute = None
        self.slider = None
        self.is_muted = None
        self.level = self.device.get_volume_level()
        if self.level is not None:
            self.level = int(self.level)
            self.is_muted = self.device.get_mute()
            self.btn_mute = ctk.CTkButton(
                self, image=self.get_btn_img(), text='', width=32, height=32,
                command=self.on_mute, font=(FONT, 16))
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
        logger.info(
            'level: %s | %s', self.level, self.device.get_friendly_name()
        )

    def on_mute(self):
        is_muted = not self.device.get_mute()
        if self.is_muted == is_muted:
            return

        self.is_muted = is_muted
        self.device.set_mute(is_muted)
        self.btn_mute.configure(image=self.get_btn_img())
        logger.info(
            'is_muted: %s | %s', is_muted, self.device.get_friendly_name()
        )

    def get_btn_img(self):
        return emoji_to_ctk_img(TXT_MUTE[self.device.get_mute()])

    def refresh_state_visibility(self, event: str):
        if self.device.get_state().name in event:
            self.set_visibility(True)
        else:
            self.set_visibility(False)

    def refresh(self):
        if self.slider is None:
            return

        level = self.device.get_volume_level()
        if self.level is not None and level != self.level:
            self.slider.set(level)
            self.on_slide(level)

        is_muted = self.device.get_mute()
        if self.is_muted is not None and is_muted != self.is_muted:
            self.btn_mute.configure(image=self.get_btn_img())
            self.is_muted = is_muted
            logger.info(
                'is_muted: %s | %s', is_muted, self.device.get_friendly_name()
            )


if __name__ == '__main__':
    window = AudioDevicesWindow()
    window.mainloop()

import logging
import time
from threading import Thread, Lock
from typing import Dict, Tuple
import mouse
from pynput import keyboard

from utils.core.Bus import Bus
from utils.core.FightInformation import FightInformation

COUNTDOWN_EVENT = "COUNTDOWN_EVENT"
CHECK_IDENTIFICATION_POINTS = "CHECK_IDENTIFICATION_POINTS"
MOUSE_CLICK = "MOUSE_CLICK"


class KM_Monitor:
    def __init__(self, bus: Bus, fight_info: FightInformation, resulutions: Dict, key_press_signal):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bus = bus
        self.fight_info = fight_info
        self.resolutions = resulutions
        self.key_press_signal = key_press_signal
        self._active = False
        self.listen_keys = [
            self.fight_info.get_config("关闭程序按键"),
            self.fight_info.get_config("模拟左侧替身按键"),
            self.fight_info.get_config("模拟右侧替身按键"),
            self.fight_info.get_config("清空倒计时按键"),
            self.fight_info.get_config("展示当前识别点位"),
        ]
        # 状态跟踪
        self.active_keys = set()  # 当前按下的按键集合
        self.active_buttons = set()  # 当前按下的鼠标按钮集合
        self.state_lock = Lock()

        # 创建监听器
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        # self.mouse_listener = mouse.Listener(
        #     on_click=self._on_mouse_click
        # )
        self.bus.subscribe("MOUSE_CLICK", self._handle_mouse_click)

    def start(self):
        """启动监听线程"""
        if self._active:
            return

        self._active = True
        self.logger.info("键盘鼠标监听器启动...")

        # 启动键盘监听
        Thread(target=self.keyboard_listener.start, daemon=True).start()
        # # 启动鼠标监听
        # Thread(target=self.mouse_listener.start, daemon=True).start()

    def stop(self):
        """停止监听"""
        if not self._active:
            return

        self.logger.info("键盘鼠标监听器停止...")
        self.keyboard_listener.stop()
        # self.mouse_listener.stop()
        self._active = False

    def _on_key_press(self, key):
        """键盘按键按下回调"""
        try:
            key_str = key.char if hasattr(key, 'char') else key.name
        except AttributeError:
            key_str = str(key)

        with self.state_lock:
            trigger_time = time.perf_counter()
            # 如果按键是新按下的（不在当前活动集合中）
            if key_str not in self.active_keys and key_str in self.listen_keys:
                self.active_keys.add(key_str)
                self._trigger_keyboard(key_str, trigger_time)

    def _on_key_release(self, key):
        """键盘按键释放回调"""
        try:
            key_str = key.char if hasattr(key, 'char') else key.name
        except AttributeError:
            key_str = str(key)

        with self.state_lock:
            # 从活动集合中移除
            if key_str in self.active_keys:
                self.active_keys.remove(key_str)

    def _trigger_keyboard(self, key, trigger_time):
        """触发键盘事件"""
        # self.logger.info(f"键盘按下: {key}")
        if key == self.fight_info.get_config("展示当前识别点位"):
            self.bus.publish(CHECK_IDENTIFICATION_POINTS)
        else:
            self.key_press_signal.emit(
                {
                    "key": key,
                    "trigger_time": trigger_time,
                    'duration': 14.85,
                }
            )

    def _handle_mouse_click(self, data: Dict):
        type = data.get('type', None)
        if type:
            if type == "RECORD":
                left, top, right, bottom = self.fight_info.get_config("窗口Rect")
                width, height = self.fight_info.get_config("默认分辨率").split("x")
                click_position = self.resolutions[self.fight_info.get_config("默认分辨率")][
                    "fight_status_templates"]["保存比赛"]["click_position"]
                self._click_and_return(click_position, 1, (
                    left, bottom - height))

    def _click_and_return(self, click_positon: Tuple, click_times=1, base_position=(0, 0)):
        pre_position = mouse.get_position()
        mouse.move(base_position[0] + click_positon[0], base_position[1] + click_positon[1])
        for i in range(click_times):
            mouse.click()
        mouse.move(pre_position[0], pre_position[1])

    # def _on_mouse_click(self, x, y, button, pressed):
    #     """鼠标点击回调"""
    #     button_name = button.name
    #
    #     if pressed:
    #         with self.state_lock:
    #             # 如果按钮是新按下的（不在当前活动集合中）
    #             if button_name not in self.active_buttons:
    #                 self.active_buttons.add(button_name)
    #                 # 立即触发鼠标事件
    #                 self._trigger_mouse(button_name, x, y)
    #     else:
    #         with self.state_lock:
    #             # 从活动集合中移除
    #             if button_name in self.active_buttons:
    #                 self.active_buttons.remove(button_name)

    # def _trigger_mouse(self, button, x, y):
    #     """触发鼠标事件"""
    #     self.logger.debug(f"鼠标点击: {button}")
    #     self.bus.publish(KM_TRIGGER, {
    #         'type': 'mouse',
    #         'button': button,
    #         'x': x,
    #         'y': y,
    #         'event': 'click'
    #     })


if __name__ == "__main__":
    bus = Bus()
    monitor = KM_Monitor(bus)
    monitor.start()
    while 1:
        continue

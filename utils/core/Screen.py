import ctypes
import ctypes
import logging
import threading
import time
from typing import Dict

import cv2
import dxcam
import numpy as np
import win32gui
from PyQt6.QtCore import pyqtSlot, QThread, pyqtSignal, QWaitCondition, QMutex

from utils.core.FightInformation import FightInformation
from utils.core.Bus import Bus

# 在顶部添加事件常量定义
SCREEN_DONE = "SCREEN_DONE"
FIGHT_INFORMATION_UPDATE_DONE = "FIGHT_INFORMATION_UPDATE_DONE"
JUDGE_DONE = "JUDGE_DONE"
FIGHT_STOP = "FIGHT_STOP"
UI_UPDATE = "UI_UPDATE"
try:
    # 设置进程 DPI 感知为 "每监视器 DPI 感知"（最高级别）
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # 2 表示 PER_MONITOR_DPI_AWARE
except Exception as e:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 1 表示 SYSTEM_DPI_AWARE
    except:
        ctypes.windll.user32.SetProcessDPIAware()  # 兼容旧系统


class TimerThread(QThread):
    """被动触发的定时器线程，用于延时后发送信号"""
    timeout = pyqtSignal(object)  # 携带数据的超时信号

    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.delay_ms = 0
        self.data = None
        self._is_triggered = False
        self._is_running = True

    @pyqtSlot(int, object)
    def trigger(self, delay_ms, data=None):
        """触发定时器，设置延时时间和数据"""
        self.mutex.lock()
        self.delay_ms = delay_ms
        self.data = data
        self._is_triggered = True
        self.condition.wakeOne()  # 唤醒等待的线程
        self.mutex.unlock()

    def run(self):
        """线程执行函数"""
        while self._is_running:
            self.mutex.lock()
            # 等待触发信号
            while not self._is_triggered and self._is_running:
                self.condition.wait(self.mutex)

            if not self._is_running:  # 检查是否需要退出
                self.mutex.unlock()
                break

            delay_ms = self.delay_ms
            data = self.data
            self._is_triggered = False  # 重置触发状态
            self.mutex.unlock()

            # 执行延时
            if delay_ms > 0:
                time.sleep(delay_ms / 1000.0)
                # 延时结束后发送信号
                self.timeout.emit(data)

    def stop(self):
        """停止线程（在应用退出时调用）"""
        self.mutex.lock()
        self._is_running = False
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()


class Screen:
    def __init__(self, bus: Bus, fight_info: FightInformation):
        self.timer_thread = TimerThread()
        self.timer_thread.timeout.connect(self.timer_publish_screen_done)
        self.timer_thread.start()  # 启动线程，线程会进入等待状态
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bus = bus  # 添加总线引用
        self.fight_info = fight_info
        # self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.camera = dxcam.create(device_idx=0, output_color="BGR")  # returns a DXCamera instance on primary monitor
        self.camera.start(target_fps=60, video_mode=True)  # Optional argument to capture a region
        # 订阅事件
        self.bus.subscribe(FIGHT_INFORMATION_UPDATE_DONE, self.handle_fight_info_update)
        self.bus.subscribe(JUDGE_DONE, self.handle_fight_info_update)

        self.find_windows = ['Qt5156QWindowIcon', 'LDPlayerMainFrame']
        self.bool_window_error = True
        self.running = True
        self.screen = None
        self.hwnd = 0
        self.resolution = None
        self.last_find_window_rect = time.perf_counter()
        self.window_rect = None
        self.screen_interval = 50
        self.logger.debug(f"初始化完成...")

    def handle_fight_info_update(self, data: Dict):
        """事件处理：战斗信息更新完成时触发截图"""
        # 使用线程避免阻塞事件循环
        if self.running:
            threading.Thread(target=self.get_screen_qt, args=(data,), daemon=True).start()
        else:
            self.bus.publish(FIGHT_STOP)

    def get_screen_qt(self, data: Dict):
        """执行截屏操作"""
        start = data.get('end_time')
        try:
            if self.hwnd == 0:
                for window_class in self.find_windows:
                    self.hwnd = win32gui.FindWindow(window_class, None)
                    if self.hwnd == 0:
                        continue
                    else:
                        break
            if self.hwnd == 0:
                self.logger.debug("hwnd=0，窗口未找到")
                self.bool_window_error = True
                print("不存在符合要求的模拟器窗口，请打开模拟器", end="\r")
                print(" " * 100, end="\r")
                # self.bus.publish(UI_UPDATE, {
                #     'type': "WINDOW",
                #     'text': "窗口：未找到",
                #     'color': "red"
                # })
                self.publish_screen_done(
                    start,
                    {
                        'screen': None,
                    }
                )
                return

            try:
                if (self.window_rect is None or
                        (time.perf_counter() - self.last_find_window_rect) > 0.5):
                    window_rect = self.get_accurate_window_rect(self.hwnd)
                    if self.window_rect != window_rect:
                        self.window_rect = window_rect
                        self.fight_info.set_config("窗口Rect", self.window_rect)
                        self.logger.debug(f"窗口Rect：{self.window_rect},窗口大小："
                                          f"{self.window_rect[2] - self.window_rect[0]}x"
                                          f"{self.window_rect[3] - self.window_rect[1]},"
                                          f"分辨率：{self.resolution}")
                    self.last_find_window_rect = time.perf_counter()
                left, top, right, bottom = self.window_rect
                if (right - left) != self.resolution[0]:
                    # self.logger.debug(f"窗口宽度：{(right - left)}（预期：{self.resolution[0]}）")
                    self.bool_window_error = True
                    print(f"游戏窗口现在宽度：{(right - left)},预期：{self.resolution[0]}", end="\r")
                    # print(" " * 100, end="\r")
                    # self.bus.publish(UI_UPDATE, {
                    #     'type': "WINDOW",
                    #     'text': f"窗口宽度：{(right - left)}（预期：{self.resolution[0]}）",
                    #     'color': "red"
                    # })
                    self.publish_screen_done(
                        start,
                        {
                            'screen': None,
                        }
                    )
                    return
                screen_time = time.perf_counter()
                # self.screen = self.camera.grab(region=(
                #     left, bottom - self.resolution[1], left + self.resolution[0], bottom))
                self.screen = self.camera.get_latest_frame()[bottom - self.resolution[1]:bottom, left:left + self.resolution[0]]
                if self.fight_info.get_config("调试模式"):
                    self.logger.debug(f"[截图耗时] {(time.perf_counter() - screen_time) * 1000:.1f}ms")
                if self.bool_window_error:
                    self.bool_window_error = False
                    print(" " * 100, end="\r")
                    # self.bus.publish(UI_UPDATE, {
                    #     'type': "WINDOW",
                    #     'text': f"当前分辨率：{self.resolution[0]}x{self.resolution[1]}",
                    #     'color': "green"
                    # })

                # self.screen = self.camera.get_latest_frame()[bottom - 900:bottom, left:left + 1600]

                # cv2.imshow("DXCAM", self.screen)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

                self.publish_screen_done(
                    start,
                    {
                        'screen': self.screen,
                        'screen_time': screen_time
                    }
                )
            except ValueError as e:
                self.bool_window_error = True
                print(f"模拟器窗口超出屏幕边界", end="\r")
                self.publish_screen_done(
                    start,
                    {
                        'screen': None,
                    }
                )
            except Exception as e:

                self.logger.error(f"截屏过程中发生{type(e)}错误: {e}")
                self.publish_screen_done(
                    start,
                    {
                        'screen': None,
                    }
                )
        except Exception as e:
            self.logger.error(f"截屏定位窗口过程中发生错误: {e}")
            self.publish_screen_done(
                start,
                {
                    'screen': None,
                }
            )

    def publish_screen_done(self, start, data):
        elapsed_time = (time.perf_counter() - start) * 1000  # 计算截图花费的时间（毫秒）
        wait_time = self.screen_interval - elapsed_time  # 计算需要等待的时间
        if wait_time > 0:
            # 触发定时器，线程会在延时后自动发送信号
            self.timer_thread.trigger(wait_time, data)
        else:
            # 如果不需要等待，直接发布事件
            self.timer_publish_screen_done(data)

    def timer_publish_screen_done(self, data):
        data['end_time'] = time.perf_counter()
        self.bus.publish(SCREEN_DONE, data)

    @staticmethod
    def get_accurate_window_rect(hwnd):
        """获取准确的窗口位置（考虑DPI和边框）"""

        # # 获取物理坐标
        # rect = wintypes.RECT()
        # ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        #
        # # 获取DPI缩放比例
        # try:
        #     dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
        #     scaling = dpi / 96.0
        # except:
        #     scaling = 1.0
        #
        # # 转换为逻辑坐标
        # left = int(rect.left / scaling)
        # top = int(rect.top / scaling)
        # right = int(rect.right / scaling)
        # bottom = int(rect.bottom / scaling)

        # 获取客户区位置（排除边框）
        client_left, client_top, client_right, client_bottom = win32gui.GetClientRect(hwnd)
        pt_top = win32gui.ClientToScreen(hwnd, (0, 0))
        pt_bottom = win32gui.ClientToScreen(hwnd, (client_right, client_bottom))

        # 返回准确的客户区位置
        return (
            pt_top[0],
            pt_top[1],
            pt_bottom[0],
            pt_bottom[1],
        )


def extract_diamond_region(image):
    """
    截取图像中的正菱形区域，其他区域置为0

    :param image: 输入的BGR图像或灰度图像
    :return: 只保留正菱形区域的图像（与输入图像通道数相同）
    """
    # 获取图像尺寸
    height, width = image.shape[:2]
    # 检查图像是否为单通道（灰度图像）
    is_gray = len(image.shape) == 2

    # 创建与图像相同大小的单通道黑色掩膜
    mask = np.zeros((height, width), dtype=np.uint8)

    # 计算菱形的四个顶点坐标
    # 菱形中心点
    center_x, center_y = width // 2, height // 2

    # 计算菱形的半径（取宽高中较小值的一半）
    radius = min(width, height) // 2

    # 菱形的四个顶点（上、右、下、左）
    top = (center_x, center_y - radius)
    right = (center_x + radius, center_y)
    bottom = (center_x, center_y + radius)
    left = (center_x - radius, center_y)

    # 创建菱形轮廓
    diamond_pts = np.array([top, right, bottom, left], dtype=np.int32)

    # 在掩膜上绘制填充的菱形
    cv2.fillPoly(mask, [diamond_pts], color=255)

    if is_gray:
        # 对于灰度图像，直接使用单通道掩膜进行按位与操作
        result = cv2.bitwise_and(image, mask)
    else:
        # 对于BGR图像，将掩膜转换为三通道，以便与BGR图像进行按位与操作
        mask_bgr = cv2.merge([mask, mask, mask])
        result = cv2.bitwise_and(image, mask_bgr)

    # 保存处理后的图像（可根据需要注释掉）
    # cv2.imwrite(f"F:/PyProject/ImageMatch/temp/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')}.png", result)
    return result

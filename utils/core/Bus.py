import logging
import os
import threading
from datetime import datetime
from typing import Dict, Callable, List, Optional

from PyQt6.QtCore import pyqtSignal

# 定义事件类型常量
SCREEN_DONE = "SCREEN_DONE"
FIGHT_INFORMATION_UPDATE_DONE = "FIGHT_INFORMATION_UPDATE_DONE"
STAND_IN_START = "STAND_IN_START"
STAND_IN_TIME_ADD = "STAND_IN_TIME_ADD"
UI_UPDATE = "UI_UPDATE"


class Bus:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        # 存储事件类型到订阅者的映射 {event_type: [callbacks]}
        self.subscribers: Dict[str, List[Callable[[Dict], None]]] = {}
        # 保证线程安全的锁
        self.lock = threading.Lock()
        self.logger.debug(f"初始化完成...")

    def subscribe(self, event_type: str, callback: Callable[[Dict], None]):
        """订阅事件：注册回调函数到指定事件类型"""
        self.logger.debug(f"[{callback.__qualname__}] 注册到{event_type}事件...")
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: Optional[Dict] = None):
        """发布事件：触发所有订阅该事件类型的回调函数"""
        with self.lock:
            callbacks = self.subscribers.get(event_type, [])
        # self.logger.info(f"{event_type} published！")
        # 在锁外执行回调（避免死锁）
        for callback in callbacks:
            # 确保传递字典（即使data为None）
            event_data = data if data is not None else {}
            callback(event_data)
            # 改为发射信号而不是直接调用回调


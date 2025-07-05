import logging
import threading
import time
from typing import Dict, Any, Union

import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QRectF
from PyQt6.QtGui import QPixmap, QImage, QBitmap, QPainter, QPainterPath
from PyQt6.QtWidgets import QGraphicsOpacityEffect

from StaticFunctions import resource_path
from utils.core.Bus import Bus
from utils.core.FightInformation import FightInformation

# 在顶部添加事件常量定义
UI_UPDATE = "UI_UPDATE"
FIGHT_OVER = "FIGHT_OVER"


class UI_Update(QObject):
    update_signal = pyqtSignal(dict)

    def __init__(self, bus: Bus, ref_map: Dict[str, Any]):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bus = bus  # 添加总线引用
        self.ref_map = ref_map
        self.last_update_time = time.perf_counter()
        self.unknown_secret_scroll = create_rounded_pixmap(QPixmap(resource_path("src/img/Fight/Status/未知密卷.png")), 50)
        self.max_ougi_1p = 4
        self.max_ougi_2p = 4
        # 订阅事件
        self.bus.subscribe(UI_UPDATE, self.handle_ui_update)
        # 连接信号到槽函数
        self.update_signal.connect(self.update_ui)
        self.logger.debug(f"初始化完成...")

    def handle_ui_update(self, data: Dict):
        threading.Thread(target=self.trigger_ui_update, args=(data,), daemon=True).start()
        self.last_update_time = time.perf_counter()

    def trigger_ui_update(self, data: Dict):
        # 在子线程中触发信号
        self.update_signal.emit(data)

    def update_ui(self, data: Dict):
        # 在主线程中执行更新操作
        stand_in_time_style = "font-family: 'Microsoft YaHei'; font-size: 40px; font-weight: bold;"
        update_type = data.get('type', '')

        if update_type == "JUDGE":
            # self.logger.debug(f"识别到判断事件：{data}")
            dic = data.get("fight_info", {})
            self.max_ougi_1p = dic.get('1P奥义点上限')
            self.max_ougi_2p = dic.get('2P奥义点上限')
            self.ref_map.get("常驻标签左").show()
            self.ref_map.get("常驻标签右").show()
            # 更新奥义点显示
            左右标签更新(self.ref_map["常驻标签左"], self._ougi_str(1, dic.get("1P奥义点")))
            左右标签更新(self.ref_map["常驻标签右"], self._ougi_str(2, dic.get("2P奥义点")))

        if update_type == "SECRET_SCROLL":
            dic = data.get('secret_scrolls')
            self.update_circular_image("1P秘卷", dic[0])
            self.update_circular_image("2P秘卷", dic[1])
            self.ref_map.get("1P秘卷").show()
            self.ref_map.get("2P秘卷").show()

        if update_type == "UI_CLEAR":
            # 重置忍者信息
            常驻标签透明效果 = QGraphicsOpacityEffect()
            常驻标签透明效果.setOpacity(0)
            self.ref_map.get("常驻标签左").hide()
            self.ref_map.get("常驻标签右").hide()
            # 重置秘卷信息
            self.ref_map.get("1P秘卷").hide()
            self.ref_map.get("2P秘卷").hide()

    def _ougi_str(self, player, num):
        color_dic = {
            0: "#00D29E",
            1: "#2AA4DB",
            2: "#2AA4DB",
            3: "#2AA4DB",
            4: "#F43232",
            5: "#F43232",
            6: "#F43232",
        }
        if player == 1:
            text = ("◆" * num + "◇" * (self.max_ougi_1p - num)).removesuffix(" ")
            bg_color = "#FFFFFF"
            color = color_dic[num]
            return text, bg_color, color
        if player == 2:
            text = ("◇" * (self.max_ougi_2p - num) + "◆" * num).removesuffix(" ")
            bg_color = "#FFFFFF"
            color = color_dic[num]
            return text, bg_color, color

    def update_circular_image(self, key: str, image_array: np.ndarray):
        label = self.ref_map.get(key)
        if label is not None:
            # 获取 QLabel 的尺寸
            label_width = label.width()
            label_height = label.height()

            # 将 NumPy 数组转换为字节流
            height, width, channel = image_array.shape
            bytes_per_line = channel * width
            # 确保数组是连续的，并转换为字节流
            image_array = np.ascontiguousarray(image_array)
            q_image = QImage(
                image_array.tobytes(),
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_BGR888  # 指定格式为 BGR
            )
            pixmap = QPixmap.fromImage(q_image)

            # 创建与 QLabel 尺寸一致的圆形图片
            circular_pixmap = create_rounded_pixmap(pixmap, label_width)
            # 设置图片到 QLabel
            label.setPixmap(circular_pixmap)


def 左右标签更新(对应标签, 文本背景色文本色):
    新文本 = 文本背景色文本色[0]
    背景色 = 文本背景色文本色[1]
    文本色 = 文本背景色文本色[2]
    对应标签.setText(新文本)
    对应标签.setStyleSheet(f"background-color: {背景色};color: {文本色}")


def create_rounded_pixmap(pixmap: QPixmap, radius: int) -> QPixmap:
    """在Qt6中创建带圆角的QPixmap"""
    if pixmap.isNull() or radius <= 0:
        return QPixmap()  # 返回空的QPixmap

    # 创建目标尺寸的QPixmap，确保尺寸有效
    dest_image = QPixmap(radius, radius)
    dest_image.fill(Qt.GlobalColor.transparent)

    painter = QPainter(dest_image)
    painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

    # 使用浮点精度创建椭圆路径
    path = QPainterPath()
    path.addEllipse(0.0, 0.0, radius, radius)  # 明确使用浮点数
    painter.setClipPath(path)

    # 计算缩放比例
    original_width = pixmap.width()
    original_height = pixmap.height()
    scale = min(radius / original_width, radius / original_height)

    # 计算缩放后的尺寸，确保为整数
    scaled_width = int(original_width * scale)
    scaled_height = int(original_height * scale)

    # 绘制图片，确保参数为整数
    painter.drawPixmap(
        (radius - scaled_width) // 2,
        (radius - scaled_height) // 2,
        scaled_width,
        scaled_height,
        pixmap
    )

    painter.end()
    return dest_image

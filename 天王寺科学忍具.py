import ctypes
import json
import logging
import os
import random
import shutil
import socket
import sys
import time
from typing import Dict

import cv2
import mouse
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QMovie, QColor, QFont, QPalette, QIcon
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsOpacityEffect, QSystemTrayIcon, QMainWindow

from StaticFunctions import get_real_path
from utils.FightInformationUpdate import FightInformationUpdate
from utils.Judge import Judge
from utils.UI_Update import UI_Update
from utils.core.Bus import Bus
from utils.core.FightInformation import FightInformation
from utils.core.KM_Monitor import KM_Monitor
from utils.core.LoggerConfig import setup_logging
from utils.core.Screen import Screen

FIGHT_INFORMATION_UPDATE_DONE = "FIGHT_INFORMATION_UPDATE_DONE"
COUNTDOWN_EVENT = "COUNTDOWN_EVENT"
FIGHT_OVER = "FIGHT_OVER"

os.environ["QT_LOGGING_RULES"] = "qt.qpa.window.warning=false"
print("本软件版本为V4.8.0")

def 发送打开次数():
    """
    向指定服务器发送 '脚本打开次数+1' 数据，并检测连接状态。
    功能:
    1. 如果服务器无法访问（如防火墙或网络问题），输出相应提示。
    2. 如果服务器可以访问，但服务端程序未启动，输出相应提示。
    3. 如果成功发送数据，输出成功信息。
    """
    服务器_IP = '182.92.178.158'
    端口 = 12345
    数据 = "脚本打开次数+1"
    try:
        # 创建一个socket对象
        客户端 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        客户端.settimeout(5)  # 设置超时时间为5秒
        # 尝试连接到服务器
        客户端.connect((服务器_IP, 端口))
        # 尝试发送数据到服务器
        客户端.send(数据.encode('utf-8'))
        print("+1")
    except socket.timeout:
        print("TIMEOUT")
    except ConnectionRefusedError:
        print("未对接")
    except socket.error as e:
        print(f"无法")
    finally:
        # 关闭客户端socket
        客户端.close()

发送打开次数()

def 强行设置DPI():
    """最强力的 DPI 设置"""
    # 设置所有可能的环境变量
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
    os.environ["QT_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_DEVICE_PIXEL_RATIO"] = "1"
    os.environ["QT_DPI_OVERRIDE"] = "96"
    os.environ["QT_FONT_DPI"] = "96"
    # Windows DPI 设置 - 更强力的方法
    if sys.platform == "win32":
        try:
            # 尝试不同的 DPI 感知级别
            # 0 = DPI_AWARENESS_INVALID
            # 1 = DPI_AWARENESS_UNAWARE  <- 我们想要这个
            # 2 = DPI_AWARENESS_SYSTEM_AWARE
            # 3 = DPI_AWARENESS_PER_MONITOR_AWARE
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 改为 1
        except:
            try:
                # 备用方法
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass

# 在创建 QApplication 之前调用
强行设置DPI()

言语 = "1"

def _load():
    try:
        if getattr(sys, 'frozen', False):
            p = sys._MEIPASS  # 改这里
        else:
            p = os.path.dirname(os.path.abspath(__file__))

        f = os.path.join(p, "文件", "诫训.txt")
        if os.path.exists(f):
            exec(open(f, encoding='utf-8').read(), globals())
    except:
        pass

_load()

def 召出内容(文件夹路径):
    try:
        os.startfile(文件夹路径)

    except Exception as e:
        print(f"复制失败：{e}")
        return False

def 显示通知(标题, 信息, 图标路径):
    # 创建一个应用程序对象
    应用程序 = QApplication(sys.argv)
    # 创建系统托盘图标对象
    托盘图标 = QSystemTrayIcon()
    # 检查图标路径是否存在
    if 图标路径 and os.path.exists(图标路径):
        托盘图标.setIcon(QIcon(图标路径))
    else:
        print(f"图标路径 '{图标路径}' 不存在，使用默认图标。")
        托盘图标.setIcon(QIcon())  # 使用默认图标
    # 设置通知消息
    托盘图标.show()
    托盘图标.showMessage(标题, 信息, QSystemTrayIcon.MessageIcon.Information,
                         5000)  # 5000毫秒 = 5秒
    # 使用 QTimer 关闭 QApplication 而不启动事件循环
    QTimer.singleShot(1000, 应用程序.quit)  # 1秒后关闭 QApplication

# 使用示例
选项列表 = [
    ("Doki Pipo☆Emotion", "奇迹般的访问数无限延伸", get_real_path("files/icon/1.ico")),
    ("Tele-telepathy", "将一个又一个的点联结起来\n连成了线 然后变成了圆", get_real_path("files/icon/6.ico")),
    ("Analogue Heart", "连接起来吧 Analogue Heart\n那最重要的 Analogue Heart",
    get_real_path("files/icon/1.ico")),
    (
        "First Love Again",
        "晚霞染红了天空[今天]将迎来落幕\n我们又留下了什么呢 在意 却又无能为力",
        get_real_path("files/icon/3.ico"),
    ),
    (
        "私はマグネット",
        "为了他人而做些什么 从前的自己想都没想过\n这对我来说是 奇迹的伟大的事情哟",
        get_real_path("files/icon/1.ico"),
    ),
    (
        "相连的Connect",
        "现实中又没有[Ctrl]+[Z]\n自己来定义有些复杂呢",
        get_real_path("files/icon/5.ico"),
    ),
]
随机标题, 随机信息, 随机图标路径 = random.choice(选项列表)
显示通知(随机标题, 随机信息, 随机图标路径)

print("""
使用教程如下:
首先,请在教程中获取文档查看使用方法
也可以观看视频教程
目前本软件默认适配的分辨率为[1920*1080]
还内置了[2560*1440],[3840*2160]的分辨率适配
如果要更换对应分辨率,请更换 配置.txt 
如果你不想把电脑分辨率设置为如上的16:9分辨率
本软件有高度自定义的内容设置
你完全可以设定完全个性化的设置

软件作者:凤灯幽夜
""")

class 根窗口(QMainWindow):
    countdown_signal = pyqtSignal(dict)  # 传递一个字典参数
    fight_over_signal = pyqtSignal(dict)
    def __init__(self):
        # 创建UI引用字典
        self.ref_map = {}
        self.resolutions = {}
        with open(get_real_path("config/Custom.json"), 'r', encoding='utf-8') as f:
            self.自定义设置 = json.load(f)
        super().__init__()
        setup_logging()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.load_resolutions()
        # 初始化环境
        self.init_environment()
        # 初始化核心组件
        self.init_core_components()
        # 创建UI
        self.init_ui()
        self.ui_update = UI_Update(self.bus, self.ref_map)
        self.bus.publish(FIGHT_INFORMATION_UPDATE_DONE)
        self.logger.info(f"初始化完成...")

    def load_resolutions(self):
        try:
            with open(get_real_path("config/Resolutions.json"),
                      'r',
                      encoding='utf-8') as f:
                self.resolutions = json.load(f)
        except FileNotFoundError:
            self.logger.error("未找到config/Resolutions.json文件")

    def init_environment(self):
        """初始化环境设置"""
        if sys.platform == 'win32':
            os.environ["PYTHONUTF8"] = "on"
            os.environ["PYTHONLEGACYWINDOWSFSENCODING"] = "1"

            os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts.warning=false"

        cv2.ocl.setUseOpenCL(True)

        self.setWindowTitle("璃奈板")
        self.setGeometry(int(self.自定义设置["主窗口位置与大小"][0]), int(self.自定义设置["主窗口位置与大小"][1]),
                         int(self.自定义设置["主窗口位置与大小"][2]), int(self.自定义设置["主窗口位置与大小"][3]))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags())
        self.设置窗口图标随机(self, get_real_path("files/icon"))
        # self.setStyleSheet("background: transparent;")
        self.setWindowOpacity(1.0)  # 80% 不透明
        # 设置窗口置顶

    def 设置窗口图标随机(self, 窗口, 图标文件夹):
        图标文件 = [
            f for f in os.listdir(图标文件夹)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.ico', '.bmp'))
        ]
        if 图标文件:
            随机图标 = random.choice(图标文件)
            图标路径 = os.path.join(图标文件夹, 随机图标)
            窗口.setWindowIcon(QIcon(图标路径))

    def init_core_components(self):
        """初始化核心组件"""
        # 初始化各个组件
        self.countdown_signal.connect(self.handle_count_down)
        self.fight_over_signal.connect(self.handle_fight_over)
        self.bus = Bus()
        self.monitor = KM_Monitor(self.bus)
        self.monitor.start()
        self.fight_info = FightInformation()
        self.screen = Screen(self.bus)
        self.screen.screen_interval = self.fight_info.get_config("默认截图间隔")
        self.screen.find_windows = self.fight_info.get_config("查找窗口")
        self.screen.resolution = [1600, 900]
        self.fight_info_update = FightInformationUpdate(self.bus, self.fight_over_signal)
        self.fight_info_update.fight_status_templates = self.resolutions[self.fight_info.get_config("默认分辨率")]["fight_status_templates"]
        self.fight_info_update.preprocess_templates()
        self.fight_info_update.roi_dic = self.resolutions[self.fight_info.get_config("默认分辨率")]["roi_dic"][self.fight_info.get_config("默认模式")]
        self.judge = Judge(self.bus, self.fight_info, self.countdown_signal)

        # self.count_down = CountDown(self.bus, self.fight_info)

    def handle_count_down(self, data: Dict):
        self.logger.debug(f"接收倒计时事件：{data}")
        try:
            self.添加倒计时标签(data.get("target"), data.get("time_perf"), data.get("time") + data.get("add"))
        except Exception as e:
            self.logger.error(f"添加倒计时标签出错：{e}")

    def handle_fight_over(self, data: Dict):
        self.清空所有倒计时标签()

    def init_ui(self):
        """创建用户界面"""

        self.ref_map["左侧倒计时"] = []  # 存储左侧的倒计时标签和计时器
        self.ref_map["右侧倒计时"] = []  # 存储左侧的倒计时标签和计时器
        self.拖动位置 = None
        self.设置界面 = None
        self.背景标签 = QLabel(self)
        self.背景标签.setGeometry(0, 0, self.width(), self.height())
        self.背景标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.背景动画 = None

        self.设置随机背景()

        self.左侧初始位置 = self.自定义设置["倒计时左初始位置"]  # 左侧初始位置
        self.右侧初始位置 = self.自定义设置["倒计时右初始位置"]  # 右侧初始位置
        self.标签大小 = self.自定义设置["倒计时标签大小"]  # 标签大小

        # 添加常驻标签
        self.创建常驻标签()

        self.关于按钮 = self.按钮批量创建(self.自定义设置["关于按钮"], lambda: self.关于窗口(get_real_path("files/收款码2.png")))
        self.设置按钮 = self.按钮批量创建(self.自定义设置["设置按钮"], self.SheZhiJieMian)
        self.左方按钮 = self.按钮批量创建(self.自定义设置["左方按钮"], lambda: self.添加倒计时标签(方位="左侧"))
        self.右方按钮 = self.按钮批量创建(self.自定义设置["右方按钮"], lambda: self.添加倒计时标签(方位="右侧"))
        self.关闭按钮 = self.按钮批量创建(self.自定义设置["关闭按钮"], lambda: self.终章())
        self.教程按钮 = self.按钮批量创建(self.自定义设置["教程按钮"], lambda: self.教程界面())

    def 按钮批量创建(self, 按钮参数, 触发函数):
        透明度 = 按钮参数[0]
        文本 = 按钮参数[1]
        几何参数 = 按钮参数[2]
        背景色 = 按钮参数[3]
        文本色 = 按钮参数[4]
        字体大小 = 按钮参数[5]
        粗细设置 = 按钮参数[6]
        圆角半径 = 按钮参数[7]
        按钮透明效果 = QGraphicsOpacityEffect()
        按钮透明效果.setOpacity(透明度)
        按钮 = QPushButton(文本, self)
        按钮.setGeometry(几何参数[0], 几何参数[1], 几何参数[2], 几何参数[3])
        按钮.setStyleSheet(
            f"background-color: {背景色};color: {文本色};font-size: {字体大小};font-weight: {粗细设置};border-radius: {圆角半径};"
        )
        按钮.setGraphicsEffect(按钮透明效果)
        按钮.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        按钮.clicked.connect(触发函数)
        return 按钮

    def 关于窗口(self, 图片路径):
        self.关于子窗口 = QWidget()
        self.关于子窗口.setWindowTitle("关于本软件 -- 凤灯幽夜")
        # 创建主布局
        主布局 = QVBoxLayout(self.关于子窗口)
        self.设置窗口图标随机(self.关于子窗口, get_real_path("files/icon"))

        # 定义文本内容列表（简化版）
        文本内容列表 = [
            ('<span style="color: #72E692;">唯一作者ID:</span> <span style="color: #000000;">凤灯幽夜</span>',
            20),
            ('<span style="color: #E672C6;">Bili_Uid:</span> <span style="color: #000000;">11898940</span>',
            20),
            ('<span style="color: #45B7D1;">讨论群:</span> <span style="color: #000000;">548419960</span>',
            20),
            ('<span style="color: #9B59B6;">版本:</span> <span style="color: #000000;">V4.8.0</span>',
            20),
            ('<span style="color: #009C94;">Lofter/Pixiv:</span> <span style="color: #000000;">凤灯幽夜</span>',
            20),
            ('<span style="color: #FFA04A;">特别鸣谢,自软件发布以来259天的唯一打赏:</span> <span style="color: #FFA04A;">来自[咖啡豆浆]的[20元]</span>',
            20)
        ]

        # 批量创建并添加文本标签
        for 内容, 字体大小 in 文本内容列表:
            标签 = self.快速创建文本标签(内容, 字体大小)
            主布局.addWidget(标签)

        # 创建并添加图片标签
        图片标签 = QLabel()
        图片 = QPixmap(图片路径)
        图片标签.setPixmap(图片)
        图片标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
        主布局.addWidget(图片标签)
        # 设置窗口大小
        窗口宽度 = max(图片.width(), 300)
        窗口高度 = 图片.height() + 30 * len(文本内容列表) + 50
        self.关于子窗口.resize(窗口宽度, 窗口高度)
        self.关于子窗口.show()

    def SheZhiJieMian(self):
        try:
            if self.设置界面 is None:  # 如果子窗口不存在，则创建
                self.设置界面 = QWidget()
                self.设置界面.setWindowTitle("设置界面")
                self.设置界面.setGeometry(*self.自定义设置["设置界面几何"])  # 子窗口位置和尺寸
                self.设置窗口图标随机(self.设置界面, get_real_path("files/icon"))
                self.宁次图片标签 = QLabel(self.设置界面)
                self.宁次图片标签.setGeometry(*self.自定义设置["宁次标签几何"])
                宁次基础图片 = QPixmap(get_real_path("files/柔拳法_忍战宁次.png"))
                宁次修改图片 = 宁次基础图片.scaled(self.自定义设置["宁次标签图片大小"][0], self.自定义设置["宁次标签图片大小"][1],
                                                   Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation)
                self.宁次图片标签.setPixmap(宁次修改图片)

                self.点穴开关 = QPushButton("目押点穴", self.设置界面)
                self.点穴开关.setGeometry(*self.自定义设置["宁次按钮几何"])
                self.点穴开关.setStyleSheet(
                    f"background-color: #FFFFFF;color: #000000;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #FF2EE7;"
                )
                self.点穴开关.clicked.connect(self.DianXueKaiGuan)

                self.模式切换标签 = QLabel(self.设置界面)
                self.模式切换标签.setGeometry(*self.自定义设置["模式标签几何"])
                模式切换基础图片 = QPixmap(get_real_path("files/决斗场设置.png"))
                模式切换修改图片 = 模式切换基础图片.scaled(
                    self.自定义设置["模式标签图片大小"][0], self.自定义设置["模式标签图片大小"][1],
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                self.模式切换标签.setPixmap(模式切换修改图片)

                self.模式切换开关 = QPushButton("决斗场", self.设置界面)
                self.模式切换开关.setGeometry(*self.自定义设置["模式按钮几何"])
                self.模式切换开关.setStyleSheet(
                    f"background-color: #FFFFFF;color: #5ACD32;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #5ACD32;"
                )
                self.模式切换开关.clicked.connect(self.MoShiQieHuan)

                self.秒数显示标签 = QLabel(f"{self.fight_info.get_config("倒计时秒数")} 秒", self.设置界面)
                self.秒数显示标签.setGeometry(*self.自定义设置["秒数标签几何"])
                self.秒数显示标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.秒数显示标签.setStyleSheet(
                    f"background-color: #FFFFFF;color: #000000;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #FFDF00;"
                )

                self.加时间按钮 = QPushButton("增加延迟", self.设置界面)
                self.加时间按钮.setGeometry(*self.自定义设置["加时按钮几何"])
                self.加时间按钮.setStyleSheet(
                    f"background-color: #FFFFFF;color: #FF000B;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #FF000B;"
                )
                self.加时间按钮.clicked.connect(lambda: self.YanChiTiaoZheng(0.1))

                self.减时间按钮 = QPushButton("减少延迟", self.设置界面)
                self.减时间按钮.setGeometry(*self.自定义设置["减时按钮几何"])
                self.减时间按钮.setStyleSheet(
                    f"background-color: #FFFFFF;color: #00FF39;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #00FF39;"
                )
                self.减时间按钮.clicked.connect(lambda: self.YanChiTiaoZheng(-0.1))

                self.范围显示按钮 = QPushButton("范围显示", self.设置界面)
                self.范围显示按钮.setGeometry(*self.自定义设置["范围按钮几何"])
                self.范围显示按钮.setStyleSheet(
                    f"background-color: #FFFFFF;color: #693C71;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #693C71;"
                )
                self.范围显示按钮.clicked.connect(
                    lambda: self.TuPianXianShi(QPixmap(get_real_path("files/X轴范围显示.png"))))
                self.范围显示标签 = QLabel(self.设置界面)
                self.范围显示标签.setGeometry(*self.自定义设置["范围标签几何"])
                范围显示基础图片 = QPixmap(get_real_path("files/范围显示.png"))
                范围显示修改图片 = 范围显示基础图片.scaled(
                    self.自定义设置["范围标签图片大小"][0], self.自定义设置["范围标签图片大小"][1],
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
                self.范围显示标签.setPixmap(范围显示修改图片)
        except Exception as e:
            self.logger.error(f"{e}")
        # 切换窗口的显示状态
        if self.设置界面.isVisible():
            self.设置界面.hide()  # 如果窗口可见，则隐藏
        else:
            self.设置界面.show()  # 如果窗口不可见，则显示

    def 添加倒计时标签(self, 方位, trigger_time=None, duration=0):
        try:
            # 根据方位选择对应的倒计时列表和初始位置
            if 方位 == "左侧":
                倒计时列表 = self.ref_map.get("左侧倒计时")
                初始位置 = self.左侧初始位置
            else:  # 右侧
                倒计时列表 = self.ref_map.get("右侧倒计时")
                初始位置 = self.右侧初始位置
            # 计算新标签的位置
            生成位置 = self.计算新标签位置(倒计时列表, 初始位置)
        except Exception as e:
            self.logger.error(f"计算位置出错：{e}")
        try:
            # 创建新的倒计时标签
            self.设置倒计时(倒计时触发时间=trigger_time, 倒计时总数=duration, 生成位置=生成位置, 方位=方位)
        except Exception as e:
            self.logger.error(f"设置倒计时出错：{e}")

    @staticmethod
    def 终章():
        应用.quit()
        print("莫以为光,就会被黑暗吞噬!")
        sys.exit(233)

    def 教程界面(self):
        self.教程窗口 = QWidget()
        self.教程窗口.setWindowTitle("教程窗口")
        self.教程窗口.setGeometry(400, 400, 800, 300)
        self.设置窗口图标随机(self.教程窗口, get_real_path("files/icon"))
        self.标签1 = QLabel("点击按钮召出文件夹,文件夹在软件同目录中", self.教程窗口)
        self.标签1.setGeometry(0, 0, 800, 60)
        self.标签1.setAlignment(Qt.AlignmentFlag.AlignLeft
                                | Qt.AlignmentFlag.AlignVCenter)
        self.标签1.setStyleSheet(
            "font-family: 黑体; font-size: 40px; color: #7DE6AA;")

        self.标签2 = QLabel("可以查看教程文档了解使用方法", self.教程窗口)
        self.标签2.setGeometry(0, 60, 800, 60)
        self.标签2.setAlignment(Qt.AlignmentFlag.AlignLeft
                                | Qt.AlignmentFlag.AlignVCenter)
        self.标签2.setStyleSheet(
            "font-family: 黑体; font-size: 40px; color: #F98CFD;")

        self.标签3 = QLabel("配置文件提供了高度自定义的功能", self.教程窗口)
        self.标签3.setGeometry(0, 120, 800, 60)
        self.标签3.setAlignment(Qt.AlignmentFlag.AlignLeft
                                | Qt.AlignmentFlag.AlignVCenter)
        self.标签3.setStyleSheet(
            "font-family: 黑体; font-size: 40px; color: #CCE03C;")

        self.标签4 = QLabel("误删文件可以点按钮重新召唤", self.教程窗口)
        self.标签4.setGeometry(0, 180, 800, 60)
        self.标签4.setAlignment(Qt.AlignmentFlag.AlignLeft
                                | Qt.AlignmentFlag.AlignVCenter)
        self.标签4.setStyleSheet(
            "font-family: 黑体; font-size: 40px; color: #4D3BE2;")

        self.按钮1 = QPushButton("点我召出教程文件夹", self.教程窗口)
        self.按钮1.setGeometry(0, 240, 800, 60)
        self.按钮1.setStyleSheet(
            "font-family: 黑体; font-size: 40px; color: #A10000; border: 2px solid #A10000;"
        )
        self.按钮1.clicked.connect(lambda: 召出内容(get_real_path("")))
        告诫之文本 = 言语
        self.标签5 = QLabel(告诫之文本, self.教程窗口)
        self.标签5.setGeometry(800, 0, 800, 1080)
        self.标签5.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.标签5.setStyleSheet(
            "font-family: 黑体; font-size: 20px; color: #EDEDED;")
        self.教程窗口.show()

    def 快速创建文本标签(self, 文本内容, 字体大小=12):
        """快速创建富文本标签的简化版本"""
        标签 = QLabel(文本内容)
        标签.setTextFormat(Qt.TextFormat.RichText)
        标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
        标签.setStyleSheet(f"font-size: {字体大小}px;")
        return 标签

    def 设置随机背景(self):
        # 直接检查exe同目录下的背景图片文件夹
        程序目录 = os.path.dirname(sys.executable) if hasattr(
            sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
        背景图片路径 = os.path.join(程序目录, "背景图片")

        if os.path.exists(背景图片路径) and os.path.isdir(背景图片路径):
            图片路径 = self.获取随机图片(背景图片路径)
            print(f"说明你选择了自己用的背景图片:{图片路径}")
        else:
            # 从打包内的文件/BG目录中选择随机图片
            bg_路径 = get_real_path("files/BG")
            if os.path.exists(bg_路径) and os.path.isdir(bg_路径):
                图片路径 = self.获取随机图片(bg_路径)
            else:
                return
        if 图片路径:
            self.应用背景图片(图片路径)

    def 获取随机图片(self, 目录路径):
        # 获取目录中所有图片文件
        图片扩展名 = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        图片文件列表 = []

        for 文件 in os.listdir(目录路径):
            文件路径 = os.path.join(目录路径, 文件)
            if os.path.isfile(文件路径):
                _, 扩展名 = os.path.splitext(文件)
                if 扩展名.lower() in 图片扩展名:
                    图片文件列表.append(文件路径)

        # 如果有图片文件，随机选择一个
        if 图片文件列表:
            return random.choice(图片文件列表)
        return None

    def 应用背景图片(self, 图片路径):
        if 图片路径 is None:
            return

        # 检查文件扩展名
        _, 扩展名 = os.path.splitext(图片路径)

        # 获取窗口/标签目标尺寸
        目标宽度 = self.width()
        目标高度 = self.height()

        # 如果是GIF文件，使用QMovie显示动态背景
        if 扩展名.lower() == '.gif':
            # 如果之前有QMovie对象，先停止并清除
            if hasattr(self, '背景动画') and self.背景动画 is not None:
                self.背景动画.stop()
            self.背景标签.setPixmap(QPixmap())
            self.背景动画 = QMovie(图片路径)

            # 先设置到标签上获取原始尺寸
            self.背景标签.setMovie(self.背景动画)
            self.背景动画.jumpToFrame(0)
            原始尺寸 = self.背景动画.currentImage().size()

            # 获取原始图片尺寸
            原始宽度 = 原始尺寸.width()
            原始高度 = 原始尺寸.height()

            # 计算缩放比例，确保图片完全覆盖目标区域
            宽度缩放比例 = 目标宽度 / 原始宽度
            高度缩放比例 = 目标高度 / 原始高度
            # 选择较大的缩放比例，确保图片能完全覆盖目标区域
            缩放比例 = max(宽度缩放比例, 高度缩放比例)

            # 计算缩放后的尺寸
            新的宽度 = int(原始宽度 * 缩放比例)
            新的高度 = int(原始高度 * 缩放比例)
            新的尺寸 = QSize(新的宽度, 新的高度)

            # 设置背景标签的大小和位置
            self.背景标签.setGeometry(self.自定义设置["动态背景X轴偏移"], self.自定义设置["动态背景Y轴偏移"], 新的宽度,
                                      新的高度)

            # 关键改进：启用平滑缩放
            self.背景标签.setScaledContents(True)

            # 设置缩放尺寸
            self.背景动画.setScaledSize(新的尺寸)
            self.背景动画.start()

        else:
            # 处理静态图片
            if hasattr(self, '背景动画') and self.背景动画 is not None:
                self.背景动画.stop()
                self.背景动画 = None

            # 创建QPixmap对象并加载图片
            背景图片 = QPixmap(图片路径)

            # 获取原始图片尺寸
            原始宽度 = 背景图片.width()
            原始高度 = 背景图片.height()

            # 计算缩放比例，确保图片完全覆盖目标区域
            宽度缩放比例 = 目标宽度 / 原始宽度
            高度缩放比例 = 目标高度 / 原始高度
            # 选择较大的缩放比例，确保图片能完全覆盖目标区域
            缩放比例 = max(宽度缩放比例, 高度缩放比例)

            # 计算缩放后的尺寸
            新的宽度 = int(原始宽度 * 缩放比例)
            新的高度 = int(原始高度 * 缩放比例)
            新的尺寸 = QSize(新的宽度, 新的高度)

            # 缩放图片到新尺寸
            背景图片 = 背景图片.scaled(
                新的尺寸,
                Qt.AspectRatioMode.KeepAspectRatio,  # 保持宽高比
                Qt.TransformationMode.SmoothTransformation)

            # 设置背景标签的大小和位置
            self.背景标签.setGeometry(self.自定义设置["静态背景X轴偏移"], self.自定义设置["静态背景Y轴偏移"], 新的宽度,
                                      新的高度)

            # 设置背景图片
            self.背景标签.setPixmap(背景图片)

    def AnJianChuLi(self, 按键):
        if 按键.lower() == self.fight_info.get_config("模拟左侧替身按键"):
            self.添加倒计时标签(方位="左侧")
        elif 按键.lower() == self.fight_info.get_config("模拟右侧替身按键"):
            self.添加倒计时标签(方位="右侧")
        elif 按键.lower() == self.fight_info.get_config("关闭程序按键"):
            self.终章()
        elif 按键.lower() == self.fight_info.get_config("清空倒计时按键"):
            self.清空所有倒计时标签()
        else:
            # print(f"检测按键：{按键}")
            pass

    def YanChiTiaoZheng(self, 延时):
        self.fight_info.set_config("倒计时秒数", round(self.fight_info.get_config("倒计时秒数") + 延时, 1))
        self.秒数显示标签.setText(f"{self.fight_info.get_config("倒计时秒数"):.1f} 秒")
        self.logger.info(f"当前倒计时: {self.fight_info.get_config("倒计时秒数"):.1f} 秒")

    def MoShiQieHuan(self):
        if self.fight_info.get_config("默认模式") == "决斗场":
            模式切换基础图片 = QPixmap(get_real_path("files/训练营设置.png"))
            模式切换修改图片 = 模式切换基础图片.scaled(
                self.自定义设置["模式标签图片大小"][0], self.自定义设置["模式标签图片大小"][1],
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.模式切换标签.setPixmap(模式切换修改图片)
            self.模式切换开关.setText("训练营")
            self.模式切换开关.setStyleSheet(
                f"background-color: #FFFFFF;color: #E45F1B;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #E45F1B;"
            )
            self.fight_info.set_config("默认模式", "训练营")
            self.fight_info_update.roi_dic = self.resolutions[self.fight_info.get_config("默认分辨率")]["roi_dic"]["训练营"]
        elif self.fight_info.get_config("默认模式") == "训练营":
            模式切换基础图片 = QPixmap(get_real_path("files/决斗场设置.png"))
            模式切换修改图片 = 模式切换基础图片.scaled(
                self.自定义设置["模式标签图片大小"][0], self.自定义设置["模式标签图片大小"][1],
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.模式切换标签.setPixmap(模式切换修改图片)
            self.模式切换开关.setText("决斗场")
            self.模式切换开关.setStyleSheet(
                f"background-color: #FFFFFF;color: #5ACD32;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #5ACD32;"
            )
            self.fight_info.set_config("默认模式", "决斗场")
            self.fight_info_update.roi_dic = self.resolutions[self.fight_info.get_config("默认分辨率")]["roi_dic"]["决斗场"]

    def TuPianXianShi(self, 图片路径):
        if hasattr(self, '图片窗口') and self.图片窗口 is not None:
            if self.图片窗口.isVisible():
                self.图片窗口.hide()
            else:
                self.图片窗口.show()
        else:
            self.图片窗口 = QWidget()
            self.图片窗口.setWindowTitle("图片显示")
            self.图片窗口.setWindowFlags(Qt.WindowType.FramelessWindowHint
                                         | Qt.WindowType.WindowStaysOnTopHint
                                         | Qt.WindowType.Tool
                                         | Qt.WindowType.WindowTransparentForInput)
            self.图片窗口.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.图片窗口.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.图片窗口.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
            self.图片窗口.setStyleSheet("background:transparent;")
            屏幕 = QApplication.primaryScreen().size()
            self.图片窗口.setGeometry(0, 0, 屏幕.width(), 屏幕.height())
            self.图片标签 = QLabel(self.图片窗口)
            self.图片标签.setGeometry(0, 0, 屏幕.width(), 屏幕.height())
            self.图片标签.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            图片 = QPixmap(图片路径)
            self.图片标签.setPixmap(
                图片.scaled(屏幕.width(), 屏幕.height(),
                            Qt.AspectRatioMode.KeepAspectRatio))
            self.图片标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.图片窗口.show()

    def DianXueKaiGuan(self):
        try:
            if self.fight_info.get_config("点穴开关") == 1:
                self.fight_info.set_config("点穴开关", 0)
                self.点穴开关.setText("已关闭")
                self.点穴开关.setStyleSheet(
                    f"background-color: #FFFFFF;color: #FF0000;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #FF0000;"
                )
            elif self.fight_info.get_config("点穴开关") == 0:
                self.fight_info.set_config("点穴开关", 1)
                self.点穴开关.setText("已开启")
                self.点穴开关.setStyleSheet(
                    f"background-color: #FFFFFF;color: #00FF34;font-size: {self.自定义设置['设置窗口字体大小']};border: {self.自定义设置['设置窗口边缘像素']} solid #00FF34;"
                )
        except Exception as e:
            print(f"{e}")

    def 左右标签更新(self, 对应标签, 文本背景色文本色):
        新文本 = 文本背景色文本色[0]
        背景色 = 文本背景色文本色[1]
        文本色 = 文本背景色文本色[2]
        对应标签.setText(新文本)
        对应标签.setStyleSheet(f"background-color: {背景色};color: {文本色}")

    def 创建常驻标签(self, ):
        左标签位置 = self.自定义设置["常驻标签左位置"]
        左标签大小 = self.自定义设置["常驻标签左大小"]
        左标签背景色 = self.自定义设置["常驻标签左背景色"]
        左标签文本色 = self.自定义设置["常驻标签左文本色"]
        右标签位置 = self.自定义设置["常驻标签右位置"]
        右标签大小 = self.自定义设置["常驻标签右大小"]
        右标签背景色 = self.自定义设置["常驻标签右背景色"]
        右标签文本色 = self.自定义设置["常驻标签右文本色"]
        标签字号 = self.自定义设置["常驻标签字号"]
        标签字体 = self.自定义设置["常驻标签字体"]
        透明度 = self.自定义设置["常驻标签透明度"]
        左标签文本 = "BY 凤灯幽夜"
        右标签文本 = "本软件纯免费"

        self.ref_map["常驻标签左"] = QLabel(self)
        self.ref_map["常驻标签左"].setGeometry(左标签位置[0], 左标签位置[1], 左标签大小[0], 左标签大小[1])
        self.ref_map["常驻标签左"].setText(左标签文本)
        self.ref_map["常驻标签左"].setFont(QFont(标签字体, 标签字号))
        # 设置左侧标签样式
        左侧调色板 = self.ref_map["常驻标签左"].palette()
        左侧调色板.setColor(QPalette.ColorRole.Window, QColor(左标签背景色))
        左侧调色板.setColor(QPalette.ColorRole.WindowText, QColor(左标签文本色))
        self.ref_map["常驻标签左"].setPalette(左侧调色板)
        self.ref_map["常驻标签左"].setAutoFillBackground(True)
        # 设置左侧标签文本对齐方式
        self.ref_map["常驻标签左"].setAlignment(Qt.AlignmentFlag.AlignLeft
                                                | Qt.AlignmentFlag.AlignVCenter)
        # 设置透明度
        常驻标签左透明效果 = QGraphicsOpacityEffect()
        常驻标签左透明效果.setOpacity(透明度)
        self.ref_map["常驻标签左"].setGraphicsEffect(常驻标签左透明效果)
        # 创建右侧常驻标签
        self.ref_map["常驻标签右"] = QLabel(self)
        self.ref_map["常驻标签右"].setGeometry(右标签位置[0], 右标签位置[1], 右标签大小[0], 右标签大小[1])
        self.ref_map["常驻标签右"].setText(右标签文本)
        self.ref_map["常驻标签右"].setFont(QFont(标签字体, 标签字号))
        # 设置右侧标签样式
        右侧调色板 = self.ref_map["常驻标签右"].palette()
        右侧调色板.setColor(QPalette.ColorRole.Window, QColor(右标签背景色))
        右侧调色板.setColor(QPalette.ColorRole.WindowText, QColor(右标签文本色))
        self.ref_map["常驻标签右"].setPalette(右侧调色板)
        self.ref_map["常驻标签右"].setAutoFillBackground(True)
        # 设置右侧标签文本对齐方式
        self.ref_map["常驻标签右"].setAlignment(Qt.AlignmentFlag.AlignRight
                                                | Qt.AlignmentFlag.AlignVCenter)
        # 设置透明度
        常驻标签右透明效果 = QGraphicsOpacityEffect()
        常驻标签右透明效果.setOpacity(透明度)
        self.ref_map["常驻标签右"].setGraphicsEffect(常驻标签右透明效果)

        self.ref_map["常驻标签右"].show()
        self.ref_map["常驻标签右"].show()

    def 计算新标签位置(self, 倒计时列表, 初始位置):
        """计算新标签应该放置的位置"""
        # 检查所有现有标签的位置
        已占用位置 = []
        for 标签, _, 位置, _ in 倒计时列表:
            if not 标签.isVisible():  # 跳过已经不可见的标签
                continue
            已占用位置.append(位置)
        # 初始位置X和Y
        X位置, Y位置 = 初始位置
        _, Y大小 = self.标签大小
        # 如果初始位置没有被占用，使用初始位置
        if 初始位置 not in 已占用位置:
            return 初始位置
        # 否则，找到一个未被占用的位置
        当前Y = Y位置
        while True:
            当前Y += Y大小
            新位置 = (X位置, 当前Y)
            if 新位置 not in 已占用位置:
                return 新位置

    def 设置倒计时(self, 倒计时触发时间, 倒计时总数, 生成位置=None, 方位="左侧"):
        self.logger.debug(f"{方位}替身触发时间:{倒计时触发时间}s,总时间：{倒计时总数}s")
        字体 = self.自定义设置["倒计时字体"]
        字号 = self.自定义设置["倒计时字号"]
        背景颜色 = self.自定义设置["倒计时背景色"]
        字体颜色 = self.自定义设置["倒计时字体色"]
        标签大小 = self.自定义设置["倒计时标签大小"]
        透明度 = self.自定义设置["倒计时透明度"]
        字体居中 = True
        # 根据方位选择对应的初始位置和倒计时列表
        if 方位 == "左侧":
            初始位置 = self.左侧初始位置
            倒计时列表 = self.ref_map.get("左侧倒计时")
        else:  # 右侧
            初始位置 = self.右侧初始位置
            倒计时列表 = self.ref_map.get("右侧倒计时")

        if 生成位置 is None:
            生成位置 = 初始位置

        if 标签大小 is None:
            标签大小 = self.标签大小

        # 创建新标签
        新倒计时标签 = QLabel(self)
        倒计时小窗X位置, 倒计时小窗Y位置 = 生成位置
        倒计时小窗X大小, 倒计时小窗Y大小 = 标签大小
        新倒计时标签.setGeometry(倒计时小窗X位置, 倒计时小窗Y位置, 倒计时小窗X大小, 倒计时小窗Y大小)
        字体对象 = QFont(字体, 字号)
        新倒计时标签.setFont(字体对象)

        # 文字对齐
        if 字体居中:
            新倒计时标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            新倒计时标签.setAlignment(Qt.AlignmentFlag.AlignRight
                                      | Qt.AlignmentFlag.AlignVCenter)

        # 设置背景色和字体颜色
        背景与字体色 = 新倒计时标签.palette()
        背景与字体色.setColor(QPalette.ColorRole.Window, QColor(背景颜色))
        背景与字体色.setColor(QPalette.ColorRole.WindowText, QColor(字体颜色))
        新倒计时标签.setPalette(背景与字体色)

        # 使背景可见（默认为透明）
        新倒计时标签.setAutoFillBackground(True)
        整体透明效果 = QGraphicsOpacityEffect()
        整体透明效果.setOpacity(透明度)  # 设置透明度 (0.0 完全透明，1.0 完全不透明)
        新倒计时标签.setGraphicsEffect(整体透明效果)
        # 为这个特定的倒计时创建一个计时器
        计时器 = QTimer(self)
        计时器.setInterval(50)  # 100毫秒间隔
        # 初始化倒计时时间
        if 倒计时触发时间:
            剩余时间 = 倒计时总数 - (time.perf_counter() - 倒计时触发时间)
            # print(f"{剩余时间:.1f}")
            新倒计时标签.setText(f"{剩余时间:.1f}")
            新倒计时标签.show()

            # 创建一个闭包函数来更新这个特定的倒计时
            def 更新这个倒计时():
                nonlocal 倒计时触发时间
                剩余时间 = 倒计时总数 - (time.perf_counter() - 倒计时触发时间)
                新倒计时标签.setText(f"{剩余时间:.1f}")
                if 剩余时间 <= 0:
                    self.logger.debug(f"{方位}替身结束时间:{time.perf_counter()}s")
                    self.logger.debug(f"{方位}替身计时:{time.perf_counter() - 倒计时触发时间}s")
                    计时器.stop()
                    新倒计时标签.setText("0.0")
                    # 延迟删除标签
                    删除计时器 = QTimer(self)
                    删除计时器.setSingleShot(True)
                    删除计时器.timeout.connect(lambda: self.删除倒计时标签(新倒计时标签, 方位))
                    删除计时器.start(100)  # 0.1秒后删除

            # 连接计时器信号到更新函数
            计时器.timeout.connect(更新这个倒计时)
        else:
            剩余时间 = self.fight_info.get_config("倒计时秒数")

            # print(f"{剩余时间:.1f}")
            新倒计时标签.setText(f"{剩余时间:.1f}")
            新倒计时标签.show()

            # 创建一个闭包函数来更新这个特定的倒计时
            def 更新这个倒计时():
                nonlocal 剩余时间
                剩余时间 -= 0.1
                剩余时间 = round(剩余时间, 1)
                新倒计时标签.setText(f"{剩余时间:.1f}")

                if 剩余时间 <= 0:
                    计时器.stop()
                    新倒计时标签.setText("0.0")
                    # 延迟删除标签
                    删除计时器 = QTimer(self)
                    删除计时器.setSingleShot(True)
                    删除计时器.timeout.connect(lambda: self.删除倒计时标签(新倒计时标签, 方位))
                    删除计时器.start(100)  # 0.1秒后删除

            # 连接计时器信号到更新函数
            计时器.timeout.connect(更新这个倒计时)
        # 启动计时器
        计时器.start()
        # 将新创建的标签和计时器存储在对应的列表中
        倒计时列表.append((新倒计时标签, 计时器, 生成位置, 标签大小))

    def 删除倒计时标签(self, 标签, 方位="左侧"):
        if 方位 == "左侧":
            倒计时列表 = self.ref_map.get("左侧倒计时")
        else:  # 右侧
            倒计时列表 = self.ref_map.get("右侧倒计时")
        for i, (当前标签, 当前计时器, _, _) in enumerate(倒计时列表):
            if 当前标签 == 标签:
                当前计时器.stop()
                当前标签.hide()
                当前标签.deleteLater()
                倒计时列表.pop(i)
                break

    def 清空所有倒计时标签(self, 方位=None):
        def 清空指定方位(倒计时列表):
            """清空指定方位的所有倒计时标签"""
            # 从后往前遍历，避免删除时索引变化的问题
            for 标签, 计时器, _, _ in reversed(倒计时列表):
                # 停止计时器
                计时器.stop()
                # 隐藏并删除标签
                标签.hide()
                标签.deleteLater()
            # 清空列表
            倒计时列表.clear()

        if 方位 == "左侧":
            清空指定方位(self.ref_map.get("左侧倒计时"))
        elif 方位 == "右侧":
            清空指定方位(self.ref_map.get("右侧倒计时"))
        else:  # 方位为None，清空所有
            清空指定方位(self.ref_map.get("左侧倒计时"))
            清空指定方位(self.ref_map.get("右侧倒计时"))

    def mousePressEvent(self, 事件):
        """鼠标按下事件"""
        if 事件.button() == Qt.MouseButton.LeftButton:
            # 记录鼠标按下时的位置
            self.拖动位置 = 事件.globalPosition().toPoint() - self.frameGeometry(
            ).topLeft()
            事件.accept()

    def mouseMoveEvent(self, 事件):
        """鼠标移动事件"""
        if 事件.buttons() == Qt.MouseButton.LeftButton and self.拖动位置 is not None:
            # 计算新位置并移动窗口
            self.move(事件.globalPosition().toPoint() - self.拖动位置)
            事件.accept()

    def mouseReleaseEvent(self, 事件):
        """鼠标释放事件"""
        if 事件.button() == Qt.MouseButton.LeftButton:
            # 重置拖动位置
            self.拖动位置 = None
            事件.accept()

def 触发_左键短按(坐标):
    mouse.move(坐标[0], 坐标[1])
    mouse.press(button='left')

    # 使用QTimer创建非阻塞延时
    def 释放鼠标():
        mouse.release(button='left')
        mouse.move(0, 0)

    # 设置单次触发的定时器，200毫秒后释放鼠标
    QTimer.singleShot(200, 释放鼠标)

if __name__ == "__main__":
    应用 = QApplication(sys.argv)
    窗口 = 根窗口()
    窗口.show()
    sys.exit(应用.exec())

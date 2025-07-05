import sys
import os
import shutil
import random
import ctypes
import mouse
import socket
from pynput import keyboard
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QGraphicsOpacityEffect, QSystemTrayIcon
from PyQt6.QtCore import Qt, QSize, QRect, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QMovie, QGuiApplication, QColor, QFont, QPalette, QIcon
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
自定义设置 = {
    # 建议根据自己情况修改的内容:
    # 由于各个电脑性能不同,所模拟的秒数也不同,
    # 建议自己测试一下误差,看看与实际差了多少秒
    "倒计时秒数": 13.5,
    "RGB容差值": 4,  # 建议不超过5,不小于1
    # 设置检测速率,数越低频率越快
    # 单位是毫秒,100ms相当于0.1秒一次,不建议大于100ms,一般100ms足够
    # 请根据性能酌情选择档位,不宜过低
    "检测速率": 100,
    # 按键触发的内容
    "关闭程序按键": "x",
    "模拟左侧替身按键": "z",
    "模拟右侧替身按键": "c",
    "清空倒计时按键": "v",#可以在游戏开始的时候清空一些紊乱的计时
    # 某些状态类内容
    "基础模式": "决斗场",
    "点穴开关": "关闭",
    "记牌开关": "开启",
    "线程开关": "开启",
    "回放开关": "开启",
    # 窗口背景自定义化
    # 事实上我建议你如果要自定义,建议一开始的图像就设置好比例和尺寸符合窗口,而不需要这里设置
    "动态背景X轴偏移": 0,  # 左右方向偏移像素量,填负数是向左
    "动态背景Y轴偏移": 0,  # 上下方向偏移像素量,填负数是向上
    "静态背景X轴偏移": 0,
    "静态背景Y轴偏移": 0,
    # 下面的内容,除非你知道你在改什么,不然不建议乱改
    # 确定知道你在做什么!
    # 主窗口相关
    "主窗口位置与大小": (810, 190, 300, 150),
    # 窗口按钮相关
    # 透明度,文本,几何参数,背景色,文本色,字体大小,粗细设置,圆角半径,
    "关于按钮": (1.0, "关于", (0, 120, 50, 30), "#FFFFFF", "#000000", "18px", "bold", "0px"),
    "设置按钮": (1.0, "设置", (50, 120, 50, 30), "#FFFE6C", "#000000", "18px", "bold", "0px"),
    "左方按钮": (1.0, "左方", (100, 120, 50, 30), "#7CDFEC", "#000000", "18px", "bold", "0px"),
    "右方按钮": (1.0, "右方", (150, 120, 50, 30), "#E06582", "#000000", "18px", "bold", "0px"),
    "关闭按钮": (1.0, "关闭", (200, 120, 50, 30), "#A285DD", "#000000", "18px", "bold", "0px"),
    "教程按钮": (1.0, "教程", (250, 120, 50, 30), "#83FF80", "#000000", "18px", "bold", "0px"),
    # 倒计时标签设置
    "倒计时透明度": 1.0,
    "倒计时字体": "黑体",
    "倒计时字号": 18,
    "倒计时背景色": "#FFDCF6",
    "倒计时字体色": "#25B7A8",
    "倒计时标签大小": (50, 30),
    "倒计时左初始位置": (0, 30),
    "倒计时右初始位置": (250, 30),
    # 常驻标签设置,主要设置字体,字号,透明度,位置,大小
    "常驻标签透明度": 1.0,
    "常驻标签字体": "黑体",
    "常驻标签字号": 18,
    "常驻标签左位置": (0, 0),
    "常驻标签左大小": (150, 30),
    "常驻标签左背景色": "#FFFFFF",
    "常驻标签左文本色": "#EC137A",
    "常驻标签右位置": (150, 0),
    "常驻标签右大小": (150, 30),
    "常驻标签右背景色": "#FFFFFF",
    "常驻标签右文本色": "#EC137A",
    # 设置窗口相关
    "设置窗口字体大小": "16px",
    "设置窗口边缘像素": "2px",
    "设置界面几何": (810, 390, 300, 105),

    "宁次标签几何": (0, 0, 75, 75),
    "宁次标签图片大小": (75, 75),
    "宁次按钮几何": (0, 75, 75, 30),

    "模式标签几何": (75, 0, 75, 75),
    "模式标签图片大小": (75, 75),
    "模式按钮几何": (75, 75, 75, 30),

    "秒数标签几何": (150, 30, 75, 45),
    "加时按钮几何": (150, 0, 75, 30),
    "减时按钮几何": (150, 75, 75, 30),

    "范围标签几何": (225, 0, 75, 75),
    "范围标签图片大小": (75, 75),
    "范围按钮几何": (225, 75, 75, 30),
    # 豆豆颜色显示相关
    # 文本,背景色,文本色
    "常驻标签左零豆_常态": ["◇◇◇◇", "#FFFFFF", "#00D29E"],
    "常驻标签左一豆_常态": ["◆◇◇◇", "#FFFFFF", "#2AA4DB"],
    "常驻标签左二豆_常态": ["◆◆◇◇", "#FFFFFF", "#2AA4DB"],
    "常驻标签左三豆_常态": ["◆◆◆◇", "#FFFFFF", "#2AA4DB"],
    "常驻标签左四豆_常态": ["◆◆◆◆", "#FFFFFF", "#FF791B"],
    "常驻标签左零豆_柱间": ["◇◇◇◇◇◇", "#FFFFFF", "#00D29E"],
    "常驻标签左一豆_柱间": ["◆◇◇◇◇◇", "#FFFFFF", "#2AA4DB"],
    "常驻标签左二豆_柱间": ["◆◆◇◇◇◇", "#FFFFFF", "#2AA4DB"],
    "常驻标签左三豆_柱间": ["◆◆◆◇◇◇", "#FFFFFF", "#2AA4DB"],
    "常驻标签左四豆_柱间": ["◆◆◆◆◇◇", "#FFFFFF", "#F43232"],
    "常驻标签左五豆_柱间": ["◆◆◆◆◆◇", "#FFFFFF", "#F43232"],
    "常驻标签左六豆_柱间": ["◆◆◆◆◆◆", "#FFFFFF", "#F43232"],
    "常驻标签左零豆_六尾鸣": ["◇◇◇◇", "#FFFFFF", "#F43232"],
    "常驻标签左一豆_六尾鸣": ["◆◇◇◇", "#FFFFFF", "#F43232"],
    "常驻标签左二豆_六尾鸣": ["◆◆◇◇", "#FFFFFF", "#F43232"],
    "常驻标签左三豆_六尾鸣": ["◆◆◆◇", "#FFFFFF", "#F43232"],
    "常驻标签左四豆_六尾鸣": ["◆◆◆◆", "#FFFFFF", "#F43232"],

    "常驻标签右零豆_常态": ["◇◇◇◇", "#FFFFFF", "#00D29E"],
    "常驻标签右一豆_常态": ["◇◇◇◆", "#FFFFFF", "#2AA4DB"],
    "常驻标签右二豆_常态": ["◇◇◆◆", "#FFFFFF", "#2AA4DB"],
    "常驻标签右三豆_常态": ["◇◆◆◆", "#FFFFFF", "#2AA4DB"],
    "常驻标签右四豆_常态": ["◆◆◆◆", "#FFFFFF", "#FF791B"],
    "常驻标签右零豆_柱间": ["◇◇◇◇◇◇", "#FFFFFF", "#00D29E"],
    "常驻标签右一豆_柱间": ["◇◇◇◇◇◆", "#FFFFFF", "#2AA4DB"],
    "常驻标签右二豆_柱间": ["◇◇◇◇◆◆", "#FFFFFF", "#2AA4DB"],
    "常驻标签右三豆_柱间": ["◇◇◇◆◆◆", "#FFFFFF", "#2AA4DB"],
    "常驻标签右四豆_柱间": ["◇◇◆◆◆◆", "#FFFFFF", "#F43232"],
    "常驻标签右五豆_柱间": ["◇◆◆◆◆◆", "#FFFFFF", "#F43232"],
    "常驻标签右六豆_柱间": ["◆◆◆◆◆◆", "#FFFFFF", "#F43232"],
    "常驻标签右零豆_六尾鸣": ["◇◇◇◇", "#FFFFFF", "#F43232"],
    "常驻标签右一豆_六尾鸣": ["◇◇◇◆", "#FFFFFF", "#F43232"],
    "常驻标签右二豆_六尾鸣": ["◇◇◆◆", "#FFFFFF", "#F43232"],
    "常驻标签右三豆_六尾鸣": ["◇◆◆◆", "#FFFFFF", "#F43232"],
    "常驻标签右四豆_六尾鸣": ["◆◆◆◆", "#FFFFFF", "#F43232"],
    # 宁次点穴相关
    # 各个模式中,须满足点位正确才会检测点穴,然后点穴模拟普攻
    "点穴点位": (1550, 700),
    "点穴最大RGB": (255, 255, 255),
    "点穴最小RGB": (176, 248, 246),
    "训练营点位": (950, 970),
    "训练营最大RGB": (253, 202, 0),
    "训练营最小RGB": (253, 202, 0),
    "模拟战点位": (100, 250),
    "模拟战最大RGB": (9, 9, 9),
    "模拟战最小RGB": (4, 4, 4),
    "决斗场点位": (65, 445),
    "决斗场最大RGB": (255, 249, 222),
    "决斗场最小RGB": (207, 204, 183),
    # 记牌点位相关
    # 须满足所有点位正确才会检测记牌,然后贴图通灵秘卷
    "秘卷点位一坐标": (1000, 830),
    "秘卷点位二坐标": (920, 860),
    "秘卷点位三坐标": (1030, 880),
    "秘卷点位四坐标": (1000, 820),
    "秘卷点位一颜色小": (255, 61, 0),
    "秘卷点位一颜色大": (255, 61, 0),
    "秘卷点位二颜色小": (255, 50, 0),
    "秘卷点位二颜色大": (255, 50, 0),
    "秘卷点位三颜色小": (255, 61, 0),
    "秘卷点位三颜色大": (255, 61, 0),
    "秘卷点位四颜色小": (255, 66, 0),
    "秘卷点位四颜色大": (255, 66, 0),
    "通灵点位一坐标": (1850, 100),
    "通灵点位二坐标": (75, 100),
    "通灵点位三坐标": (1097, 75),
    "通灵点位四坐标": (970, 90),
    "通灵点位一颜色小": (138, 40, 16),
    "通灵点位一颜色大": (138, 40, 16),
    "通灵点位二颜色小": (99, 78, 138),
    "通灵点位二颜色大": (99, 78, 138),
    "通灵点位三颜色小": (255, 255, 254),
    "通灵点位三颜色大": (255, 255, 254),
    "通灵点位四颜色小": (255, 255, 255),
    "通灵点位四颜色大": (255, 255, 255),
    # 记牌标签窗口设置
    # 设置检测XY起始点与XY范围,与最终的窗口中的缩放XY大小
    "左通灵显示标签几何": (90, 2, 360, 120, 90, 30),
    "右通灵显示标签几何": (1465, 2, 360, 120, 90, 30),
    "左秘卷显示标签一几何": (659, 631, 57, 57, 30, 30),
    "左秘卷显示标签二几何": (337, 631, 57, 57, 30, 30),
    "左秘卷显示标签三几何": (14, 631, 57, 57, 30, 30),
    "右秘卷显示标签一几何": (1213, 632, 57, 57, 30, 30),
    "右秘卷显示标签二几何": (1535, 632, 57, 57, 30, 30),
    "右秘卷显示标签三几何": (1862, 632, 57, 57, 30, 30),
    # 秘卷通灵记录相关
    # 设置放在窗口中的XY位置与XY大小
    "左通灵显示标签": (50, 60, 90, 30),
    "右通灵显示标签": (160, 60, 90, 30),
    "左秘卷显示标签一": (110, 90, 30, 30),
    "左秘卷显示标签二": (80, 90, 30, 30),
    "左秘卷显示标签三": (50, 90, 30, 30),
    "右秘卷显示标签一": (160, 90, 30, 30),
    "右秘卷显示标签二": (190, 90, 30, 30),
    "右秘卷显示标签三": (220, 90, 30, 30),
    # 豆豆颜色区间
    # 靠这个决定豆豆,核心功能
    "暗青最大RGB": (60, 55, 103),
    "暗青最小RGB": (13, 3, 1),
    "亮蓝最大RGB": (225, 255, 255),
    "亮蓝最小RGB": (0, 120, 170),
    "赤金最大RGB": (255, 255, 206),
    "赤金最小RGB": (179, 19, 1),
    # 回放点位相关
    # 须满足所有点位正确才会自动保存回放
    "回放点位一坐标": (1500, 40),
    "回放点位二坐标": (1690, 50),
    "回放点位三坐标": (1690, 60),
    "回放点位四坐标": (1450, 40),
    "回放点位一颜色大": (252, 202, 0),
    "回放点位一颜色小": (227, 182, 0),
    "回放点位二颜色大": (174, 184, 180),
    "回放点位二颜色小": (170, 181, 178),
    "回放点位三颜色大": (175, 185, 179),
    "回放点位三颜色小": (171, 181, 177),
    "回放点位四颜色大": (184, 123, 65),
    "回放点位四颜色小": (184, 122, 64),
    # 鼠标点击坐标
    # 模拟鼠标点击坐标
    "宁次点穴普攻坐标": (1700, 900),
    "回放点位点击坐标": (1500, 40),
    # 各个坐标点位_决斗场
    # 决斗场的各个豆位置
    "左方第一个豆_决斗场": (206, 110),
    "左方第二个豆_决斗场": (237, 110),
    "左方第三个豆_决斗场": (267, 110),
    "左方第四个豆_决斗场": (297, 110),
    "左方第五个豆_决斗场": (328, 110),
    "左方第六个豆_决斗场": (358, 110),
    "右方第一个豆_决斗场": (1708, 110),
    "右方第二个豆_决斗场": (1677, 110),
    "右方第三个豆_决斗场": (1646, 110),
    "右方第四个豆_决斗场": (1616, 110),
    "右方第五个豆_决斗场": (1586, 110),
    "右方第六个豆_决斗场": (1555, 110),
    # 各个坐标点位_训练营
    # 训练营的各个豆位置
    "左方第一个豆_训练营": (187, 105),
    "左方第二个豆_训练营": (217, 105),
    "左方第三个豆_训练营": (247, 105),
    "左方第四个豆_训练营": (278, 105),
    "左方第五个豆_训练营": (308, 105),
    "左方第六个豆_训练营": (338, 105),
    "右方第一个豆_训练营": (1669, 108),
    "右方第二个豆_训练营": (1639, 108),
    "右方第三个豆_训练营": (1608, 108),
    "右方第四个豆_训练营": (1577, 108),
    "右方第五个豆_训练营": (1547, 108),
    "右方第六个豆_训练营": (1516, 108),
    # 柱间检测相关_决斗场
    # 柱间检测头像点位,需要满足所有点位符合才会视作柱间在场
    "左柱间点位_决斗场": [(120, 20), (120, 30), (130, 20), (130, 20)],
    "右柱间点位_决斗场": [(1785, 15), (1785, 25), (1795, 15), (1795, 25)],
    "秽土柱间最大RGB_决斗场": (50, 50, 33),
    "秽土柱间最小RGB_决斗场": (49, 49, 31),
    "创立柱间最大RGB_决斗场": (46, 45, 28),
    "创立柱间最小RGB_决斗场": (46, 45, 27),
    # 柱间检测相关_训练营
    "左柱间点位_训练营": [(100, 10), (100, 20), (110, 10), (110, 20)],
    "右柱间点位_训练营": [(1745, 15), (1745, 25), (1755, 15), (1755, 25)],
    "秽土柱间最大RGB_训练营": (50, 49, 32),
    "秽土柱间最小RGB_训练营": (50, 49, 31),
    "创立柱间最大RGB_训练营": (46, 45, 28),
    "创立柱间最小RGB_训练营": (45, 44, 27),

}
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
def 加载配置():
    # 获取当前执行文件的目录
    if hasattr(sys, 'frozen'):  # 检查是否是打包的exe
        运行目录 = os.path.dirname(sys.executable)
    else:
        运行目录 = os.path.dirname(os.path.abspath(__file__))

    配置文件名 = os.path.join(运行目录, '配置.txt')

    if os.path.exists(配置文件名):
        with open(配置文件名, 'r', encoding='utf-8') as f:
            配置代码 = f.read()
        exec(配置代码, globals())
        print(f"配置文件 '{配置文件名}' 已加载")
    else:
        print("常规启动")


加载配置()
RGB容差值 = 自定义设置["RGB容差值"]
基础模式 = {"状态": 自定义设置["基础模式"], }
点穴开关 = {"状态": 自定义设置["点穴开关"], }
记牌开关 = {"状态": 自定义设置["记牌开关"], }
线程开关 = {"状态": 自定义设置["线程开关"], }
回放开关 = {"状态": 自定义设置["回放开关"], }
回放点位相关 = {
    "回放点位一坐标": 自定义设置["回放点位一坐标"],
    "回放点位二坐标": 自定义设置["回放点位二坐标"],
    "回放点位三坐标": 自定义设置["回放点位三坐标"],
    "回放点位四坐标": 自定义设置["回放点位四坐标"],
    "回放点位一颜色小": 自定义设置["回放点位一颜色小"],
    "回放点位一颜色大": 自定义设置["回放点位一颜色大"],
    "回放点位二颜色小": 自定义设置["回放点位二颜色小"],
    "回放点位二颜色大": 自定义设置["回放点位二颜色大"],
    "回放点位三颜色小": 自定义设置["回放点位三颜色小"],
    "回放点位三颜色大": 自定义设置["回放点位三颜色大"],
    "回放点位四颜色小": 自定义设置["回放点位四颜色小"],
    "回放点位四颜色大": 自定义设置["回放点位四颜色大"],
    "回放点位点击坐标": 自定义设置["回放点位点击坐标"],
}
记牌点位相关 = {
    "秘卷点位一坐标": 自定义设置["秘卷点位一坐标"],
    "秘卷点位二坐标": 自定义设置["秘卷点位二坐标"],
    "秘卷点位三坐标": 自定义设置["秘卷点位三坐标"],
    "秘卷点位四坐标": 自定义设置["秘卷点位四坐标"],
    "秘卷点位一颜色小": 自定义设置["秘卷点位一颜色小"],
    "秘卷点位一颜色大": 自定义设置["秘卷点位一颜色大"],
    "秘卷点位二颜色小": 自定义设置["秘卷点位二颜色小"],
    "秘卷点位二颜色大": 自定义设置["秘卷点位二颜色大"],
    "秘卷点位三颜色小": 自定义设置["秘卷点位三颜色小"],
    "秘卷点位三颜色大": 自定义设置["秘卷点位三颜色大"],
    "秘卷点位四颜色小": 自定义设置["秘卷点位四颜色小"],
    "秘卷点位四颜色大": 自定义设置["秘卷点位四颜色大"],
    "通灵点位一坐标": 自定义设置["通灵点位一坐标"],
    "通灵点位二坐标": 自定义设置["通灵点位二坐标"],
    "通灵点位三坐标": 自定义设置["通灵点位三坐标"],
    "通灵点位四坐标": 自定义设置["通灵点位四坐标"],
    "通灵点位一颜色小": 自定义设置["通灵点位一颜色小"],
    "通灵点位一颜色大": 自定义设置["通灵点位一颜色大"],
    "通灵点位二颜色小": 自定义设置["通灵点位二颜色小"],
    "通灵点位二颜色大": 自定义设置["通灵点位二颜色大"],
    "通灵点位三颜色小": 自定义设置["通灵点位三颜色小"],
    "通灵点位三颜色大": 自定义设置["通灵点位三颜色大"],
    "通灵点位四颜色小": 自定义设置["通灵点位四颜色小"],
    "通灵点位四颜色大": 自定义设置["通灵点位四颜色大"],

}
宁次点穴相关 = {
    "点穴点位": 自定义设置["点穴点位"],
    "点穴最大RGB": 自定义设置["点穴最大RGB"],
    "点穴最小RGB": 自定义设置["点穴最小RGB"],
    "训练营点位": 自定义设置["训练营点位"],
    "训练营最大RGB": 自定义设置["训练营最大RGB"],
    "训练营最小RGB": 自定义设置["训练营最小RGB"],
    "模拟战点位": 自定义设置["模拟战点位"],
    "模拟战最大RGB": 自定义设置["模拟战最大RGB"],
    "模拟战最小RGB": 自定义设置["模拟战最小RGB"],
    "决斗场点位": 自定义设置["决斗场点位"],
    "决斗场最大RGB": 自定义设置["决斗场最大RGB"],
    "决斗场最小RGB": 自定义设置["决斗场最小RGB"],
}
豆豆颜色区间 = {
    "暗青最大RGB": 自定义设置["暗青最大RGB"],
    "暗青最小RGB": 自定义设置["暗青最小RGB"],
    "亮蓝最大RGB": 自定义设置["亮蓝最大RGB"],
    "亮蓝最小RGB": 自定义设置["亮蓝最小RGB"],
    "赤金最大RGB": 自定义设置["赤金最大RGB"],
    "赤金最小RGB": 自定义设置["赤金最小RGB"],
}
各个坐标点位_决斗场 = {
    "左方第一个豆": 自定义设置["左方第一个豆_决斗场"],
    "左方第二个豆": 自定义设置["左方第二个豆_决斗场"],
    "左方第三个豆": 自定义设置["左方第三个豆_决斗场"],
    "左方第四个豆": 自定义设置["左方第四个豆_决斗场"],
    "左方第五个豆": 自定义设置["左方第五个豆_决斗场"],
    "左方第六个豆": 自定义设置["左方第六个豆_决斗场"],
    "右方第一个豆": 自定义设置["右方第一个豆_决斗场"],
    "右方第二个豆": 自定义设置["右方第二个豆_决斗场"],
    "右方第三个豆": 自定义设置["右方第三个豆_决斗场"],
    "右方第四个豆": 自定义设置["右方第四个豆_决斗场"],
    "右方第五个豆": 自定义设置["右方第五个豆_决斗场"],
    "右方第六个豆": 自定义设置["右方第六个豆_决斗场"],
}
各个坐标点位_训练营 = {
    "左方第一个豆": 自定义设置["左方第一个豆_训练营"],
    "左方第二个豆": 自定义设置["左方第二个豆_训练营"],
    "左方第三个豆": 自定义设置["左方第三个豆_训练营"],
    "左方第四个豆": 自定义设置["左方第四个豆_训练营"],
    "左方第五个豆": 自定义设置["左方第五个豆_训练营"],
    "左方第六个豆": 自定义设置["左方第六个豆_训练营"],
    "右方第一个豆": 自定义设置["右方第一个豆_训练营"],
    "右方第二个豆": 自定义设置["右方第二个豆_训练营"],
    "右方第三个豆": 自定义设置["右方第三个豆_训练营"],
    "右方第四个豆": 自定义设置["右方第四个豆_训练营"],
    "右方第五个豆": 自定义设置["右方第五个豆_训练营"],
    "右方第六个豆": 自定义设置["右方第六个豆_训练营"],
}
柱间检测相关_决斗场 = {
    "左柱间点位": 自定义设置["左柱间点位_决斗场"],
    "右柱间点位": 自定义设置["右柱间点位_决斗场"],
    "秽土柱间最大RGB": 自定义设置["秽土柱间最大RGB_决斗场"],
    "秽土柱间最小RGB": 自定义设置["秽土柱间最小RGB_决斗场"],
    "创立柱间最大RGB": 自定义设置["创立柱间最大RGB_决斗场"],
    "创立柱间最小RGB": 自定义设置["创立柱间最小RGB_决斗场"],
}
柱间检测相关_训练营 = {
    "左柱间点位": 自定义设置["左柱间点位_训练营"],
    "右柱间点位": 自定义设置["右柱间点位_训练营"],
    "秽土柱间最大RGB": 自定义设置["秽土柱间最大RGB_训练营"],
    "秽土柱间最小RGB": 自定义设置["秽土柱间最小RGB_训练营"],
    "创立柱间最大RGB": 自定义设置["创立柱间最大RGB_训练营"],
    "创立柱间最小RGB": 自定义设置["创立柱间最小RGB_训练营"],
}
左右豆豆数量 = {
    "左方豆豆数量": 999,
    "右方豆豆数量": 999,
}
各个豆豆状态 = {
    "左方第一个豆": "混沌",
    "左方第二个豆": "混沌",
    "左方第三个豆": "混沌",
    "左方第四个豆": "混沌",
    "左方第五个豆": "混沌",
    "左方第六个豆": "混沌",
    "右方第一个豆": "混沌",
    "右方第二个豆": "混沌",
    "右方第三个豆": "混沌",
    "右方第四个豆": "混沌",
    "右方第五个豆": "混沌",
    "右方第六个豆": "混沌",
}
各个坐标点位 = 各个坐标点位_决斗场
柱间检测相关 = 柱间检测相关_决斗场


def 路径修正(相对路径):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 相对路径)
    return 相对路径


def 召出内容(文件夹路径):
    try:
        # 获取当前执行文件所在的目录
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe文件
            脚本目录 = os.path.dirname(sys.executable)
        else:
            # 如果是普通的Python脚本
            脚本目录 = os.path.dirname(os.path.abspath(__file__))

        # 如果是相对路径，转换为基于脚本目录的绝对路径
        if not os.path.isabs(文件夹路径):
            源文件夹路径 = os.path.join(脚本目录, 文件夹路径)
        else:
            源文件夹路径 = 文件夹路径

        # 检查源文件夹是否存在
        if not os.path.exists(源文件夹路径) or not os.path.isdir(源文件夹路径):
            print(f"错误：源文件夹 '{源文件夹路径}' 不存在")
            return False

        # 获取源文件夹中的所有内容
        源文件夹内容 = os.listdir(源文件夹路径)

        if not 源文件夹内容:
            print("源文件夹为空，无需复制")
            return False

        # 检查脚本目录中是否已存在所有内容
        已存在的项目 = []
        for 项目 in 源文件夹内容:
            目标项目路径 = os.path.join(脚本目录, 项目)
            if os.path.exists(目标项目路径):
                已存在的项目.append(项目)

        if 已存在的项目:
            print(f"以下项目已存在于目标位置，跳过复制：{', '.join(已存在的项目)}")
            # 如果所有项目都已存在，则返回False
            if len(已存在的项目) == len(源文件夹内容):
                return False

        # 复制文件夹内容到脚本目录
        复制计数 = 0
        for 项目 in 源文件夹内容:
            源项目路径 = os.path.join(源文件夹路径, 项目)
            目标项目路径 = os.path.join(脚本目录, 项目)

            # 跳过已存在的项目
            if os.path.exists(目标项目路径):
                continue

            if os.path.isdir(源项目路径):
                # 如果是文件夹，使用copytree
                shutil.copytree(源项目路径, 目标项目路径)
                print(f"文件夹复制完成：{源项目路径} -> {目标项目路径}")
            else:
                # 如果是文件，使用copy2
                shutil.copy2(源项目路径, 目标项目路径)
                print(f"文件复制完成：{源项目路径} -> {目标项目路径}")

            复制计数 += 1

        if 复制计数 > 0:
            print(f"总共复制了 {复制计数} 个项目到 {脚本目录}")
            return True
        else:
            print("没有新项目需要复制")
            return False

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
    托盘图标.showMessage(标题, 信息, QSystemTrayIcon.MessageIcon.Information, 5000)  # 5000毫秒 = 5秒
    # 使用 QTimer 关闭 QApplication 而不启动事件循环
    QTimer.singleShot(1000, 应用程序.quit)  # 1秒后关闭 QApplication
# 使用示例
选项列表 = [
    ("Doki Pipo☆Emotion", "奇迹般的访问数无限延伸",路径修正("文件/icon/1.ico")),
    ("Tele-telepathy", "将一个又一个的点联结起来\n连成了线 然后变成了圆",路径修正("文件/icon/6.ico")),
    ("Analogue Heart", "连接起来吧 Analogue Heart\n那最重要的 Analogue Heart",路径修正("文件/icon/1.ico")),
    ("First Love Again", "晚霞染红了天空[今天]将迎来落幕\n我们又留下了什么呢 在意 却又无能为力",路径修正("文件/icon/3.ico"),),
    ("私はマグネット","为了他人而做些什么 从前的自己想都没想过\n这对我来说是 奇迹的伟大的事情哟",路径修正("文件/icon/1.ico"),),
    ("相连的Connect","现实中又没有[Ctrl]+[Z]\n自己来定义有些复杂呢",路径修正("文件/icon/5.ico"),),
]
随机标题, 随机信息,随机图标路径 = random.choice(选项列表)
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


class 按键监听线程(QThread):
    AnJianAnXiaXinHao = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        def on_press(key):
            try:
                按键名称 = key.char
            except AttributeError:
                按键名称 = str(key)
            self.AnJianAnXiaXinHao.emit(按键名称)

        with keyboard.Listener(on_press=on_press) as 监听器:
            监听器.join()


class 屏幕检测线程(QThread):
    # 定义信号
    XiangSuJianCeXinHao = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.运行中 = True
        self._drag_pos = None

    def run(self):
        while self.运行中:
            try:
                # 发送截屏信号
                self.XiangSuJianCeXinHao.emit(["截屏"])
                self.XiangSuJianCeXinHao.emit(["检测"])
                self.msleep(自定义设置["检测速率"])
            except Exception as e:
                print(f"屏幕检测错误: {e}")

    def 停止(self):
        self.运行中 = False
        self.wait()


class 根窗口(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("璃奈板")
        self.setGeometry(int(自定义设置["主窗口位置与大小"][0]), int(自定义设置["主窗口位置与大小"][1]),
                         int(自定义设置["主窗口位置与大小"][2]), int(自定义设置["主窗口位置与大小"][3]))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(self.windowFlags())
        self.设置窗口图标随机(self, 路径修正("文件/icon"))
        # self.setStyleSheet("background: transparent;")
        self.setWindowOpacity(1.0)  # 80% 不透明
        self.左侧倒计时 = []  # 存储左侧的倒计时标签和计时器
        self.右侧倒计时 = []  # 存储右侧的倒计时标签和计时器
        self.拖动位置 = None
        self.设置界面 = None
        self.背景标签 = QLabel(self)
        self.背景标签.setGeometry(0, 0, self.width(), self.height())
        self.背景标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.背景动画 = None

        self.设置随机背景()

        self.左侧初始位置 = 自定义设置["倒计时左初始位置"]  # 左侧初始位置
        self.右侧初始位置 = 自定义设置["倒计时右初始位置"]  # 右侧初始位置
        self.标签大小 = 自定义设置["倒计时标签大小"]  # 标签大小
        self.左通灵显示标签 = QLabel(self)
        self.左通灵显示标签.setGeometry(*自定义设置["左通灵显示标签"])
        self.右通灵显示标签 = QLabel(self)
        self.右通灵显示标签.setGeometry(*自定义设置["右通灵显示标签"])
        self.左秘卷显示标签一 = QLabel(self)
        self.左秘卷显示标签二 = QLabel(self)
        self.左秘卷显示标签三 = QLabel(self)
        self.左秘卷显示标签一.setGeometry(*自定义设置["左秘卷显示标签一"])
        self.左秘卷显示标签二.setGeometry(*自定义设置["左秘卷显示标签二"])
        self.左秘卷显示标签三.setGeometry(*自定义设置["左秘卷显示标签三"])
        self.右秘卷显示标签一 = QLabel(self)
        self.右秘卷显示标签二 = QLabel(self)
        self.右秘卷显示标签三 = QLabel(self)
        self.右秘卷显示标签一.setGeometry(*自定义设置["右秘卷显示标签一"])
        self.右秘卷显示标签二.setGeometry(*自定义设置["右秘卷显示标签二"])
        self.右秘卷显示标签三.setGeometry(*自定义设置["右秘卷显示标签三"])

        # 添加常驻标签
        self.创建常驻标签()

        # 初始化全局屏幕截图变量
        self.当前屏幕截图 = None

        self.关于按钮 = self.按钮批量创建(自定义设置["关于按钮"], lambda: self.关于窗口(路径修正("文件/收款码2.png")))
        self.设置按钮 = self.按钮批量创建(自定义设置["设置按钮"], self.SheZhiJieMian)
        self.左方按钮 = self.按钮批量创建(自定义设置["左方按钮"], lambda: self.添加倒计时标签(方位="左侧"))
        self.右方按钮 = self.按钮批量创建(自定义设置["右方按钮"], lambda: self.添加倒计时标签(方位="右侧"))
        self.关闭按钮 = self.按钮批量创建(自定义设置["关闭按钮"], 终章)
        self.教程按钮 = self.按钮批量创建(自定义设置["教程按钮"], lambda: self.教程界面())

        self.监听线程 = 按键监听线程()
        self.监听线程.AnJianAnXiaXinHao.connect(self.AnJianChuLi)
        self.监听线程.start()

        self.初始化屏幕检测()

    def 教程界面(self):
        self.教程窗口 = QWidget()
        self.教程窗口.setWindowTitle("教程窗口")
        self.教程窗口.setGeometry(400, 400, 800, 300)
        self.设置窗口图标随机(self.教程窗口, 路径修正("文件/icon"))
        self.标签1 = QLabel("点击按钮召出文件夹,文件夹在软件同目录中", self.教程窗口)
        self.标签1.setGeometry(0, 0, 800, 60)
        self.标签1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.标签1.setStyleSheet("font-family: 黑体; font-size: 40px; color: #7DE6AA;")

        self.标签2 = QLabel("可以查看教程文档了解使用方法", self.教程窗口)
        self.标签2.setGeometry(0, 60, 800, 60)
        self.标签2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.标签2.setStyleSheet("font-family: 黑体; font-size: 40px; color: #F98CFD;")

        self.标签3 = QLabel("配置文件提供了高度自定义的功能", self.教程窗口)
        self.标签3.setGeometry(0, 120, 800, 60)
        self.标签3.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.标签3.setStyleSheet("font-family: 黑体; font-size: 40px; color: #CCE03C;")

        self.标签4 = QLabel("误删文件可以点按钮重新召唤", self.教程窗口)
        self.标签4.setGeometry(0, 180, 800, 60)
        self.标签4.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.标签4.setStyleSheet("font-family: 黑体; font-size: 40px; color: #4D3BE2;")

        self.按钮1 = QPushButton("点我召出教程文件夹", self.教程窗口)
        self.按钮1.setGeometry(0, 240, 800, 60)
        self.按钮1.setStyleSheet("font-family: 黑体; font-size: 40px; color: #A10000; border: 2px solid #A10000;")
        self.按钮1.clicked.connect(lambda: 召出内容(路径修正("文件/内嵌内容")))
        告诫之文本 = 言语
        self.标签5 = QLabel(告诫之文本, self.教程窗口)
        self.标签5.setGeometry(800, 0, 800, 1080)
        self.标签5.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.标签5.setStyleSheet("font-family: 黑体; font-size: 20px; color: #EDEDED;")

        self.教程窗口.show()

    def 设置窗口图标随机(self, 窗口, 图标文件夹):
        图标文件 = [f for f in os.listdir(图标文件夹) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.ico', '.bmp'))]
        if 图标文件:
            随机图标 = random.choice(图标文件)
            图标路径 = os.path.join(图标文件夹, 随机图标)
            窗口.setWindowIcon(QIcon(图标路径))

    def 快速创建文本标签(self, 文本内容, 字体大小=12):
        """快速创建富文本标签的简化版本"""
        标签 = QLabel(文本内容)
        标签.setTextFormat(Qt.TextFormat.RichText)
        标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
        标签.setStyleSheet(f"font-size: {字体大小}px;")
        return 标签

    def 关于窗口(self, 图片路径):
        self.关于子窗口 = QWidget()
        self.关于子窗口.setWindowTitle("关于本软件 -- 凤灯幽夜")
        # 创建主布局
        主布局 = QVBoxLayout(self.关于子窗口)
        self.设置窗口图标随机(self.关于子窗口, 路径修正("文件/icon"))

        # 定义文本内容列表（简化版）
        文本内容列表 = [
            ('<span style="color: #72E692;">唯一作者ID:</span> <span style="color: #000000;">凤灯幽夜</span>', 20),
            ('<span style="color: #E672C6;">Bili_Uid:</span> <span style="color: #000000;">11898940</span>', 20),
            ('<span style="color: #45B7D1;">讨论群:</span> <span style="color: #000000;">548419960</span>', 20),
            ('<span style="color: #9B59B6;">版本:</span> <span style="color: #000000;">V4.8.0</span>', 20),
            ('<span style="color: #009C94;">Lofter/Pixiv:</span> <span style="color: #000000;">凤灯幽夜</span>', 20),
            (
            '<span style="color: #FFA04A;">特别鸣谢,自软件发布以来259天的唯一打赏:</span> <span style="color: #FFA04A;">来自[咖啡豆浆]的[20元]</span>',
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

    def 设置随机背景(self):
        # 直接检查exe同目录下的背景图片文件夹
        程序目录 = os.path.dirname(sys.executable) if hasattr(sys, '_MEIPASS') else os.path.dirname(
            os.path.abspath(__file__))
        背景图片路径 = os.path.join(程序目录, "背景图片")

        if os.path.exists(背景图片路径) and os.path.isdir(背景图片路径):
            图片路径 = self.获取随机图片(背景图片路径)
            print(f"说明你选择了自己用的背景图片:{图片路径}")
        else:
            # 从打包内的文件/BG目录中选择随机图片
            bg_路径 = 路径修正("文件/BG")
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
            self.背景标签.setGeometry(
                自定义设置["动态背景X轴偏移"],
                自定义设置["动态背景Y轴偏移"],
                新的宽度,
                新的高度
            )

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
                Qt.TransformationMode.SmoothTransformation
            )

            # 设置背景标签的大小和位置
            self.背景标签.setGeometry(
                自定义设置["静态背景X轴偏移"],
                自定义设置["静态背景Y轴偏移"],
                新的宽度,
                新的高度
            )

            # 设置背景图片
            self.背景标签.setPixmap(背景图片)

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
            f"background-color: {背景色};color: {文本色};font-size: {字体大小};font-weight: {粗细设置};border-radius: {圆角半径};")
        按钮.setGraphicsEffect(按钮透明效果)
        按钮.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        按钮.clicked.connect(触发函数)
        return 按钮

    def AnJianChuLi(self, 按键):
        if   按键.lower() == 自定义设置["模拟左侧替身按键"]:
            self.添加倒计时标签(方位="左侧")
        elif 按键.lower() == 自定义设置["模拟右侧替身按键"]:
            self.添加倒计时标签(方位="右侧")
        elif 按键.lower() == 自定义设置["关闭程序按键"]:
            终章()
        elif 按键.lower() == 自定义设置["清空倒计时按键"]:
            self.清空所有倒计时标签()
        else:
            # print(f"检测按键：{按键}")
            pass

    def SheZhiJieMian(self):
        if self.设置界面 is None:  # 如果子窗口不存在，则创建
            self.设置界面 = QWidget()
            self.设置界面.setWindowTitle("设置界面")
            self.设置界面.setGeometry(*自定义设置["设置界面几何"])  # 子窗口位置和尺寸
            self.设置窗口图标随机(self.设置界面, 路径修正("文件/icon"))
            self.宁次图片标签 = QLabel(self.设置界面)
            self.宁次图片标签.setGeometry(*自定义设置["宁次标签几何"])
            宁次基础图片 = QPixmap(路径修正("文件/柔拳法_忍战宁次.png"))
            宁次修改图片 = 宁次基础图片.scaled(自定义设置["宁次标签图片大小"][0], 自定义设置["宁次标签图片大小"][1],
                                               Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
            self.宁次图片标签.setPixmap(宁次修改图片)

            self.点穴开关 = QPushButton("目押点穴", self.设置界面)
            self.点穴开关.setGeometry(*自定义设置["宁次按钮几何"])
            self.点穴开关.setStyleSheet(
                f"background-color: #FFFFFF;color: #000000;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #FF2EE7;")
            self.点穴开关.clicked.connect(self.DianXueKaiGuan)

            self.模式切换标签 = QLabel(self.设置界面)
            self.模式切换标签.setGeometry(*自定义设置["模式标签几何"])
            模式切换基础图片 = QPixmap(路径修正("文件/决斗场设置.png"))
            模式切换修改图片 = 模式切换基础图片.scaled(自定义设置["模式标签图片大小"][0],
                                                       自定义设置["模式标签图片大小"][1],
                                                       Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation)
            self.模式切换标签.setPixmap(模式切换修改图片)

            self.模式切换开关 = QPushButton("决斗场", self.设置界面)
            self.模式切换开关.setGeometry(*自定义设置["模式按钮几何"])
            self.模式切换开关.setStyleSheet(
                f"background-color: #FFFFFF;color: #5ACD32;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #5ACD32;")
            self.模式切换开关.clicked.connect(self.MoShiQieHuan)

            self.秒数显示标签 = QLabel(f"{自定义设置['倒计时秒数']} 秒", self.设置界面)
            self.秒数显示标签.setGeometry(*自定义设置["秒数标签几何"])
            self.秒数显示标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.秒数显示标签.setStyleSheet(
                f"background-color: #FFFFFF;color: #000000;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #FFDF00;")

            self.加时间按钮 = QPushButton("增加延迟", self.设置界面)
            self.加时间按钮.setGeometry(*自定义设置["加时按钮几何"])
            self.加时间按钮.setStyleSheet(
                f"background-color: #FFFFFF;color: #FF000B;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #FF000B;")
            self.加时间按钮.clicked.connect(lambda: self.YanChiTiaoZheng(0.1))

            self.减时间按钮 = QPushButton("减少延迟", self.设置界面)
            self.减时间按钮.setGeometry(*自定义设置["减时按钮几何"])
            self.减时间按钮.setStyleSheet(
                f"background-color: #FFFFFF;color: #00FF39;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #00FF39;")
            self.减时间按钮.clicked.connect(lambda: self.YanChiTiaoZheng(-0.1))

            self.范围显示按钮 = QPushButton("范围显示", self.设置界面)
            self.范围显示按钮.setGeometry(*自定义设置["范围按钮几何"])
            self.范围显示按钮.setStyleSheet(
                f"background-color: #FFFFFF;color: #693C71;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #693C71;")
            self.范围显示按钮.clicked.connect(lambda: self.TuPianXianShi(QPixmap(路径修正("文件/X轴范围显示.png"))))
            self.范围显示标签 = QLabel(self.设置界面)
            self.范围显示标签.setGeometry(*自定义设置["范围标签几何"])
            范围显示基础图片 = QPixmap(路径修正("文件/范围显示.png"))
            范围显示修改图片 = 范围显示基础图片.scaled(自定义设置["范围标签图片大小"][0],
                                                       自定义设置["范围标签图片大小"][1],
                                                       Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation)
            self.范围显示标签.setPixmap(范围显示修改图片)
        # 切换窗口的显示状态
        if self.设置界面.isVisible():
            self.设置界面.hide()  # 如果窗口可见，则隐藏
        else:
            self.设置界面.show()  # 如果窗口不可见，则显示

    def YanChiTiaoZheng(self, 延时):
        自定义设置["倒计时秒数"] += 延时
        self.秒数显示标签.setText(f"{自定义设置['倒计时秒数']:.1f} 秒")
        print(f"当前倒计时: {自定义设置['倒计时秒数']:.1f} 秒")

    def MoShiQieHuan(self):
        global 柱间检测相关, 各个坐标点位
        if 基础模式["状态"] == "决斗场":
            模式切换基础图片 = QPixmap(路径修正("文件/训练营设置.png"))
            模式切换修改图片 = 模式切换基础图片.scaled(自定义设置["模式标签图片大小"][0],
                                                       自定义设置["模式标签图片大小"][1],
                                                       Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation)
            self.模式切换标签.setPixmap(模式切换修改图片)
            self.模式切换开关.setText("训练营")
            self.模式切换开关.setStyleSheet(
                f"background-color: #FFFFFF;color: #E45F1B;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #E45F1B;")
            基础模式["状态"] = "训练营"
            柱间检测相关 = 柱间检测相关_训练营
            各个坐标点位 = 各个坐标点位_训练营
        elif 基础模式["状态"] == "训练营":
            模式切换基础图片 = QPixmap(路径修正("文件/决斗场设置.png"))
            模式切换修改图片 = 模式切换基础图片.scaled(自定义设置["模式标签图片大小"][0],
                                                       自定义设置["模式标签图片大小"][1],
                                                       Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation)
            self.模式切换标签.setPixmap(模式切换修改图片)
            self.模式切换开关.setText("决斗场")
            self.模式切换开关.setStyleSheet(
                f"background-color: #FFFFFF;color: #5ACD32;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #5ACD32;")
            基础模式["状态"] = "决斗场"
            柱间检测相关 = 柱间检测相关_决斗场
            各个坐标点位 = 各个坐标点位_决斗场

    def 标签改图显示(self, 对应标签, 对应配置):
        截取X坐标 = 对应配置[0]
        截取Y坐标 = 对应配置[1]
        截取X大小 = 对应配置[2]
        截取Y大小 = 对应配置[3]
        显示X大小 = 对应配置[4]
        显示Y大小 = 对应配置[5]
        截取区域 = QRect(截取X坐标, 截取Y坐标, 截取X大小, 截取Y大小)
        裁剪内容 = self.当前屏幕截图.copy(截取区域)
        裁剪内容 = 裁剪内容.scaled(显示X大小, 显示Y大小, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
        对应标签.setPixmap(裁剪内容)

    def TuPianXianShi(self, 图片路径):
        if hasattr(self, '图片窗口') and self.图片窗口 is not None:
            if self.图片窗口.isVisible():
                self.图片窗口.hide()
            else:
                self.图片窗口.show()
        else:
            self.图片窗口 = QWidget()
            self.图片窗口.setWindowTitle("图片显示")
            self.图片窗口.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowTransparentForInput)
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
            self.图片标签.setPixmap(图片.scaled(屏幕.width(), 屏幕.height(), Qt.AspectRatioMode.KeepAspectRatio))
            self.图片标签.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.图片窗口.show()

    def TongLingJiLu(self):
        self.标签改图显示(对应标签=self.左通灵显示标签, 对应配置=自定义设置["左通灵显示标签几何"])
        self.标签改图显示(对应标签=self.右通灵显示标签, 对应配置=自定义设置["右通灵显示标签几何"])

    def MiJuanJiLu(self):
        self.标签改图显示(对应标签=self.左秘卷显示标签一, 对应配置=自定义设置["左秘卷显示标签一几何"])
        self.标签改图显示(对应标签=self.左秘卷显示标签二, 对应配置=自定义设置["左秘卷显示标签二几何"])
        self.标签改图显示(对应标签=self.左秘卷显示标签三, 对应配置=自定义设置["左秘卷显示标签三几何"])
        self.标签改图显示(对应标签=self.右秘卷显示标签一, 对应配置=自定义设置["右秘卷显示标签一几何"])
        self.标签改图显示(对应标签=self.右秘卷显示标签二, 对应配置=自定义设置["右秘卷显示标签二几何"])
        self.标签改图显示(对应标签=self.右秘卷显示标签三, 对应配置=自定义设置["右秘卷显示标签三几何"])

    def DianXueKaiGuan(self):
        if 点穴开关["状态"] == "开启":
            点穴开关["状态"] = "关闭"
            self.点穴开关.setText("已关闭")
            self.点穴开关.setStyleSheet(
                f"background-color: #FFFFFF;color: #FF0000;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #FF0000;")
        elif 点穴开关["状态"] == "关闭":
            点穴开关["状态"] = "开启"
            self.点穴开关.setText("已开启")
            self.点穴开关.setStyleSheet(
                f"background-color: #FFFFFF;color: #00FF34;font-size: {自定义设置['设置窗口字体大小']};border: {自定义设置['设置窗口边缘像素']} solid #00FF34;")

    def mousePressEvent(self, 事件):
        """鼠标按下事件"""
        if 事件.button() == Qt.MouseButton.LeftButton:
            # 记录鼠标按下时的位置
            self.拖动位置 = 事件.globalPosition().toPoint() - self.frameGeometry().topLeft()
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

    def 初始化屏幕检测(self):
        self.JianCeXianCheng = 屏幕检测线程()
        self.JianCeXianCheng.XiangSuJianCeXinHao.connect(self.ChuLiXiangSuJianCeXinHao)
        self.JianCeXianCheng.start()

    def ChuLiXiangSuJianCeXinHao(self, 信号):
        if 信号[0] == "截屏":  # 先触发截屏,保存截屏内容为全局变量
            self.函数_截屏()
        elif 信号[0] == "检测":  # 根据已经有的截屏全局变量检测像素,给出信息
            self.函数_检测()
        elif 信号[0] == "左方替身":
            self.添加倒计时标签(方位="左侧")
        elif 信号[0] == "右方替身":
            self.添加倒计时标签(方位="右侧")
        elif 信号[0] == "目押点穴":
            触发_左键短按(自定义设置["宁次点穴普攻坐标"])

    def 函数_截屏(self):
        try:
            # 截取全屏并更新全局变量
            self.当前屏幕截图 = QGuiApplication.primaryScreen().grabWindow(0)
        except Exception as e:
            print(f"截屏错误: {e}")

    def 获取像素RGB(self, 像素X轴坐标, 像素Y轴坐标):
        截屏的图像 = self.当前屏幕截图
        转换完毕的截屏图片 = 截屏的图像.toImage()
        # PyQt6中pixelColor方法使用方式相同
        RGB的三色 = 转换完毕的截屏图片.pixelColor(像素X轴坐标, 像素Y轴坐标)
        return RGB的三色.red(), RGB的三色.green(), RGB的三色.blue()

    def 像素RGB检测(self, 小的RGB范围, 大的RGB范围, 被检测点位的RGB):
        if ((小的RGB范围[0] - RGB容差值) <= 被检测点位的RGB[0] <= (大的RGB范围[0] + RGB容差值) and
                (小的RGB范围[1] - RGB容差值) <= 被检测点位的RGB[1] <= (大的RGB范围[1] + RGB容差值) and
                (小的RGB范围[2] - RGB容差值) <= 被检测点位的RGB[2] <= (大的RGB范围[2] + RGB容差值)):
            return True
        else:
            return False

    def 函数_检测(self):
        try:
            if self.当前屏幕截图:
                # 获取指定坐标的像素值
                self.豆豆检测()
                self.豆豆数量检测()
                self.点穴检测()
                self.记牌检测()
                self.回放检测()
        except Exception as e:
            print(f"像素检测错误: {e}")

    def 左右标签更新(self, 对应标签, 文本背景色文本色):
        新文本 = 文本背景色文本色[0]
        背景色 = 文本背景色文本色[1]
        文本色 = 文本背景色文本色[2]
        对应标签.setText(新文本)
        对应标签.setStyleSheet(f"background-color: {背景色};color: {文本色}")

    def 柱间检测(self, 方位):
        if 方位 == "左侧":
            左柱间像素列表 = [
                self.获取像素RGB(柱间检测相关["左柱间点位"][0][0], 柱间检测相关["左柱间点位"][0][1], ),
                self.获取像素RGB(柱间检测相关["左柱间点位"][1][0], 柱间检测相关["左柱间点位"][1][1], ),
                self.获取像素RGB(柱间检测相关["左柱间点位"][2][0], 柱间检测相关["左柱间点位"][2][1], ),
                self.获取像素RGB(柱间检测相关["左柱间点位"][3][0], 柱间检测相关["左柱间点位"][3][1], ),
            ]
            for 像素 in 左柱间像素列表:
                # 检查当前像素的RGB值是否在允许范围内
                if (self.像素RGB检测(柱间检测相关["秽土柱间最小RGB"], 柱间检测相关["秽土柱间最大RGB"], 像素) or
                        self.像素RGB检测(柱间检测相关["创立柱间最小RGB"], 柱间检测相关["创立柱间最大RGB"], 像素)):
                    return True
            # 各个豆豆状态["右方第五个豆"] = "虚空"
            # 各个豆豆状态["右方第六个豆"] = "虚空"
            return False
        if 方位 == "右侧":
            右柱间像素列表 = [
                self.获取像素RGB(柱间检测相关["右柱间点位"][0][0], 柱间检测相关["右柱间点位"][0][1], ),
                self.获取像素RGB(柱间检测相关["右柱间点位"][1][0], 柱间检测相关["右柱间点位"][1][1], ),
                self.获取像素RGB(柱间检测相关["右柱间点位"][2][0], 柱间检测相关["右柱间点位"][2][1], ),
                self.获取像素RGB(柱间检测相关["右柱间点位"][3][0], 柱间检测相关["右柱间点位"][3][1], ),
            ]
            # print(右柱间像素列表)
            for 像素 in 右柱间像素列表:
                # 检查当前像素的RGB值是否在允许范围内
                if (self.像素RGB检测(柱间检测相关["秽土柱间最小RGB"], 柱间检测相关["秽土柱间最大RGB"], 像素) or
                        self.像素RGB检测(柱间检测相关["创立柱间最小RGB"], 柱间检测相关["创立柱间最大RGB"], 像素)):
                    return True
            # 各个豆豆状态["右方第五个豆"] = "虚空"
            # 各个豆豆状态["右方第六个豆"] = "虚空"
            return False

    def 豆豆数量检测(self):
        # print(各个豆豆状态)
        if (各个豆豆状态["左方第一个豆"] == "暗青" and 各个豆豆状态["左方第二个豆"] == "暗青" and
                各个豆豆状态["左方第三个豆"] == "暗青" and 各个豆豆状态["左方第四个豆"] == "暗青"):
            if self.柱间检测("左侧"):
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左零豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左零豆_常态"])
            if 左右豆豆数量["左方豆豆数量"] == 1:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["左方替身"])
            左右豆豆数量["左方豆豆数量"] = 0
        elif (各个豆豆状态["左方第一个豆"] == "亮蓝" and 各个豆豆状态["左方第二个豆"] == "暗青" and
              各个豆豆状态["左方第三个豆"] == "暗青" and 各个豆豆状态["左方第四个豆"] == "暗青"):
            if self.柱间检测("左侧"):
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左一豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左一豆_常态"])
            if 左右豆豆数量["左方豆豆数量"] == 2:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["左方替身"])
            左右豆豆数量["左方豆豆数量"] = 1
        elif (各个豆豆状态["左方第一个豆"] == "亮蓝" and 各个豆豆状态["左方第二个豆"] == "亮蓝" and
              各个豆豆状态["左方第三个豆"] == "暗青" and 各个豆豆状态["左方第四个豆"] == "暗青"):
            if self.柱间检测("左侧"):
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左二豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左二豆_常态"])
            if 左右豆豆数量["左方豆豆数量"] == 3:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["左方替身"])
            左右豆豆数量["左方豆豆数量"] = 2
        elif (各个豆豆状态["左方第一个豆"] == "亮蓝" and 各个豆豆状态["左方第二个豆"] == "亮蓝" and
              各个豆豆状态["左方第三个豆"] == "亮蓝" and 各个豆豆状态["左方第四个豆"] == "暗青"):
            if self.柱间检测("左侧"):
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左三豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左三豆_常态"])
            if 左右豆豆数量["左方豆豆数量"] == 4:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["左方替身"])
            左右豆豆数量["左方豆豆数量"] = 3
        elif (各个豆豆状态["左方第一个豆"] == "赤金" and 各个豆豆状态["左方第二个豆"] == "赤金" and
              各个豆豆状态["左方第三个豆"] == "赤金" and 各个豆豆状态["左方第四个豆"] == "赤金" and
              各个豆豆状态["左方第五个豆"] == "赤金" and 各个豆豆状态["左方第六个豆"] == "暗青" and
              self.柱间检测("左侧")):
            self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左五豆_柱间"])
            if 左右豆豆数量["左方豆豆数量"] == 6:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["左方替身"])
            左右豆豆数量["左方豆豆数量"] = 5
        elif (各个豆豆状态["左方第一个豆"] == "赤金" and 各个豆豆状态["左方第二个豆"] == "赤金" and
              各个豆豆状态["左方第三个豆"] == "赤金" and 各个豆豆状态["左方第四个豆"] == "赤金" and
              各个豆豆状态["左方第五个豆"] == "赤金" and 各个豆豆状态["左方第六个豆"] == "赤金" and
              self.柱间检测("左侧")):
            self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左六豆_柱间"])
            左右豆豆数量["左方豆豆数量"] = 6
        elif (各个豆豆状态["左方第一个豆"] == "赤金" and 各个豆豆状态["左方第二个豆"] == "赤金" and
              各个豆豆状态["左方第三个豆"] == "赤金" and 各个豆豆状态["左方第四个豆"] == "赤金"):
            if self.柱间检测("左侧"):
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左四豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左四豆_常态"])
            if 左右豆豆数量["左方豆豆数量"] == 5:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["左方替身"])
            左右豆豆数量["左方豆豆数量"] = 4
        elif (各个豆豆状态["左方第一个豆"] == "赤金" and 各个豆豆状态["左方第二个豆"] == "暗青" and
              各个豆豆状态["左方第三个豆"] == "暗青" and 各个豆豆状态["左方第四个豆"] == "暗青"):
            self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左一豆_六尾鸣"])
            if 左右豆豆数量["左方豆豆数量"] == 2:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["左方替身"])
            左右豆豆数量["左方豆豆数量"] = 1
        elif (各个豆豆状态["左方第一个豆"] == "赤金" and 各个豆豆状态["左方第二个豆"] == "赤金" and
              各个豆豆状态["左方第三个豆"] == "暗青" and 各个豆豆状态["左方第四个豆"] == "暗青"):
            self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左二豆_六尾鸣"])
            if 左右豆豆数量["左方豆豆数量"] == 3:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["左方替身"])
            左右豆豆数量["左方豆豆数量"] = 2
        elif (各个豆豆状态["左方第一个豆"] == "赤金" and 各个豆豆状态["左方第二个豆"] == "赤金" and
              各个豆豆状态["左方第三个豆"] == "赤金" and 各个豆豆状态["左方第四个豆"] == "暗青"):
            self.左右标签更新(self.常驻标签左, 自定义设置["常驻标签左三豆_六尾鸣"])
            if 左右豆豆数量["左方豆豆数量"] == 4:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["左方替身"])
            左右豆豆数量["左方豆豆数量"] = 3

        if (各个豆豆状态["右方第一个豆"] == "暗青" and 各个豆豆状态["右方第二个豆"] == "暗青" and
                各个豆豆状态["右方第三个豆"] == "暗青" and 各个豆豆状态["右方第四个豆"] == "暗青"):
            if self.柱间检测("右侧"):
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右零豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右零豆_常态"])
            if 左右豆豆数量["右方豆豆数量"] == 1:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["右方替身"])
            左右豆豆数量["右方豆豆数量"] = 0
        elif (各个豆豆状态["右方第一个豆"] == "亮蓝" and 各个豆豆状态["右方第二个豆"] == "暗青" and
              各个豆豆状态["右方第三个豆"] == "暗青" and 各个豆豆状态["右方第四个豆"] == "暗青"):
            if self.柱间检测("右侧"):
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右一豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右一豆_常态"])
            if 左右豆豆数量["右方豆豆数量"] == 2:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["右方替身"])
            左右豆豆数量["右方豆豆数量"] = 1
        elif (各个豆豆状态["右方第一个豆"] == "亮蓝" and 各个豆豆状态["右方第二个豆"] == "亮蓝" and
              各个豆豆状态["右方第三个豆"] == "暗青" and 各个豆豆状态["右方第四个豆"] == "暗青"):
            if self.柱间检测("右侧"):
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右二豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右二豆_常态"])
            if 左右豆豆数量["右方豆豆数量"] == 3:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["右方替身"])
            左右豆豆数量["右方豆豆数量"] = 2
        elif (各个豆豆状态["右方第一个豆"] == "亮蓝" and 各个豆豆状态["右方第二个豆"] == "亮蓝" and
              各个豆豆状态["右方第三个豆"] == "亮蓝" and 各个豆豆状态["右方第四个豆"] == "暗青"):
            if self.柱间检测("右侧"):
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右三豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右三豆_常态"])
            if 左右豆豆数量["右方豆豆数量"] == 4:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["右方替身"])
            左右豆豆数量["右方豆豆数量"] = 3
        elif (各个豆豆状态["右方第一个豆"] == "赤金" and 各个豆豆状态["右方第二个豆"] == "赤金" and
              各个豆豆状态["右方第三个豆"] == "赤金" and 各个豆豆状态["右方第四个豆"] == "赤金" and
              各个豆豆状态["右方第五个豆"] == "赤金" and 各个豆豆状态["右方第六个豆"] == "暗青" and
              self.柱间检测("右侧")):
            self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右五豆_柱间"])
            if 左右豆豆数量["右方豆豆数量"] == 6:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["右方替身"])
            左右豆豆数量["右方豆豆数量"] = 5
        elif (各个豆豆状态["右方第一个豆"] == "赤金" and 各个豆豆状态["右方第二个豆"] == "赤金" and
              各个豆豆状态["右方第三个豆"] == "赤金" and 各个豆豆状态["右方第四个豆"] == "赤金" and
              各个豆豆状态["右方第五个豆"] == "赤金" and 各个豆豆状态["右方第六个豆"] == "赤金" and
              self.柱间检测("右侧")):
            self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右六豆_柱间"])
            左右豆豆数量["右方豆豆数量"] = 6
        elif (各个豆豆状态["右方第一个豆"] == "赤金" and 各个豆豆状态["右方第二个豆"] == "赤金" and
              各个豆豆状态["右方第三个豆"] == "赤金" and 各个豆豆状态["右方第四个豆"] == "赤金"):
            if self.柱间检测("右侧"):
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右四豆_柱间"])
            else:
                self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右四豆_常态"])
            if 左右豆豆数量["右方豆豆数量"] == 5:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["右方替身"])
            左右豆豆数量["右方豆豆数量"] = 4
        elif (各个豆豆状态["右方第一个豆"] == "赤金" and 各个豆豆状态["右方第二个豆"] == "暗青" and
              各个豆豆状态["右方第三个豆"] == "暗青" and 各个豆豆状态["右方第四个豆"] == "暗青"):
            self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右一豆_六尾鸣"])
            if 左右豆豆数量["右方豆豆数量"] == 2:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["右方替身"])
            左右豆豆数量["右方豆豆数量"] = 1
        elif (各个豆豆状态["右方第一个豆"] == "赤金" and 各个豆豆状态["右方第二个豆"] == "赤金" and
              各个豆豆状态["右方第三个豆"] == "暗青" and 各个豆豆状态["右方第四个豆"] == "暗青"):
            self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右二豆_六尾鸣"])
            if 左右豆豆数量["右方豆豆数量"] == 3:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["右方替身"])
            左右豆豆数量["右方豆豆数量"] = 2
        elif (各个豆豆状态["右方第一个豆"] == "赤金" and 各个豆豆状态["右方第二个豆"] == "赤金" and
              各个豆豆状态["右方第三个豆"] == "赤金" and 各个豆豆状态["右方第四个豆"] == "暗青"):
            self.左右标签更新(self.常驻标签右, 自定义设置["常驻标签右三豆_六尾鸣"])
            if 左右豆豆数量["右方豆豆数量"] == 4:
                self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["右方替身"])
            左右豆豆数量["右方豆豆数量"] = 3
        #print(各个豆豆状态)

    def 点穴检测(self):
        if 点穴开关["状态"] == "开启":
            训练营检测RGB = self.获取像素RGB(宁次点穴相关["训练营点位"][0], 宁次点穴相关["训练营点位"][1], )
            模拟战检测RGB = self.获取像素RGB(宁次点穴相关["模拟战点位"][0], 宁次点穴相关["模拟战点位"][1], )
            决斗场检测RGB = self.获取像素RGB(宁次点穴相关["决斗场点位"][0], 宁次点穴相关["决斗场点位"][1], )
            if (self.像素RGB检测(宁次点穴相关["训练营最小RGB"], 宁次点穴相关["训练营最大RGB"], 训练营检测RGB, ) or
                    self.像素RGB检测(宁次点穴相关["模拟战最小RGB"], 宁次点穴相关["模拟战最大RGB"], 模拟战检测RGB, ) or
                    self.像素RGB检测(宁次点穴相关["决斗场最小RGB"], 宁次点穴相关["决斗场最大RGB"], 决斗场检测RGB, )):
                宁次检测RGB = self.获取像素RGB(宁次点穴相关["点穴点位"][0], 宁次点穴相关["点穴点位"][1], )
                if self.像素RGB检测(宁次点穴相关["点穴最小RGB"], 宁次点穴相关["点穴最大RGB"], 宁次检测RGB):
                    self.JianCeXianCheng.XiangSuJianCeXinHao.emit(["目押点穴"])

    def 豆豆检测(self):
        左一豆像素 = self.获取像素RGB(各个坐标点位["左方第一个豆"][0], 各个坐标点位["左方第一个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 左一豆像素):
            各个豆豆状态["左方第一个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 左一豆像素):
            各个豆豆状态["左方第一个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 左一豆像素):
            各个豆豆状态["左方第一个豆"] = "暗青"
        左二豆像素 = self.获取像素RGB(各个坐标点位["左方第二个豆"][0], 各个坐标点位["左方第二个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 左二豆像素):
            各个豆豆状态["左方第二个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 左二豆像素):
            各个豆豆状态["左方第二个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 左二豆像素):
            各个豆豆状态["左方第二个豆"] = "暗青"
        左三豆像素 = self.获取像素RGB(各个坐标点位["左方第三个豆"][0], 各个坐标点位["左方第三个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 左三豆像素):
            各个豆豆状态["左方第三个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 左三豆像素):
            各个豆豆状态["左方第三个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 左三豆像素):
            各个豆豆状态["左方第三个豆"] = "暗青"
        左四豆像素 = self.获取像素RGB(各个坐标点位["左方第四个豆"][0], 各个坐标点位["左方第四个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 左四豆像素):
            各个豆豆状态["左方第四个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 左四豆像素):
            各个豆豆状态["左方第四个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 左四豆像素):
            各个豆豆状态["左方第四个豆"] = "暗青"
        左五豆像素 = self.获取像素RGB(各个坐标点位["左方第五个豆"][0], 各个坐标点位["左方第五个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 左五豆像素):
            各个豆豆状态["左方第五个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 左五豆像素):
            各个豆豆状态["左方第五个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 左五豆像素):
            各个豆豆状态["左方第五个豆"] = "暗青"
        左六豆像素 = self.获取像素RGB(各个坐标点位["左方第六个豆"][0], 各个坐标点位["左方第六个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 左六豆像素):
            各个豆豆状态["左方第六个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 左六豆像素):
            各个豆豆状态["左方第六个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 左六豆像素):
            各个豆豆状态["左方第六个豆"] = "暗青"

        右一豆像素 = self.获取像素RGB(各个坐标点位["右方第一个豆"][0], 各个坐标点位["右方第一个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 右一豆像素):
            各个豆豆状态["右方第一个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 右一豆像素):
            各个豆豆状态["右方第一个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 右一豆像素):
            各个豆豆状态["右方第一个豆"] = "暗青"
        右二豆像素 = self.获取像素RGB(各个坐标点位["右方第二个豆"][0], 各个坐标点位["右方第二个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 右二豆像素):
            各个豆豆状态["右方第二个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 右二豆像素):
            各个豆豆状态["右方第二个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 右二豆像素):
            各个豆豆状态["右方第二个豆"] = "暗青"
        右三豆像素 = self.获取像素RGB(各个坐标点位["右方第三个豆"][0], 各个坐标点位["右方第三个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 右三豆像素):
            各个豆豆状态["右方第三个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 右三豆像素):
            各个豆豆状态["右方第三个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 右三豆像素):
            各个豆豆状态["右方第三个豆"] = "暗青"
        右四豆像素 = self.获取像素RGB(各个坐标点位["右方第四个豆"][0], 各个坐标点位["右方第四个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 右四豆像素):
            各个豆豆状态["右方第四个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 右四豆像素):
            各个豆豆状态["右方第四个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 右四豆像素):
            各个豆豆状态["右方第四个豆"] = "暗青"
        右五豆像素 = self.获取像素RGB(各个坐标点位["右方第五个豆"][0], 各个坐标点位["右方第五个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 右五豆像素):
            各个豆豆状态["右方第五个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 右五豆像素):
            各个豆豆状态["右方第五个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 右五豆像素):
            各个豆豆状态["右方第五个豆"] = "暗青"
        右六豆像素 = self.获取像素RGB(各个坐标点位["右方第六个豆"][0], 各个坐标点位["右方第六个豆"][1], )
        if self.像素RGB检测(豆豆颜色区间["赤金最小RGB"], 豆豆颜色区间["赤金最大RGB"], 右六豆像素):
            各个豆豆状态["右方第六个豆"] = "赤金"
        elif self.像素RGB检测(豆豆颜色区间["亮蓝最小RGB"], 豆豆颜色区间["亮蓝最大RGB"], 右六豆像素):
            各个豆豆状态["右方第六个豆"] = "亮蓝"
        elif self.像素RGB检测(豆豆颜色区间["暗青最小RGB"], 豆豆颜色区间["暗青最大RGB"], 右六豆像素):
            各个豆豆状态["右方第六个豆"] = "暗青"

    def 记牌检测(self):
        if 记牌开关["状态"] == "开启":
            秘卷检测点位一RGB = self.获取像素RGB(记牌点位相关["秘卷点位一坐标"][0], 记牌点位相关["秘卷点位一坐标"][1], )
            秘卷检测点位二RGB = self.获取像素RGB(记牌点位相关["秘卷点位二坐标"][0], 记牌点位相关["秘卷点位二坐标"][1], )
            秘卷检测点位三RGB = self.获取像素RGB(记牌点位相关["秘卷点位三坐标"][0], 记牌点位相关["秘卷点位三坐标"][1], )
            秘卷检测点位四RGB = self.获取像素RGB(记牌点位相关["秘卷点位四坐标"][0], 记牌点位相关["秘卷点位四坐标"][1], )
            if (self.像素RGB检测(记牌点位相关["秘卷点位一颜色小"], 记牌点位相关["秘卷点位一颜色大"],
                                 秘卷检测点位一RGB) and
                    self.像素RGB检测(记牌点位相关["秘卷点位二颜色小"], 记牌点位相关["秘卷点位二颜色大"],
                                     秘卷检测点位二RGB) and
                    self.像素RGB检测(记牌点位相关["秘卷点位三颜色小"], 记牌点位相关["秘卷点位三颜色大"],
                                     秘卷检测点位三RGB) and
                    self.像素RGB检测(记牌点位相关["秘卷点位四颜色小"], 记牌点位相关["秘卷点位四颜色大"],
                                     秘卷检测点位四RGB)):
                self.MiJuanJiLu()
            通灵检测点位一RGB = self.获取像素RGB(记牌点位相关["通灵点位一坐标"][0], 记牌点位相关["通灵点位一坐标"][1], )
            通灵检测点位二RGB = self.获取像素RGB(记牌点位相关["通灵点位二坐标"][0], 记牌点位相关["通灵点位二坐标"][1], )
            通灵检测点位三RGB = self.获取像素RGB(记牌点位相关["通灵点位三坐标"][0], 记牌点位相关["通灵点位三坐标"][1], )
            通灵检测点位四RGB = self.获取像素RGB(记牌点位相关["通灵点位四坐标"][0], 记牌点位相关["通灵点位四坐标"][1], )
            if (self.像素RGB检测(记牌点位相关["通灵点位一颜色小"], 记牌点位相关["通灵点位一颜色大"],
                                 通灵检测点位一RGB) and
                    self.像素RGB检测(记牌点位相关["通灵点位二颜色小"], 记牌点位相关["通灵点位二颜色大"],
                                     通灵检测点位二RGB) and
                    self.像素RGB检测(记牌点位相关["通灵点位三颜色小"], 记牌点位相关["通灵点位三颜色大"],
                                     通灵检测点位三RGB) and
                    self.像素RGB检测(记牌点位相关["通灵点位四颜色小"], 记牌点位相关["通灵点位四颜色大"],
                                     通灵检测点位四RGB)):
                self.TongLingJiLu()

    def 回放检测(self):
        if 回放开关["状态"] == "开启":
            回放检测点位一RGB = self.获取像素RGB(回放点位相关["回放点位一坐标"][0], 回放点位相关["回放点位一坐标"][1], )
            回放检测点位二RGB = self.获取像素RGB(回放点位相关["回放点位二坐标"][0], 回放点位相关["回放点位二坐标"][1], )
            回放检测点位三RGB = self.获取像素RGB(回放点位相关["回放点位三坐标"][0], 回放点位相关["回放点位三坐标"][1], )
            回放检测点位四RGB = self.获取像素RGB(回放点位相关["回放点位四坐标"][0], 回放点位相关["回放点位四坐标"][1], )
            # print(回放检测点位一RGB,回放检测点位二RGB,回放检测点位三RGB,回放检测点位四RGB)
            if (self.像素RGB检测(回放点位相关["回放点位一颜色小"], 回放点位相关["回放点位一颜色大"],
                                 回放检测点位一RGB) and
                    self.像素RGB检测(回放点位相关["回放点位二颜色小"], 回放点位相关["回放点位二颜色大"],
                                     回放检测点位二RGB) and
                    self.像素RGB检测(回放点位相关["回放点位三颜色小"], 回放点位相关["回放点位三颜色大"],
                                     回放检测点位三RGB) and
                    self.像素RGB检测(回放点位相关["回放点位四颜色小"], 回放点位相关["回放点位四颜色大"],
                                     回放检测点位四RGB)):
                触发_左键短按(自定义设置["回放点位点击坐标"])

    def closeEvent(self, 事件):
        self.JianCeXianCheng.停止()
        super().closeEvent(事件)

    def 创建常驻标签(self, ):
        左标签位置 = 自定义设置["常驻标签左位置"]
        左标签大小 = 自定义设置["常驻标签左大小"]
        左标签背景色 = 自定义设置["常驻标签左背景色"]
        左标签文本色 = 自定义设置["常驻标签左文本色"]
        右标签位置 = 自定义设置["常驻标签右位置"]
        右标签大小 = 自定义设置["常驻标签右大小"]
        右标签背景色 = 自定义设置["常驻标签右背景色"]
        右标签文本色 = 自定义设置["常驻标签右文本色"]
        标签字号 = 自定义设置["常驻标签字号"]
        标签字体 = 自定义设置["常驻标签字体"]
        透明度 = 自定义设置["常驻标签透明度"]
        左标签文本 = "BY 凤灯幽夜"
        右标签文本 = "本软件纯免费"

        self.常驻标签左 = QLabel(self)
        self.常驻标签左.setGeometry(左标签位置[0], 左标签位置[1], 左标签大小[0], 左标签大小[1])
        self.常驻标签左.setText(左标签文本)
        self.常驻标签左.setFont(QFont(标签字体, 标签字号))
        # 设置左侧标签样式
        左侧调色板 = self.常驻标签左.palette()
        左侧调色板.setColor(QPalette.ColorRole.Window, QColor(左标签背景色))
        左侧调色板.setColor(QPalette.ColorRole.WindowText, QColor(左标签文本色))
        self.常驻标签左.setPalette(左侧调色板)
        self.常驻标签左.setAutoFillBackground(True)
        # 设置左侧标签文本对齐方式
        self.常驻标签左.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # 设置透明度
        常驻标签左透明效果 = QGraphicsOpacityEffect()
        常驻标签左透明效果.setOpacity(透明度)
        self.常驻标签左.setGraphicsEffect(常驻标签左透明效果)
        # 创建右侧常驻标签
        self.常驻标签右 = QLabel(self)
        self.常驻标签右.setGeometry(右标签位置[0], 右标签位置[1], 右标签大小[0], 右标签大小[1])
        self.常驻标签右.setText(右标签文本)
        self.常驻标签右.setFont(QFont(标签字体, 标签字号))
        # 设置右侧标签样式
        右侧调色板 = self.常驻标签右.palette()
        右侧调色板.setColor(QPalette.ColorRole.Window, QColor(右标签背景色))
        右侧调色板.setColor(QPalette.ColorRole.WindowText, QColor(右标签文本色))
        self.常驻标签右.setPalette(右侧调色板)
        self.常驻标签右.setAutoFillBackground(True)
        # 设置右侧标签文本对齐方式
        self.常驻标签右.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        # 设置透明度
        常驻标签右透明效果 = QGraphicsOpacityEffect()
        常驻标签右透明效果.setOpacity(透明度)
        self.常驻标签右.setGraphicsEffect(常驻标签右透明效果)

        self.常驻标签左.show()
        self.常驻标签右.show()

    def 添加倒计时标签(self, 方位="左侧"):
        # 根据方位选择对应的倒计时列表和初始位置
        if 方位 == "左侧":
            倒计时列表 = self.左侧倒计时
            初始位置 = self.左侧初始位置
        else:  # 右侧
            倒计时列表 = self.右侧倒计时
            初始位置 = self.右侧初始位置
        # 计算新标签的位置
        生成位置 = self.计算新标签位置(倒计时列表, 初始位置)
        # 创建新的倒计时标签
        self.设置倒计时(倒计时秒数=自定义设置["倒计时秒数"], 生成位置=生成位置, 方位=方位)

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

    def 设置倒计时(self, 字体=自定义设置["倒计时字体"], 字号=自定义设置["倒计时字号"],
                   背景颜色=自定义设置["倒计时背景色"], 字体颜色=自定义设置["倒计时字体色"], 生成位置=None,
                   标签大小=自定义设置["倒计时标签大小"], 透明度=自定义设置["倒计时透明度"], 字体居中=True,
                   倒计时秒数=自定义设置["倒计时秒数"], 方位="左侧"):
        # 根据方位选择对应的初始位置和倒计时列表
        if 方位 == "左侧":
            初始位置 = self.左侧初始位置
            倒计时列表 = self.左侧倒计时
        else:  # 右侧
            初始位置 = self.右侧初始位置
            倒计时列表 = self.右侧倒计时

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
            新倒计时标签.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

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

        # 初始化倒计时时间
        剩余时间 = 倒计时秒数
        # print(f"{剩余时间:.1f}")
        新倒计时标签.setText(f"{剩余时间:.1f}")
        新倒计时标签.show()

        # 为这个特定的倒计时创建一个计时器
        计时器 = QTimer(self)
        计时器.setInterval(100)  # 100毫秒间隔

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
            倒计时列表 = self.左侧倒计时
        else:  # 右侧
            倒计时列表 = self.右侧倒计时
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
            清空指定方位(self.左侧倒计时)
        elif 方位 == "右侧":
            清空指定方位(self.右侧倒计时)
        else:  # 方位为None，清空所有
            清空指定方位(self.左侧倒计时)
            清空指定方位(self.右侧倒计时)


def 终章():
    应用.quit()
    print("莫以为光,就会被黑暗吞噬!")
    sys.exit(233)


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
# pyinstaller --onefile --add-data "文件;文件" --icon=文件/RINA1.ico 天王寺科学忍具V4.8.py
# pyinstaller --onefile --noconsole --add-data "文件;文件" --icon=文件/RINA1.ico 天王寺科学忍具V4.8.py
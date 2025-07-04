import logging
import logging.config
import os.path
from logging.handlers import RotatingFileHandler

from StaticFunctions import resource_path, get_real_exe_path
import logging
import time
from time import time_ns


class LogRecord_ns(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        self.created_ns = time_ns()  # Fetch precise timestamp
        super().__init__(*args, **kwargs)


class Formatter_ns(logging.Formatter):
    # 修改为4位小数格式
    default_nsec_format = '%s.%04d'  # 从 .%09d 改为 .%04d

    def formatTime(self, record, datefmt=None):
        if datefmt is not None:
            return super().formatTime(record, datefmt)

        # 将纳秒转换为秒的浮点数
        seconds = record.created_ns / 1e9
        ct = self.converter(seconds)
        t = time.strftime(self.default_time_format, ct)

        # 提取毫秒部分并转换为4位小数
        # 1. 计算小数部分（秒的小数部分）
        fractional_seconds = seconds - int(seconds)
        # 2. 转换为毫秒并保留4位小数
        milliseconds = fractional_seconds * 10000  # 10000 = 10^4

        # 使用新的格式：整数部分 + 4位小数
        s = self.default_nsec_format % (t, int(milliseconds))
        return s


logging.setLogRecordFactory(LogRecord_ns)


# logging日志等级详解
# DEBUG  - 对应最详细的内容，比如Judge的奥义点，图像匹配的识别结果，Bus总线上发布的事件
# INFO   - 对应用户能看到的最低一级消息，比如类的初始化或者事件的发生
# WARN   - 对应出错但不可能不影响程序运行的问题，即已经做出了一定的Try-Except措施的
# ERROR  - 对应会直接导致程序崩溃的问题

def setup_logging():
    # 创建根记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # 设置全局最低日志级别

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台只显示INFO及以上级别

    ns_formatter = Formatter_ns('[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s')
    console_handler.setFormatter(ns_formatter)

    # 添加处理器到根记录器
    root_logger.addHandler(console_handler)

    # 添加log文件处理器
    if not os.path.exists(f"{get_real_exe_path()}\\log"):
        os.makedirs(f"{get_real_exe_path()}\\log")

    file_handler = RotatingFileHandler(
        f"{get_real_exe_path()}\\log\\天王寺科学忍具.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # 文件记录更详细

    file_handler.setFormatter(ns_formatter)
    root_logger.addHandler(file_handler)
    # 禁用 comtypes 的日志
    comtypes_logger = logging.getLogger("comtypes")
    comtypes_logger.setLevel(logging.WARNING)  # 设置为 WARNING 或更高
    comtypes_logger.propagate = False  # 防止传播到根日志器
    root_logger.info("Logger根记录器初始化完成...")

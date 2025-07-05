import ctypes
import os
import sys

import cv2

def resource_path(relative_path):
    """
    获取程序解压到的临时目录的文件的位置
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    # 强制转换为长路径（仅限Windows）
    if sys.platform.startswith('win'):
        from ctypes import windll, create_unicode_buffer
        try:
            buf = create_unicode_buffer(512)
            windll.kernel32.GetLongPathNameW(base_path, buf, 512)
            base_path = buf.value
        except Exception:
            pass
    # print(base_path)
    full_path = os.path.normpath(os.path.join(base_path, relative_path))
    return full_path

def get_real_path(relative_path=""):
    """
    获取基于可执行文件位置的绝对路径

    参数:
        relative_path: 相对于可执行文件的相对路径，默认为空字符串（即返回可执行文件所在目录）

    返回:
        基于可执行文件位置的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        if sys.platform == 'win32':
            # Windows平台获取可执行文件路径
            buf = ctypes.create_unicode_buffer(1024)
            ctypes.windll.kernel32.GetModuleFileNameW(None, buf, 1024)
            exe_dir = os.path.dirname(os.path.abspath(buf.value))
        else:
            # 其他平台获取可执行文件路径
            exe_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        # 如果是普通Python脚本运行
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    # 组合路径并规范化
    return os.path.normpath(os.path.join(exe_dir, relative_path))

def cv_save(image_path,image_array):
    """
    image_array:图像数组；image_path:图像的保存全路径
    """
    cv2.imencode('.png', image_array)[1].tofile(image_path)


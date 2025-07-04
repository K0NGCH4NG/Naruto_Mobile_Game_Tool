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


def get_real_exe_path():
    """
    获取可执行文件真实路径
    """
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            buf = ctypes.create_unicode_buffer(1024)
            ctypes.windll.kernel32.GetModuleFileNameW(None, buf, 1024)
            return os.path.dirname(os.path.abspath(buf.value))
        else:
            return os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        return os.path.dirname(os.path.abspath(__file__))


def cv_save(image_path,image_array):
    """
    image_array:图像数组；image_path:图像的保存全路径
    """
    cv2.imencode('.png', image_array)[1].tofile(image_path)


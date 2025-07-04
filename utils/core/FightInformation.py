import json
import logging
import os
import threading
from typing import Dict, Any
from StaticFunctions import get_real_exe_path


class FightInformation:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_path = f"{get_real_exe_path()}/config/Settings.json"

        # 数据结构：key : { 'lock': Lock, 'data': value }
        # 此下皆是调试参数
        self.setting_dics: Dict[str, Dict[str, Any]] = {
            # 基本是程序自定的东西，不建议用户修改
            "查找窗口": {'lock': threading.Lock(), 'data': ['Qt5156QWindowIcon', 'LDPlayerMainFrame']},
            "关闭程序按键": {'lock': threading.Lock(), 'data': 'x'},
            "模拟左侧替身按键": {'lock': threading.Lock(), 'data': 'z'},
            "模拟右侧替身按键": {'lock': threading.Lock(), 'data': 'c'},
            "清空倒计时按键": {'lock': threading.Lock(), 'data': 'v'},

            "默认分辨率": {'lock': threading.Lock(), 'data': "1600x900"},
            "默认截图间隔": {'lock': threading.Lock(), 'data': 50},
            "倒计时秒数": {'lock': threading.Lock(), 'data': 13.5},
            "回放开关": {'lock': threading.Lock(), 'data': 0},
            "点穴开关": {'lock': threading.Lock(), 'data': 0},
            "默认模式": {'lock': threading.Lock(), 'data': "决斗场"},

        }

        # 加载配置
        self._load_config()
        self.logger.debug("初始化完成...")

    def _load_config(self):
        """加载配置文件，不存在则创建"""
        # 确保配置目录存在
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(self.config_path):
            # 提取需要持久化的配置项（排除临时键）
            default_config = {}
            for key, value_dict in self.setting_dics.items():
                # if key not in self.temp_keys:
                with value_dict['lock']:
                    default_config[key] = value_dict['data']

            # 保存默认配置到文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            self.logger.info("创建默认配置文件: %s", self.config_path)

        # 读取配置文件并更新设置
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 遍历所有设置项
            for key, value_dict in self.setting_dics.items():
                # 跳过临时键（不需要从配置文件加载）
                # if key in self.temp_keys:
                #     continue

                # 如果配置文件中有此键，更新内存中的值
                if key in config_data:
                    with value_dict['lock']:
                        # 保留原始数据类型
                        if isinstance(value_dict['data'], int):
                            value_dict['data'] = int(config_data[key])
                        elif isinstance(value_dict['data'], float):
                            value_dict['data'] = float(config_data[key])
                        elif isinstance(value_dict['data'], bool):
                            # 处理布尔值（JSON保存为bool，但可能被读取为int）
                            if isinstance(config_data[key], bool):
                                value_dict['data'] = config_data[key]
                            else:
                                value_dict['data'] = bool(int(config_data[key]))
                        else:
                            value_dict['data'] = config_data[key]

            self.logger.info("成功加载配置文件: %s", self.config_path)

        except Exception as e:
            self.logger.error("加载配置文件失败: %s", str(e))

    def get_config(self, key: str) -> Any:
        """
        线程安全地获取设置项,key：需要取的设置项名称
        """
        with self.setting_dics[key]['lock']:
            # self.logger.debug(f"获取{key}，取到{self.dics[key].get('data', None)}")
            return self.setting_dics[key].get('data', None)

    def set_config(self, key: str, value: Any):
        """
        线程安全地设置设置项,key：需要取的设置项名称，value是要存的设置项，需要符合预期格式
        """
        with self.setting_dics[key]['lock']:
            # self.logger.debug(f"设置{key}为{value}")
            self.setting_dics[key]['data'] = value
        # 如果是需要持久化的键，更新配置文件
        # if key not in self.temp_keys:
        try:
            # 读取现有配置
            config_data = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

            # 更新配置值
            config_data[key] = value
            # 写入文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)

            self.logger.debug("更新配置文件: %s = %s", key, value)

        except Exception as e:
            self.logger.error("更新配置文件失败: %s", str(e))

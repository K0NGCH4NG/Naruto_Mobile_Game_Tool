import concurrent.futures
import logging
import time
from typing import Dict

import cv2
import numpy as np

from StaticFunctions import resource_path
from utils.core.Bus import Bus
from utils.core.ImageMatch import ImageMatch
from utils.core.Screen import extract_diamond_region

# 在顶部添加事件常量定义
SCREEN_DONE = "SCREEN_DONE"
FIGHT_INFORMATION_UPDATE_DONE = "FIGHT_INFORMATION_UPDATE_DONE"
UI_UPDATE = "UI_UPDATE"
JUDGE_START = "JUDGE_START"
FIGHT_OVER = "FIGHT_OVER"
CHECK_IDENTIFICATION_POINTS = "CHECK_IDENTIFICATION_POINTS"
FIGHT_STOP = "FIGHT_STOP"

class FightInformationUpdate:

    def __init__(self, bus: Bus,fight_over_signal):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bus = bus  # 添加总线引用
        self.matcher = ImageMatch.from_cache(resource_path("src/model/IM.pkl"))
        self.screen = None
        # 订阅事件
        self.bus.subscribe(SCREEN_DONE, self.handle_screen_done)
        self.bus.subscribe(CHECK_IDENTIFICATION_POINTS,
                           self.handle_check_identification_points)
        self.bus.subscribe(FIGHT_STOP, self.handle_fight_stop)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.fight_over_signal=fight_over_signal

        # 定义模板
        # roi格式均为： (x1,x2,y1,y2)
        self.fight_status_templates = None
        # 定义各个判断函数所用的区域
        self.roi_dic = None
        # # 预处理模板
        # self.preprocess_templates()

        self.last_vs_time = None
        self.vs_type = None
        # 1代表识别到Winner，等待开始下一次战斗
        # 2代表识别到战斗，等待Winner结束
        self.fight_status_code = 1

        self.bool_recognize_ninja_1p = 0
        self.bool_recognize_ninja_2p = 0
        self.self_ninja = None
        self.ninja_name_1p = None
        self.ninja_name_2p = None
        self.max_ougi_1p = 4
        self.max_ougi_2p = 4
        self.match_ninja_time = None
        self.logger.debug("初始化完成...")

    def preprocess_templates(self):
        """预处理模板图像"""
        self.logger.debug("预处理模版图像：")
        for key, template in self.fight_status_templates.items():
            try:
                template_path = resource_path(f"{template['path']}{key}.png")
                self.logger.debug("模板路径：%s", template_path)
                with open(template_path, 'rb') as f:
                    img_array = np.frombuffer(f.read(), dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if img is None:
                        raise FileNotFoundError(f"文件存在但无法读取: {template_path}")
                    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    template["gray"] = img_gray  # 直接给原字典添加 gray 属性
            except Exception as e:
                self.logger.error(f"模板预处理失败: {e}")

    def handle_screen_done(self, data: Dict):
        """处理截图完成事件"""
        # 并行执行所有识别任务
        screen = data.get('screen', None)
        if screen is None or screen.size == 0:
            self.bus.publish(FIGHT_INFORMATION_UPDATE_DONE)
            return

        if screen.shape[:2] != (900, 1600):
            self.screen = cv2.resize(screen, (1600, 900), interpolation=cv2.INTER_LANCZOS4)
        else:
            self.screen = screen
        screen_gray = cv2.cvtColor(self.screen, cv2.COLOR_BGR2GRAY)
        # start = time.perf_counter()
        future_dict = {}  # 用于存储线程任务和对应的任务名称
        futures = []  # 用于等待的Future列表
        if self.fight_status_code == 1:
            fight_status_code = self.executor.submit(
                self.recognize_fight_status, screen_gray, ["60"])
            future_dict["对局状态"] = fight_status_code
            futures.append(fight_status_code)

        if self.fight_status_code == 2:
            if self.last_vs_time and self.vs_type and time.perf_counter(
            ) - self.last_vs_time > 0.06:
                imgs = self.extract_secret_scroll(self.screen)
                # if imgs is not None:
                #     self.bus.publish(UI_UPDATE, {
                #         'type': 'SECRET_SCROLL',
                #         'secret_scrolls': imgs
                #     })
                self.last_vs_time = None
                self.vs_type = None

            fight_status_code = self.executor.submit(
                self.recognize_fight_status, screen_gray, ["Winner"])
            future_dict["对局状态"] = fight_status_code
            futures.append(fight_status_code)

            if (self.bool_recognize_ninja_1p == 0 or self.bool_recognize_ninja_2p == 0) and time.perf_counter() - self.match_ninja_time > 0.1:
                if self.match_ninja_time and time.perf_counter() - self.match_ninja_time < 3:
                    ninja_name = self.executor.submit(
                        self.match_ninja, screen_gray, [
                            self.bool_recognize_ninja_1p,
                            self.bool_recognize_ninja_2p
                        ])
                    future_dict["忍者姓名"] = ninja_name
                    futures.append(ninja_name)
                else:
                    for index, flag in enumerate([
                        self.bool_recognize_ninja_1p,
                        self.bool_recognize_ninja_2p
                    ]):
                        if flag == 0:
                            if index == 0:
                                self.max_ougi_1p = 4
                                self.bool_recognize_ninja_1p = 1
                            else:
                                self.max_ougi_2p = 4
                                self.bool_recognize_ninja_2p = 1

            if self.bool_recognize_ninja_1p == 1 and self.bool_recognize_ninja_2p == 1:
                ougis_and_timestamp = self.executor.submit(
                    self.recognize_ougi, self.screen, data.get('screen_time'))
                future_dict["双方奥义点和时间戳"] = ougis_and_timestamp
                futures.append(ougis_and_timestamp)
        if futures:
            concurrent.futures.wait(futures)
        results = {}
        for key, future in future_dict.items():
            results[key] = future.result()
        result = results["对局状态"]
        # self.logger.debug(f"[更新战斗信息耗时]：{(time.perf_counter() - start) * 1000:.1f}ms")
        if result:
            if result[0] == 2:
                # 检测到了60,要截取密卷刷新UI了
                self.last_vs_time = time.perf_counter()
                self.vs_type = result[1]
                self.match_ninja_time = time.perf_counter()
                self.bus.publish(FIGHT_INFORMATION_UPDATE_DONE)
                return
            if result[0] == 1:
                # 检测到了胜者标志，这一对局结束，重置各个战斗信息
                self.handle_fight_stop({})
                self.bus.publish(FIGHT_INFORMATION_UPDATE_DONE)
                return
        if self.fight_status_code == 2 and (self.bool_recognize_ninja_1p == 1 and self.bool_recognize_ninja_2p == 1):
            temp_data = {
                "对局状态": self.fight_status_code,
                "双方奥义点和时间戳": results.get("双方奥义点和时间戳", None),
                "1P奥义点": results.get("双方奥义点和时间戳", (None, None))[0],
                "2P奥义点": results.get("双方奥义点和时间戳", (None, None))[1],
                "1P奥义点上限": self.max_ougi_1p,
                "2P奥义点上限": self.max_ougi_2p,
                "1P忍者名称": self.ninja_name_1p,
                "2P忍者名称": self.ninja_name_2p,
            }
            # self.logger.debug(temp_data)
            self.bus.publish(JUDGE_START, temp_data)
        else:
            self.bus.publish(FIGHT_INFORMATION_UPDATE_DONE)

    def extract_secret_scroll(self, screen):
        secret_scroll_regions = self.roi_dic["秘卷区域"]
        if not secret_scroll_regions:
            return None
        temp = []
        for roi in secret_scroll_regions:
            x1, x2, y1, y2 = roi
            temp.append(screen[y1:y2, x1:x2])
        return temp

    def recognize_fight_status(self, screen, need_recognize):
        """
        识别对局状态
        返回 (对局状态:int,置信度最高的图片id,str)
        """

        # 定义匹配任务函数
        def match_task(key, tmpl, frame):
            try:
                x1, x2, y1, y2 = tmpl["roi"]
                roi_gray = frame[y1:y2, x1:x2]
                # 尺寸校验
                if roi_gray.shape[0] < tmpl["gray"].shape[0] or roi_gray.shape[
                    1] < tmpl["gray"].shape[1]:
                    return None
                temp_result = cv2.matchTemplate(roi_gray, tmpl["gray"],
                                                cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(temp_result)
                return (key, max_val) if max_val > 0 else None
            except Exception as e:
                self.logger.error(f"匹配任务异常: {e}")
                return None

        try:
            # self.logger.info("战斗状态识别开始")
            results = []
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=4) as executor:
                for i in need_recognize:
                    results.append(
                        executor.submit(match_task, i,
                                        self.fight_status_templates[i],
                                        screen))
            concurrent.futures.wait(results)
            # 获取 Future 对象的结果并筛选出有效的结果
            valid_results = []
            for future in results:
                result = future.result()  # 获取 Future 对象的结果
                if result is not None:
                    valid_results.append(result)
            # self.logger.info("战斗状态识别结束")
            # 按置信度降序排列并取最大的 result
            max_result = None
            if valid_results:
                # 按置信度（元组的第二个元素）降序排列
                valid_results.sort(key=lambda x: x[1], reverse=True)
                max_result = valid_results[0]  # 取置信度最大的 result
                # self.logger.debug(f"战斗状态识别结果：[{max_result[0]}] ({max_result[1]:.3f})")
            if max_result and max_result[1] > self.fight_status_templates[
                max_result[0]].get("threshold"):
                fight_status_code = self.fight_status_templates[
                    max_result[0]].get("fight_status_code", 1)
                self.fight_status_code = fight_status_code
                if fight_status_code == 1:
                    self.logger.info(f"胜负已分 [{max_result[1]:.3f}]")
                elif fight_status_code == 2:
                    self.logger.info(f"战斗开始 [{max_result[1]:.3f}]")
                return fight_status_code, max_result[0]
            return None

        except Exception as e:
            self.logger.error(f"识别战斗状态时出错：{e}")
            return None

    def recognize_ougi(self, screen, screen_time):
        """识别奥义点"""

        def vectorized_count(regions):
            regions = np.array(regions)
            crops = [screen[y1:y2, x1:x2] for x1, x2, y1, y2 in regions]
            v_channels = [
                cv2.cvtColor(c, cv2.COLOR_BGR2HSV)[..., 2] for c in crops
            ]
            masks = [v < 180 for v in v_channels]
            return sum(1 for mask in masks if np.mean(mask) > 0.5)

        try:
            if self.ninja_name_1p in ["宇智波鼬[百战]"]:
                count1 = self.max_ougi_1p - vectorized_count(
                    self.roi_dic["百战鼬奥义点1"][:self.max_ougi_1p])
            else:
                count1 = self.max_ougi_1p - vectorized_count(
                    self.roi_dic["奥义点1"][:self.max_ougi_1p])
            if self.ninja_name_2p in ["宇智波鼬[百战]"]:
                count2 = self.max_ougi_2p - vectorized_count(
                    self.roi_dic["百战鼬奥义点2"][:self.max_ougi_2p])
            else:
                count2 = self.max_ougi_2p - vectorized_count(
                    self.roi_dic["奥义点2"][:self.max_ougi_2p])

            # for i in range(count1):
            #     if self.ninja_name_1p in ["宇智波鼬[百战]"]:
            #         count1 += self.count_ougi(screen, self.roi_dic["百战鼬奥义点1"][i])
            #
            #     else:
            #         count1 += self.count_ougi(screen, self.roi_dic["奥义点1"][i])
            # for i in range(count2):
            #     if self.ninja_name_2p in ["宇智波鼬[百战]"]:
            #         count2 += self.count_ougi(screen, self.roi_dic["百战鼬奥义点2"][i])
            #     else:
            #         count2 += self.count_ougi(screen, self.roi_dic["奥义点2"][i])

            # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:23]}] 1P 【{count1}】 ： 2P【{count2}】")
            return count1, count2, screen_time
        except Exception as e:
            self.logger.error(f"识别奥义点时出错：{e}")
            return 2, 2, screen_time

    @staticmethod
    def count_ougi(screen, region, threshold=180):
        """
        region=(x_start,x_end,y_start,y_end)
        """
        # 使用 NumPy 的向量化操作
        cropped_image = screen[region[2]:region[3], region[0]:region[1]]

        # 将图片转换到 HSV 颜色空间
        hsv_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

        # 分离 V（亮度）通道
        v_channel = hsv_image[:, :, 2]

        # 创建掩码来标识亮度低于阈值的像素
        v_mask = v_channel < threshold

        # 计算符合条件的像素数量和占比
        count = np.sum(v_mask)
        total = v_channel.size  # 所有通道的像素数应该相同，任意通道的 size 都可以
        y = count / total * 100

        # 如果符合条件的像素占比超过 50%，则返回 -1，否则返回 0
        return -1 if y > 50 else 0

    def match_ninja(self, screen, match_list):
        ninja_names = {"1P": "非特殊", "2P": "非特殊"}
        try:
            futures = [None, None]
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=2) as executor:
                for index, roi in enumerate(self.roi_dic["头像区域"]):
                    if match_list[index] == 0:
                        x1, x2, y1, y2 = roi
                        # cv2.imwrite(f"{index + 1}P_{random()}.jpg", extract_diamond_region(screen[y1:y2, x1:x2]))
                        futures[index] = executor.submit(
                            self.matcher.match,  # 函数引用
                            extract_diamond_region(screen[y1:y2,
                                                   x1:x2]),  # 第一个参数
                            min_match_count=15,  # 命名参数
                            ratio_thresh=0.7,  # 命名参数
                            aggregation='max',  # 命名参数
                            num_workers=5,  # 命名参数
                            top_k=5  # 命名参数
                        )
            concurrent.futures.wait(futures)

            for i, future in enumerate(futures):
                if future:
                    result = future.result()
                    # self.logger.info(f"{i + 1}P忍者识别结果:{result}")
                    if result and result['success']:
                        if result.get('best_match', None):
                            self.logger.info(
                                f"{i + 1}P忍者识别成功:{result.get('best_match', '非特殊')}"
                            )
                            ninja_names[f"{i + 1}P"] = result.get(
                                'best_match', '非特殊')
                            if i == 0:
                                self.bool_recognize_ninja_1p = 1
                                self.ninja_name_1p = result.get(
                                    'best_match', '非特殊')
                            else:
                                self.bool_recognize_ninja_2p = 1
                                self.ninja_name_2p = result.get(
                                    'best_match', '非特殊')
                            if result.get('best_match','非特殊') in ["千手柱间[秽土转生]", "千手柱间[木叶创立]"]:
                                if i == 0:
                                    self.max_ougi_1p = 6
                                else:
                                    self.max_ougi_2p = 6
                                self.logger.info(f"{i + 1}P奥义点上限设为6")
                            # self.logger.debug("匹配结果摘要:")
                            # self.logger.debug(f"最佳匹配: {result.get('best_match', '非特殊')}")
                            # self.logger.info("Top 5匹配:")
                            # for match in result['top_matches']:
                            #     self.logger.info(f"  #{match['rank']} {match['class_name']}: "
                            #                      f"类别分={match['class_score']}, 样本分={match['best_sample_score']}")
                        else:
                            if i == 0:
                                self.bool_recognize_ninja_1p = 1
                                self.ninja_name_1p = '非特殊'
                                self.logger.info("1P忍者非特殊忍者")
                            else:
                                self.bool_recognize_ninja_2p = 1
                                self.ninja_name_2p = '非特殊'
                                self.logger.info("2P忍者非特殊忍者")
            return ninja_names
        except Exception as e:
            self.logger.error(f"识别忍者时出错：{e}")
            return ninja_names

    def handle_check_identification_points(self, data: Dict):
        if self.screen is None or self.screen.size == 0:
            return
        display_img = self.screen.copy()

        # 定义不同区域的显示颜色
        colors = {
            "奥义点1": (0, 0, 255),  # 红色
            "奥义点2": (0, 0, 255),  # 红色
            "百战鼬奥义点1": (0, 255, 0),  # 绿色
            "百战鼬奥义点2": (0, 255, 0),  # 绿色
            "HP": (255, 0, 0),  # 蓝色
            "技能": (0, 255, 255),  # 黄色
            "己方位置": (255, 0, 255),  # 紫色
            "头像区域": (255, 255, 0)  # 青色
        }

        # 遍历所有区域并绘制
        for key, regions in self.roi_dic.items():
            color = colors.get(key, (255, 255, 255))  # 默认白色
            # print(key)
            if key == "HP":
                # HP是双层列表结构
                for sub_regions in regions:
                    for rect in sub_regions:
                        if rect:  # 确保区域非空
                            x1, x2, y1, y2 = rect
                            # print(f"({x1},{y1},{x2-x1},{y2-y1})")
                            cv2.rectangle(display_img, (x1, y1), (x2, y2),
                                          color, 1)
            else:
                # 其他单层列表结构
                for rect in regions:
                    if rect:  # 确保区域非空
                        x1, x2, y1, y2 = rect
                        # print(f"({x1},{y1},{x2 - x1},{y2 - y1})")
                        cv2.rectangle(display_img, (x1, y1), (x2, y2), color,
                                      1)

        # 显示结果图像
        cv2.imshow("ROI Visualization", display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def handle_fight_stop(self, data: Dict):
        """
        手动暂停战斗
        """
        self.fight_status_code = 1
        self.bool_recognize_ninja_1p = 0
        self.bool_recognize_ninja_2p = 0
        self.self_ninja = None
        self.ninja_name_1p = None
        self.ninja_name_2p = None
        self.max_ougi_1p = 4
        self.max_ougi_2p = 4
        self.bus.publish(FIGHT_OVER)
        self.fight_over_signal.emit({})


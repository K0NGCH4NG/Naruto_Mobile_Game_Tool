import concurrent.futures
import logging
import threading
import time
from collections import Counter
from datetime import datetime
from typing import Dict

# 导入各个用到的类
from utils.core.Bus import Bus
from utils.core.FightInformation import FightInformation

FIGHT_INFORMATION_UPDATE_DONE = "FIGHT_INFORMATION_UPDATE_DONE"
UI_UPDATE = "UI_UPDATE"
COUNTDOWN_EVENT = "COUNTDOWN_EVENT"
JUDGE_START = "JUDGE_START"
FIGHT_OVER = "FIGHT_OVER"
JUDGE_DONE = "JUDGE_DONE"

class Judge:
    def __init__(self, bus: Bus, fight_info: FightInformation, countdown_signal=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bus = bus
        self.fight_info = fight_info
        self.judge_times = (0.3, 0.23)  # 第一个是奥义点数量下降的判断时间，第二个是奥义点数量上升的判断时间
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.countdown_signal = countdown_signal
        self.ougi_judge_dic = {
            "1P奥义点": None,
            "1P开始判断标志": False,
            "1P方向": None,  # 0表示下降 1表示上升
            "1P待判断奥义点": None,
            "1P待判断时间": None,
            "1P替身时刻": None,
            "1P倒计时触发时刻": None,
            "1P奥义触发时刻": None,

            "2P奥义点": None,
            "2P开始判断标志": False,
            "2P方向": None,
            "2P待判断奥义点": None,
            "2P待判断时间": None,
            "2P替身时刻": None,
            "2P倒计时触发时刻": None,
            "2P奥义触发时刻": None
        }
        # 订阅事件
        self.bus.subscribe(JUDGE_START, self.handle_judge_start)
        self.logger.debug(f"初始化完成...")

    def handle_judge_start(self, data: Dict, ):
        # 使用线程避免阻塞事件循环
        threading.Thread(target=self._judge, args=(data,), daemon=True).start()

    def handle_fight_over(self, data: Dict):
        self.ougi_judge_dic = {
            "1P奥义点": None,
            "1P开始判断标志": False,
            "1P方向": None,  # 0表示下降 1表示上升
            "1P待判断奥义点": None,
            "1P待判断时间": None,
            "1P替身时刻": None,
            "1P倒计时触发时刻": None,
            "1P奥义触发时刻": None,

            "2P奥义点": None,
            "2P开始判断标志": False,
            "2P方向": None,
            "2P待判断奥义点": None,
            "2P待判断时间": None,
            "2P替身时刻": None,
            "2P倒计时触发时刻": None,
            "2P奥义触发时刻": None
        }

    def _judge(self, data):
        try:
            ougis = data.get("双方奥义点和时间戳", None)
            if ougis is None:
                self.logger.debug("双方奥义点和时间戳为空")
                self.bus.publish(JUDGE_DONE)
                return
            if not self.ougi_judge_dic[f"1P奥义点"] and not self.ougi_judge_dic[f"2P奥义点"]:
                self.ougi_judge_dic[f"1P奥义点"] = ougis[0]
                self.ougi_judge_dic[f"2P奥义点"] = ougis[1]
                self.bus.publish(JUDGE_DONE)
                return
            # self.logger.debug(f"[奥义点] [{self.ougi_judge_dic[f"1P奥义点"]}->{ougis[0]}] [{self.ougi_judge_dic[f"2P奥义点"]}->{ougis[1]}]")
            futures = [self.executor.submit(self._judge_single, 1, ougis), self.executor.submit(self._judge_single, 2, ougis)]
            concurrent.futures.wait(futures)
            self.bus.publish(JUDGE_DONE)
            # self.logger.debug(f"JUDGE成功判断")
            self.bus.publish(UI_UPDATE, {
                'type': 'JUDGE',
                'fight_info': data
            })

        except Exception as e:
            self.logger.error(f"判断过程中发生错误: {e}")

    def _judge_single(self, player, ougis):
        try:
            ougi = ougis[player - 1]
            player_key = f"{player}P"
            if not self.ougi_judge_dic[f"{player_key}开始判断标志"]:
                if ougi != self.ougi_judge_dic[f"{player_key}奥义点"]:
                    self.ougi_judge_dic[f"{player_key}方向"] = 1 if ougi > self.ougi_judge_dic[f"{player_key}奥义点"] else 0
                    self.ougi_judge_dic[f"{player_key}开始判断标志"] = True
                    self.ougi_judge_dic[f"{player_key}待判断奥义点"] = ougi
                    self.ougi_judge_dic[f"{player_key}替身时刻"] = ougis[2]
                return

            if self.ougi_judge_dic[f"{player_key}开始判断标志"]:
                if ougi == self.ougi_judge_dic[f"{player_key}待判断奥义点"]:
                    self.ougi_judge_dic[f"{player_key}待判断时间"] = ougis[2]
                    self.logger.debug(
                        f"[{player_key}] [{self.ougi_judge_dic[f"{player_key}奥义点"]}->{self.ougi_judge_dic[f"{player_key}待判断奥义点"]}] [Time:{self.ougi_judge_dic[f"{player_key}待判断时间"] - self.ougi_judge_dic[f"{player_key}替身时刻"]:.6f}]")
                else:
                    self.logger.debug(f"[{player_key}] [{self.ougi_judge_dic[f"{player_key}奥义点"]}->{self.ougi_judge_dic[f"{player_key}待判断奥义点"]}] [Reset]")
                    self.ougi_judge_dic[f"{player_key}开始判断标志"] = False
                    self.ougi_judge_dic[f"{player_key}待判断时间"] = None
                    self.ougi_judge_dic[f"{player_key}替身时刻"] = None
                    return

            if self.ougi_judge_dic[f"{player_key}待判断时间"] - self.ougi_judge_dic[f"{player_key}替身时刻"] > self.judge_times[self.ougi_judge_dic[f"{player_key}方向"]]:
                trigger_time = self.ougi_judge_dic[f"{player_key}替身时刻"]
                try:
                    if trigger_time and self.ougi_judge_dic[f"{player_key}奥义点"] - self.ougi_judge_dic[f"{player_key}待判断奥义点"] in [1]:
                        end_time = time.perf_counter()
                        if self.ougi_judge_dic[f"{player_key}倒计时触发时刻"] is None or end_time - self.ougi_judge_dic[f"{player_key}倒计时触发时刻"] > 1:
                            self.ougi_judge_dic[f"{player_key}倒计时触发时刻"] = trigger_time
                            # 发布替身事件
                            self.countdown_signal.emit(
                                {
                                    'type': "START",
                                    'target': f'{"左" if player_key == "1P" else "右"}侧',
                                    'time': 15.00,
                                    'add': -0.20,
                                    'time_perf': trigger_time
                                }
                            )
                            self.logger.info(f"[{player_key}] 替身")
                        else:
                            self.logger.debug(f"距离上次触发不到1秒:{end_time - self.ougi_judge_dic[f"{player_key}倒计时触发时刻"]}")
                    if self.ougi_judge_dic[f"{player_key}奥义点"] - self.ougi_judge_dic[f"{player_key}待判断奥义点"] in [4, 5, 6]:
                        end_time = time.perf_counter()
                        if self.ougi_judge_dic[f"{player_key}奥义触发时刻"] is None or end_time - self.ougi_judge_dic[f"{player_key}奥义触发时刻"] > 3:
                            self.ougi_judge_dic[f"{player_key}奥义触发时刻"] = trigger_time
                            self.logger.info(f"[{player_key}] 奥义")
                        else:
                            self.logger.debug(f"距离上次触发不到3秒:{end_time - self.ougi_judge_dic[f"{player_key}倒计时触发时刻"]}")
                finally:
                    self.ougi_judge_dic[f"{player_key}奥义点"] = self.ougi_judge_dic[f"{player_key}待判断奥义点"]
                    self.ougi_judge_dic[f"{player_key}开始判断标志"] = False
                    self.ougi_judge_dic[f"{player_key}待判断时间"] = None
                    self.ougi_judge_dic[f"{player_key}替身时刻"] = None
                return True

        except Exception as e:
            self.logger.error(f"[{player_key}] 判断时出错: {e}")
            return False

    def _judge_skill_command(self):
        current_ninja_skills = self.ninja_skills.get_skills(self.fight_info.get_data("己方忍者"))
        if current_ninja_skills:
            # print("取出出招表")
            pass
            # print(current_ninja_skills)

            # self.bus.publish(
            #     UI_UPDATE,
            #     {
            #         'type':"SKILL",
            #         'data':[
            #
            #         ]
            #     }
            # )

import logging

import cv2
import numpy as np
import os
import time
import pickle
import json
import shutil
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor


def cv_imread(file_path):
    """读取图像（支持中文路径）并转换为灰度图"""
    cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    return cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)


def keypoint_to_dict(kp):
    """将关键点对象转换为可序列化的字典"""
    return {
        'pt': kp.pt,
        'size': kp.size,
        'angle': kp.angle,
        'response': kp.response,
        'octave': kp.octave,
        'class_id': kp.class_id
    }


def dict_to_keypoint(kp_dict):
    """将字典转换回关键点对象"""
    kp = cv2.KeyPoint()
    kp.pt = tuple(kp_dict['pt'])
    kp.size = kp_dict['size']
    kp.angle = kp_dict['angle']
    kp.response = kp_dict['response']
    kp.octave = kp_dict['octave']
    kp.class_id = kp_dict['class_id']
    return kp


class ImageMatch:
    def __init__(self, mode='match', config=None, cache_file="feature_cache.pkl"):
        """
        图像匹配器

        :param mode: 工作模式 - 'train' 或 'match'
        :param config: 配置字典，训练模式下需要提供'database_dir'
        :param cache_file: 特征缓存文件路径
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cache_file = cache_file
        self.mode = mode
        self.config = config or {}

        # 初始化SIFT检测器和FLANN匹配器
        self.sift = cv2.SIFT_create()

        flann_index_kdtree = 1
        index_params = dict(algorithm=flann_index_kdtree, trees=5)
        search_params = dict(checks=50)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        if mode == 'match':
            self._load_cache()
        elif mode == 'train':
            if 'database_dir' not in self.config:
                raise ValueError("训练模式需要提供 'database_dir' 配置")
            self.database = self._extract_features()
            self._save_cache()
        else:
            raise ValueError(f"无效模式: {mode}. 必须是 'train' 或 'match'")

    def _extract_features(self):
        """提取数据库特征"""
        database_dir = self.config['database_dir']
        min_samples = self.config.get('min_samples_per_class', 1)
        num_workers = self.config.get('num_workers', 4)

        database = defaultdict(list)
        self.logger.info(f"⏳ 正在提取特征: {database_dir}")
        start_time = time.time()

        # 获取所有类别目录
        class_dirs = [d for d in os.listdir(database_dir)
                      if os.path.isdir(os.path.join(database_dir, d))]

        # 使用线程池并行处理
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = []
            for class_name in class_dirs:
                class_dir = os.path.join(database_dir, class_name)
                if not self._has_valid_images(class_dir):
                    self.logger.warning(f"⚠️ 跳过空目录: {class_name}")
                    continue
                futures.append(executor.submit(
                    self._process_class_dir, class_dir, class_name, min_samples
                ))

            for future in futures:
                class_name, class_data = future.result()
                if class_data:  # 只添加有有效数据的类别
                    database[class_name] = class_data

        elapsed = time.time() - start_time
        self.logger.info(f"✅ 特征提取完成: {len(database)} 个类别, {sum(len(v) for v in database.values())} 个样本, 耗时: {elapsed:.1f}秒")
        return dict(database)

    @staticmethod
    def _preprocess_img(img):
        """
        预处理增强特征
        :param img:
        :return:
        """
        # ===== 预处理增强 =====
        if len(img.shape) == 3:  # 确保灰度化
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.equalizeHist(img)  # 对比度增强
        img = cv2.GaussianBlur(img, (3, 3), 0)  # 降噪
        # # 显示结果图像
        # cv2.imshow("ROI Visualization", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return img

    def _process_class_dir(self, class_dir, class_name, min_samples=1):
        """处理单个类别的目录"""
        class_data = []
        processed = 0

        for filename in sorted(os.listdir(class_dir)):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            img_path = os.path.join(class_dir, filename)
            if not os.path.exists(img_path):
                self.logger.warning(f"⚠️ 文件不存在 - {img_path}")
                continue

            try:
                img = cv_imread(img_path)
                if img is None:
                    self.logger.warning(f"⚠️ 无法读取图像: {img_path}")
                    continue

                kp, des = self.sift.detectAndCompute(self._preprocess_img(img), None)  # 使用预处理后的图像

                if des is None or len(des) < 10:  # 忽略特征点太少的图像
                    self.logger.warning(f"⚠️ 特征不足: {img_path} - {len(kp) if kp else 0}个关键点")
                    continue

                # 存储特征和元数据
                class_data.append({
                    'class_name': class_name,
                    'image_path': img_path,
                    'keypoints': kp,  # 原始KeyPoint对象
                    'descriptors': des,
                    'filename': filename
                })
                processed += 1

                # 限制每个类别的最小样本数
                if min_samples > 0 and processed >= min_samples:
                    break

            except Exception as e:
                self.logger.error(f"⚠️ 处理 {img_path} 时出错: {str(e)}")

        if class_data:
            self.logger.info(f"🏷️ 类别 '{class_name}' 提取了 {len(class_data)} 个样本")
            return class_name, class_data
        return class_name, None

    def _has_valid_images(self, class_dir):
        """检查目录是否包含有效的图像文件"""
        for filename in os.listdir(class_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                return True
        return False

    def _save_cache(self):
        """保存特征缓存 - 使用安全写入方法避免文件损坏"""
        # 准备可序列化的数据库
        serializable_db = {}
        for class_name, samples in self.database.items():
            serializable_samples = []
            for sample in samples:
                # 转换关键点为可序列化格式
                serializable_kp = [keypoint_to_dict(kp) for kp in sample['keypoints']]

                serializable_samples.append({
                    'class_name': sample['class_name'],
                    'image_path': sample['image_path'],
                    'keypoints': serializable_kp,  # 可序列化格式
                    'descriptors': sample['descriptors'],
                    'filename': sample['filename']
                })
            serializable_db[class_name] = serializable_samples

        cache_data = {
            'database': serializable_db,
            'config': self.config,
            'timestamp': time.time()
        }

        try:
            # 使用临时文件写入，避免写入过程中断导致文件损坏
            temp_file = self.cache_file + ".tmp"

            with open(temp_file, 'wb') as f:
                pickle.dump(cache_data, f)

            # 写入完成后再重命名为目标文件
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
            shutil.move(temp_file, self.cache_file)

            file_size = os.path.getsize(self.cache_file) / (1024 * 1024)  # MB
            self.logger.info(f"💾 特征缓存已保存: {self.cache_file} ({file_size:.2f} MB)")
            return True
        except Exception as e:
            self.logger.error(f"❌ 保存缓存失败: {str(e)}")
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return False

    def _load_cache(self):
        """加载特征缓存"""
        if not os.path.exists(self.cache_file):
            self.logger.error(f"缓存文件不存在: {self.cache_file}")
            raise FileNotFoundError(f"缓存文件不存在: {self.cache_file}")

        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)

            # 转换回原始KeyPoint格式
            original_db = {}
            for class_name, samples in cache_data['database'].items():
                original_samples = []
                for sample in samples:
                    # 转换回KeyPoint对象
                    original_kp = [dict_to_keypoint(kp_dict) for kp_dict in sample['keypoints']]

                    original_samples.append({
                        'class_name': sample['class_name'],
                        'image_path': sample['image_path'],
                        'keypoints': original_kp,  # 原始KeyPoint对象
                        'descriptors': sample['descriptors'],
                        'filename': sample['filename']
                    })
                original_db[class_name] = original_samples

            self.database = original_db
            self.config = cache_data.get('config', {})
            timestamp = cache_data.get('timestamp', 0)

            # 显示缓存信息
            date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            num_classes = len(self.database)
            num_samples = sum(len(v) for v in self.database.values())

            self.logger.debug(f"加载特征缓存: {self.cache_file}")
            self.logger.debug(f"创建时间: {date_str}")
            self.logger.debug(f"类别数量: {num_classes}")
            self.logger.debug(f"样本总数: {num_samples}")
            self.logger.info(f"图像匹配库缓存已加载...")
            return True
        except Exception as e:
            # 尝试提供更具体的错误信息
            if isinstance(e, EOFError):
                self.logger.error(f"缓存文件已损坏或为空: {self.cache_file}")
                self.logger.error("请删除缓存文件并重新运行训练模式")
            else:
                self.logger.error(f"加载缓存失败: {str(e)}")
            raise RuntimeError(f"加载缓存失败: {str(e)}")

    def match(self, query_img, min_match_count=10, ratio_thresh=0.7,
              aggregation='max', num_workers=4, top_k=5):
        """
        匹配查询图像

        :param query_img: 查询图像(灰度图)
        :param min_match_count: 最小匹配点数阈值
        :param ratio_thresh: Lowe's ratio测试阈值
        :param aggregation: 分数聚合策略 ('max', 'avg', 'weighted')
        :param num_workers: 并行工作线程数
        :param top_k: 返回前K个结果
        :return: 匹配结果字典
        """
        # print("🔎 开始匹配...")
        start_time = time.time()
        query_kp, query_des = self.sift.detectAndCompute(self._preprocess_img(query_img), None)  # 使用预处理后的图像
        if query_des is None:
            self.logger.warning("⚠️ 查询图像未提取到特征")
            return {'success': False, 'error': 'No features detected in query image'}

        # print(f"  查询图像提取到 {len(query_kp)} 个关键点")

        # 存储每个类别的匹配结果
        class_results = {}

        # 使用线程池并行匹配
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for class_name, class_samples in self.database.items():
                futures = []
                for sample_data in class_samples:
                    futures.append(executor.submit(
                        self._match_single_sample,
                        query_des,
                        sample_data,
                        ratio_thresh
                    ))

                # 收集该类别的所有匹配结果
                sample_results = [future.result() for future in futures]

                # 根据聚合策略计算类别分数
                if aggregation == 'max':
                    class_score = max(score for score, _, _ in sample_results)
                elif aggregation == 'avg':
                    class_score = sum(score for score, _, _ in sample_results) / len(sample_results)
                elif aggregation == 'weighted':
                    total_weight = 0
                    weighted_sum = 0
                    for score, _, _ in sample_results:
                        weight = np.sqrt(score)  # 使用平方根作为权重
                        weighted_sum += score * weight
                        total_weight += weight
                    class_score = weighted_sum / total_weight if total_weight > 0 else 0
                else:
                    class_score = max(score for score, _, _ in sample_results)

                # 找到该类别的代表性样本
                best_sample_idx = np.argmax([score for score, _, _ in sample_results])
                best_sample_score, best_matches, best_sample_data = sample_results[best_sample_idx]

                class_results[class_name] = {
                    'class_score': class_score,
                    'best_sample': best_sample_data,
                    'matches': best_matches,
                    'best_sample_score': best_sample_score
                }

        # 获取前K个匹配结果
        sorted_classes = sorted(
            class_results.items(),
            key=lambda x: x[1]['class_score'],
            reverse=True
        )[:top_k]

        # 准备结果
        result = {
            'success': True,
            'query_features': len(query_kp),
            'min_match_count': min_match_count,
            'ratio_thresh': ratio_thresh,
            'elapsed_time': time.time() - start_time,
            'top_matches': []
        }

        # 检查最佳匹配是否达到阈值
        best_match = sorted_classes[0] if sorted_classes else None
        if best_match and best_match[1]['best_sample_score'] >= min_match_count:
            result['best_match'] = best_match[0]
        else:
            result['best_match'] = None

        # 构建top_matches列表
        for i, (class_name, class_data) in enumerate(sorted_classes):
            sample_data = class_data['best_sample']
            match_info = {
                'rank': i + 1,
                'class_name': class_name,
                'class_score': round(class_data['class_score'], 2),
                'best_sample_score': class_data['best_sample_score'],
                'sample_path': sample_data['image_path'],
                'sample_filename': sample_data['filename']
            }
            result['top_matches'].append(match_info)

        # print(f"✅ 匹配完成! 耗时: {result['elapsed_time']:.2f}秒")
        # print(f"  最佳匹配: {result.get('best_match', '无')}")
        # for match in result['top_matches'][:3]:
        #     print(f"  #{match['rank']} {match['class_name']}: 类别分={match['class_score']}, 样本分={match['best_sample_score']}")

        return result

    def _match_single_sample(self, query_des, sample_data, ratio_thresh):
        """匹配单个数据库样本"""
        db_des = sample_data['descriptors']

        # 使用FLANN进行KNN匹配
        matches = self.flann.knnMatch(query_des, db_des, k=2)

        # 应用Lowe's ratio测试筛选良好匹配
        good_matches = []
        for match_pair in matches:
            if len(match_pair) < 2:
                continue
            m, n = match_pair
            if m.distance < ratio_thresh * n.distance:
                good_matches.append(m)

        return len(good_matches), good_matches, sample_data

    def match_file(self, query_path, **kwargs):
        """从文件加载查询图像并进行匹配"""
        query_img = cv_imread(query_path)
        if query_img is None:
            self.logger.warning(f"⚠️ 无法读取图像: {query_path}")
            return {'success': False, 'error': f'Unable to read image: {query_path}'}

        self.logger.debug(f"🔍 匹配图像: {os.path.basename(query_path)}")
        return self.match(query_img, **kwargs)

    def get_database_info(self):
        """获取数据库信息"""
        if not hasattr(self, 'database'):
            return {'error': 'Database not loaded'}

        num_classes = len(self.database)
        num_samples = sum(len(v) for v in self.database.values())
        class_info = {cls: len(samples) for cls, samples in self.database.items()}

        return {
            'num_classes': num_classes,
            'num_samples': num_samples,
            'classes': class_info
        }

    @staticmethod
    def train(database_dir, cache_file="feature_cache.pkl",
              min_samples_per_class=1, num_workers=4):
        """
        训练模式: 提取特征并保存到缓存

        :param database_dir: 数据库图像目录
        :param cache_file: 缓存文件路径
        :param min_samples_per_class: 每个类别最少提取的样本数
        :param num_workers: 并行工作线程数
        :return: ImageMatch实例
        """
        config = {
            'database_dir': database_dir,
            'min_samples_per_class': min_samples_per_class,
            'num_workers': num_workers
        }
        return ImageMatch(
            mode='train',
            config=config,
            cache_file=cache_file
        )

    @staticmethod
    def from_cache(cache_file="feature_cache.pkl"):
        """
        匹配模式: 直接从缓存加载特征

        :param cache_file: 缓存文件路径
        :return: ImageMatch实例
        """
        return ImageMatch(
            mode='match',
            cache_file=cache_file
        )


# 使用示例
if __name__ == "__main__":
    # 训练模式：提取特征并保存缓存
    print("===== 训练模式 =====")
    trainer = ImageMatch.train(
        database_dir="avatar_database",
        cache_file="IM.pkl",
        min_samples_per_class=2,
        num_workers=4
    )

    # 获取数据库信息
    db_info = trainer.get_database_info()
    print("\n数据库信息:")
    print(f"类别数量: {db_info['num_classes']}")
    print(f"样本总数: {db_info['num_samples']}")
    print("各类别样本数:")
    for cls, count in db_info['classes'].items():
        print(f"  {cls}: {count}个样本")

    # 匹配模式：直接从缓存加载
    print("\n===== 匹配模式 =====")
    matcher = ImageMatch.from_cache("IM.pkl")

    # 进行匹配
    query_path = "val/2025-06-16_15-35-52.840365.png"
    result = matcher.match_file(
        query_path,
        min_match_count=15,
        ratio_thresh=0.7,
        aggregation='max',
        num_workers=4,
        top_k=5
    )

    # 显示匹配结果
    if result['success']:
        print("\n匹配结果摘要:")
        print(f"最佳匹配: {result.get('best_match', '无')}")
        print("Top 5匹配:")
        for match in result['top_matches']:
            print(f"  #{match['rank']} {match['class_name']}: "
                  f"类别分={match['class_score']}, 样本分={match['best_sample_score']}")

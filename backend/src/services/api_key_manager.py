# services/api_key_manager.py
import os
import sys
import random
from collections import defaultdict, deque
from typing import List, Dict
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入环境变量加载器
from src.env_loader import load_environment_variables
load_environment_variables()  # 确保环境变量已加载

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIKeyManager:
    def __init__(self):
        self.key_pools = defaultdict(deque)
        self.key_indexes = defaultdict(int)
        self.key_weights = defaultdict(dict)
        self.load_keys()
        self.strategy = os.getenv('API_KEY_STRATEGY', 'round-robin').lower()
        logger.info("API Key Manager initialized")


    def load_keys(self):
        # 加载 Gemini Pro 密钥
        for i in range(1, 11):  # 支持最多 10 个密钥
            key = os.getenv(f'GOOGLE_API_KEY_PRO_{i}')
            if key:
                self.key_pools['gemini-2.5-pro'].append(key)
        
        # 加载 Gemini Flash 密钥
        for i in range(1, 11):
            key = os.getenv(f'GOOGLE_API_KEY_FLASH_{i}')
            if key:
                self.key_pools['gemini-2.5-flash'].append(key)
        
        # # 加载 DeepSeek 密钥
        # for i in range(1, 11):
        #     key = os.getenv(f'DEEPSEEK_API_KEY_{i}')
        #     if key:
        #         self.key_pools['deepseek-r1'].append(key)
    
    def get_key(self, model: str) -> str:
        """获取指定模型的API密钥"""
        pool = self.key_pools.get(model)
        if not pool:
            raise ValueError(f"No keys available for model: {model}")
        
        if self.strategy == 'random':
            return random.choice(list(pool))
        elif self.strategy == 'weighted':
            return self._get_weighted_key(model)
        else:  # round-robin (default)
            return self._get_round_robin_key(model)
    
    def _get_round_robin_key(self, model: str) -> str:
        """轮询策略获取密钥"""
        key = self.key_pools[model][self.key_indexes[model]]
        self.key_indexes[model] = (self.key_indexes[model] + 1) % len(self.key_pools[model])
        return key
    
    def _get_weighted_key(self, model: str) -> str:
        """权重策略获取密钥（需要预先设置权重）"""
        # 实现权重逻辑（示例简化版）
        return random.choice(list(self.key_pools[model]))
    
    def add_custom_key(self, model: str, key: str):
        """添加临时自定义密钥"""
        if model not in self.key_pools:
            self.key_pools[model] = deque()
        self.key_pools[model].appendleft(key)  # 添加到队列前端优先使用
    
    def get_key_count(self, model: str) -> int:
        """获取指定模型的可用密钥数量"""
        return len(self.key_pools.get(model, []))

# 单例模式实例
api_key_manager = APIKeyManager()
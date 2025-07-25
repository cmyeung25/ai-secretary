"""
記憶管理增強功能模組
提供更智能的記憶分類、搜索和管理功能
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

class MemoryClassifier:
    """記憶分類器，將不同類型的記憶進行智能分類"""
    
    MEMORY_TYPES = {
        "personal_info": {
            "keywords": ["生日", "年齡", "住址", "電話", "郵箱", "職業", "公司"],
            "patterns": [r"\d{4}年\d{1,2}月\d{1,2}日", r"\d{1,2}月\d{1,2}日"],
            "weight": 1.0
        },
        "preferences": {
            "keywords": ["喜歡", "不喜歡", "偏好", "習慣", "愛好"],
            "patterns": [r"我(喜歡|不喜歡|偏好)", r"我的(習慣|愛好)是"],
            "weight": 0.8
        },
        "health": {
            "keywords": ["過敏", "疾病", "健康", "醫生", "藥物", "症狀"],
            "patterns": [r"對.*過敏", r"患有.*病"],
            "weight": 1.0
        },
        "relationships": {
            "keywords": ["朋友", "同事", "家人", "老闆", "客戶", "聯絡人"],
            "patterns": [r".*是我的.*", r"我的.*是.*"],
            "weight": 0.9
        },
        "work": {
            "keywords": ["工作", "項目", "會議", "任務", "截止日期", "同事"],
            "patterns": [r"項目.*", r"會議.*", r"任務.*"],
            "weight": 0.7
        },
        "decisions": {
            "keywords": ["決定", "選擇", "計劃", "打算"],
            "patterns": [r"我決定.*", r"我選擇.*", r"我計劃.*"],
            "weight": 0.9
        }
    }
    
    def classify_memory(self, text: str, speaker: str) -> Dict[str, Any]:
        """對記憶進行分類"""
        classification = {
            "primary_type": "general",
            "secondary_types": [],
            "confidence": 0.0,
            "importance": 0.5,
            "keywords": []
        }
        
        text_lower = text.lower()
        scores = {}
        
        # 計算每種類型的分數
        for memory_type, config in self.MEMORY_TYPES.items():
            score = 0.0
            matched_keywords = []
            
            # 關鍵字匹配
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += 1.0
                    matched_keywords.append(keyword)
            
            # 模式匹配
            for pattern in config["patterns"]:
                if re.search(pattern, text):
                    score += 2.0
            
            # 應用權重
            score *= config["weight"]
            
            if score > 0:
                scores[memory_type] = score
                classification["keywords"].extend(matched_keywords)
        
        if scores:
            # 確定主要類型
            primary_type = max(scores, key=scores.get)
            classification["primary_type"] = primary_type
            classification["confidence"] = min(scores[primary_type] / 5.0, 1.0)
            
            # 確定次要類型
            secondary_types = [t for t, s in scores.items() 
                             if t != primary_type and s >= 1.0]
            classification["secondary_types"] = secondary_types
            
            # 計算重要性
            importance = 0.5 + (classification["confidence"] * 0.5)
            if primary_type in ["personal_info", "health", "decisions"]:
                importance += 0.2
            classification["importance"] = min(importance, 1.0)
        
        return classification

class MemoryContextAnalyzer:
    """記憶上下文分析器，分析記憶之間的關聯性"""
    
    def analyze_context(self, current_memory: str, related_memories: List[Dict]) -> Dict[str, Any]:
        """分析記憶的上下文關聯"""
        context = {
            "temporal_relations": [],
            "entity_relations": [],
            "topic_relations": [],
            "contradiction_check": []
        }
        
        # 提取當前記憶中的實體
        current_entities = self._extract_entities(current_memory)
        
        for memory in related_memories:
            memory_text = memory.get("content", "")
            memory_entities = self._extract_entities(memory_text)
            
            # 檢查實體關聯
            common_entities = set(current_entities) & set(memory_entities)
            if common_entities:
                context["entity_relations"].append({
                    "memory": memory,
                    "common_entities": list(common_entities),
                    "relation_strength": len(common_entities) / max(len(current_entities), len(memory_entities))
                })
            
            # 檢查矛盾
            contradiction = self._check_contradiction(current_memory, memory_text)
            if contradiction:
                context["contradiction_check"].append({
                    "memory": memory,
                    "contradiction_type": contradiction
                })
        
        return context
    
    def _extract_entities(self, text: str) -> List[str]:
        """簡單的實體提取（可以用更複雜的 NER 替換）"""
        # 提取人名、地名、組織名等
        entities = []
        
        # 簡單的人名模式
        name_patterns = [
            r'[A-Z][a-z]+\s+[A-Z][a-z]+',  # 英文姓名
            r'[\u4e00-\u9fff]{2,4}',        # 中文姓名
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        return list(set(entities))
    
    def _check_contradiction(self, text1: str, text2: str) -> Optional[str]:
        """檢查兩段文本是否存在矛盾"""
        # 簡單的矛盾檢查邏輯
        contradiction_patterns = [
            (r"喜歡.*", r"不喜歡.*"),
            (r"是.*", r"不是.*"),
            (r"有.*", r"沒有.*"),
        ]
        
        for positive_pattern, negative_pattern in contradiction_patterns:
            if re.search(positive_pattern, text1) and re.search(negative_pattern, text2):
                return "preference_contradiction"
            if re.search(negative_pattern, text1) and re.search(positive_pattern, text2):
                return "preference_contradiction"
        
        return None

class MemoryPriorityManager:
    """記憶優先級管理器，管理記憶的重要性和保留策略"""
    
    def calculate_priority(self, memory: Dict[str, Any], classification: Dict[str, Any], 
                          context: Dict[str, Any]) -> float:
        """計算記憶的優先級分數"""
        priority = 0.5  # 基礎分數
        
        # 基於分類的優先級
        importance = classification.get("importance", 0.5)
        priority += importance * 0.3
        
        # 基於類型的優先級
        primary_type = classification.get("primary_type", "general")
        type_weights = {
            "personal_info": 0.9,
            "health": 0.9,
            "decisions": 0.8,
            "relationships": 0.7,
            "work": 0.6,
            "preferences": 0.5,
            "general": 0.3
        }
        priority += type_weights.get(primary_type, 0.3) * 0.2
        
        # 基於關聯性的優先級
        entity_relations = context.get("entity_relations", [])
        if entity_relations:
            avg_relation_strength = sum(r["relation_strength"] for r in entity_relations) / len(entity_relations)
            priority += avg_relation_strength * 0.2
        
        # 矛盾檢查（降低優先級）
        contradictions = context.get("contradiction_check", [])
        if contradictions:
            priority -= len(contradictions) * 0.1
        
        # 時間衰減（較舊的記憶優先級略微降低）
        timestamp = memory.get("timestamp")
        if timestamp:
            try:
                memory_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                days_old = (datetime.now() - memory_time.replace(tzinfo=None)).days
                time_decay = max(0, 1 - (days_old / 365))  # 一年後完全衰減
                priority *= (0.8 + 0.2 * time_decay)
            except:
                pass
        
        return min(max(priority, 0.0), 1.0)  # 限制在 0-1 範圍內

class SmartMemoryRetrieval:
    """智能記憶檢索器，提供更智能的記憶檢索策略"""
    
    def __init__(self):
        self.classifier = MemoryClassifier()
        self.context_analyzer = MemoryContextAnalyzer()
        self.priority_manager = MemoryPriorityManager()
    
    def enhanced_search(self, query: str, all_results: List[Dict], 
                       user_context: Dict = None) -> List[Dict]:
        """增強的記憶搜索，考慮上下文和優先級"""
        enhanced_results = []
        
        for result in all_results:
            # 分類記憶
            classification = self.classifier.classify_memory(
                result.get("content", ""), 
                result.get("metadata", {}).get("speaker", "")
            )
            
            # 分析上下文
            context = self.context_analyzer.analyze_context(
                query, [r for r in all_results if r != result]
            )
            
            # 計算優先級
            priority = self.priority_manager.calculate_priority(
                result, classification, context
            )
            
            # 增強結果
            enhanced_result = result.copy()
            enhanced_result.update({
                "classification": classification,
                "context_analysis": context,
                "priority_score": priority,
                "enhanced_score": result.get("score", 0.0) * (1 + priority)
            })
            
            enhanced_results.append(enhanced_result)
        
        # 按增強分數排序
        enhanced_results.sort(key=lambda x: x["enhanced_score"], reverse=True)
        
        return enhanced_results

def create_memory_summary(memories: List[Dict]) -> str:
    """創建記憶摘要"""
    if not memories:
        return "沒有找到相關記憶。"
    
    summary = "記憶摘要：\n\n"
    
    # 按類型分組
    by_type = {}
    for memory in memories:
        classification = memory.get("classification", {})
        primary_type = classification.get("primary_type", "general")
        
        if primary_type not in by_type:
            by_type[primary_type] = []
        by_type[primary_type].append(memory)
    
    # 生成摘要
    type_names = {
        "personal_info": "個人信息",
        "health": "健康相關",
        "relationships": "人際關係",
        "work": "工作相關",
        "preferences": "個人偏好",
        "decisions": "決策記錄",
        "general": "一般信息"
    }
    
    for memory_type, type_memories in by_type.items():
        type_name = type_names.get(memory_type, memory_type)
        summary += f"## {type_name} ({len(type_memories)} 條記錄)\n"
        
        for memory in type_memories[:3]:  # 只顯示前3條
            content = memory.get("content", "")[:100]
            priority = memory.get("priority_score", 0.0)
            summary += f"- {content}... (重要性: {priority:.2f})\n"
        
        if len(type_memories) > 3:
            summary += f"- ... 還有 {len(type_memories) - 3} 條記錄\n"
        
        summary += "\n"
    
    return summary


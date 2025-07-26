from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import sys
import os

from src.services.api_key_manager import api_key_manager

# 添加主項目路徑以便導入 AI 秘書模組
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from main import AISecretary


chat_bp = Blueprint('chat', __name__)

def get_ai_secretary(model, api_key):
    """獲取或創建 AI 秘書實例"""
    # 每次都創建新實例以確保使用最新配置
    return AISecretary(model, api_key)

@chat_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    """處理聊天請求"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': '缺少消息內容'}), 400
        
        user_message = data['message']
        model = data.get('model', 'gemini-2.5-pro')

        try:
            api_key = api_key_manager.get_key(model)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
         
          
        secretary = get_ai_secretary(model, api_key)
        
        # 獲取 AI 回覆
        ai_response = secretary.chat(user_message)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'user_message': user_message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'處理請求時發生錯誤：{str(e)}'
        }), 500

@chat_bp.route('/health', methods=['GET'])
@cross_origin()
def health():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI 秘書服務正常運行'
    })

@chat_bp.route('/key-info', methods=['GET'])
def key_info():
    """获取各模型的密钥信息"""
    models = ['gemini-2.5-pro', 'gemini-2.5-flash']
    info = {
        model: {
            'key_count': api_key_manager.get_key_count(model),
            'strategy': api_key_manager.strategy
        } for model in models
    }
    return jsonify(info)

@chat_bp.route('/health')
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'key_manager': 'active',
        'models': {
            'gemini-2.5-pro': api_key_manager.get_key_count('gemini-2.5-pro') > 0,
            'gemini-2.5-flash': api_key_manager.get_key_count('gemini-2.5-flash') > 0,
        }
    })

// components/ModelSelector.jsx
import React, { useState, useEffect } from 'react';

const ModelSelector = ({ onModelChange }) => {
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-pro');
  const [customApiKey, setCustomApiKey] = useState('');
  const [keyInfo, setKeyInfo] = useState({});
  
  // 获取后端密钥信息
  useEffect(() => {
    const fetchKeyInfo = async () => {
      try {
        const response = await fetch('/api/key-info');
        const data = await response.json();
        setKeyInfo(data);
      } catch (error) {
        console.error('Failed to fetch key info:', error);
      }
    };
    
    fetchKeyInfo();
  }, []);

  const handleModelChange = (e) => {
    const model = e.target.value;
    setSelectedModel(model);
    onModelChange(model, customApiKey);
  };

  const handleKeyChange = (e) => {
    const key = e.target.value;
    setCustomApiKey(key);
    onModelChange(selectedModel, key);
  };

  // 获取模型密钥数量
  const getKeyCount = (model) => {
    return keyInfo[model]?.key_count || 0;
  };

  // 获取密钥策略名称
  const getStrategyName = () => {
    if (!keyInfo[selectedModel]) return '';
    const strategy = keyInfo[selectedModel].strategy;
    
    const strategyNames = {
      'round-robin': '轮询策略',
      'random': '随机策略',
      'weighted': '权重策略'
    };
    
    return strategyNames[strategy] || strategy;
  };

  return (
    <div className="model-selector">
      <div className="form-group">
        <label htmlFor="model-select">選擇模型:</label>
        <select 
          id="model-select" 
          value={selectedModel} 
          onChange={handleModelChange}
          className="form-control"
        >
          <option value="gemini-2.5-pro">
            Gemini 2.5 Pro ({getKeyCount('gemini-2.5-pro')} keys)
          </option>
          <option value="gemini-2.5-flash">
            Gemini 2.5 Flash ({getKeyCount('gemini-2.5-flash')} keys)
          </option>
        </select>
        
        <div className="key-info">
          <small>
            当前策略: {getStrategyName()} | 
            可用密钥: {getKeyCount(selectedModel)}
          </small>
        </div>
      </div>
    </div>
  );
};

export default ModelSelector; // components/ModelSelector.jsx;
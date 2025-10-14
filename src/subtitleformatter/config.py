"""
Configuration management for SubtitleFormatter.
"""

import os
import yaml
from datetime import datetime
from typing import Dict, Any


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """加载并处理配置
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        处理后的配置字典
    """
    print("正在加载配置...")
    
    # 读取基础配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 处理输出文件路径
    output_file = config['output_file']
    
    # 1. 处理时间戳
    if '{timestamp}' in output_file:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        # 使用 replace 而不是 format，避免处理其他占位符
        output_file = output_file.replace('{timestamp}', timestamp)
    
    # 2. 处理输入文件名
    if '{input_file_basename}' in output_file:
        input_file = config.get('input_file', '')
        # 获取输入文件的基础名称（不含路径和扩展名）
        basename = os.path.splitext(os.path.basename(input_file))[0]
        output_file = output_file.replace('{input_file_basename}', basename)
    
    config['output_file'] = output_file
    
    # 确保所有必要的目录都存在
    # 1. 输出目录
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 2. 临时文件目录（如果启用调试）
    debug_config = config.get('debug', {})
    if debug_config.get('enabled', False):
        temp_dir = debug_config.get('temp_dir', 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
    
    return config


def create_config_from_args(args) -> Dict[str, Any]:
    """从命令行参数创建配置
    
    Args:
        args: 命令行参数对象
        
    Returns:
        配置字典
    """
    config = {
        'input_file': args.input_file,
        'output_file': args.output or f"output_{args.input_file}",
        'max_width': args.max_width,
        'language': args.language,
        'model_size': args.model_size,
        'debug': {
            'enabled': args.debug,
            'temp_dir': 'data/debug'
        }
    }
    
    # 确保输出目录存在
    output_dir = os.path.dirname(config['output_file'])
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 确保调试目录存在
    if config['debug']['enabled']:
        debug_dir = config['debug']['temp_dir']
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
    
    return config

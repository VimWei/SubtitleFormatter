import os
import yaml
from datetime import datetime
from modules.debug_output import DebugOutput
from modules.model_manager import ModelManager
from modules.text_cleaner import TextCleaner
from modules.sentence_handler import SentenceHandler
from modules.filler_remover import FillerRemover
from modules.line_breaker import LineBreaker

def load_config():
    """加载并处理配置"""
    print("正在加载配置...")
    config_path = 'config.yaml'
    
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

def process_file(config):
    """处理文件的核心函数"""
    # 初始化处理环境
    print("\n正在初始化处理环境...")
    
    # 1. 创建调试输出器
    debug_config = config.get('debug', {})
    config['debug_output'] = DebugOutput(
        debug=debug_config.get('enabled', False),
        temp_dir=debug_config.get('temp_dir', 'temp'),
        max_width=config['max_width']
    )
    debug_output = config['debug_output']
    
    # 2. 加载语言模型
    print("正在加载语言模型...")
    config['nlp'] = ModelManager.get_model(config)
    
    # 开始文件处理流程
    print("\n开始处理文件...")
    
    # 读取输入文件
    input_file = config['input_file']
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    # 传入文件名信息
    debug_output.show_step("读入文件", text, {'input_file': input_file})

    # 1. 基础文本清理
    print("\n正在进行文本清理...")
    cleaner = TextCleaner()
    cleaned_text, clean_stats = cleaner.process(text)
    debug_output.show_step("文本清理", cleaned_text, clean_stats)

    # 2. 智能断句
    print("\n正在进行智能断句...")
    sentence_handler = SentenceHandler(config)
    sentences = sentence_handler.process(cleaned_text)
    debug_output.show_step("智能断句", sentences)

    # 3. 停顿词处理
    print("\n正在处理停顿词...")
    filler_remover = FillerRemover(config)
    processed_sentences, filler_stats = filler_remover.process(sentences)
    debug_output.show_step("停顿词处理", processed_sentences, filler_stats)

    # 4. 智能断行
    print("\n正在进行智能断行...")
    line_breaker = LineBreaker(config)
    final_text = line_breaker.process(processed_sentences)
    debug_output.show_step("智能断行", final_text)

    # 保存结果
    print(f"\n正在保存结果到文件: {config['output_file']}")
    with open(config['output_file'], 'w', encoding='utf-8') as f:
        f.write(final_text)

    # 添加这一行来保存日志
    debug_output.save_log()

    print(f"\n处理完成！输出文件：{config['output_file']}")

def main():
    # 加载配置
    config = load_config()
    
    # 处理文件
    process_file(config)

if __name__ == '__main__':
    main() 
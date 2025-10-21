#!/usr/bin/env python3
"""
SubtitleFormatter Scripts Manager
统一管理所有独立脚本
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional


class ScriptsManager:
    """脚本管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.scripts_dir = self.project_root / "scripts"
        self.scripts_registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """加载脚本注册表"""
        return {
        "text-diff": {
            "path": "text_diff/main.py",
            "description": "文本差异检测工具 - 比较两个文本文件，识别词汇差异",
            "dependency_group": "diff",
            "usage": "scripts_manager.py text-diff <old_file> <new_file> [options]",
            "examples": [
                "scripts_manager.py text-diff old.txt new.txt",
                "scripts_manager.py text-diff old.txt new.txt --json --html",
                "scripts_manager.py text-diff old.txt new.txt --output result.json"
            ],
            "category": "text_processing"
        },
        "clean-vtt": {
            "path": "clean_vtt.py",
            "description": "VTT文件清理工具 - 清理和格式化VTT字幕文件",
            "dependency_group": "clean-vtt",
            "usage": "scripts_manager.py clean-vtt <input_file> [options]",
            "examples": [
                "scripts_manager.py clean-vtt input.vtt"
            ],
            "category": "converter"
        },
        "transcript-converter": {
            "path": "transcript_converter/transcript_converter.py",
            "description": "字幕格式转换工具 - 将非标准格式转换为SRT格式",
            "dependency_group": None,  # 无外部依赖
            "usage": "scripts_manager.py transcript-converter <input_file>",
            "examples": [
                "scripts_manager.py transcript-converter input.transcript"
            ],
            "category": "converter"
        },
        "srt-resegment": {
            "path": "srt_resegment_by_json.py",
            "description": "SRT重分段工具 - 基于JSON时间戳重新分段SRT文件",
            "dependency_group": None,  # 无外部依赖
            "usage": "scripts_manager.py srt-resegment <json_file> <srt_file>",
            "examples": [
                "scripts_manager.py srt-resegment timestamps.json input.srt"
            ],
            "category": "converter"
        },
        "release": {
            "path": "release.py",
            "description": "版本发布工具 - 自动化版本发布流程",
            "dependency_group": "release",
            "usage": "scripts_manager.py release [bump_type]",
            "examples": [
                "scripts_manager.py release patch",
                "scripts_manager.py release minor"
            ],
            "category": "dev_tools"
        }
        }
    
    def list_scripts(self, category: Optional[str] = None):
        """列出所有可用脚本"""
        print("SubtitleFormatter 脚本工具")
        print("=" * 50)
        
        scripts = self.scripts_registry
        if category:
            scripts = {k: v for k, v in scripts.items() if v.get('category') == category}
        
        if not scripts:
            print(f"没有找到类别为 '{category}' 的脚本")
            return
        
        for script_name, info in scripts.items():
            print(f"\n📁 {script_name}")
            print(f"   描述: {info['description']}")
            print(f"   用法: {info['usage']}")
            if info.get('examples'):
                print("   示例:")
                for example in info['examples']:
                    print(f"     {example}")
        
        print(f"\n总计: {len(scripts)} 个脚本")
    
    def show_help(self, script_name: str):
        """显示脚本帮助信息"""
        if script_name not in self.scripts_registry:
            print(f"错误：脚本 '{script_name}' 不存在")
            self.list_scripts()
            return
        
        info = self.scripts_registry[script_name]
        script_path = self.scripts_dir / info['path']
        
        if not script_path.exists():
            print(f"错误：脚本文件不存在: {script_path}")
            return
        
        print(f"脚本帮助: {script_name}")
        print("=" * 50)
        print(f"描述: {info['description']}")
        print(f"用法: {info['usage']}")
        
        if info.get('examples'):
            print("\n示例:")
            for example in info['examples']:
                print(f"  {example}")
        
        # 添加路径说明
        print(f"\n📁 路径说明:")
        print(f"  • 输入文件: 默认从 data/input/ 目录读取")
        print(f"  • 输出文件: 默认保存到 data/output/ 目录")
        print(f"  • 只需提供文件名，无需完整路径")
        print(f"  • 例如: scripts_manager.py diff old.txt new.txt")
        
        # 尝试运行脚本的 --help 命令
        print(f"\n详细帮助:")
        try:
            subprocess.run([sys.executable, str(script_path), "--help"], 
                         check=True, cwd=self.scripts_dir)
        except subprocess.CalledProcessError:
            print("  该脚本不支持 --help 选项")
        except Exception as e:
            print(f"  运行帮助命令时出错: {e}")
    
    def run_script(self, script_name: str, *args):
        """运行指定脚本"""
        if script_name not in self.scripts_registry:
            print(f"错误：脚本 '{script_name}' 不存在")
            print("\n可用的脚本:")
            self.list_scripts()
            return 1
        
        info = self.scripts_registry[script_name]
        script_path = self.scripts_dir / info['path']
        
        if not script_path.exists():
            print(f"错误：脚本文件不存在: {script_path}")
            return 1
        
        # 检查脚本环境
        if info.get('dependency_group'):
            if not self._ensure_requirements(script_name):
                print("警告：依赖检查失败，但继续运行脚本")
        
        # 处理默认路径
        processed_args = self._process_default_paths(script_name, list(args))
        
        # 运行脚本 - 使用 uv run 来确保在正确的环境中运行
        try:
            # 使用 uv run 来运行脚本，确保在正确的虚拟环境中
            cmd = ["uv", "run", "python", str(script_path)] + processed_args
            print(f"运行命令: {' '.join(cmd)}")
            print(f"💡 提示: 输入文件默认从 data/input/ 读取，输出文件默认保存到 data/output/")
            # 使用项目根目录作为工作目录，这样相对路径能正确解析
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode
        except Exception as e:
            print(f"运行脚本时出错: {e}")
            return 1
    
    def _process_default_paths(self, script_name: str, args: list) -> list:
        """处理默认路径，将文件名转换为完整路径"""
        processed_args = []
        
        # 确保数据目录存在
        input_dir = self.project_root / "data" / "input"
        output_dir = self.project_root / "data" / "output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 特殊处理：为 transcript-converter 自动添加输出目录
        if script_name == "transcript-converter" and len(args) == 1:
            # 如果只有一个参数（输入文件），自动添加输出目录
            # 注意：transcript-converter 期望参数顺序为 [输入文件, 输出目录]
            # 所以先处理输入文件，再添加输出目录
            pass  # 在下面的循环中处理输入文件，然后在这里添加输出目录
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            # 如果是文件参数（不是选项），处理路径
            if not arg.startswith('-'):
                # 检查是否是相对路径（不包含路径分隔符）
                if '/' not in arg and '\\' not in arg:
                    # 检查文件是否在 data/input/ 目录中
                    input_file = input_dir / arg
                    if input_file.exists():
                        processed_args.append(str(input_file))
                        print(f"📁 使用输入文件: {input_file}")
                    else:
                        # 如果不在 data/input/ 中，保持原路径
                        processed_args.append(arg)
                        print(f"📁 使用指定文件: {arg}")
                else:
                    # 已经是完整路径，保持不变
                    processed_args.append(arg)
            else:
                # 处理输出选项
                if arg in ['--output', '-o'] and i + 1 < len(args):
                    output_file = args[i + 1]
                    # 如果输出文件没有路径，放到 data/output/ 中
                    if '/' not in output_file and '\\' not in output_file:
                        output_path = output_dir / output_file
                        processed_args.extend([arg, str(output_path)])
                        print(f"📁 输出文件将保存到: {output_path}")
                        i += 1  # 跳过下一个参数
                    else:
                        processed_args.extend([arg, output_file])
                        i += 1  # 跳过下一个参数
                else:
                    processed_args.append(arg)
            
            i += 1
        
        # 特殊处理：为 transcript-converter 自动添加输出目录
        if script_name == "transcript-converter" and len(args) == 1:
            # 如果只有一个参数（输入文件），自动添加输出目录
            processed_args.append(str(output_dir))
            print(f"📁 输出文件将保存到: {output_dir}")
        
        return processed_args
    
    def _ensure_requirements(self, script_name: str) -> bool:
        """确保脚本依赖已安装"""
        if script_name not in self.scripts_registry:
            return True
        
        info = self.scripts_registry[script_name]
        dependency_group = info.get('dependency_group')
        
        if not dependency_group:
            print(f"脚本 '{script_name}' 无外部依赖")
            return True
        
        try:
            # 使用 uv 来安装依赖组
            print(f"使用 uv 安装脚本依赖组: {dependency_group}")
            result = subprocess.run(
                ["uv", "pip", "install", "--group", dependency_group], 
                check=True, 
                capture_output=True,
                text=True
            )
            print(f"脚本依赖组 '{dependency_group}' 安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"uv 安装依赖失败: {e}")
            if e.stderr:
                print(f"错误信息: {e.stderr}")
            return False
        except Exception as e:
            print(f"检查依赖时出错: {e}")
            return False
    
    def install_script(self, script_name: str):
        """安装脚本依赖"""
        if script_name not in self.scripts_registry:
            print(f"错误：脚本 '{script_name}' 不存在")
            return 1
        
        info = self.scripts_registry[script_name]
        dependency_group = info.get('dependency_group')
        
        if not dependency_group:
            print(f"脚本 '{script_name}' 无外部依赖")
            return 0
        
        try:
            print(f"使用 uv 安装脚本 '{script_name}' 的依赖组 '{dependency_group}'...")
            result = subprocess.run(
                ["uv", "pip", "install", "--group", dependency_group], 
                check=True,
                capture_output=True,
                text=True
            )
            print(f"脚本 '{script_name}' 依赖安装完成")
            return 0
        except subprocess.CalledProcessError as e:
            print(f"uv 安装依赖失败: {e}")
            if e.stderr:
                print(f"错误信息: {e.stderr}")
            return 1
        except Exception as e:
            print(f"安装依赖时出错: {e}")
            return 1
    
    def show_categories(self):
        """显示脚本分类"""
        categories = {}
        for script_name, info in self.scripts_registry.items():
            category = info.get('category', 'other')
            if category not in categories:
                categories[category] = []
            categories[category].append(script_name)
        
        print("脚本分类:")
        print("=" * 30)
        for category, scripts in categories.items():
            print(f"\n📂 {category} ({len(scripts)} 个脚本)")
            for script in scripts:
                print(f"  - {script}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("SubtitleFormatter Scripts Manager")
        print("用法: scripts_manager.py <command> [args...]")
        print("\n命令:")
        print("  list                   列出所有脚本")
        print("  list <category>        列出指定分类的脚本")
        print("  help <script_name>     显示脚本帮助")
        print("  run <script_name>      运行脚本")
        print("  install <script_name>  安装脚本依赖")
        print("  categories             显示脚本分类")
        print("\n示例:")
        print("  scripts_manager.py list")
        print("  scripts_manager.py diff Old.txt New.txt")
        print("  scripts_manager.py help diff")
        sys.exit(1)
    
    manager = ScriptsManager()
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == "list":
        category = args[0] if args else None
        manager.list_scripts(category)
    elif command == "help":
        if not args:
            print("错误：请指定脚本名称")
            sys.exit(1)
        manager.show_help(args[0])
    elif command == "run":
        if not args:
            print("错误：请指定脚本名称")
            sys.exit(1)
        script_name = args[0]
        script_args = args[1:]
        exit_code = manager.run_script(script_name, *script_args)
        sys.exit(exit_code)
    elif command == "install":
        if not args:
            print("错误：请指定脚本名称")
            sys.exit(1)
        exit_code = manager.install_script(args[0])
        sys.exit(exit_code)
    elif command == "categories":
        manager.show_categories()
    else:
        # 如果没有匹配的命令，尝试直接运行脚本
        exit_code = manager.run_script(command, *args)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()

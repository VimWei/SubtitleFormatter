#!/usr/bin/env python3
"""
插件测试运行脚本

用于运行第三阶段开发的所有插件测试：
- 单个插件测试
- 集成测试
- 性能测试
- 覆盖率测试
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_tests(test_path=None, verbose=False, coverage=False, parallel=False):
    """
    运行测试
    
    Args:
        test_path: 测试路径，如果为None则运行所有测试
        verbose: 是否显示详细输出
        coverage: 是否生成覆盖率报告
        parallel: 是否并行运行测试
    """
    # 构建pytest命令
    cmd = ["uv", "run", "pytest"]
    
    if verbose:
        cmd.append("-v")
    
    if parallel:
        cmd.extend(["-n", "auto"])
    
    if coverage:
        # 注意：需要安装 pytest-cov 插件才能使用覆盖率功能
        # pip install pytest-cov
        cmd.extend([
            "--cov=plugins.builtin",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/plugins/builtin")
        cmd.append("tests/plugins/integration")
    
    print(f"运行命令: {' '.join(cmd)}")
    print("=" * 60)
    
    # 运行测试
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        print("\n" + "=" * 60)
        print("所有测试通过！")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"测试失败，退出码: {e.returncode}")
        return False


def run_individual_plugin_tests():
    """运行单个插件测试"""
    plugins = [
        "text_cleaning",
        "punctuation_adder", 
        "text_to_sentences",
        "sentence_splitter"
    ]
    
    print("运行单个插件测试...")
    print("=" * 60)
    
    all_passed = True
    for plugin in plugins:
        print(f"\n测试 {plugin} 插件...")
        test_path = f"tests/plugins/builtin/{plugin}/test_plugin.py"
        if not run_tests(test_path, verbose=True):
            all_passed = False
    
    return all_passed


def run_integration_tests():
    """运行集成测试"""
    print("\n运行集成测试...")
    print("=" * 60)
    return run_tests("tests/plugins/integration", verbose=True)


def run_all_tests():
    """运行所有测试"""
    print("运行所有插件测试...")
    print("=" * 60)
    return run_tests(verbose=True, coverage=False)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="运行插件测试")
    parser.add_argument(
        "--plugin", 
        choices=["text_cleaning", "punctuation_adder", "text_to_sentences", "sentence_splitter"],
        help="运行指定插件的测试"
    )
    parser.add_argument(
        "--integration", 
        action="store_true",
        help="运行集成测试"
    )
    parser.add_argument(
        "--all", 
        action="store_true",
        help="运行所有测试"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="生成覆盖率报告"
    )
    parser.add_argument(
        "--parallel", 
        action="store_true",
        help="并行运行测试"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="显示详细输出"
    )
    
    args = parser.parse_args()
    
    # 如果没有指定任何选项，默认运行所有测试
    if not any([args.plugin, args.integration, args.all]):
        args.all = True
    
    success = True
    
    if args.plugin:
        test_path = f"tests/plugins/builtin/{args.plugin}/test_plugin.py"
        success = run_tests(test_path, verbose=args.verbose, coverage=args.coverage, parallel=args.parallel)
    elif args.integration:
        success = run_integration_tests()
    elif args.all:
        success = run_all_tests()
    
    if success:
        print("\n测试完成！")
        sys.exit(0)
    else:
        print("\n测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()

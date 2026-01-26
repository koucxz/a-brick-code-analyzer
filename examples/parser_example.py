"""
AST 解析器使用示例
"""

from a_brick_code_analyzer import PythonParser, ParserFactory


def example_basic_usage():
    """基础使用示例"""
    print("=" * 50)
    print("示例 1: 基础使用")
    print("=" * 50)

    # 创建解析器
    parser = PythonParser()

    # 解析代码字符串
    code = '''
def calculate_sum(numbers):
    """计算数字列表的总和"""
    total = 0
    for num in numbers:
        if num > 0:
            total += num
    return total

class Calculator:
    """简单计算器类"""

    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b
'''

    result = parser.parse(code)

    print(f"语言: {result.language}")
    print(f"总行数: {result.total_lines}")
    print(f"代码行数: {result.code_lines}")
    print(f"注释行数: {result.comment_lines}")
    print(f"空白行数: {result.blank_lines}")
    print(f"\n发现 {len(result.nodes)} 个代码节点:")

    for node in result.nodes:
        print(f"  - {node.node_type.value}: {node.name} "
              f"(行 {node.line_start}-{node.line_end}, 复杂度: {node.complexity})")
        if node.params:
            print(f"    参数: {', '.join(node.params)}")
        if node.docstring:
            print(f"    文档: {node.docstring}")


def example_parse_file():
    """解析文件示例"""
    print("\n" + "=" * 50)
    print("示例 2: 解析文件")
    print("=" * 50)

    parser = PythonParser()

    # 解析当前示例文件
    result = parser.parse_file(__file__)

    print(f"文件: {result.file_path}")
    print(f"函数数量: {len(result.get_functions())}")
    print(f"类数量: {len(result.get_classes())}")

    print("\n函数列表:")
    for func in result.get_functions():
        print(f"  - {func.name}() [复杂度: {func.complexity}]")


def example_factory_usage():
    """使用工厂模式示例"""
    print("\n" + "=" * 50)
    print("示例 3: 使用解析器工厂")
    print("=" * 50)

    # 根据文件扩展名自动选择解析器
    parser = ParserFactory.get_parser_by_file("example.py")

    if parser:
        print(f"自动选择的解析器: {parser.__class__.__name__}")
        print(f"支持的扩展名: {parser.get_supported_extensions()}")

    # 查看所有支持的语言
    print(f"\n支持的语言: {ParserFactory.get_supported_languages()}")
    print(f"支持的扩展名: {ParserFactory.get_supported_extensions()}")


def example_complexity_analysis():
    """复杂度分析示例"""
    print("\n" + "=" * 50)
    print("示例 4: 复杂度分析")
    print("=" * 50)

    parser = PythonParser()

    # 高复杂度函数
    complex_code = '''
def process_data(data, mode):
    """处理数据的复杂函数"""
    result = []

    if mode == "filter":
        for item in data:
            if item > 0:
                if item % 2 == 0:
                    result.append(item * 2)
                else:
                    result.append(item)
    elif mode == "transform":
        for item in data:
            try:
                result.append(transform(item))
            except ValueError:
                continue
    else:
        result = data

    return result
'''

    result = parser.parse(complex_code)
    func = result.nodes[0]

    print(f"函数: {func.name}")
    print(f"圈复杂度: {func.complexity}")
    print(f"行数: {func.line_end - func.line_start + 1}")

    if func.complexity > 10:
        print("[WARNING] 函数复杂度过高，建议重构")
    elif func.complexity > 5:
        print("[INFO] 函数复杂度较高，考虑简化")
    else:
        print("[OK] 函数复杂度合理")


def example_import_analysis():
    """导入分析示例"""
    print("\n" + "=" * 50)
    print("示例 5: 导入分析")
    print("=" * 50)

    parser = PythonParser()

    code = '''
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict
'''

    result = parser.parse(code)

    print(f"发现 {len(result.imports)} 个导入:")
    for imp in result.imports:
        print(f"  - {imp}")


if __name__ == "__main__":
    # 运行所有示例
    example_basic_usage()
    example_parse_file()
    example_factory_usage()
    example_complexity_analysis()
    example_import_analysis()

    print("\n" + "=" * 50)
    print("所有示例运行完成!")
    print("=" * 50)

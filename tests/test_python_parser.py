"""
测试 Python 解析器
"""

import unittest
from a_brick_code_analyzer import PythonParser, NodeType


class TestPythonParser(unittest.TestCase):
    """测试 Python 解析器"""

    def setUp(self):
        """初始化测试"""
        self.parser = PythonParser()

    def test_parse_simple_function(self):
        """测试解析简单函数"""
        code = '''
def hello(name):
    """Say hello"""
    return f"Hello, {name}!"
'''
        result = self.parser.parse(code)

        self.assertEqual(result.language, "python")
        self.assertEqual(len(result.nodes), 1)

        func = result.nodes[0]
        self.assertEqual(func.node_type, NodeType.FUNCTION)
        self.assertEqual(func.name, "hello")
        self.assertEqual(func.params, ["name"])
        self.assertEqual(func.docstring, "Say hello")
        self.assertGreater(func.complexity, 0)

    def test_parse_class(self):
        """测试解析类"""
        code = '''
class Calculator:
    """A simple calculator"""

    def add(self, a, b):
        """Add two numbers"""
        return a + b

    def subtract(self, a, b):
        """Subtract two numbers"""
        return a - b
'''
        result = self.parser.parse(code)

        # 应该有 1 个类和 2 个方法
        classes = result.get_classes()
        methods = result.get_methods()

        self.assertEqual(len(classes), 1)
        self.assertEqual(len(methods), 2)

        calc_class = classes[0]
        self.assertEqual(calc_class.name, "Calculator")
        self.assertEqual(calc_class.docstring, "A simple calculator")

    def test_parse_decorators(self):
        """测试解析装饰器"""
        code = '''
@staticmethod
@cache
def compute(x):
    return x * 2
'''
        result = self.parser.parse(code)

        func = result.nodes[0]
        self.assertEqual(len(func.decorators), 2)
        self.assertIn("staticmethod", func.decorators)
        self.assertIn("cache", func.decorators)

    def test_parse_imports(self):
        """测试解析导入语句"""
        code = '''
import os
import sys
from pathlib import Path
from typing import List, Dict
'''
        result = self.parser.parse(code)

        self.assertIn("os", result.imports)
        self.assertIn("sys", result.imports)
        self.assertIn("pathlib.Path", result.imports)
        self.assertIn("typing.List", result.imports)
        self.assertIn("typing.Dict", result.imports)

    def test_complexity_calculation(self):
        """测试复杂度计算"""
        code = '''
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
    elif x < 0:
        while x < 0:
            x += 1
    return x
'''
        result = self.parser.parse(code)

        func = result.nodes[0]
        # 应该有较高的复杂度（多个分支）
        self.assertGreater(func.complexity, 3)

    def test_line_counting(self):
        """测试行数统计"""
        code = '''# This is a comment
import os

def hello():
    """Docstring"""
    pass

# Another comment
'''
        result = self.parser.parse(code)

        self.assertGreater(result.total_lines, 0)
        self.assertGreater(result.comment_lines, 0)
        self.assertGreater(result.blank_lines, 0)
        self.assertGreater(result.code_lines, 0)

    def test_syntax_error_handling(self):
        """测试语法错误处理"""
        code = '''
def broken_function(
    # 缺少闭合括号
'''
        result = self.parser.parse(code)

        self.assertTrue(len(result.errors) > 0)
        self.assertIn("语法错误", result.errors[0])

    def test_async_function(self):
        """测试异步函数"""
        code = '''
async def fetch_data(url):
    """Fetch data asynchronously"""
    return await get(url)
'''
        result = self.parser.parse(code)

        func = result.nodes[0]
        self.assertEqual(func.name, "fetch_data")
        self.assertTrue(func.metadata.get('is_async'))


if __name__ == '__main__':
    unittest.main()

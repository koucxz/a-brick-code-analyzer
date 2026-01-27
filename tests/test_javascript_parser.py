"""
测试 JavaScript/TypeScript 解析器
"""

import unittest
from unittest.mock import patch
from a_brick_code_analyzer import ParserFactory


class TestJavaScriptParser(unittest.TestCase):
    """测试 JavaScript 解析器"""

    def setUp(self):
        """初始化测试"""
        # 检查是否支持 JavaScript
        self.js_supported = '.js' in ParserFactory.get_supported_extensions()
        if self.js_supported:
            self.parser = ParserFactory.get_parser('javascript')
        else:
            self.parser = None

    @unittest.skipUnless(lambda self: self.js_supported, "JavaScript support not available")
    def test_parse_simple_function(self):
        """测试解析简单函数"""
        code = '''
function hello(name) {
    // Say hello
    return `Hello, ${name}!`;
}
'''
        result = self.parser.parse(code)

        self.assertEqual(result.language, "javascript")
        self.assertEqual(len(result.nodes), 1)

        func = result.nodes[0]
        self.assertEqual(func.name, "hello")
        self.assertEqual(func.params, ["name"])
        self.assertGreater(func.complexity, 0)

    @unittest.skipUnless(lambda self: self.js_supported, "JavaScript support not available")
    def test_parse_class(self):
        """测试解析类"""
        code = '''
class Calculator {
    // A simple calculator

    add(a, b) {
        // Add two numbers
        return a + b;
    }

    subtract(a, b) {
        // Subtract two numbers
        return a - b;
    }
}
'''
        result = self.parser.parse(code)

        # 应该有 1 个类和 2 个方法
        classes = [node for node in result.nodes if node.node_type.name == 'CLASS']
        methods = [node for node in result.nodes if node.node_type.name == 'METHOD']

        self.assertEqual(len(classes), 1)
        self.assertEqual(len(methods), 2)

        calc_class = classes[0]
        self.assertEqual(calc_class.name, "Calculator")

    @unittest.skipUnless(lambda self: self.js_supported, "JavaScript support not available")
    def test_parse_imports(self):
        """测试解析导入语句"""
        code = '''
import React from 'react';
import { useState, useEffect } from 'react';
import * as utils from './utils';
const fs = require('fs');
'''
        result = self.parser.parse(code)

        # 应该包含导入语句
        self.assertTrue(len(result.imports) > 0)

    @unittest.skipUnless(lambda self: self.js_supported, "JavaScript support not available")
    def test_complexity_calculation(self):
        """测试复杂度计算"""
        code = '''
function complexFunction(x) {
    if (x > 0) {
        for (let i = 0; i < x; i++) {
            if (i % 2 === 0) {
                console.log(i);
            }
        }
    } else if (x < 0) {
        while (x < 0) {
            x++;
        }
    }
    return x;
}
'''
        result = self.parser.parse(code)

        func = result.nodes[0]
        # 应该有较高的复杂度（多个分支）
        self.assertGreater(func.complexity, 3)

    @unittest.skipUnless(lambda self: self.js_supported, "JavaScript support not available")
    def test_line_counting(self):
        """测试行数统计"""
        code = '''// This is a comment
import React from 'react';

function hello() {
    // Docstring equivalent
    return "Hello";
}

// Another comment
'''
        result = self.parser.parse(code)

        self.assertGreater(result.total_lines, 0)
        self.assertGreater(result.comment_lines, 0)
        self.assertGreater(result.blank_lines, 0)
        self.assertGreater(result.code_lines, 0)

    @unittest.skipUnless(lambda self: self.js_supported, "JavaScript support not available")
    def test_syntax_error_handling(self):
        """测试语法错误处理"""
        code = '''
function brokenFunction( {
    // 缺少闭合括号
'''
        result = self.parser.parse(code)

        self.assertTrue(len(result.errors) > 0)


class TestTypeScriptParser(unittest.TestCase):
    """测试 TypeScript 解析器"""

    def setUp(self):
        """初始化测试"""
        # 检查是否支持 TypeScript
        self.ts_supported = '.ts' in ParserFactory.get_supported_extensions()
        if self.ts_supported:
            self.parser = ParserFactory.get_parser('typescript')
        else:
            self.parser = None

    @unittest.skipUnless(lambda self: self.ts_supported, "TypeScript support not available")
    def test_parse_typescript_function(self):
        """测试解析 TypeScript 函数"""
        code = '''
function greet(name: string): string {
    // Say hello with type annotations
    return `Hello, ${name}!`;
}
'''
        result = self.parser.parse(code)

        self.assertEqual(result.language, "typescript")
        self.assertEqual(len(result.nodes), 1)

        func = result.nodes[0]
        self.assertEqual(func.name, "greet")
        self.assertEqual(func.params, ["name"])

    @unittest.skipUnless(lambda self: self.ts_supported, "TypeScript support not available")
    def test_parse_typescript_class(self):
        """测试解析 TypeScript 类"""
        code = '''
class Calculator {
    private result: number = 0;

    add(a: number, b: number): number {
        this.result = a + b;
        return this.result;
    }

    getResult(): number {
        return this.result;
    }
}
'''
        result = self.parser.parse(code)

        # 应该有 1 个类和 2 个方法
        classes = [node for node in result.nodes if node.node_type.name == 'CLASS']
        methods = [node for node in result.nodes if node.node_type.name == 'METHOD']

        self.assertEqual(len(classes), 1)
        self.assertEqual(len(methods), 2)

        calc_class = classes[0]
        self.assertEqual(calc_class.name, "Calculator")

    @unittest.skipUnless(lambda self: self.ts_supported, "TypeScript support not available")
    def test_parse_typescript_imports(self):
        """测试解析 TypeScript 导入语句"""
        code = '''
import { Component, OnInit } from '@angular/core';
import * as _ from 'lodash';
import { Observable } from 'rxjs';
'''
        result = self.parser.parse(code)

        # 应该包含导入语句
        self.assertTrue(len(result.imports) > 0)


if __name__ == '__main__':
    unittest.main()
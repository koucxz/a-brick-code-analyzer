"""
Python 代码解析器
使用 Python 标准库 ast 模块进行解析
"""

import ast
from typing import List
from pathlib import Path

from .base import BaseParser, ParseResult, CodeNode, NodeType


class PythonParser(BaseParser):
    """Python 代码解析器"""

    def __init__(self):
        self.supported_extensions = ['.py']

    def parse(self, code: str, file_path: str = "") -> ParseResult:
        """
        解析 Python 代码

        Args:
            code: Python 源代码字符串
            file_path: 文件路径（可选）

        Returns:
            ParseResult: 解析结果
        """
        result = ParseResult(
            file_path=file_path,
            language="python"
        )

        try:
            # 解析代码为 AST
            tree = ast.parse(code)

            # 统计代码行数
            lines = code.split('\n')
            result.total_lines = len(lines)
            result.blank_lines = sum(1 for line in lines if not line.strip())
            result.comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            result.code_lines = result.total_lines - result.blank_lines - result.comment_lines

            # 提取节点信息
            visitor = PythonASTVisitor()
            visitor.visit(tree)

            result.nodes = visitor.nodes
            result.imports = visitor.imports

        except SyntaxError as e:
            result.errors.append(f"语法错误: {str(e)}")
        except Exception as e:
            result.errors.append(f"解析错误: {str(e)}")

        return result

    def parse_file(self, file_path: str) -> ParseResult:
        """
        解析 Python 文件

        Args:
            file_path: 文件路径

        Returns:
            ParseResult: 解析结果
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.parse(code, file_path)
        except FileNotFoundError:
            result = ParseResult(file_path=file_path, language="python")
            result.errors.append(f"文件不存在: {file_path}")
            return result
        except Exception as e:
            result = ParseResult(file_path=file_path, language="python")
            result.errors.append(f"读取文件错误: {str(e)}")
            return result

    def get_supported_extensions(self) -> List[str]:
        """获取支持的文件扩展名"""
        return self.supported_extensions


class PythonASTVisitor(ast.NodeVisitor):
    """Python AST 访问器，用于提取代码信息"""

    def __init__(self):
        self.nodes: List[CodeNode] = []
        self.imports: List[str] = []
        self.current_class: str = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """访问函数定义"""
        # 判断是函数还是方法
        node_type = NodeType.METHOD if self.current_class else NodeType.FUNCTION

        # 提取参数
        params = [arg.arg for arg in node.args.args]

        # 提取装饰器
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]

        # 提取文档字符串
        docstring = ast.get_docstring(node)

        # 计算圈复杂度
        complexity = self._calculate_complexity(node)

        code_node = CodeNode(
            node_type=node_type,
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            complexity=complexity,
            params=params,
            decorators=decorators,
            docstring=docstring,
            metadata={
                'class': self.current_class,
                'is_async': isinstance(node, ast.AsyncFunctionDef)
            }
        )

        self.nodes.append(code_node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """访问异步函数定义"""
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """访问类定义"""
        # 提取装饰器
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]

        # 提取文档字符串
        docstring = ast.get_docstring(node)

        # 提取基类
        bases = [self._get_name(base) for base in node.bases]

        code_node = CodeNode(
            node_type=NodeType.CLASS,
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            decorators=decorators,
            docstring=docstring,
            metadata={
                'bases': bases
            }
        )

        self.nodes.append(code_node)

        # 进入类作用域
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_Import(self, node: ast.Import):
        """访问 import 语句"""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """访问 from...import 语句"""
        module = node.module or ''
        for alias in node.names:
            import_str = f"{module}.{alias.name}" if module else alias.name
            self.imports.append(import_str)
        self.generic_visit(node)

    def _get_decorator_name(self, decorator) -> str:
        """获取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            return self._get_name(decorator.func)
        elif isinstance(decorator, ast.Attribute):
            return self._get_name(decorator)
        return str(decorator)

    def _get_name(self, node) -> str:
        """获取节点名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_name(node.value)
            return f"{value}.{node.attr}"
        return str(node)

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        计算圈复杂度（McCabe complexity）
        基础复杂度为 1，每个分支点 +1
        """
        complexity = 1

        for child in ast.walk(node):
            # 分支语句
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            # 异常处理
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            # 布尔运算符
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # 列表推导式
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1

        return complexity

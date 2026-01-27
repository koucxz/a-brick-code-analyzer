"""
JavaScript/TypeScript 代码解析器
使用 Tree-sitter 进行解析
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import re

try:
    from tree_sitter import Language, Parser, Query, QueryCursor
    import tree_sitter_javascript as tsjs
    import tree_sitter_typescript as tst
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

from .base import BaseParser, ParseResult, CodeNode, NodeType


class JavaScriptParser(BaseParser):
    """JavaScript 代码解析器"""

    def __init__(self):
        if not TREE_SITTER_AVAILABLE:
            raise ImportError(
                "Tree-sitter is required for JavaScript parsing. "
                "Install with: pip install tree-sitter tree-sitter-javascript"
            )

        self.supported_extensions = ['.js', '.jsx']
        self.js_language = Language(tsjs.language())
        self.parser = Parser(self.js_language)

    def parse(self, code: str, file_path: str = "") -> ParseResult:
        """
        解析 JavaScript 代码

        Args:
            code: 源代码字符串
            file_path: 文件路径（可选）

        Returns:
            ParseResult: 解析结果
        """
        try:
            # 解析代码
            tree = self.parser.parse(bytes(code, "utf8"))
            root_node = tree.root_node

            # 检查是否有语法错误
            errors = []
            if root_node.has_error:
                errors.append("JavaScript syntax error detected")

            # 初始化结果
            nodes = []
            imports = []

            # 提取导入语句
            imports = self._extract_imports(root_node, code)

            # 遍历 AST 提取节点信息
            self._traverse_ast(root_node, code, nodes)

            # 计算行数统计
            total_lines, code_lines, comment_lines, blank_lines = self._count_lines(code)

            return ParseResult(
                file_path=file_path,
                language="javascript",
                nodes=nodes,
                imports=imports,
                total_lines=total_lines,
                code_lines=code_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                errors=errors
            )
        except Exception as e:
            return ParseResult(
                file_path=file_path,
                language="javascript",
                errors=[f"JavaScript parsing error: {str(e)}"]
            )

    def parse_file(self, file_path: str) -> ParseResult:
        """
        解析 JavaScript 文件

        Args:
            file_path: 文件路径

        Returns:
            ParseResult: 解析结果
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.parse(code, file_path)
        except Exception as e:
            return ParseResult(
                file_path=file_path,
                language="javascript",
                errors=[f"File reading error: {str(e)}"]
            )

    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名

        Returns:
            List[str]: 扩展名列表
        """
        return self.supported_extensions

    def _extract_imports(self, root_node, code: str) -> List[str]:
        """提取导入语句"""
        imports = []

        # 确定使用的语言（JavaScript 或 TypeScript）
        language = getattr(self, 'ts_language', self.js_language)

        # 查找 import 语句 - 使用 Query 构造函数和 QueryCursor
        try:
            import_query = Query(language, """
            (import_statement) @import
            """)

            query_cursor = QueryCursor(import_query)
            captures_dict = query_cursor.captures(root_node)

            # captures_dict 是一个字典，键是捕获名，值是节点列表
            for capture_name, nodes in captures_dict.items():
                for node in nodes:
                    if node.type == 'import_statement':
                        import_text = code[node.start_byte:node.end_byte]
                        imports.append(import_text.strip())
        except Exception as e:
            # 如果查询失败，记录错误但继续执行
            pass

        # 查找 require 语句 - 使用 Query 构造函数和 QueryCursor
        try:
            require_query = Query(language, """
            (call_expression
              function: (identifier) @func
              arguments: (arguments (string))
            )
            """)

            query_cursor = QueryCursor(require_query)
            captures_dict = query_cursor.captures(root_node)

            # 检查是否有 func 捕获
            if 'func' in captures_dict:
                for node in captures_dict['func']:
                    func_name = code[node.start_byte:node.end_byte]
                    if func_name == 'require':
                        # 找到对应的 require 调用
                        require_call = node.parent
                        if require_call and require_call.type == 'call_expression':
                            require_text = code[require_call.start_byte:require_call.end_byte]
                            imports.append(require_text.strip())
        except Exception as e:
            # 如果查询失败，记录错误但继续执行
            pass

        return imports

    def _traverse_ast(self, node, code: str, nodes: List[CodeNode]):
        """遍历 AST 提取节点信息"""
        if node.type == 'function_declaration':
            self._handle_function_declaration(node, code, nodes)
        elif node.type == 'method_definition':
            self._handle_method_definition(node, code, nodes)
        elif node.type == 'class_declaration':
            self._handle_class_declaration(node, code, nodes)
        elif node.type == 'variable_declarator':
            self._handle_variable_declarator(node, code, nodes)

        # 递归处理子节点
        for child in node.children:
            self._traverse_ast(child, code, nodes)

    def _handle_function_declaration(self, node, code: str, nodes: List[CodeNode]):
        """处理函数声明"""
        # 获取函数名
        name_node = None
        for child in node.children:
            if child.type == 'identifier':
                name_node = child
                break

        if name_node:
            name = code[name_node.start_byte:name_node.end_byte]
            line_start = name_node.start_point[0] + 1
            line_end = node.end_point[0] + 1

            # 获取参数
            params = self._extract_function_params(node, code)

            # 计算复杂度（简化版）
            complexity = self._calculate_complexity(node, code)

            nodes.append(CodeNode(
                node_type=NodeType.FUNCTION,
                name=name,
                line_start=line_start,
                line_end=line_end,
                complexity=complexity,
                params=params
            ))

    def _handle_method_definition(self, node, code: str, nodes: List[CodeNode]):
        """处理方法定义"""
        # 获取方法名
        name_node = None
        for child in node.children:
            if child.type in ['property_identifier', 'identifier', 'string']:
                name_node = child
                break

        if name_node:
            name = code[name_node.start_byte:name_node.end_byte]
            line_start = name_node.start_point[0] + 1
            line_end = node.end_point[0] + 1

            # 获取参数
            params = self._extract_function_params(node, code)

            # 计算复杂度
            complexity = self._calculate_complexity(node, code)

            nodes.append(CodeNode(
                node_type=NodeType.METHOD,
                name=name,
                line_start=line_start,
                line_end=line_end,
                complexity=complexity,
                params=params
            ))

    def _handle_class_declaration(self, node, code: str, nodes: List[CodeNode]):
        """处理类声明"""
        # 获取类名
        name_node = None
        for child in node.children:
            if child.type in ['identifier', 'type_identifier']:
                name_node = child
                break

        if name_node:
            name = code[name_node.start_byte:name_node.end_byte]
            line_start = name_node.start_point[0] + 1
            line_end = node.end_point[0] + 1

            nodes.append(CodeNode(
                node_type=NodeType.CLASS,
                name=name,
                line_start=line_start,
                line_end=line_end
            ))

    def _handle_variable_declarator(self, node, code: str, nodes: List[CodeNode]):
        """处理变量声明"""
        # 获取变量名
        name_node = node.child_by_field_name('name')
        if name_node:
            name = code[name_node.start_byte:name_node.end_byte]
            line_start = name_node.start_point[0] + 1
            line_end = name_node.end_point[0] + 1

            nodes.append(CodeNode(
                node_type=NodeType.VARIABLE,
                name=name,
                line_start=line_start,
                line_end=line_end
            ))

    def _extract_function_params(self, node, code: str) -> List[str]:
        """提取函数参数"""
        params = []
        parameters_node = node.child_by_field_name('parameters')
        if parameters_node:
            # 遍历参数列表
            for child in parameters_node.children:
                if child.type == 'identifier':
                    # JavaScript 参数
                    param_name = code[child.start_byte:child.end_byte]
                    params.append(param_name)
                elif child.type == 'assignment_pattern':
                    # 处理默认参数 (JavaScript)
                    left = child.child_by_field_name('left')
                    if left and left.type == 'identifier':
                        param_name = code[left.start_byte:left.end_byte]
                        params.append(param_name)
                elif child.type == 'required_parameter':
                    # TypeScript 参数
                    # 在 required_parameter 中查找 identifier
                    for param_child in child.children:
                        if param_child.type == 'identifier':
                            param_name = code[param_child.start_byte:param_child.end_byte]
                            params.append(param_name)
                            break
        return params

    def _calculate_complexity(self, node, code: str) -> int:
        """计算圈复杂度（简化版）"""
        complexity = 1  # 基础复杂度

        # 查找控制流语句
        control_flow_types = [
            'if_statement', 'for_statement', 'while_statement', 'do_statement',
            'switch_statement', 'catch_clause', 'conditional_expression'
        ]

        def count_control_flow(n):
            nonlocal complexity
            if n.type in control_flow_types:
                complexity += 1
            for child in n.children:
                count_control_flow(child)

        count_control_flow(node)
        return complexity

    def _count_lines(self, code: str):
        """计算行数统计"""
        lines = code.split('\n')
        total_lines = len(lines)
        code_lines = 0
        comment_lines = 0
        blank_lines = 0

        in_block_comment = False

        for line in lines:
            stripped = line.strip()

            # 检查块注释开始/结束
            if '/*' in stripped:
                in_block_comment = True
                comment_lines += 1
                continue
            if '*/' in stripped:
                in_block_comment = False
                comment_lines += 1
                continue

            if in_block_comment:
                comment_lines += 1
                continue

            if not stripped:
                blank_lines += 1
            elif stripped.startswith('//'):
                comment_lines += 1
            else:
                code_lines += 1

        return total_lines, code_lines, comment_lines, blank_lines


class TypeScriptParser(JavaScriptParser):
    """TypeScript 代码解析器"""

    def __init__(self):
        if not TREE_SITTER_AVAILABLE:
            raise ImportError(
                "Tree-sitter is required for TypeScript parsing. "
                "Install with: pip install tree-sitter tree-sitter-typescript"
            )

        self.supported_extensions = ['.ts', '.tsx']
        self.ts_language = Language(tst.language_typescript())
        self.js_language = self.ts_language  # 兼容父类方法
        self.parser = Parser(self.ts_language)

    def parse(self, code: str, file_path: str = "") -> ParseResult:
        """
        解析 TypeScript 代码

        Args:
            code: 源代码字符串
            file_path: 文件路径（可选）

        Returns:
            ParseResult: 解析结果
        """
        try:
            # 解析代码
            tree = self.parser.parse(bytes(code, "utf8"))
            root_node = tree.root_node

            # 检查是否有语法错误
            errors = []
            if root_node.has_error:
                errors.append("TypeScript syntax error detected")

            # 初始化结果
            nodes = []
            imports = []

            # 提取导入语句
            imports = self._extract_imports(root_node, code)

            # 遍历 AST 提取节点信息
            self._traverse_ast(root_node, code, nodes)

            # 计算行数统计
            total_lines, code_lines, comment_lines, blank_lines = self._count_lines(code)

            return ParseResult(
                file_path=file_path,
                language="typescript",
                nodes=nodes,
                imports=imports,
                total_lines=total_lines,
                code_lines=code_lines,
                comment_lines=comment_lines,
                blank_lines=blank_lines,
                errors=errors
            )
        except Exception as e:
            return ParseResult(
                file_path=file_path,
                language="typescript",
                errors=[f"TypeScript parsing error: {str(e)}"]
            )

    def parse_file(self, file_path: str) -> ParseResult:
        """
        解析 TypeScript 文件

        Args:
            file_path: 文件路径

        Returns:
            ParseResult: 解析结果
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.parse(code, file_path)
        except Exception as e:
            return ParseResult(
                file_path=file_path,
                language="typescript",
                errors=[f"File reading error: {str(e)}"]
            )

    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名

        Returns:
            List[str]: 扩展名列表
        """
        return self.supported_extensions
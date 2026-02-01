"""
命名规范规则
"""

import re
from typing import List

from ..base import NodeRule, RuleViolation, Severity
from ...base import CodeNode, ParseResult, NodeType


class FunctionNamingRule(NodeRule):
    """检查函数命名规范"""

    rule_id = "naming/function-naming"
    name = "函数命名规范"
    description = "强制函数遵循命名规范"
    category = "naming"
    default_severity = Severity.WARN
    default_options = {"style": "snake_case"}
    target_node_types = [NodeType.FUNCTION, NodeType.METHOD]

    PATTERNS = {
        'snake_case': r'^[a-z_][a-z0-9_]*$',
        'camelCase': r'^[a-z][a-zA-Z0-9]*$',
        'PascalCase': r'^[A-Z][a-zA-Z0-9]*$',
    }

    # 忽略的特殊方法（Python dunder 方法）
    IGNORE_PATTERNS = [r'^__.*__$']

    def check_node(self, node: CodeNode, parse_result: ParseResult) -> List[RuleViolation]:
        violations = []
        style = self.options.get('style', 'snake_case')
        pattern = self.PATTERNS.get(style)

        if not pattern:
            return violations

        # 跳过特殊方法
        for ignore_pattern in self.IGNORE_PATTERNS:
            if re.match(ignore_pattern, node.name):
                return violations

        if not re.match(pattern, node.name):
            violations.append(self.create_violation(
                message=f"函数 '{node.name}' 不符合 {style} 命名规范",
                file_path=parse_result.file_path,
                line_start=node.line_start,
                line_end=node.line_end,
                node_name=node.name,
                node_type=node.node_type.value,
                suggestion=f"重命名以符合 {style} 规范",
                metadata={'style': style, 'pattern': pattern}
            ))

        return violations


class ClassNamingRule(NodeRule):
    """检查类命名规范"""

    rule_id = "naming/class-naming"
    name = "类命名规范"
    description = "强制类遵循命名规范"
    category = "naming"
    default_severity = Severity.WARN
    default_options = {"style": "PascalCase"}
    target_node_types = [NodeType.CLASS]

    PATTERNS = {
        'snake_case': r'^[a-z_][a-z0-9_]*$',
        'camelCase': r'^[a-z][a-zA-Z0-9]*$',
        'PascalCase': r'^[A-Z][a-zA-Z0-9]*$',
    }

    def check_node(self, node: CodeNode, parse_result: ParseResult) -> List[RuleViolation]:
        violations = []
        style = self.options.get('style', 'PascalCase')
        pattern = self.PATTERNS.get(style)

        if not pattern:
            return violations

        if not re.match(pattern, node.name):
            violations.append(self.create_violation(
                message=f"类 '{node.name}' 不符合 {style} 命名规范",
                file_path=parse_result.file_path,
                line_start=node.line_start,
                line_end=node.line_end,
                node_name=node.name,
                node_type=node.node_type.value,
                suggestion=f"重命名以符合 {style} 规范",
                metadata={'style': style, 'pattern': pattern}
            ))

        return violations


# 导出所有命名规则
NAMING_RULES = [
    FunctionNamingRule,
    ClassNamingRule,
]

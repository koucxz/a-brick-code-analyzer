"""
复杂度相关规则
"""

from typing import List

from ..base import NodeRule, RuleViolation, Severity
from ...base import CodeNode, ParseResult, NodeType


class MaxComplexityRule(NodeRule):
    """检查函数/方法的圈复杂度"""

    rule_id = "complexity/max-complexity"
    name = "最大圈复杂度"
    description = "限制函数的圈复杂度"
    category = "complexity"
    default_severity = Severity.WARN
    default_options = {"max": 10}
    target_node_types = [NodeType.FUNCTION, NodeType.METHOD]

    def check_node(self, node: CodeNode, parse_result: ParseResult) -> List[RuleViolation]:
        violations = []
        max_complexity = self.options.get('max', 10)

        if node.complexity > max_complexity:
            violations.append(self.create_violation(
                message=f"函数 '{node.name}' 的圈复杂度为 {node.complexity}（最大允许 {max_complexity}）",
                file_path=parse_result.file_path,
                line_start=node.line_start,
                line_end=node.line_end,
                node_name=node.name,
                node_type=node.node_type.value,
                suggestion=f"考虑将 '{node.name}' 拆分为更小的函数",
                metadata={'actual': node.complexity, 'max': max_complexity}
            ))

        return violations


class MaxFunctionLinesRule(NodeRule):
    """检查函数/方法的行数"""

    rule_id = "complexity/max-function-lines"
    name = "函数最大行数"
    description = "限制函数的行数"
    category = "complexity"
    default_severity = Severity.WARN
    default_options = {"max": 50}
    target_node_types = [NodeType.FUNCTION, NodeType.METHOD]

    def check_node(self, node: CodeNode, parse_result: ParseResult) -> List[RuleViolation]:
        violations = []
        max_lines = self.options.get('max', 50)
        actual_lines = node.line_end - node.line_start + 1

        if actual_lines > max_lines:
            violations.append(self.create_violation(
                message=f"函数 '{node.name}' 有 {actual_lines} 行（最大允许 {max_lines}）",
                file_path=parse_result.file_path,
                line_start=node.line_start,
                line_end=node.line_end,
                node_name=node.name,
                node_type=node.node_type.value,
                suggestion=f"考虑将 '{node.name}' 拆分为更小的函数",
                metadata={'actual': actual_lines, 'max': max_lines}
            ))

        return violations


class MaxParamsRule(NodeRule):
    """检查函数参数数量"""

    rule_id = "complexity/max-params"
    name = "最大参数数量"
    description = "限制函数的参数数量"
    category = "complexity"
    default_severity = Severity.WARN
    default_options = {"max": 5}
    target_node_types = [NodeType.FUNCTION, NodeType.METHOD]

    def check_node(self, node: CodeNode, parse_result: ParseResult) -> List[RuleViolation]:
        violations = []
        max_params = self.options.get('max', 5)

        # 排除 'self' 和 'cls'（Python 方法）
        params = [p for p in node.params if p not in ('self', 'cls')]
        actual_params = len(params)

        if actual_params > max_params:
            violations.append(self.create_violation(
                message=f"函数 '{node.name}' 有 {actual_params} 个参数（最大允许 {max_params}）",
                file_path=parse_result.file_path,
                line_start=node.line_start,
                line_end=node.line_end,
                node_name=node.name,
                node_type=node.node_type.value,
                suggestion="考虑使用配置对象或数据类来减少参数数量",
                metadata={'actual': actual_params, 'max': max_params, 'params': params}
            ))

        return violations


# 导出所有复杂度规则
COMPLEXITY_RULES = [
    MaxComplexityRule,
    MaxFunctionLinesRule,
    MaxParamsRule,
]

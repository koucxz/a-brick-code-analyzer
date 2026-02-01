"""
代码结构规则
"""

from typing import List

from ..base import BaseRule, RuleViolation, Severity
from ...base import ParseResult


class MaxFileLinesRule(BaseRule):
    """检查文件行数"""

    rule_id = "structure/max-file-lines"
    name = "文件最大行数"
    description = "限制文件的总行数"
    category = "structure"
    default_severity = Severity.WARN
    default_options = {"max": 500}

    def check(self, parse_result: ParseResult) -> List[RuleViolation]:
        violations = []
        max_lines = self.options.get('max', 500)

        if parse_result.total_lines > max_lines:
            violations.append(self.create_violation(
                message=f"文件有 {parse_result.total_lines} 行（最大允许 {max_lines}）",
                file_path=parse_result.file_path,
                line_start=1,
                line_end=parse_result.total_lines,
                suggestion="考虑将文件拆分为多个模块",
                metadata={'actual': parse_result.total_lines, 'max': max_lines}
            ))

        return violations


class MaxClassesPerFileRule(BaseRule):
    """检查每个文件的类数量"""

    rule_id = "structure/max-classes-per-file"
    name = "每文件最大类数量"
    description = "限制每个文件中的类数量"
    category = "structure"
    default_severity = Severity.WARN
    default_options = {"max": 5}

    def check(self, parse_result: ParseResult) -> List[RuleViolation]:
        violations = []
        max_classes = self.options.get('max', 5)

        classes = parse_result.get_classes()
        actual_classes = len(classes)

        if actual_classes > max_classes:
            violations.append(self.create_violation(
                message=f"文件有 {actual_classes} 个类（最大允许 {max_classes}）",
                file_path=parse_result.file_path,
                line_start=1,
                line_end=parse_result.total_lines,
                suggestion="考虑将部分类移动到单独的模块",
                metadata={
                    'actual': actual_classes,
                    'max': max_classes,
                    'classes': [c.name for c in classes]
                }
            ))

        return violations


class MaxFunctionsPerFileRule(BaseRule):
    """检查每个文件的函数数量"""

    rule_id = "structure/max-functions-per-file"
    name = "每文件最大函数数量"
    description = "限制每个文件中的顶层函数数量"
    category = "structure"
    default_severity = Severity.WARN
    default_options = {"max": 20}

    def check(self, parse_result: ParseResult) -> List[RuleViolation]:
        violations = []
        max_functions = self.options.get('max', 20)

        functions = parse_result.get_functions()
        actual_functions = len(functions)

        if actual_functions > max_functions:
            violations.append(self.create_violation(
                message=f"文件有 {actual_functions} 个函数（最大允许 {max_functions}）",
                file_path=parse_result.file_path,
                line_start=1,
                line_end=parse_result.total_lines,
                suggestion="考虑将部分函数移动到单独的模块或组织为类",
                metadata={
                    'actual': actual_functions,
                    'max': max_functions,
                    'functions': [f.name for f in functions]
                }
            ))

        return violations


# 导出所有结构规则
STRUCTURE_RULES = [
    MaxFileLinesRule,
    MaxClassesPerFileRule,
    MaxFunctionsPerFileRule,
]

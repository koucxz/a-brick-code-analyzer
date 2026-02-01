"""
Lint 结果数据结构
"""

from dataclasses import dataclass, field
from typing import List

from .base import RuleViolation, Severity


@dataclass
class LintResult:
    """单个文件的 lint 结果"""
    file_path: str
    violations: List[RuleViolation] = field(default_factory=list)
    error_count: int = 0
    warning_count: int = 0
    parse_errors: List[str] = field(default_factory=list)

    def add_violation(self, violation: RuleViolation):
        """添加违规并更新计数"""
        self.violations.append(violation)
        if violation.severity == Severity.ERROR:
            self.error_count += 1
        elif violation.severity == Severity.WARN:
            self.warning_count += 1

    @property
    def has_errors(self) -> bool:
        """是否有错误"""
        return self.error_count > 0

    @property
    def has_warnings(self) -> bool:
        """是否有警告"""
        return self.warning_count > 0

    @property
    def has_issues(self) -> bool:
        """是否有任何问题"""
        return len(self.violations) > 0 or len(self.parse_errors) > 0


@dataclass
class LintReport:
    """多个文件的聚合 lint 报告"""
    results: List[LintResult] = field(default_factory=list)

    def add_result(self, result: LintResult):
        """添加单个文件的结果"""
        self.results.append(result)

    @property
    def total_errors(self) -> int:
        """总错误数"""
        return sum(r.error_count for r in self.results)

    @property
    def total_warnings(self) -> int:
        """总警告数"""
        return sum(r.warning_count for r in self.results)

    @property
    def total_violations(self) -> int:
        """总违规数"""
        return sum(len(r.violations) for r in self.results)

    @property
    def files_with_issues(self) -> int:
        """有问题的文件数"""
        return sum(1 for r in self.results if r.has_issues)

    @property
    def total_files(self) -> int:
        """总文件数"""
        return len(self.results)

    @property
    def has_errors(self) -> bool:
        """是否有错误"""
        return self.total_errors > 0

    def get_all_violations(self) -> List[RuleViolation]:
        """获取所有违规"""
        violations = []
        for result in self.results:
            violations.extend(result.violations)
        return violations

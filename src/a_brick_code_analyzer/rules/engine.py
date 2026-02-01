"""
规则引擎核心
"""

from pathlib import Path
from typing import List, Dict, Type, Optional
import fnmatch

from .base import BaseRule, Severity
from .result import LintResult, LintReport
from .config import RuleConfig


class RuleEngine:
    """规则引擎核心类"""

    def __init__(self):
        self._rules: Dict[str, BaseRule] = {}
        self._rule_classes: Dict[str, Type[BaseRule]] = {}
        self._config: Optional[RuleConfig] = None

    def register_rule(self, rule_class: Type[BaseRule]):
        """注册规则类"""
        self._rule_classes[rule_class.rule_id] = rule_class

    def register_builtin_rules(self):
        """注册所有内置规则"""
        from .builtin import get_all_builtin_rules
        for rule_class in get_all_builtin_rules():
            self.register_rule(rule_class)

    def load_config(self, config_path: str = None, search_dir: str = None):
        """从文件加载配置"""
        self._config = RuleConfig.load(config_path, search_dir)
        self._apply_config()

    def use_preset(self, preset_name: str):
        """使用预设配置"""
        self._config = RuleConfig._load_preset(preset_name)
        self._apply_config()

    def _apply_config(self):
        """应用配置到规则"""
        if not self._config:
            return

        self._rules.clear()

        for rule_id, rule_class in self._rule_classes.items():
            rule_config = self._config.get_rule_config(rule_id)

            if rule_config:
                severity_value = rule_config.get('severity', rule_class.default_severity)
                options = rule_config.get('options', {})

                severity = self._config.parse_severity(severity_value)

                if severity != Severity.OFF:
                    self._rules[rule_id] = rule_class(severity=severity, options=options)
            else:
                # 未配置的规则使用默认值
                self._rules[rule_id] = rule_class()

    def configure_rule(self, rule_id: str, severity: Severity = None, options: Dict = None):
        """手动配置单个规则"""
        if rule_id not in self._rule_classes:
            raise ValueError(f"未知规则: {rule_id}")

        rule_class = self._rule_classes[rule_id]

        if severity == Severity.OFF:
            # 禁用规则
            if rule_id in self._rules:
                del self._rules[rule_id]
        else:
            self._rules[rule_id] = rule_class(
                severity=severity or rule_class.default_severity,
                options=options or {}
            )

    def lint(self, parse_result) -> LintResult:
        """
        检查单个解析结果

        Args:
            parse_result: 代码解析结果

        Returns:
            LintResult 包含所有违规
        """
        result = LintResult(file_path=parse_result.file_path)

        # 添加解析错误
        result.parse_errors = parse_result.errors.copy()

        # 运行所有启用的规则
        for rule in self._rules.values():
            if rule.is_enabled() and rule.supports_language(parse_result.language):
                violations = rule.check(parse_result)
                for violation in violations:
                    result.add_violation(violation)

        return result

    def lint_file(self, file_path: str) -> LintResult:
        """
        检查单个文件

        Args:
            file_path: 文件路径

        Returns:
            LintResult 包含所有违规
        """
        from ..factory import ParserFactory

        parser = ParserFactory.get_parser_by_file(file_path)
        if not parser:
            result = LintResult(file_path=file_path)
            result.parse_errors.append(f"没有可用的解析器: {file_path}")
            return result

        parse_result = parser.parse_file(file_path)
        return self.lint(parse_result)

    def lint_files(self, file_paths: List[str]) -> LintReport:
        """
        检查多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            LintReport 聚合结果
        """
        report = LintReport()
        for file_path in file_paths:
            if not self._should_ignore(file_path):
                result = self.lint_file(file_path)
                report.add_result(result)
        return report

    def lint_directory(
        self,
        directory: str,
        recursive: bool = True,
        extensions: List[str] = None
    ) -> LintReport:
        """
        检查目录中的所有文件

        Args:
            directory: 目录路径
            recursive: 是否递归搜索
            extensions: 要包含的文件扩展名（默认：所有支持的扩展名）

        Returns:
            LintReport 聚合结果
        """
        from ..factory import ParserFactory

        if extensions is None:
            extensions = ParserFactory.get_supported_extensions()

        dir_path = Path(directory)
        pattern = "**/*" if recursive else "*"

        file_paths = []
        for ext in extensions:
            file_paths.extend(str(p) for p in dir_path.glob(f"{pattern}{ext}"))

        return self.lint_files(file_paths)

    def _should_ignore(self, file_path: str) -> bool:
        """检查文件是否应该被忽略"""
        if not self._config or not self._config.ignore_patterns:
            return False

        for pattern in self._config.ignore_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def get_enabled_rules(self) -> List[BaseRule]:
        """获取已启用的规则列表"""
        return [r for r in self._rules.values() if r.is_enabled()]

    def get_rule(self, rule_id: str) -> Optional[BaseRule]:
        """根据 ID 获取规则"""
        return self._rules.get(rule_id)

    def get_registered_rules(self) -> List[str]:
        """获取所有已注册的规则 ID"""
        return list(self._rule_classes.keys())

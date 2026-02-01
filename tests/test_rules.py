"""
规则引擎测试
"""

import unittest
import tempfile
import os
import json

from a_brick_code_analyzer import (
    RuleEngine,
    RuleConfig,
    Severity,
    PythonParser,
)
from a_brick_code_analyzer.rules.builtin.complexity import (
    MaxComplexityRule,
    MaxFunctionLinesRule,
    MaxParamsRule,
)


class TestRuleEngine(unittest.TestCase):
    """规则引擎测试"""

    def setUp(self):
        self.engine = RuleEngine()
        self.engine.register_builtin_rules()
        self.parser = PythonParser()

    def test_register_builtin_rules(self):
        """测试注册内置规则"""
        rules = self.engine.get_registered_rules()
        self.assertIn('complexity/max-complexity', rules)
        self.assertIn('complexity/max-function-lines', rules)
        self.assertIn('complexity/max-params', rules)
        self.assertIn('naming/function-naming', rules)
        self.assertIn('naming/class-naming', rules)
        self.assertIn('structure/max-file-lines', rules)

    def test_use_preset_recommended(self):
        """测试使用推荐预设"""
        self.engine.use_preset('recommended')
        enabled_rules = self.engine.get_enabled_rules()
        self.assertTrue(len(enabled_rules) > 0)

    def test_use_preset_strict(self):
        """测试使用严格预设"""
        self.engine.use_preset('strict')
        enabled_rules = self.engine.get_enabled_rules()
        # 严格模式下所有规则应该是 ERROR 级别
        for rule in enabled_rules:
            self.assertEqual(rule.severity, Severity.ERROR)

    def test_use_preset_minimal(self):
        """测试使用最小预设"""
        self.engine.use_preset('minimal')
        enabled_rules = self.engine.get_enabled_rules()
        # 最小模式只有复杂度规则
        rule_ids = [r.rule_id for r in enabled_rules]
        self.assertIn('complexity/max-complexity', rule_ids)

    def test_lint_simple_code(self):
        """测试检查简单代码"""
        code = '''
def hello():
    print("Hello, World!")
'''
        self.engine.use_preset('recommended')
        parse_result = self.parser.parse(code, "test.py")
        result = self.engine.lint(parse_result)

        self.assertEqual(result.file_path, "test.py")
        # 简单代码不应该有违规
        self.assertEqual(result.error_count, 0)

    def test_lint_complex_function(self):
        """测试检查复杂函数"""
        # 创建一个高复杂度的函数
        code = '''
def complex_function(a, b, c, d, e, f):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            return 1
                        else:
                            return 2
                    else:
                        return 3
                else:
                    return 4
            else:
                return 5
        else:
            return 6
    else:
        return 7
'''
        # 使用较低的阈值来确保触发违规
        self.engine.use_preset('recommended')
        self.engine.configure_rule(
            'complexity/max-complexity',
            severity=Severity.WARN,
            options={'max': 5}
        )
        parse_result = self.parser.parse(code, "test.py")
        result = self.engine.lint(parse_result)

        # 应该有复杂度违规
        complexity_violations = [
            v for v in result.violations
            if v.rule_id == 'complexity/max-complexity'
        ]
        self.assertTrue(len(complexity_violations) > 0)

    def test_lint_too_many_params(self):
        """测试检查参数过多"""
        code = '''
def too_many_params(a, b, c, d, e, f, g, h):
    pass
'''
        self.engine.use_preset('recommended')
        parse_result = self.parser.parse(code, "test.py")
        result = self.engine.lint(parse_result)

        # 应该有参数数量违规
        param_violations = [
            v for v in result.violations
            if v.rule_id == 'complexity/max-params'
        ]
        self.assertTrue(len(param_violations) > 0)

    def test_lint_naming_violation(self):
        """测试检查命名违规"""
        code = '''
def BadFunctionName():
    pass

class bad_class_name:
    pass
'''
        self.engine.use_preset('recommended')
        parse_result = self.parser.parse(code, "test.py")
        result = self.engine.lint(parse_result)

        # 应该有命名违规
        naming_violations = [
            v for v in result.violations
            if 'naming' in v.rule_id
        ]
        self.assertTrue(len(naming_violations) >= 2)

    def test_configure_rule(self):
        """测试手动配置规则"""
        self.engine.use_preset('recommended')

        # 修改复杂度阈值
        self.engine.configure_rule(
            'complexity/max-complexity',
            severity=Severity.ERROR,
            options={'max': 5}
        )

        rule = self.engine.get_rule('complexity/max-complexity')
        self.assertEqual(rule.severity, Severity.ERROR)
        self.assertEqual(rule.options['max'], 5)

    def test_disable_rule(self):
        """测试禁用规则"""
        self.engine.use_preset('recommended')

        # 禁用命名规则
        self.engine.configure_rule('naming/function-naming', severity=Severity.OFF)

        rule = self.engine.get_rule('naming/function-naming')
        self.assertIsNone(rule)

    def test_lint_result_counts(self):
        """测试结果计数"""
        code = '''
def BadName(a, b, c, d, e, f, g):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return 1
    return 0
'''
        self.engine.use_preset('strict')
        parse_result = self.parser.parse(code, "test.py")
        result = self.engine.lint(parse_result)

        # 严格模式下应该有错误
        self.assertTrue(result.has_errors)
        self.assertTrue(result.error_count > 0)


class TestRuleConfig(unittest.TestCase):
    """规则配置测试"""

    def test_load_default_config(self):
        """测试加载默认配置"""
        config = RuleConfig.load(search_dir=tempfile.gettempdir())
        self.assertIsNotNone(config)
        self.assertIn('complexity/max-complexity', config.rules)

    def test_load_json_config(self):
        """测试加载 JSON 配置"""
        config_data = {
            "extends": ["recommended"],
            "rules": {
                "complexity/max-complexity": ["error", {"max": 5}],
                "naming/function-naming": "off"
            }
        }

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = RuleConfig.load(config_path)

            # 检查规则配置
            complexity_config = config.get_rule_config('complexity/max-complexity')
            self.assertEqual(complexity_config['severity'], 'error')
            self.assertEqual(complexity_config['options']['max'], 5)

            naming_config = config.get_rule_config('naming/function-naming')
            self.assertEqual(naming_config['severity'], 'off')
        finally:
            os.unlink(config_path)

    def test_parse_severity(self):
        """测试解析 severity"""
        config = RuleConfig()

        self.assertEqual(config.parse_severity('error'), Severity.ERROR)
        self.assertEqual(config.parse_severity('warn'), Severity.WARN)
        self.assertEqual(config.parse_severity('off'), Severity.OFF)
        self.assertEqual(config.parse_severity(2), Severity.ERROR)
        self.assertEqual(config.parse_severity(1), Severity.WARN)
        self.assertEqual(config.parse_severity(0), Severity.OFF)

    def test_preset_configs(self):
        """测试预设配置"""
        recommended = RuleConfig._get_recommended_config()
        strict = RuleConfig._get_strict_config()
        minimal = RuleConfig._get_minimal_config()

        # 推荐配置应该有多个规则
        self.assertTrue(len(recommended.rules) > 3)

        # 严格配置的复杂度阈值应该更低
        self.assertEqual(
            strict.rules['complexity/max-complexity']['options']['max'],
            8
        )
        self.assertEqual(
            recommended.rules['complexity/max-complexity']['options']['max'],
            10
        )

        # 最小配置只有一个规则
        self.assertEqual(len(minimal.rules), 1)


class TestLintReport(unittest.TestCase):
    """Lint 报告测试"""

    def setUp(self):
        self.engine = RuleEngine()
        self.engine.register_builtin_rules()
        self.engine.use_preset('recommended')
        self.parser = PythonParser()

    def test_lint_multiple_files(self):
        """测试检查多个文件"""
        codes = [
            ('file1.py', 'def good_function(): pass'),
            ('file2.py', 'def BadFunction(): pass'),
        ]

        results = []
        for file_path, code in codes:
            parse_result = self.parser.parse(code, file_path)
            result = self.engine.lint(parse_result)
            results.append(result)

        from a_brick_code_analyzer import LintReport
        report = LintReport()
        for result in results:
            report.add_result(result)

        self.assertEqual(report.total_files, 2)
        self.assertTrue(report.files_with_issues >= 1)

    def test_report_aggregation(self):
        """测试报告聚合"""
        from a_brick_code_analyzer import LintResult, LintReport, RuleViolation

        report = LintReport()

        # 添加有错误的结果
        result1 = LintResult(file_path="file1.py")
        result1.add_violation(RuleViolation(
            rule_id="test/rule",
            severity=Severity.ERROR,
            message="Test error",
            file_path="file1.py",
            line_start=1,
            line_end=1
        ))
        report.add_result(result1)

        # 添加有警告的结果
        result2 = LintResult(file_path="file2.py")
        result2.add_violation(RuleViolation(
            rule_id="test/rule",
            severity=Severity.WARN,
            message="Test warning",
            file_path="file2.py",
            line_start=1,
            line_end=1
        ))
        report.add_result(result2)

        self.assertEqual(report.total_errors, 1)
        self.assertEqual(report.total_warnings, 1)
        self.assertEqual(report.total_violations, 2)
        self.assertEqual(report.files_with_issues, 2)
        self.assertTrue(report.has_errors)


if __name__ == '__main__':
    unittest.main()

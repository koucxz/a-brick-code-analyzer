"""
内置规则测试
"""

import unittest

from a_brick_code_analyzer import PythonParser, Severity
from a_brick_code_analyzer.rules.builtin.complexity import (
    MaxComplexityRule,
    MaxFunctionLinesRule,
    MaxParamsRule,
)
from a_brick_code_analyzer.rules.builtin.naming import (
    FunctionNamingRule,
    ClassNamingRule,
)
from a_brick_code_analyzer.rules.builtin.structure import (
    MaxFileLinesRule,
    MaxClassesPerFileRule,
    MaxFunctionsPerFileRule,
)


class TestComplexityRules(unittest.TestCase):
    """复杂度规则测试"""

    def setUp(self):
        self.parser = PythonParser()

    def test_max_complexity_pass(self):
        """测试复杂度通过"""
        code = '''
def simple_function(x):
    if x > 0:
        return x
    return 0
'''
        rule = MaxComplexityRule(options={'max': 10})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 0)

    def test_max_complexity_fail(self):
        """测试复杂度超标"""
        code = '''
def complex_function(a, b, c):
    if a:
        if b:
            if c:
                for i in range(10):
                    if i > 5:
                        while True:
                            break
    return 0
'''
        rule = MaxComplexityRule(options={'max': 3})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 1)
        self.assertIn('complex_function', violations[0].message)

    def test_max_function_lines_pass(self):
        """测试函数行数通过"""
        code = '''
def short_function():
    x = 1
    y = 2
    return x + y
'''
        rule = MaxFunctionLinesRule(options={'max': 10})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 0)

    def test_max_function_lines_fail(self):
        """测试函数行数超标"""
        # 创建一个超过 5 行的函数
        lines = ['def long_function():']
        for i in range(10):
            lines.append(f'    x{i} = {i}')
        lines.append('    return x0')
        code = '\n'.join(lines)

        rule = MaxFunctionLinesRule(options={'max': 5})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 1)

    def test_max_params_pass(self):
        """测试参数数量通过"""
        code = '''
def few_params(a, b, c):
    return a + b + c
'''
        rule = MaxParamsRule(options={'max': 5})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 0)

    def test_max_params_fail(self):
        """测试参数数量超标"""
        code = '''
def many_params(a, b, c, d, e, f, g):
    pass
'''
        rule = MaxParamsRule(options={'max': 5})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 1)

    def test_max_params_excludes_self(self):
        """测试参数数量排除 self"""
        code = '''
class MyClass:
    def method(self, a, b, c, d, e):
        pass
'''
        rule = MaxParamsRule(options={'max': 5})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        # self 不计入，所以只有 5 个参数，刚好通过
        self.assertEqual(len(violations), 0)


class TestNamingRules(unittest.TestCase):
    """命名规则测试"""

    def setUp(self):
        self.parser = PythonParser()

    def test_function_naming_snake_case_pass(self):
        """测试函数 snake_case 命名通过"""
        code = '''
def my_function():
    pass

def another_function_name():
    pass
'''
        rule = FunctionNamingRule(options={'style': 'snake_case'})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 0)

    def test_function_naming_snake_case_fail(self):
        """测试函数 snake_case 命名失败"""
        code = '''
def MyFunction():
    pass

def anotherFunction():
    pass
'''
        rule = FunctionNamingRule(options={'style': 'snake_case'})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 2)

    def test_function_naming_camel_case(self):
        """测试函数 camelCase 命名"""
        code = '''
def myFunction():
    pass
'''
        rule = FunctionNamingRule(options={'style': 'camelCase'})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 0)

    def test_function_naming_ignores_dunder(self):
        """测试函数命名忽略 dunder 方法"""
        code = '''
class MyClass:
    def __init__(self):
        pass

    def __str__(self):
        return ""
'''
        rule = FunctionNamingRule(options={'style': 'snake_case'})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        # dunder 方法应该被忽略
        self.assertEqual(len(violations), 0)

    def test_class_naming_pascal_case_pass(self):
        """测试类 PascalCase 命名通过"""
        code = '''
class MyClass:
    pass

class AnotherClassName:
    pass
'''
        rule = ClassNamingRule(options={'style': 'PascalCase'})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 0)

    def test_class_naming_pascal_case_fail(self):
        """测试类 PascalCase 命名失败"""
        code = '''
class my_class:
    pass

class anotherClass:
    pass
'''
        rule = ClassNamingRule(options={'style': 'PascalCase'})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 2)


class TestStructureRules(unittest.TestCase):
    """结构规则测试"""

    def setUp(self):
        self.parser = PythonParser()

    def test_max_file_lines_pass(self):
        """测试文件行数通过"""
        code = '''
def func1():
    pass

def func2():
    pass
'''
        rule = MaxFileLinesRule(options={'max': 100})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 0)

    def test_max_file_lines_fail(self):
        """测试文件行数超标"""
        # 创建超过 10 行的代码
        lines = [f'x{i} = {i}' for i in range(20)]
        code = '\n'.join(lines)

        rule = MaxFileLinesRule(options={'max': 10})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 1)

    def test_max_classes_per_file_pass(self):
        """测试每文件类数量通过"""
        code = '''
class Class1:
    pass

class Class2:
    pass
'''
        rule = MaxClassesPerFileRule(options={'max': 5})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 0)

    def test_max_classes_per_file_fail(self):
        """测试每文件类数量超标"""
        classes = [f'class Class{i}:\n    pass\n' for i in range(6)]
        code = '\n'.join(classes)

        rule = MaxClassesPerFileRule(options={'max': 3})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 1)

    def test_max_functions_per_file_pass(self):
        """测试每文件函数数量通过"""
        code = '''
def func1():
    pass

def func2():
    pass
'''
        rule = MaxFunctionsPerFileRule(options={'max': 10})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 0)

    def test_max_functions_per_file_fail(self):
        """测试每文件函数数量超标"""
        functions = [f'def func{i}():\n    pass\n' for i in range(10)]
        code = '\n'.join(functions)

        rule = MaxFunctionsPerFileRule(options={'max': 5})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)
        self.assertEqual(len(violations), 1)


class TestRuleSeverity(unittest.TestCase):
    """规则严重级别测试"""

    def setUp(self):
        self.parser = PythonParser()

    def test_rule_severity_warn(self):
        """测试警告级别"""
        code = 'def BadName(): pass'
        rule = FunctionNamingRule(severity=Severity.WARN)
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].severity, Severity.WARN)

    def test_rule_severity_error(self):
        """测试错误级别"""
        code = 'def BadName(): pass'
        rule = FunctionNamingRule(severity=Severity.ERROR)
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)

        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].severity, Severity.ERROR)

    def test_rule_disabled(self):
        """测试禁用规则"""
        code = 'def BadName(): pass'
        rule = FunctionNamingRule(severity=Severity.OFF)

        self.assertFalse(rule.is_enabled())


class TestRuleViolationMetadata(unittest.TestCase):
    """规则违规元数据测试"""

    def setUp(self):
        self.parser = PythonParser()

    def test_violation_has_metadata(self):
        """测试违规包含元数据"""
        code = '''
def func(a, b, c, d, e, f, g):
    pass
'''
        rule = MaxParamsRule(options={'max': 3})
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)

        self.assertEqual(len(violations), 1)
        violation = violations[0]

        # 检查元数据
        self.assertIn('actual', violation.metadata)
        self.assertIn('max', violation.metadata)
        self.assertIn('params', violation.metadata)
        self.assertEqual(violation.metadata['actual'], 7)
        self.assertEqual(violation.metadata['max'], 3)

    def test_violation_has_suggestion(self):
        """测试违规包含建议"""
        code = 'def BadName(): pass'
        rule = FunctionNamingRule()
        parse_result = self.parser.parse(code, "test.py")
        violations = rule.check(parse_result)

        self.assertEqual(len(violations), 1)
        self.assertIsNotNone(violations[0].suggestion)


if __name__ == '__main__':
    unittest.main()

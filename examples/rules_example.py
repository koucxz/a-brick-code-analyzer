"""
规则引擎使用示例
演示如何使用规则引擎进行代码质量检查
"""

from a_brick_code_analyzer import (
    RuleEngine,
    PythonParser,
    Severity,
)


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例 1: 基础使用")
    print("=" * 60)

    # 创建规则引擎
    engine = RuleEngine()
    engine.register_builtin_rules()
    engine.use_preset('recommended')

    # 要检查的代码
    code = '''
def calculate_sum(numbers):
    """计算数字列表的总和"""
    total = 0
    for num in numbers:
        total += num
    return total


class Calculator:
    """简单计算器类"""

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
'''

    # 解析并检查
    parser = PythonParser()
    parse_result = parser.parse(code, "example.py")
    result = engine.lint(parse_result)

    # 输出结果
    print(f"文件: {result.file_path}")
    print(f"错误: {result.error_count}, 警告: {result.warning_count}")

    if result.violations:
        print("\n违规列表:")
        for v in result.violations:
            severity = "ERROR" if v.severity == Severity.ERROR else "WARN"
            print(f"  [{severity}] 行 {v.line_start}: {v.message}")
    else:
        print("\n没有发现违规!")

    print()


def example_complex_code():
    """检查复杂代码示例"""
    print("=" * 60)
    print("示例 2: 检查复杂代码")
    print("=" * 60)

    engine = RuleEngine()
    engine.register_builtin_rules()
    engine.use_preset('recommended')

    # 有问题的代码
    code = '''
def ProcessData(data, config, options, flags, settings, params, extra):
    """这个函数有太多参数和太高的复杂度"""
    result = []
    if data:
        if config:
            if options:
                for item in data:
                    if item > 0:
                        if flags:
                            if settings:
                                result.append(item * 2)
                            else:
                                result.append(item)
                        else:
                            result.append(item)
                    else:
                        result.append(0)
            else:
                result = data
        else:
            result = []
    return result


class bad_class_name:
    """类名不符合 PascalCase 规范"""

    def BadMethodName(self):
        """方法名不符合 snake_case 规范"""
        pass
'''

    parser = PythonParser()
    parse_result = parser.parse(code, "bad_example.py")
    result = engine.lint(parse_result)

    print(f"文件: {result.file_path}")
    print(f"错误: {result.error_count}, 警告: {result.warning_count}")
    print(f"\n发现 {len(result.violations)} 个违规:")

    for v in result.violations:
        severity = "ERROR" if v.severity == Severity.ERROR else "WARN"
        print(f"\n  [{severity}] {v.rule_id}")
        print(f"    行 {v.line_start}-{v.line_end}: {v.message}")
        if v.suggestion:
            print(f"    建议: {v.suggestion}")

    print()


def example_custom_config():
    """自定义配置示例"""
    print("=" * 60)
    print("示例 3: 自定义配置")
    print("=" * 60)

    engine = RuleEngine()
    engine.register_builtin_rules()
    engine.use_preset('recommended')

    # 自定义规则配置
    engine.configure_rule(
        'complexity/max-complexity',
        severity=Severity.ERROR,
        options={'max': 5}
    )
    engine.configure_rule(
        'complexity/max-params',
        severity=Severity.ERROR,
        options={'max': 3}
    )
    # 禁用命名检查
    engine.configure_rule('naming/function-naming', severity=Severity.OFF)
    engine.configure_rule('naming/class-naming', severity=Severity.OFF)

    code = '''
def process(a, b, c, d, e):
    if a:
        if b:
            if c:
                if d:
                    return e
    return 0
'''

    parser = PythonParser()
    parse_result = parser.parse(code, "custom.py")
    result = engine.lint(parse_result)

    print(f"自定义配置:")
    print(f"  - 最大复杂度: 5 (ERROR)")
    print(f"  - 最大参数: 3 (ERROR)")
    print(f"  - 命名检查: 禁用")
    print()
    print(f"检查结果: {result.error_count} 错误, {result.warning_count} 警告")

    for v in result.violations:
        severity = "ERROR" if v.severity == Severity.ERROR else "WARN"
        print(f"  [{severity}] {v.rule_id}: {v.message}")

    print()


def example_presets():
    """预设配置示例"""
    print("=" * 60)
    print("示例 4: 不同预设配置对比")
    print("=" * 60)

    code = '''
def func(a, b, c, d, e, f):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return f
    return 0
'''

    parser = PythonParser()
    parse_result = parser.parse(code, "test.py")

    presets = ['minimal', 'recommended', 'strict']

    for preset in presets:
        engine = RuleEngine()
        engine.register_builtin_rules()
        engine.use_preset(preset)

        result = engine.lint(parse_result)
        print(f"\n预设 '{preset}':")
        print(f"  启用规则数: {len(engine.get_enabled_rules())}")
        print(f"  错误: {result.error_count}, 警告: {result.warning_count}")

    print()


def example_lint_report():
    """多文件检查报告示例"""
    print("=" * 60)
    print("示例 5: 多文件检查报告")
    print("=" * 60)

    engine = RuleEngine()
    engine.register_builtin_rules()
    engine.use_preset('recommended')

    # 模拟多个文件
    files = [
        ("module_a.py", '''
def good_function():
    return 42
'''),
        ("module_b.py", '''
def BadFunction():
    pass

class bad_class:
    pass
'''),
        ("module_c.py", '''
def complex_func(a, b, c, d, e, f, g):
    if a:
        if b:
            if c:
                return d
    return 0
'''),
    ]

    from a_brick_code_analyzer import LintReport

    parser = PythonParser()
    report = LintReport()

    for file_path, code in files:
        parse_result = parser.parse(code, file_path)
        result = engine.lint(parse_result)
        report.add_result(result)

    print(f"检查了 {report.total_files} 个文件")
    print(f"有问题的文件: {report.files_with_issues}")
    print(f"总计: {report.total_errors} 错误, {report.total_warnings} 警告")
    print()

    print("各文件详情:")
    for result in report.results:
        status = "OK" if not result.has_issues else f"{result.error_count}E/{result.warning_count}W"
        print(f"  {result.file_path}: {status}")

    print()


def example_available_rules():
    """列出所有可用规则"""
    print("=" * 60)
    print("示例 6: 所有可用规则")
    print("=" * 60)

    engine = RuleEngine()
    engine.register_builtin_rules()

    print("已注册的规则:")
    for rule_id in sorted(engine.get_registered_rules()):
        print(f"  - {rule_id}")

    print()


def main():
    """运行所有示例"""
    example_basic_usage()
    example_complex_code()
    example_custom_config()
    example_presets()
    example_lint_report()
    example_available_rules()

    print("=" * 60)
    print("所有示例运行完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()

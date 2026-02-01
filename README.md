# a-brick-code-analyzer

代码分析工具，结合 AST 解析、规则引擎和 LLM 集成，用于代码质量分析、安全漏洞检测和性能优化建议。

## 特性

- **AST 解析**: 深度代码结构分析
- **规则引擎**: 可自定义的代码质量规则
- **LLM 集成**: AI 驱动的代码洞察
- **安全检测**: 识别潜在的安全漏洞
- **性能分析**: 提供优化建议

## 支持的语言

| 语言 | 扩展名 | 功能支持 | 安装要求 |
|------|--------|----------|----------|
| Python | `.py` | ✅ 完整支持 | 基础安装 |
| JavaScript | `.js`, `.jsx` | ✅ 完整支持 | `pip install -e .[javascript]` |
| TypeScript | `.ts`, `.tsx` | ✅ 完整支持 | `pip install -e .[javascript]` |

### 功能支持详情

所有支持的语言都提供以下功能：
- 📊 **代码节点分析**: 函数、类、方法、变量
- 🔍 **导入语句识别**: import/require 语句分析
- 📈 **复杂度计算**: 圈复杂度分析
- 📏 **行数统计**: 代码行、注释行、空白行统计
- ⚠️ **错误处理**: 语法错误检测和报告

## 安装

基础安装（仅 Python 支持）：
```bash
pip install -e .
```

完整安装（包含 JavaScript/TypeScript 支持）：
```bash
pip install -e .[javascript]
```

## 快速开始

### Python 解析
```python
from a_brick_code_analyzer import PythonParser, ParserFactory

# 基础使用
parser = PythonParser()
code = '''
def hello(name):
    return f"Hello, {name}!"
'''
result = parser.parse(code)
print(f"发现 {len(result.nodes)} 个代码节点")

# 使用工厂模式
parser = ParserFactory.get_parser_by_file("example.py")
if parser:
    result = parser.parse_file("example.py")
```

### JavaScript/TypeScript 解析
```python
from a_brick_code_analyzer import ParserFactory

# 自动识别文件类型
js_parser = ParserFactory.get_parser_by_file("example.js")
ts_parser = ParserFactory.get_parser_by_file("example.ts")

if js_parser:
    js_result = js_parser.parse_file("example.js")
    print(f"JavaScript: 发现 {len(js_result.nodes)} 个代码节点")

if ts_parser:
    ts_result = ts_parser.parse_file("example.ts")
    print(f"TypeScript: 发现 {len(ts_result.nodes)} 个代码节点")

# 手动指定语言
js_parser = ParserFactory.get_parser("javascript")
ts_parser = ParserFactory.get_parser("typescript")
```

### JavaScript/TypeScript 功能特性

JavaScript 和 TypeScript 解析器支持以下功能：

- **函数解析**: 提取函数声明、参数、复杂度
- **类和方法**: 识别类定义和方法
- **变量声明**: 检测变量声明（`const`, `let`, `var`）
- **导入分析**: 识别 `import` 语句和 `require()` 调用
- **复杂度计算**: 基于圈复杂度的代码复杂度分析
- **行数统计**: 详细的代码行、注释行、空白行统计
- **错误处理**: 优雅处理语法错误

## 规则引擎

规则引擎提供 ESLint 风格的代码质量检查功能。

### 基础使用

```python
from a_brick_code_analyzer import RuleEngine, PythonParser, Severity

# 创建规则引擎
engine = RuleEngine()
engine.register_builtin_rules()
engine.use_preset('recommended')  # 使用推荐预设

# 检查代码
parser = PythonParser()
code = '''
def BadFunctionName(a, b, c, d, e, f, g):
    if a:
        if b:
            if c:
                return d
    return 0
'''
parse_result = parser.parse(code, "example.py")
result = engine.lint(parse_result)

# 输出结果
print(f"错误: {result.error_count}, 警告: {result.warning_count}")
for violation in result.violations:
    print(f"  行 {violation.line_start}: [{violation.rule_id}] {violation.message}")
```

### 内置规则

| 规则 ID | 描述 | 默认选项 |
|---------|------|----------|
| `complexity/max-complexity` | 最大圈复杂度 | `{max: 10}` |
| `complexity/max-function-lines` | 函数最大行数 | `{max: 50}` |
| `complexity/max-params` | 最大参数数量 | `{max: 5}` |
| `naming/function-naming` | 函数命名规范 | `{style: "snake_case"}` |
| `naming/class-naming` | 类命名规范 | `{style: "PascalCase"}` |
| `structure/max-file-lines` | 文件最大行数 | `{max: 500}` |
| `structure/max-classes-per-file` | 每文件最大类数量 | `{max: 5}` |
| `structure/max-functions-per-file` | 每文件最大函数数量 | `{max: 20}` |

### 预设配置

- **recommended**: 推荐配置，平衡的规则设置
- **strict**: 严格配置，所有规则为 ERROR 级别，阈值更低
- **minimal**: 最小配置，仅包含关键规则

### 自定义配置

#### 代码中配置

```python
engine = RuleEngine()
engine.register_builtin_rules()
engine.use_preset('recommended')

# 修改规则配置
engine.configure_rule(
    'complexity/max-complexity',
    severity=Severity.ERROR,
    options={'max': 8}
)

# 禁用规则
engine.configure_rule('naming/function-naming', severity=Severity.OFF)
```

#### 配置文件

支持 `.analyzerrc.json`、`.analyzerrc.yaml` 或 `pyproject.toml` 配置：

**`.analyzerrc.json`**
```json
{
  "extends": ["recommended"],
  "rules": {
    "complexity/max-complexity": ["error", { "max": 10 }],
    "complexity/max-function-lines": ["warn", { "max": 50 }],
    "naming/function-naming": "off"
  },
  "ignorePatterns": ["**/node_modules/**", "**/__pycache__/**"]
}
```

**`pyproject.toml`**
```toml
[tool.analyzer]
extends = ["recommended"]

[tool.analyzer.rules]
"complexity/max-complexity" = ["error", { max = 10 }]
"naming/function-naming" = "off"
```

### 检查目录

```python
engine = RuleEngine()
engine.register_builtin_rules()
engine.load_config()  # 自动加载配置文件

# 检查整个目录
report = engine.lint_directory("src/", recursive=True)

print(f"检查了 {report.total_files} 个文件")
print(f"总计: {report.total_errors} 错误, {report.total_warnings} 警告")
```

## 运行示例

### 基础示例（Python）
```bash
python examples/parser_example.py
```

### JavaScript/TypeScript 示例
```bash
# 需要先安装 JavaScript/TypeScript 支持
pip install -e .[javascript]

# 运行 JS/TS 示例
python examples/js_ts_example.py
```

### 规则引擎示例
```bash
python examples/rules_example.py
```

## 运行测试

```bash
python -m pytest
```

## TODO

- [x] 规则引擎：可自定义的代码质量规则
- [ ] LLM 集成：AI 驱动的代码洞察
- [ ] 安全检测：识别潜在的安全漏洞
- [ ] 性能分析：提供优化建议
- [x] 支持 JavaScript 和 TypeScript
- [ ] 支持更多语言（Go 等）

## 许可证

MIT
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

### LLM 代码分析示例

#### 1. 安装 Ollama

访问 https://ollama.com/download 下载并安装 Ollama。

#### 2. 下载模型

```bash
ollama pull qwen3-coder
```

推荐模型（2025 年更新）：

| 模型 | 参数量 | 说明 |
|------|--------|------|
| `qwen3-coder` | 30B | **代码首选**，效果最好，需 24GB+ 显存 |
| `deepseek-r1` | 7.6B | 推理能力强，支持中文，性价比高 |
| `qwen3` | 4B/8B | 通用模型，支持思考链 |
| `codellama:7b` | 7B | 经典代码模型 |
| `llama3.2:3b` | 3B | 轻量快速，入门推荐 |
| `deepseek-coder-v2` | 16B | 代码专用，支持中文 |

> 💡 显存充足首选 `qwen3-coder`，显存有限用 `deepseek-r1` 或 `llama3.2:3b`

#### 3. 运行示例

```bash
python examples/llm_example.py
```

#### 4. 代码中使用

```python
from a_brick_code_analyzer import CodeAnalyzer, AnalysisType

# 创建分析器（默认使用 llama3.2:3b）
analyzer = CodeAnalyzer()

# 或指定更强的模型
analyzer = CodeAnalyzer(model="qwen3-coder")

code = '''
def calculate(a, b, c, d, e, f):
    if a > 0:
        if b > 0:
            return a + b
    return 0
'''

# 代码审查
result = analyzer.review(code)
print(result.content)

# 安全检查
result = analyzer.check_security(code)

# 代码解释
result = analyzer.explain(code)

# 复杂度分析
result = analyzer.analyze_complexity(code)

# 性能优化建议
result = analyzer.optimize_performance(code)

# 生成文档
result = analyzer.generate_docs(code)
```

#### 5. LLM 分析示例

**代码审查示例**

```python
from a_brick_code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

code = '''
def calculate_discount(price, discount_type, user_level, is_vip, has_coupon):
    if discount_type == "percentage":
        if user_level > 5:
            if is_vip:
                if has_coupon:
                    return price * 0.5
                else:
                    return price * 0.6
            else:
                return price * 0.7
        else:
            return price * 0.9
    else:
        return price - 20
'''

result = analyzer.review(code)
print(result.content)
# 输出: 代码问题分析、命名规范建议、重构建议等
print(f"耗时: {result.duration_ms:.0f}ms, Token: {result.total_tokens}")
```

**安全检查示例**

```python
from a_brick_code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

code = '''
import subprocess

def run_command(user_input):
    # 危险: 命令注入漏洞
    result = subprocess.run(user_input, shell=True, capture_output=True)
    return result.stdout.decode()

def read_file(filename):
    # 危险: 路径遍历漏洞
    with open(f"/data/{filename}", "r") as f:
        return f.read()
'''

result = analyzer.check_security(code)
print(result.content)
# 输出: 识别命令注入、路径遍历等安全漏洞，并提供修复建议
```

**性能优化示例**

```python
from a_brick_code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

code = '''
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates

def process_data(data):
    result = []
    for item in data:
        result = result + [item * 2]  # 低效的列表拼接
    return result
'''

result = analyzer.optimize_performance(code)
print(result.content)
# 输出: 识别 O(n²) 复杂度问题、低效列表操作，提供优化建议
```

## 运行测试

```bash
python -m pytest
```

## TODO

- [x] 规则引擎：可自定义的代码质量规则
- [x] LLM 集成：AI 驱动的代码洞察
- [x] 安全检测：识别潜在的安全漏洞
- [x] 性能分析：提供优化建议
- [x] 支持 JavaScript 和 TypeScript
- [ ] 支持更多语言（Go 等）

## 许可证

MIT
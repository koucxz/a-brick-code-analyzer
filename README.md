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

## 运行测试

```bash
python -m pytest
```

## TODO

- [ ] 规则引擎：可自定义的代码质量规则
- [ ] LLM 集成：AI 驱动的代码洞察
- [ ] 安全检测：识别潜在的安全漏洞
- [ ] 性能分析：提供优化建议
- [x] 支持 JavaScript 和 TypeScript
- [ ] 支持更多语言（Go 等）

## 许可证

MIT
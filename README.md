# a-brick-code-analyzer

代码分析工具，结合 AST 解析、规则引擎和 LLM 集成，用于代码质量分析、安全漏洞检测和性能优化建议。

## 特性

- **AST 解析**: 深度代码结构分析
- **规则引擎**: 可自定义的代码质量规则
- **LLM 集成**: AI 驱动的代码洞察
- **安全检测**: 识别潜在的安全漏洞
- **性能分析**: 提供优化建议

## 安装

```bash
pip install -e .
```

## 快速开始

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

## 运行示例

```bash
python examples/parser_example.py
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
- [ ] 支持更多语言（JavaScript、TypeScript、Go 等）

## 许可证

MIT
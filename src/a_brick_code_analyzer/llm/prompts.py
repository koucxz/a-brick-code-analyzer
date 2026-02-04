"""
代码分析 Prompt 模板
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class AnalysisType(Enum):
    """分析类型"""
    CODE_REVIEW = "code_review"
    COMPLEXITY = "complexity"
    SECURITY = "security"
    PERFORMANCE = "performance"
    REFACTOR = "refactor"
    EXPLAIN = "explain"
    DOCSTRING = "docstring"


@dataclass
class PromptTemplate:
    """Prompt 模板"""
    name: str
    template: str
    description: str
    analysis_type: AnalysisType


# 预定义的 Prompt 模板
PROMPTS = {
    AnalysisType.CODE_REVIEW: PromptTemplate(
        name="代码审查",
        analysis_type=AnalysisType.CODE_REVIEW,
        description="全面的代码审查，包括质量、风格、潜在问题",
        template="""你是一个专业的代码审查专家。请审查以下代码并提供改进建议。

## 代码信息
- 文件: {file_path}
- 语言: {language}
- 总行数: {total_lines}
- 代码行数: {code_lines}

## 代码内容
```{language}
{code}
```

## AST 分析结果
{ast_summary}

## 规则检查结果
{lint_results}

请从以下方面进行审查：
1. **代码质量**: 可读性、可维护性、命名规范
2. **潜在问题**: Bug 风险、边界情况、异常处理
3. **最佳实践**: 是否遵循语言惯例和设计模式
4. **改进建议**: 具体的优化方案

请用中文回答，给出具体的代码示例。""",
    ),

    AnalysisType.COMPLEXITY: PromptTemplate(
        name="复杂度分析",
        analysis_type=AnalysisType.COMPLEXITY,
        description="分析代码复杂度并提供简化建议",
        template="""你是一个代码优化专家。请分析以下代码的复杂度问题。

## 代码信息
- 文件: {file_path}
- 语言: {language}

## 复杂度较高的函数
{complexity_info}

## 代码内容
```{language}
{code}
```

请分析：
1. **复杂度来源**: 是什么导致了高复杂度（嵌套、条件分支、循环等）
2. **影响评估**: 这种复杂度会带来什么问题
3. **重构方案**: 具体的简化步骤和代码示例

请用中文回答。""",
    ),

    AnalysisType.SECURITY: PromptTemplate(
        name="安全分析",
        analysis_type=AnalysisType.SECURITY,
        description="检测潜在的安全漏洞",
        template="""你是一个安全审计专家。请分析以下代码的安全性。

## 代码信息
- 文件: {file_path}
- 语言: {language}

## 代码内容
```{language}
{code}
```

## 导入的模块
{imports}

请检查以下安全问题：
1. **注入漏洞**: SQL 注入、命令注入、XSS 等
2. **敏感数据**: 硬编码密码、密钥泄露
3. **输入验证**: 是否正确验证用户输入
4. **权限问题**: 不安全的文件操作、权限提升
5. **依赖风险**: 使用的库是否有已知漏洞

对于每个发现的问题，请提供：
- 风险等级（高/中/低）
- 问题位置
- 修复建议

请用中文回答。""",
    ),

    AnalysisType.PERFORMANCE: PromptTemplate(
        name="性能分析",
        analysis_type=AnalysisType.PERFORMANCE,
        description="分析性能瓶颈并提供优化建议",
        template="""你是一个性能优化专家。请分析以下代码的性能问题。

## 代码信息
- 文件: {file_path}
- 语言: {language}

## 代码内容
```{language}
{code}
```

## AST 分析结果
{ast_summary}

请分析：
1. **时间复杂度**: 算法效率，是否有 O(n²) 或更差的操作
2. **空间复杂度**: 内存使用，是否有不必要的数据复制
3. **I/O 操作**: 文件、网络操作是否高效
4. **循环优化**: 是否有可以向量化或并行化的循环
5. **缓存机会**: 是否有重复计算可以缓存

对于每个问题，请提供具体的优化代码示例。

请用中文回答。""",
    ),

    AnalysisType.REFACTOR: PromptTemplate(
        name="重构建议",
        analysis_type=AnalysisType.REFACTOR,
        description="提供代码重构方案",
        template="""你是一个重构专家。请为以下代码提供重构建议。

## 代码信息
- 文件: {file_path}
- 语言: {language}

## 代码内容
```{language}
{code}
```

## 当前问题
{lint_results}

请提供重构方案：
1. **设计模式**: 是否可以应用合适的设计模式
2. **函数拆分**: 过长的函数如何拆分
3. **类重组**: 类的职责是否单一，是否需要拆分或合并
4. **代码复用**: 是否有重复代码可以提取
5. **接口优化**: API 设计是否合理

请提供重构前后的代码对比。

请用中文回答。""",
    ),

    AnalysisType.EXPLAIN: PromptTemplate(
        name="代码解释",
        analysis_type=AnalysisType.EXPLAIN,
        description="解释代码的功能和逻辑",
        template="""请解释以下代码的功能和实现逻辑。

## 代码信息
- 文件: {file_path}
- 语言: {language}

## 代码内容
```{language}
{code}
```

请提供：
1. **功能概述**: 这段代码的主要功能是什么
2. **执行流程**: 代码的执行步骤
3. **关键逻辑**: 核心算法或业务逻辑的解释
4. **输入输出**: 函数的参数和返回值说明
5. **依赖关系**: 与其他模块的关系

请用中文回答，适合初学者理解。""",
    ),

    AnalysisType.DOCSTRING: PromptTemplate(
        name="文档生成",
        analysis_type=AnalysisType.DOCSTRING,
        description="为代码生成文档字符串",
        template="""请为以下代码生成文档字符串（docstring）。

## 代码信息
- 语言: {language}

## 代码内容
```{language}
{code}
```

请为每个函数和类生成符合 {language} 规范的文档字符串，包括：
1. 功能描述
2. 参数说明（类型和含义）
3. 返回值说明
4. 异常说明（如果有）
5. 使用示例（如果合适）

请直接输出带有文档字符串的完整代码。""",
    ),
}


class PromptBuilder:
    """Prompt 构建器"""

    def __init__(self):
        self.templates = PROMPTS.copy()

    def get_template(self, analysis_type: AnalysisType) -> PromptTemplate:
        """获取模板"""
        return self.templates[analysis_type]

    def build(
        self,
        analysis_type: AnalysisType,
        code: str,
        file_path: str = "",
        language: str = "python",
        total_lines: int = 0,
        code_lines: int = 0,
        ast_summary: str = "",
        lint_results: str = "",
        complexity_info: str = "",
        imports: str = "",
        **kwargs
    ) -> str:
        """
        构建 Prompt

        Args:
            analysis_type: 分析类型
            code: 代码内容
            file_path: 文件路径
            language: 编程语言
            total_lines: 总行数
            code_lines: 代码行数
            ast_summary: AST 分析摘要
            lint_results: 规则检查结果
            complexity_info: 复杂度信息
            imports: 导入列表
            **kwargs: 其他参数

        Returns:
            str: 构建好的 Prompt
        """
        template = self.templates[analysis_type]
        return template.template.format(
            code=code,
            file_path=file_path or "未知",
            language=language,
            total_lines=total_lines,
            code_lines=code_lines,
            ast_summary=ast_summary or "无",
            lint_results=lint_results or "无",
            complexity_info=complexity_info or "无",
            imports=imports or "无",
            **kwargs
        )

    def register_template(self, analysis_type: AnalysisType, template: PromptTemplate) -> None:
        """注册自定义模板"""
        self.templates[analysis_type] = template

    def list_templates(self) -> list:
        """列出所有模板"""
        return [
            {
                "type": t.analysis_type.value,
                "name": t.name,
                "description": t.description,
            }
            for t in self.templates.values()
        ]

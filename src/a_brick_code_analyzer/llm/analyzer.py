"""
LLM 代码分析器
结合 AST 解析结果和 LLM 进行智能代码分析
"""

from typing import Optional, List, Union
from pathlib import Path

from .base import LLMConfig, LLMResponse
from .ollama_client import OllamaClient, RECOMMENDED_MODELS
from .prompts import PromptBuilder, AnalysisType

from ..base import ParseResult, CodeNode, NodeType
from ..factory import ParserFactory
from ..rules import RuleEngine, LintResult


class CodeAnalyzer:
    """
    LLM 代码分析器

    结合 AST 解析和 LLM 进行智能代码分析
    """

    def __init__(
        self,
        model: Optional[str] = None,
        config: Optional[LLMConfig] = None,
        client: Optional[OllamaClient] = None,
    ):
        """
        初始化分析器

        Args:
            model: 模型名称，如 "qwen2.5-coder:7b"
            config: LLM 配置
            client: 已有的 Ollama 客户端实例
        """
        if client:
            self.client = client
        else:
            self.client = OllamaClient(config=config, model=model)

        self.prompt_builder = PromptBuilder()
        self.parser_factory = ParserFactory()
        self.rule_engine = RuleEngine()
        self.rule_engine.use_preset("recommended")

    def set_model(self, model: str) -> None:
        """切换模型"""
        self.client.set_model(model)

    def get_model(self) -> str:
        """获取当前模型"""
        return self.client.get_current_model()

    def is_available(self) -> bool:
        """检查 LLM 服务是否可用"""
        return self.client.is_available()

    def _format_ast_summary(self, parse_result: ParseResult) -> str:
        """格式化 AST 分析摘要"""
        lines = []

        functions = parse_result.get_functions()
        if functions:
            lines.append(f"### 函数 ({len(functions)} 个)")
            for func in functions:
                complexity_tag = f" [复杂度: {func.complexity}]" if func.complexity > 0 else ""
                params = ", ".join(func.params) if func.params else ""
                lines.append(f"- `{func.name}({params})`{complexity_tag} (行 {func.line_start}-{func.line_end})")

        classes = parse_result.get_classes()
        if classes:
            lines.append(f"\n### 类 ({len(classes)} 个)")
            for cls in classes:
                lines.append(f"- `{cls.name}` (行 {cls.line_start}-{cls.line_end})")

        methods = parse_result.get_methods()
        if methods:
            lines.append(f"\n### 方法 ({len(methods)} 个)")
            for method in methods:
                complexity_tag = f" [复杂度: {method.complexity}]" if method.complexity > 0 else ""
                lines.append(f"- `{method.name}`{complexity_tag}")

        return "\n".join(lines) if lines else "无结构信息"

    def _format_lint_results(self, lint_result: LintResult) -> str:
        """格式化规则检查结果"""
        if not lint_result.violations:
            return "无违规"

        lines = [f"共 {lint_result.total_violations} 个问题 (错误: {lint_result.error_count}, 警告: {lint_result.warning_count})"]
        for v in lint_result.violations:
            lines.append(f"- [{v.severity.name}] 行 {v.line}: {v.message} ({v.rule_id})")

        return "\n".join(lines)

    def _format_complexity_info(self, parse_result: ParseResult, threshold: int = 5) -> str:
        """格式化复杂度信息"""
        high_complexity = []

        for node in parse_result.nodes:
            if node.node_type in (NodeType.FUNCTION, NodeType.METHOD) and node.complexity > threshold:
                high_complexity.append(node)

        if not high_complexity:
            return "无高复杂度函数"

        lines = []
        for node in sorted(high_complexity, key=lambda x: x.complexity, reverse=True):
            lines.append(f"- `{node.name}`: 复杂度 {node.complexity} (行 {node.line_start}-{node.line_end})")

        return "\n".join(lines)

    def analyze(
        self,
        code: str,
        analysis_type: AnalysisType = AnalysisType.CODE_REVIEW,
        file_path: str = "",
        language: Optional[str] = None,
    ) -> LLMResponse:
        """
        分析代码

        Args:
            code: 代码内容
            analysis_type: 分析类型
            file_path: 文件路径
            language: 编程语言，如果不指定则自动检测

        Returns:
            LLMResponse: LLM 分析结果
        """
        # 自动检测语言
        if language is None:
            if file_path:
                ext = Path(file_path).suffix
                language = self.parser_factory._extension_map.get(ext, "python")
            else:
                language = "python"

        # 解析代码
        try:
            parser = self.parser_factory.get_parser(language)
            parse_result = parser.parse(code, file_path)
        except Exception as e:
            parse_result = ParseResult(
                file_path=file_path,
                language=language,
                errors=[str(e)]
            )

        # 规则检查
        lint_result = self.rule_engine.lint(parse_result)

        # 构建 Prompt
        prompt = self.prompt_builder.build(
            analysis_type=analysis_type,
            code=code,
            file_path=file_path,
            language=language,
            total_lines=parse_result.total_lines,
            code_lines=parse_result.code_lines,
            ast_summary=self._format_ast_summary(parse_result),
            lint_results=self._format_lint_results(lint_result),
            complexity_info=self._format_complexity_info(parse_result),
            imports=", ".join(parse_result.imports) if parse_result.imports else "无",
        )

        # 调用 LLM
        return self.client.generate(prompt)

    def analyze_file(
        self,
        file_path: Union[str, Path],
        analysis_type: AnalysisType = AnalysisType.CODE_REVIEW,
    ) -> LLMResponse:
        """
        分析文件

        Args:
            file_path: 文件路径
            analysis_type: 分析类型

        Returns:
            LLMResponse: LLM 分析结果
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        code = file_path.read_text(encoding="utf-8")
        return self.analyze(
            code=code,
            analysis_type=analysis_type,
            file_path=str(file_path),
        )

    def review(self, code: str, file_path: str = "") -> LLMResponse:
        """代码审查（快捷方法）"""
        return self.analyze(code, AnalysisType.CODE_REVIEW, file_path)

    def explain(self, code: str, file_path: str = "") -> LLMResponse:
        """代码解释（快捷方法）"""
        return self.analyze(code, AnalysisType.EXPLAIN, file_path)

    def check_security(self, code: str, file_path: str = "") -> LLMResponse:
        """安全检查（快捷方法）"""
        return self.analyze(code, AnalysisType.SECURITY, file_path)

    def suggest_refactor(self, code: str, file_path: str = "") -> LLMResponse:
        """重构建议（快捷方法）"""
        return self.analyze(code, AnalysisType.REFACTOR, file_path)

    def analyze_complexity(self, code: str, file_path: str = "") -> LLMResponse:
        """复杂度分析（快捷方法）"""
        return self.analyze(code, AnalysisType.COMPLEXITY, file_path)

    def optimize_performance(self, code: str, file_path: str = "") -> LLMResponse:
        """性能优化（快捷方法）"""
        return self.analyze(code, AnalysisType.PERFORMANCE, file_path)

    def generate_docs(self, code: str, file_path: str = "") -> LLMResponse:
        """生成文档（快捷方法）"""
        return self.analyze(code, AnalysisType.DOCSTRING, file_path)

    def chat(self, message: str, code: Optional[str] = None) -> LLMResponse:
        """
        自由对话模式

        Args:
            message: 用户消息
            code: 可选的代码上下文

        Returns:
            LLMResponse: LLM 响应
        """
        if code:
            full_message = f"{message}\n\n```\n{code}\n```"
        else:
            full_message = message

        return self.client.chat([{"role": "user", "content": full_message}])

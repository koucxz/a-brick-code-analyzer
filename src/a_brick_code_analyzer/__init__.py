"""
AST 解析模块
提供代码解析、结构分析、规则引擎和 LLM 集成功能
"""

from .base import BaseParser, ParseResult, NodeType, CodeNode
from .python_parser import PythonParser
from .factory import ParserFactory
from .rules import (
    RuleEngine,
    RuleConfig,
    BaseRule,
    NodeRule,
    Severity,
    RuleViolation,
    LintResult,
    LintReport,
)
from .llm import (
    CodeAnalyzer,
    OllamaClient,
    LLMConfig,
    LLMResponse,
    AnalysisType,
    RECOMMENDED_MODELS,
    select_model_interactive,
)

__all__ = [
    # 解析器
    'BaseParser',
    'ParseResult',
    'NodeType',
    'CodeNode',
    'PythonParser',
    'ParserFactory',

    # 规则引擎
    'RuleEngine',
    'RuleConfig',
    'BaseRule',
    'NodeRule',
    'Severity',
    'RuleViolation',
    'LintResult',
    'LintReport',

    # LLM 集成
    'CodeAnalyzer',
    'OllamaClient',
    'LLMConfig',
    'LLMResponse',
    'AnalysisType',
    'RECOMMENDED_MODELS',
    'select_model_interactive',
]

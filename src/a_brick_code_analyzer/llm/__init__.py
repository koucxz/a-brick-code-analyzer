"""
LLM 集成模块
提供基于 Ollama 的本地 LLM 代码分析功能
"""

from .base import (
    BaseLLMClient,
    LLMConfig,
    LLMResponse,
    ModelInfo,
    ModelProvider,
)
from .ollama_client import (
    OllamaClient,
    RECOMMENDED_MODELS,
    DEFAULT_MODEL,
    select_model_interactive,
)
from .prompts import (
    PromptBuilder,
    PromptTemplate,
    AnalysisType,
)
from .analyzer import CodeAnalyzer

__all__ = [
    # 基类
    "BaseLLMClient",
    "LLMConfig",
    "LLMResponse",
    "ModelInfo",
    "ModelProvider",
    # Ollama 客户端
    "OllamaClient",
    "RECOMMENDED_MODELS",
    "DEFAULT_MODEL",
    "select_model_interactive",
    # Prompt
    "PromptBuilder",
    "PromptTemplate",
    "AnalysisType",
    # 分析器
    "CodeAnalyzer",
]

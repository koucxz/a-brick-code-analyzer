"""
LLM 客户端抽象基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class ModelProvider(Enum):
    """模型提供者"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    CUSTOM = "custom"


@dataclass
class ModelInfo:
    """模型信息"""
    name: str
    provider: ModelProvider
    size: Optional[str] = None  # 如 "7B", "14B"
    description: Optional[str] = None
    context_length: int = 4096
    supports_chinese: bool = True


@dataclass
class LLMResponse:
    """LLM 响应结果"""
    content: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMConfig:
    """LLM 配置"""
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    timeout: int = 120  # 秒
    base_url: Optional[str] = None
    api_key: Optional[str] = None


class BaseLLMClient(ABC):
    """LLM 客户端基类"""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        生成文本

        Args:
            prompt: 提示词
            **kwargs: 额外参数

        Returns:
            LLMResponse: 生成结果
        """
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """
        对话模式

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            **kwargs: 额外参数

        Returns:
            LLMResponse: 生成结果
        """
        pass

    @abstractmethod
    def list_models(self) -> List[ModelInfo]:
        """
        列出可用模型

        Returns:
            List[ModelInfo]: 模型列表
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查服务是否可用

        Returns:
            bool: 是否可用
        """
        pass

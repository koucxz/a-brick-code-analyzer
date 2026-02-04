"""
Ollama 客户端实现
"""

import json
import time
from typing import List, Dict, Any, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from .base import (
    BaseLLMClient,
    LLMConfig,
    LLMResponse,
    ModelInfo,
    ModelProvider,
)


# 默认模型
DEFAULT_MODEL = "llama3.2:3b"

# 推荐的代码分析模型（2025 年更新）
RECOMMENDED_MODELS = {
    "qwen3-coder": ModelInfo(
        name="qwen3-coder",
        provider=ModelProvider.OLLAMA,
        size="30B",
        description="Qwen3 代码专用，效果最好，需 24GB+ 显存",
        context_length=128000,
        supports_chinese=True,
    ),
    "deepseek-r1": ModelInfo(
        name="deepseek-r1",
        provider=ModelProvider.OLLAMA,
        size="7.6B",
        description="DeepSeek R1，推理能力强，性价比高",
        context_length=128000,
        supports_chinese=True,
    ),
    "qwen3:8b": ModelInfo(
        name="qwen3:8b",
        provider=ModelProvider.OLLAMA,
        size="8B",
        description="Qwen3 通用模型，支持思考链",
        context_length=128000,
        supports_chinese=True,
    ),
    "deepseek-coder-v2:16b": ModelInfo(
        name="deepseek-coder-v2:16b",
        provider=ModelProvider.OLLAMA,
        size="16B",
        description="DeepSeek Coder V2，代码专用",
        context_length=128000,
        supports_chinese=True,
    ),
    "codellama:7b": ModelInfo(
        name="codellama:7b",
        provider=ModelProvider.OLLAMA,
        size="7B",
        description="Meta CodeLlama，经典代码模型",
        context_length=16384,
        supports_chinese=False,
    ),
    "llama3.2:3b": ModelInfo(
        name="llama3.2:3b",
        provider=ModelProvider.OLLAMA,
        size="3B",
        description="Meta Llama 3.2，轻量快速，入门推荐",
        context_length=128000,
        supports_chinese=False,
    ),
}


class OllamaClient(BaseLLMClient):
    """Ollama 客户端"""

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, config: Optional[LLMConfig] = None, model: Optional[str] = None):
        """
        初始化 Ollama 客户端

        Args:
            config: LLM 配置，如果不提供则使用默认配置
            model: 模型名称，如果提供则覆盖 config 中的模型
        """
        if config is None:
            config = LLMConfig(model=model or DEFAULT_MODEL)
        elif model:
            config.model = model

        if config.base_url is None:
            config.base_url = self.DEFAULT_BASE_URL

        super().__init__(config)

    def _request(self, endpoint: str, data: Optional[Dict] = None, method: str = "GET") -> Dict:
        """发送 HTTP 请求"""
        url = f"{self.config.base_url}{endpoint}"

        if data:
            body = json.dumps(data).encode("utf-8")
            req = Request(url, data=body, method=method)
            req.add_header("Content-Type", "application/json")
        else:
            req = Request(url, method=method)

        try:
            with urlopen(req, timeout=self.config.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            raise ConnectionError(f"HTTP 错误 {e.code}: {e.reason}")
        except URLError as e:
            raise ConnectionError(f"无法连接到 Ollama 服务: {e.reason}")

    def _stream_request(self, endpoint: str, data: Dict) -> str:
        """发送流式请求并收集完整响应"""
        url = f"{self.config.base_url}{endpoint}"
        body = json.dumps(data).encode("utf-8")
        req = Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")

        full_response = ""
        try:
            with urlopen(req, timeout=self.config.timeout) as response:
                for line in response:
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        if "response" in chunk:
                            full_response += chunk["response"]
                        elif "message" in chunk:
                            full_response += chunk["message"].get("content", "")
        except HTTPError as e:
            raise ConnectionError(f"HTTP 错误 {e.code}: {e.reason}")
        except URLError as e:
            raise ConnectionError(f"无法连接到 Ollama 服务: {e.reason}")

        return full_response

    def is_available(self) -> bool:
        """检查 Ollama 服务是否可用"""
        try:
            self._request("/api/tags")
            return True
        except Exception:
            return False

    def list_models(self) -> List[ModelInfo]:
        """列出已安装的模型"""
        try:
            response = self._request("/api/tags")
            models = []
            for model_data in response.get("models", []):
                name = model_data.get("name", "")
                # 如果是推荐模型，使用预定义信息
                if name in RECOMMENDED_MODELS:
                    models.append(RECOMMENDED_MODELS[name])
                else:
                    # 否则创建基本信息
                    models.append(ModelInfo(
                        name=name,
                        provider=ModelProvider.OLLAMA,
                        size=model_data.get("details", {}).get("parameter_size"),
                        description=model_data.get("details", {}).get("family"),
                    ))
            return models
        except Exception:
            return []

    def list_recommended_models(self) -> List[ModelInfo]:
        """列出推荐的代码分析模型"""
        return list(RECOMMENDED_MODELS.values())

    def pull_model(self, model_name: str) -> bool:
        """
        下载模型

        Args:
            model_name: 模型名称

        Returns:
            bool: 是否成功
        """
        try:
            # 注意：这是一个长时间操作，实际使用时应该用流式处理显示进度
            self._request("/api/pull", {"name": model_name}, method="POST")
            return True
        except Exception:
            return False

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本"""
        start_time = time.time()

        data = {
            "model": kwargs.get("model", self.config.model),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
            }
        }

        response = self._request("/api/generate", data, method="POST")
        duration_ms = (time.time() - start_time) * 1000

        return LLMResponse(
            content=response.get("response", ""),
            model=response.get("model", self.config.model),
            prompt_tokens=response.get("prompt_eval_count"),
            completion_tokens=response.get("eval_count"),
            total_tokens=(response.get("prompt_eval_count", 0) or 0) +
                        (response.get("eval_count", 0) or 0),
            duration_ms=duration_ms,
            metadata={
                "done": response.get("done"),
                "context": response.get("context"),
            }
        )

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """对话模式"""
        start_time = time.time()

        data = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
            }
        }

        response = self._request("/api/chat", data, method="POST")
        duration_ms = (time.time() - start_time) * 1000

        message = response.get("message", {})

        return LLMResponse(
            content=message.get("content", ""),
            model=response.get("model", self.config.model),
            prompt_tokens=response.get("prompt_eval_count"),
            completion_tokens=response.get("eval_count"),
            total_tokens=(response.get("prompt_eval_count", 0) or 0) +
                        (response.get("eval_count", 0) or 0),
            duration_ms=duration_ms,
            metadata={
                "done": response.get("done"),
            }
        )

    def set_model(self, model: str) -> None:
        """切换模型"""
        self.config.model = model

    def get_current_model(self) -> str:
        """获取当前模型"""
        return self.config.model


def select_model_interactive() -> str:
    """
    交互式选择模型

    Returns:
        str: 选择的模型名称
    """
    print("\n可用的代码分析模型：")
    print("-" * 60)

    models = list(RECOMMENDED_MODELS.values())
    for i, model in enumerate(models, 1):
        chinese_tag = "✓ 中文" if model.supports_chinese else "✗ 英文"
        print(f"  {i}. {model.name}")
        print(f"     {model.description}")
        print(f"     参数量: {model.size} | 上下文: {model.context_length} | {chinese_tag}")
        print()

    while True:
        try:
            choice = input("请选择模型 (输入数字，默认 1): ").strip()
            if not choice:
                choice = "1"
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                selected = models[idx].name
                print(f"\n已选择: {selected}")
                return selected
            else:
                print("无效选择，请重试")
        except ValueError:
            print("请输入有效数字")
        except KeyboardInterrupt:
            print("\n已取消")
            return models[0].name

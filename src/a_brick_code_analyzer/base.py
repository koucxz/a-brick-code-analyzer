"""
基础解析器抽象类和数据结构
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class NodeType(Enum):
    """AST 节点类型"""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    MODULE = "module"


@dataclass
class CodeNode:
    """代码节点信息"""
    node_type: NodeType
    name: str
    line_start: int
    line_end: int
    complexity: int = 0
    params: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParseResult:
    """解析结果"""
    file_path: str
    language: str
    nodes: List[CodeNode] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    errors: List[str] = field(default_factory=list)

    def get_functions(self) -> List[CodeNode]:
        """获取所有函数节点"""
        return [node for node in self.nodes if node.node_type == NodeType.FUNCTION]

    def get_classes(self) -> List[CodeNode]:
        """获取所有类节点"""
        return [node for node in self.nodes if node.node_type == NodeType.CLASS]

    def get_methods(self) -> List[CodeNode]:
        """获取所有方法节点"""
        return [node for node in self.nodes if node.node_type == NodeType.METHOD]


class BaseParser(ABC):
    """解析器基类"""

    @abstractmethod
    def parse(self, code: str, file_path: str = "") -> ParseResult:
        """
        解析代码

        Args:
            code: 源代码字符串
            file_path: 文件路径（可选）

        Returns:
            ParseResult: 解析结果
        """
        pass

    @abstractmethod
    def parse_file(self, file_path: str) -> ParseResult:
        """
        解析文件

        Args:
            file_path: 文件路径

        Returns:
            ParseResult: 解析结果
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        获取支持的文件扩展名

        Returns:
            List[str]: 扩展名列表
        """
        pass

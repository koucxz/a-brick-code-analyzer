"""
规则引擎基础类和数据结构
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Type, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from ..base import ParseResult, CodeNode, NodeType


class Severity(Enum):
    """规则严重级别（ESLint 风格）"""
    OFF = 0      # 禁用
    WARN = 1     # 警告
    ERROR = 2    # 错误


@dataclass
class RuleViolation:
    """规则违规信息"""
    rule_id: str                    # 规则 ID，如 "complexity/max-complexity"
    severity: Severity              # 严重级别
    message: str                    # 可读消息
    file_path: str                  # 文件路径
    line_start: int                 # 起始行号
    line_end: int                   # 结束行号
    column_start: Optional[int] = None  # 起始列（可选）
    column_end: Optional[int] = None    # 结束列（可选）
    node_name: Optional[str] = None     # 代码节点名称
    node_type: Optional[str] = None     # 代码节点类型
    suggestion: Optional[str] = None    # 修复建议
    metadata: Dict[str, Any] = field(default_factory=dict)  # 额外元数据


class BaseRule(ABC):
    """规则抽象基类"""

    # 规则元数据（子类需要覆盖）
    rule_id: str = ""           # 唯一标识，如 "complexity/max-complexity"
    name: str = ""              # 可读名称
    description: str = ""       # 详细描述
    category: str = ""          # 分类：complexity, naming, structure 等
    default_severity: Severity = Severity.WARN
    default_options: Dict[str, Any] = {}

    # 支持的语言（空列表表示支持所有语言）
    supported_languages: List[str] = []

    def __init__(self, severity: Severity = None, options: Dict[str, Any] = None):
        self.severity = severity if severity is not None else self.default_severity
        self.options = {**self.default_options, **(options or {})}

    @abstractmethod
    def check(self, parse_result: 'ParseResult') -> List[RuleViolation]:
        """
        检查解析结果中的违规

        Args:
            parse_result: 代码解析结果

        Returns:
            违规列表
        """
        pass

    def is_enabled(self) -> bool:
        """检查规则是否启用"""
        return self.severity != Severity.OFF

    def supports_language(self, language: str) -> bool:
        """检查规则是否支持指定语言"""
        if not self.supported_languages:
            return True
        return language.lower() in [lang.lower() for lang in self.supported_languages]

    def create_violation(
        self,
        message: str,
        file_path: str,
        line_start: int,
        line_end: int,
        **kwargs
    ) -> RuleViolation:
        """创建违规的辅助方法"""
        return RuleViolation(
            rule_id=self.rule_id,
            severity=self.severity,
            message=message,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            **kwargs
        )


class NodeRule(BaseRule):
    """基于节点的规则便捷基类"""

    # 此规则适用的节点类型
    target_node_types: List['NodeType'] = []

    def check(self, parse_result: 'ParseResult') -> List[RuleViolation]:
        """检查解析结果中所有相关节点"""
        violations = []

        if not self.supports_language(parse_result.language):
            return violations

        for node in parse_result.nodes:
            if self._should_check_node(node):
                node_violations = self.check_node(node, parse_result)
                violations.extend(node_violations)

        return violations

    def _should_check_node(self, node: 'CodeNode') -> bool:
        """判断是否应该检查此节点"""
        if not self.target_node_types:
            return True
        return node.node_type in self.target_node_types

    @abstractmethod
    def check_node(self, node: 'CodeNode', parse_result: 'ParseResult') -> List[RuleViolation]:
        """
        检查单个节点

        Args:
            node: 代码节点
            parse_result: 完整解析结果（用于上下文）

        Returns:
            此节点的违规列表
        """
        pass

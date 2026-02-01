"""
规则引擎模块
提供可自定义的代码质量规则检查
"""

from .base import Severity, RuleViolation, BaseRule, NodeRule
from .result import LintResult, LintReport
from .config import RuleConfig
from .engine import RuleEngine

__all__ = [
    # 核心类
    'RuleEngine',
    'RuleConfig',

    # 基础类
    'BaseRule',
    'NodeRule',
    'Severity',
    'RuleViolation',

    # 结果类
    'LintResult',
    'LintReport',
]

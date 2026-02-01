"""
内置规则模块
"""

from typing import List, Type

from ..base import BaseRule
from .complexity import COMPLEXITY_RULES
from .naming import NAMING_RULES
from .structure import STRUCTURE_RULES


def get_all_builtin_rules() -> List[Type[BaseRule]]:
    """获取所有内置规则类"""
    return [
        *COMPLEXITY_RULES,
        *NAMING_RULES,
        *STRUCTURE_RULES,
    ]


# 导出所有规则类
__all__ = [
    'get_all_builtin_rules',
    'COMPLEXITY_RULES',
    'NAMING_RULES',
    'STRUCTURE_RULES',
]

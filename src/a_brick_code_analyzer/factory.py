"""
解析器工厂
根据文件类型自动选择合适的解析器
"""

from pathlib import Path
from typing import Optional

from .base import BaseParser
from .python_parser import PythonParser

# 可选的 JavaScript/TypeScript 支持
try:
    from .javascript_parser import JavaScriptParser, TypeScriptParser
    JAVASCRIPT_SUPPORT = True
except ImportError:
    JAVASCRIPT_SUPPORT = False


class ParserFactory:
    """解析器工厂类"""

    # 注册的解析器
    _parsers = {
        'python': PythonParser,
    }

    # 文件扩展名到语言的映射
    _extension_map = {
        '.py': 'python',
    }

    # 动态注册 JavaScript/TypeScript 解析器（如果可用）
    if JAVASCRIPT_SUPPORT:
        _parsers.update({
            'javascript': JavaScriptParser,
            'typescript': TypeScriptParser,
        })
        _extension_map.update({
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
        })

    @classmethod
    def get_parser(cls, language: str) -> Optional[BaseParser]:
        """
        根据语言获取解析器

        Args:
            language: 编程语言名称

        Returns:
            BaseParser: 解析器实例，如果不支持则返回 None
        """
        parser_class = cls._parsers.get(language.lower())
        if parser_class:
            return parser_class()
        return None

    @classmethod
    def get_parser_by_file(cls, file_path: str) -> Optional[BaseParser]:
        """
        根据文件路径自动选择解析器

        Args:
            file_path: 文件路径

        Returns:
            BaseParser: 解析器实例，如果不支持则返回 None
        """
        ext = Path(file_path).suffix.lower()
        language = cls._extension_map.get(ext)
        if language:
            return cls.get_parser(language)
        return None

    @classmethod
    def register_parser(cls, language: str, parser_class: type, extensions: list):
        """
        注册新的解析器

        Args:
            language: 语言名称
            parser_class: 解析器类
            extensions: 支持的文件扩展名列表
        """
        cls._parsers[language.lower()] = parser_class
        for ext in extensions:
            cls._extension_map[ext.lower()] = language.lower()

    @classmethod
    def get_supported_languages(cls) -> list:
        """
        获取所有支持的语言

        Returns:
            list: 支持的语言列表
        """
        return list(cls._parsers.keys())

    @classmethod
    def get_supported_extensions(cls) -> list:
        """
        获取所有支持的文件扩展名

        Returns:
            list: 支持的扩展名列表
        """
        return list(cls._extension_map.keys())

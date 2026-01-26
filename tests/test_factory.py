"""
测试解析器工厂
"""

import unittest
from a_brick_code_analyzer import ParserFactory, PythonParser


class TestParserFactory(unittest.TestCase):
    """测试解析器工厂"""

    def test_get_parser_by_language(self):
        """测试根据语言获取解析器"""
        parser = ParserFactory.get_parser('python')
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, PythonParser)

    def test_get_parser_by_file(self):
        """测试根据文件路径获取解析器"""
        parser = ParserFactory.get_parser_by_file('test.py')
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, PythonParser)

    def test_unsupported_language(self):
        """测试不支持的语言"""
        parser = ParserFactory.get_parser('unknown')
        self.assertIsNone(parser)

    def test_unsupported_file_extension(self):
        """测试不支持的文件扩展名"""
        parser = ParserFactory.get_parser_by_file('test.xyz')
        self.assertIsNone(parser)

    def test_get_supported_languages(self):
        """测试获取支持的语言列表"""
        languages = ParserFactory.get_supported_languages()
        self.assertIn('python', languages)
        self.assertIsInstance(languages, list)

    def test_get_supported_extensions(self):
        """测试获取支持的扩展名列表"""
        extensions = ParserFactory.get_supported_extensions()
        self.assertIn('.py', extensions)
        self.assertIsInstance(extensions, list)


if __name__ == '__main__':
    unittest.main()

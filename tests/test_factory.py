"""
测试解析器工厂
"""

import unittest
from a_brick_code_analyzer import ParserFactory, PythonParser

# 检查是否支持 JavaScript/TypeScript
try:
    from a_brick_code_analyzer import JavaScriptParser, TypeScriptParser
    JAVASCRIPT_SUPPORT = True
except ImportError:
    JAVASCRIPT_SUPPORT = False


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

    @unittest.skipUnless(JAVASCRIPT_SUPPORT, "JavaScript support not available")
    def test_get_javascript_parser_by_language(self):
        """测试根据语言获取 JavaScript 解析器"""
        parser = ParserFactory.get_parser('javascript')
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, JavaScriptParser)

    @unittest.skipUnless(JAVASCRIPT_SUPPORT, "JavaScript support not available")
    def test_get_typescript_parser_by_language(self):
        """测试根据语言获取 TypeScript 解析器"""
        parser = ParserFactory.get_parser('typescript')
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, TypeScriptParser)

    @unittest.skipUnless(JAVASCRIPT_SUPPORT, "JavaScript support not available")
    def test_get_javascript_parser_by_file(self):
        """测试根据文件路径获取 JavaScript 解析器"""
        parser = ParserFactory.get_parser_by_file('test.js')
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, JavaScriptParser)

    @unittest.skipUnless(JAVASCRIPT_SUPPORT, "JavaScript support not available")
    def test_get_typescript_parser_by_file(self):
        """测试根据文件路径获取 TypeScript 解析器"""
        parser = ParserFactory.get_parser_by_file('test.ts')
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, TypeScriptParser)

    @unittest.skipUnless(JAVASCRIPT_SUPPORT, "JavaScript support not available")
    def test_get_supported_languages_with_js_ts(self):
        """测试获取支持的语言列表（包含 JS/TS）"""
        languages = ParserFactory.get_supported_languages()
        self.assertIn('python', languages)
        self.assertIn('javascript', languages)
        self.assertIn('typescript', languages)
        self.assertIsInstance(languages, list)

    @unittest.skipUnless(JAVASCRIPT_SUPPORT, "JavaScript support not available")
    def test_get_supported_extensions_with_js_ts(self):
        """测试获取支持的扩展名列表（包含 JS/TS）"""
        extensions = ParserFactory.get_supported_extensions()
        self.assertIn('.py', extensions)
        self.assertIn('.js', extensions)
        self.assertIn('.jsx', extensions)
        self.assertIn('.ts', extensions)
        self.assertIn('.tsx', extensions)
        self.assertIsInstance(extensions, list)


if __name__ == '__main__':
    unittest.main()

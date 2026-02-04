"""
LLM 代码分析示例

使用前请确保：
1. 安装 Ollama: https://ollama.com/download
2. 下载模型: ollama pull llama3.2:3b
3. 启动服务: ollama serve (通常安装后自动启动)
"""

from a_brick_code_analyzer import (
    CodeAnalyzer,
    OllamaClient,
    AnalysisType,
    RECOMMENDED_MODELS,
    select_model_interactive,
)
from a_brick_code_analyzer.llm import DEFAULT_MODEL


def example_basic_usage():
    """基础用法示例"""
    print("=" * 60)
    print("示例 1: 基础用法")
    print("=" * 60)

    # 创建分析器，使用默认模型
    analyzer = CodeAnalyzer(model=DEFAULT_MODEL)

    # 检查服务是否可用
    if not analyzer.is_available():
        print("错误: Ollama 服务未启动")
        print("请运行: ollama serve")
        return

    # 要分析的代码
    code = '''
def calculate_discount(price, discount_type, user_level, is_vip, has_coupon):
    if discount_type == "percentage":
        if user_level > 5:
            if is_vip:
                if has_coupon:
                    return price * 0.5
                else:
                    return price * 0.6
            else:
                if has_coupon:
                    return price * 0.7
                else:
                    return price * 0.8
        else:
            if is_vip:
                return price * 0.85
            else:
                return price * 0.9
    else:
        if user_level > 5:
            return price - 50
        else:
            return price - 20
'''

    print("\n正在分析代码...")
    result = analyzer.review(code)
    print("\n分析结果:")
    print("-" * 40)
    print(result.content)
    print("-" * 40)
    print(f"耗时: {result.duration_ms:.0f}ms")
    print(f"Token: {result.total_tokens}")


def example_select_model():
    """交互式选择模型示例"""
    print("=" * 60)
    print("示例 2: 选择模型")
    print("=" * 60)

    # 方式 1: 交互式选择
    # model = select_model_interactive()

    # 方式 2: 查看推荐模型
    print("\n推荐的代码分析模型:")
    for name, info in RECOMMENDED_MODELS.items():
        print(f"  - {name}: {info.description}")

    # 方式 3: 查看已安装的模型
    client = OllamaClient()
    if client.is_available():
        print("\n已安装的模型:")
        for model in client.list_models():
            print(f"  - {model.name}")


def example_different_analysis_types():
    """不同分析类型示例"""
    print("=" * 60)
    print("示例 3: 不同分析类型")
    print("=" * 60)

    analyzer = CodeAnalyzer(model=DEFAULT_MODEL)

    if not analyzer.is_available():
        print("错误: Ollama 服务未启动")
        return

    code = '''
import os
import subprocess

def run_command(user_input):
    # 危险: 命令注入漏洞
    result = subprocess.run(user_input, shell=True, capture_output=True)
    return result.stdout.decode()

def read_file(filename):
    # 危险: 路径遍历漏洞
    with open(f"/data/{filename}", "r") as f:
        return f.read()
'''

    print("\n可用的分析类型:")
    for t in AnalysisType:
        print(f"  - {t.value}")

    print("\n正在进行安全分析...")
    result = analyzer.check_security(code)
    print("\n安全分析结果:")
    print("-" * 40)
    print(result.content)


def example_analyze_file():
    """分析文件示例"""
    print("=" * 60)
    print("示例 4: 分析文件")
    print("=" * 60)

    analyzer = CodeAnalyzer(model=DEFAULT_MODEL)

    if not analyzer.is_available():
        print("错误: Ollama 服务未启动")
        return

    # 分析当前文件
    import os
    current_file = os.path.abspath(__file__)

    print(f"\n正在分析文件: {current_file}")
    result = analyzer.analyze_file(current_file, AnalysisType.EXPLAIN)
    print("\n代码解释:")
    print("-" * 40)
    print(result.content[:1000] + "..." if len(result.content) > 1000 else result.content)


def example_chat_mode():
    """对话模式示例"""
    print("=" * 60)
    print("示例 5: 对话模式")
    print("=" * 60)

    analyzer = CodeAnalyzer(model=DEFAULT_MODEL)

    if not analyzer.is_available():
        print("错误: Ollama 服务未启动")
        return

    code = "sorted(data, key=lambda x: x['score'], reverse=True)[:10]"

    print("\n问题: 这行代码是什么意思？")
    result = analyzer.chat("这行代码是什么意思？请用中文解释。", code)
    print("\n回答:")
    print(result.content)


def example_switch_model():
    """切换模型示例"""
    print("=" * 60)
    print("示例 6: 切换模型")
    print("=" * 60)

    analyzer = CodeAnalyzer(model=DEFAULT_MODEL)

    print(f"当前模型: {analyzer.get_model()}")

    # 切换到其他模型
    analyzer.set_model("llama3.2:1b")
    print(f"切换后: {analyzer.get_model()}")

    # 切换回来
    analyzer.set_model(DEFAULT_MODEL)
    print(f"切换回: {analyzer.get_model()}")


if __name__ == "__main__":
    print("\nLLM 代码分析示例")
    print("=" * 60)

    # 检查 Ollama 服务
    client = OllamaClient()
    if not client.is_available():
        print("\n[!] Ollama 服务未启动!")
        print("\n请按以下步骤操作:")
        print("1. 安装 Ollama: https://ollama.com/download")
        print(f"2. 下载模型: ollama pull {DEFAULT_MODEL}")
        print("3. 启动服务: ollama serve")
        print("\n安装完成后重新运行此示例。")
    else:
        print("\n[OK] Ollama 服务已启动")

        # 运行示例
        example_select_model()
        # example_basic_usage()  # 取消注释以运行
        # example_different_analysis_types()
        # example_chat_mode()

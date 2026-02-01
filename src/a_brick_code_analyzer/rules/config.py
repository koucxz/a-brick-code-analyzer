"""
规则配置加载器
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from .base import Severity

# 尝试导入 YAML 支持
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class RuleConfig:
    """规则引擎配置"""

    # 规则配置: rule_id -> {severity, options}
    rules: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # 全局设置
    ignore_patterns: List[str] = field(default_factory=list)

    # 继承的配置
    extends: List[str] = field(default_factory=list)

    # 插件
    plugins: List[str] = field(default_factory=list)

    @classmethod
    def load(cls, config_path: str = None, search_dir: str = None) -> 'RuleConfig':
        """
        从文件加载配置

        搜索顺序:
        1. 指定的路径
        2. .analyzerrc.json
        3. .analyzerrc.yaml / .analyzerrc.yml
        4. analyzer.config.json
        5. pyproject.toml [tool.analyzer]
        """
        if config_path:
            return cls._load_file(config_path)

        # 确定搜索目录
        search_path = Path(search_dir) if search_dir else Path.cwd()

        # 搜索配置文件
        search_files = [
            '.analyzerrc.json',
            '.analyzerrc.yaml',
            '.analyzerrc.yml',
            'analyzer.config.json',
        ]

        for filename in search_files:
            file_path = search_path / filename
            if file_path.exists():
                return cls._load_file(str(file_path))

        # 尝试 pyproject.toml
        pyproject_path = search_path / 'pyproject.toml'
        if pyproject_path.exists():
            config = cls._load_pyproject(str(pyproject_path))
            if config:
                return config

        # 返回默认配置
        return cls._get_default_config()

    @classmethod
    def _load_file(cls, path: str) -> 'RuleConfig':
        """从指定文件加载配置"""
        file_path = Path(path)

        if file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif file_path.suffix in ('.yaml', '.yml'):
            if not YAML_AVAILABLE:
                raise ImportError("需要安装 PyYAML 来支持 YAML 配置文件: pip install pyyaml")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {file_path.suffix}")

        return cls._from_dict(data)

    @classmethod
    def _load_pyproject(cls, path: str) -> Optional['RuleConfig']:
        """从 pyproject.toml 加载配置"""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                return None

        with open(path, 'rb') as f:
            data = tomllib.load(f)

        analyzer_config = data.get('tool', {}).get('analyzer', {})
        if analyzer_config:
            return cls._from_dict(analyzer_config)
        return None

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'RuleConfig':
        """从字典创建配置"""
        config = cls()

        # 处理 extends
        extends = data.get('extends', [])
        if isinstance(extends, str):
            extends = [extends]
        config.extends = extends

        # 先加载基础配置
        for base_config_name in extends:
            base_config = cls._load_preset(base_config_name)
            config.rules.update(base_config.rules)

        # 解析规则配置
        rules_data = data.get('rules', {})
        for rule_id, rule_config in rules_data.items():
            config.rules[rule_id] = cls._parse_rule_config(rule_config)

        config.ignore_patterns = data.get('ignorePatterns', [])
        config.plugins = data.get('plugins', [])

        return config

    @classmethod
    def _parse_rule_config(cls, config) -> Dict[str, Any]:
        """解析单个规则配置"""
        # ESLint 风格: 可以是单独的 severity 或 [severity, options]
        if isinstance(config, (int, str)):
            return {'severity': config, 'options': {}}
        elif isinstance(config, list):
            severity = config[0] if config else 'warn'
            options = config[1] if len(config) > 1 else {}
            return {'severity': severity, 'options': options}
        elif isinstance(config, dict):
            return {
                'severity': config.get('severity', 'warn'),
                'options': config.get('options', {})
            }
        return {'severity': 'warn', 'options': {}}

    @classmethod
    def _load_preset(cls, name: str) -> 'RuleConfig':
        """加载预设配置"""
        presets = {
            'recommended': cls._get_recommended_config(),
            'strict': cls._get_strict_config(),
            'minimal': cls._get_minimal_config(),
        }
        return presets.get(name, cls())

    @classmethod
    def _get_default_config(cls) -> 'RuleConfig':
        """获取默认配置"""
        return cls._get_recommended_config()

    @classmethod
    def _get_recommended_config(cls) -> 'RuleConfig':
        """推荐预设 - 平衡的规则"""
        return cls(rules={
            'complexity/max-complexity': {'severity': 'warn', 'options': {'max': 10}},
            'complexity/max-function-lines': {'severity': 'warn', 'options': {'max': 50}},
            'complexity/max-params': {'severity': 'warn', 'options': {'max': 5}},
            'naming/function-naming': {'severity': 'warn', 'options': {'style': 'snake_case'}},
            'naming/class-naming': {'severity': 'warn', 'options': {'style': 'PascalCase'}},
            'structure/max-file-lines': {'severity': 'warn', 'options': {'max': 500}},
            'structure/max-classes-per-file': {'severity': 'warn', 'options': {'max': 5}},
            'structure/max-functions-per-file': {'severity': 'warn', 'options': {'max': 20}},
        })

    @classmethod
    def _get_strict_config(cls) -> 'RuleConfig':
        """严格预设 - 所有规则为 error"""
        return cls(rules={
            'complexity/max-complexity': {'severity': 'error', 'options': {'max': 8}},
            'complexity/max-function-lines': {'severity': 'error', 'options': {'max': 30}},
            'complexity/max-params': {'severity': 'error', 'options': {'max': 4}},
            'naming/function-naming': {'severity': 'error', 'options': {'style': 'snake_case'}},
            'naming/class-naming': {'severity': 'error', 'options': {'style': 'PascalCase'}},
            'structure/max-file-lines': {'severity': 'error', 'options': {'max': 300}},
            'structure/max-classes-per-file': {'severity': 'error', 'options': {'max': 3}},
            'structure/max-functions-per-file': {'severity': 'error', 'options': {'max': 10}},
        })

    @classmethod
    def _get_minimal_config(cls) -> 'RuleConfig':
        """最小预设 - 仅关键规则"""
        return cls(rules={
            'complexity/max-complexity': {'severity': 'error', 'options': {'max': 15}},
        })

    def get_rule_config(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """获取指定规则的配置"""
        return self.rules.get(rule_id)

    def parse_severity(self, value) -> Severity:
        """解析 severity 值"""
        if isinstance(value, Severity):
            return value
        if isinstance(value, int):
            return Severity(value)
        if isinstance(value, str):
            return Severity[value.upper()]
        return Severity.WARN

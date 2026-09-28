import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = "config.toml"


@dataclass
class Config:
    data_path: str = "data/tasks.json"
    theme: str = "dark"


def load(path: str | Path = DEFAULT_CONFIG_PATH) -> Config:
    """Carrega a configuração do arquivo TOML. Se ele não existir, usa os padrões."""
    path = Path(path)
    if not path.exists():
        return Config()
    return load_from_string(path.read_text(encoding="utf-8"))


def load_from_string(toml_code: str) -> Config:
    """Útil para testes."""
    data = tomllib.loads(toml_code)
    defaults = Config()
    return Config(
        data_path=data.get("data_path", defaults.data_path),
        theme=data.get("theme", defaults.theme),
    )

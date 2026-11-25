import os
import sys
from fetcher import load_test_repository
from graph import build_dfs_graph, print_graph

EXPECTED_ARGS_COUNT = 2
KEY_VALUE_PARTS = 2
REQUIRED_KEYS = {"package_name", "repo_url", "test_mode", "version"}


def parse_toml_value(raw_val):
    """Преобразует строковое значение из TOML в нужный тип данных."""
    val = raw_val.strip()
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    if (val.startswith('"') and val.endswith('"')) or (
        val.startswith("'") and val.endswith("'")
    ):
        return val[1:-1]
    raise ValueError(f"Некорректный формат значения: {raw_val}")


def load_config(file_path):
    """Читает и проверяет конфигурационный файл формата TOML."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл конфигурации не найден: {file_path}")

    config = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            clean = line.strip()
            if not clean or clean.startswith("#"):
                continue
            if "=" not in clean:
                raise ValueError(f"Ошибка синтаксиса в строке {line_num}")
            parts = clean.split("=", maxsplit=1)
            if len(parts) != KEY_VALUE_PARTS:
                raise ValueError(
                    f"Неверная пара ключ-значение в строке {line_num}")
            key = parts[0].strip()
            config[key] = parse_toml_value(parts[1])

    validate_config(config)
    return config


def validate_config(config):
    """Проверяет наличие и корректность всех обязательных параметров."""
    missing = REQUIRED_KEYS - set(config.keys())
    if missing:
        raise ValueError(f"Отсутствуют параметры: {', '.join(missing)}")
    if not isinstance(
        config["package_name"], str) or not config["package_name"]:
        raise ValueError("Имя пакета должно быть непустой строкой")
    if not isinstance(config["repo_url"], str) or not config["repo_url"]:
        raise ValueError("URL или путь репозитория должен быть строкой")
    if not isinstance(config["test_mode"], bool):
        raise ValueError("Режим работы test_mode должен быть true или false")
    if not isinstance(config["version"], str) or not config["version"]:
        raise ValueError("Версия пакета должна быть непустой строкой")


def main():
    """Точка входа в приложение для Этапа 3."""
    if len(sys.argv) != EXPECTED_ARGS_COUNT:
        print("Использование: python3 src/main.py <путь_к_config.toml>")
        sys.exit(1)

    try:
        config = load_config(sys.argv[1])
        test_repo = {}
        if config["test_mode"]:
            test_repo = load_test_repository(config["repo_url"])

        pkg = config["package_name"]
        ver = config["version"]
        print(f"Граф зависимостей для пакета {pkg} ({ver}):")
        graph = build_dfs_graph(pkg, ver, config, test_repo)
        print_graph(graph)
    except (FileNotFoundError, ValueError, ConnectionError) as err:
        print(f"Ошибка выполнения: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()

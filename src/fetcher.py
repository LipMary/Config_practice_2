import json
import os
import urllib.error
import urllib.request

REQUEST_TIMEOUT = 10


def fetch_npm_dependencies(repo_url, package_name, version):
    """Загружает прямые зависимости npm-пакета заданной версии по URL."""
    clean_url = repo_url.rstrip("/")
    target_url = f"{clean_url}/{package_name}/{version}"

    try:
        with urllib.request.urlopen(
            target_url, timeout=REQUEST_TIMEOUT) as resp:
            raw_data = resp.read().decode("utf-8")
            package_data = json.loads(raw_data)
    except urllib.error.HTTPError as err:
        raise ValueError(f"Пакет или версия не найдены (HTTP {err.code})")
    except urllib.error.URLError as err:
        raise ConnectionError(
            f"Ошибка сети при обращении к {target_url}: {err.reason}")

    return package_data.get("dependencies", {})


def load_test_repository(file_path):
    """Читает тестовый граф зависимостей из локального текстового файла."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Тестовый репозиторий не найден: {file_path}")

    repo_graph = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            clean = line.strip()
            if not clean or ":" not in clean:
                continue
            pkg, deps_str = clean.split(":", maxsplit=1)
            deps_list = [d.strip() for d in deps_str.split(",") if d.strip()]
            repo_graph[pkg.strip()] = {dep: "test" for dep in deps_list}

    return repo_graph

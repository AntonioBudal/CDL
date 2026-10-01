"""Teste de fronteira de isolamento entre Document Intelligence e o produto Leitorum."""

import ast
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def test_no_forbidden_imports_in_source_and_tests():
    """Garante que nenhum arquivo Python importa código de backend/ ou frontend/."""
    root = get_project_root()
    forbidden_modules = {
        "backend",
        "frontend",
        "caderno",
        "caderno_leitura",
        "iniciar",
        "app",
    }

    python_files = list(root.glob("src/**/*.py")) + list(root.glob("tests/**/*.py"))
    assert len(python_files) > 0, "Nenhum arquivo Python encontrado para auditoria."

    violations = []

    for file_path in python_files:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".")[0]
                    if root_name in forbidden_modules:
                        violations.append(
                            f"{file_path.name}:{node.lineno} import direto proibido '{alias.name}'"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_name = node.module.split(".")[0]
                    if root_name in forbidden_modules:
                        violations.append(
                            f"{file_path.name}:{node.lineno} import proibido de '{node.module}'"
                        )

    assert not violations, (
        f"Violação de fronteira técnica detectada! "
        f"Document Intelligence não deve depender do backend/frontend: {violations}"
    )


def test_no_hardcoded_production_database_path():
    """Garante que nenhum arquivo referencia o banco de dados ativo de produção."""
    root = get_project_root()
    forbidden_tokens = ["caderno.db", "backend/data", "backend\\data"]

    text_files = (
        list(root.glob("src/**/*.py"))
        + list(root.glob("tests/**/*.py"))
    )

    violations = []
    for file_path in text_files:
        if file_path.name == "test_boundary.py":
            continue
        content = file_path.read_text(encoding="utf-8").lower()
        for token in forbidden_tokens:
            if token in content:
                violations.append(f"{file_path.name} contém referência ao banco ativo: '{token}'")

    assert not violations, f"Referências ao banco de produção encontradas em código: {violations}"

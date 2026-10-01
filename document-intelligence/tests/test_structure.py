"""Testes de integridade da estrutura de diretórios e arquivos de governança."""

from pathlib import Path


def get_project_root() -> Path:
    """Retorna o diretório raiz de document-intelligence."""
    return Path(__file__).parent.parent


def test_package_import():
    """Verifica se o pacote leitorum_di pode ser importado com sucesso."""
    import leitorum_di
    assert hasattr(leitorum_di, "__version__")
    assert leitorum_di.__version__ is not None


def test_mandatory_directories_exist():
    """Verifica a presença de todas as pastas fundamentais do domínio."""
    root = get_project_root()
    expected_dirs = [
        ".specify",
        ".specify/memory",
        "specs",
        "docs",
        "docs/adr",
        "docs/ldf-examples",
        "docs/schemas",
        "experiments",
        "experiments/EXP-000",
        "dataset",
        "dataset/fixtures",
        "models",
        "evaluation",
        "tests",
        "src/leitorum_di",
        "src/leitorum_di/contracts",
        "src/leitorum_di/metrics",
    ]
    for rel_path in expected_dirs:
        d = root / rel_path
        assert d.exists(), f"Diretório mandatório não encontrado: {rel_path}"
        assert d.is_dir(), f"Caminho existe mas não é diretório: {rel_path}"


def test_essential_documentation_and_contract_files_exist():
    """Verifica a presença dos arquivos de governança, constituição e contratos."""
    root = get_project_root()
    expected_files = [
        "AGENTS.md",
        "CLAUDE.md",
        "README.md",
        "pyproject.toml",
        ".gitignore",
        ".specify/feature.json",
        ".specify/memory/constitution.md",
        "specs/README.md",
        "docs/ldf.md",
        "docs/api-local.md",
        "docs/dataset-and-evaluation.md",
        "docs/metrics.md",
        "docs/models-and-licensing.md",
        "docs/roadmap-experiments.md",
        "docs/adr/README.md",
        "docs/adr/template-madr.md",
        "docs/schemas/ldf-1.0.schema.json",
        "docs/ldf-examples/ldf-1.0-minimal.json",
        "docs/ldf-examples/ldf-1.0-annotated-page.json",
        "experiments/EXP-000/README.md",
        "experiments/EXP-000/environment.md",
        "experiments/EXP-000/RESULTS.md",
        "experiments/EXP-000/evaluation-manifest.md",
        "experiments/EXP-001-context.md",
        "dataset/README.md",
        "dataset/fixtures/README.md",
        "dataset/fixtures/synthetic-line-sample.json",
        "models/README.md",
        "models/.gitkeep",
        "evaluation/README.md",
        "evaluation/.gitkeep",
    ]
    for rel_path in expected_files:
        f = root / rel_path
        assert f.exists(), f"Arquivo mandatório não encontrado: {rel_path}"
        assert f.is_file(), f"Caminho existe mas não é arquivo: {rel_path}"

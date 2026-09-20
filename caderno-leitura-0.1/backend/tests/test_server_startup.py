"""Testes automatizados para resiliência de inicialização e prevenção de conflitos de porta (T032)."""
import io
import socket
import sys
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from iniciar import check_port_available, main as iniciar_main


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_check_port_available_on_free_and_occupied_port():
    port = find_free_port()

    # Porta livre deve retornar True
    assert check_port_available("127.0.0.1", port) is True

    # Ocupa a porta com listener ativo
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", port))
        s.listen(1)

        # Agora deve retornar False
        assert check_port_available("127.0.0.1", port) is False

    # Após fechar o listener, volta a ficar livre
    assert check_port_available("127.0.0.1", port) is True


def test_iniciar_main_detects_occupied_port_and_exits_gracefully(capsys: pytest.CaptureFixture):
    port = find_free_port()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", port))
        s.listen(1)

        # Dispara o iniciar_main com a porta ocupada
        exit_code = iniciar_main(["--port", str(port)])
        assert exit_code == 1

    captured = capsys.readouterr()
    assert "[ERRO DE PORTA]" in captured.err
    assert f"A porta {port} já está em uso" in captured.err
    assert "--port" in captured.err

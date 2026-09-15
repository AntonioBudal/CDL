"""Inicia o caderno no PC ou na rede privada."""
import argparse
import io
import socket
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path
import sys



ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))

LAN_NETWORKS = tuple(
    IPv4Network(value)
    for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16")
)


def is_lan(ip: IPv4Address) -> bool:
    return any(ip in network for network in LAN_NETWORKS)


def read_options():
    parser = argparse.ArgumentParser(description="Iniciar o Caderno de Leitura.")
    parser.add_argument("--host", type=IPv4Address, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--ip", type=IPv4Address, help="IP do PC para o link e QR Code.")
    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        parser.error("--port deve estar entre 1 e 65535.")
    if not (args.host.is_unspecified or args.host.is_loopback or is_lan(args.host)):
        parser.error("--host deve ser 127.0.0.1, 0.0.0.0 ou um IPv4 da rede privada.")
    if args.ip is not None and (not args.host.is_unspecified or not is_lan(args.ip)):
        parser.error("--ip exige --host 0.0.0.0 e um IPv4 da rede privada.")
    return args


def local_addresses() -> list[IPv4Address]:
    try:
        records = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
    except OSError:
        return []
    addresses = {IPv4Address(record[4][0]) for record in records}
    return sorted(ip for ip in addresses if is_lan(ip))


def print_qr(url: str) -> None:
    try:
        import qrcode
    except ImportError:
        print("QR indisponivel. Execute INSTALAR.cmd; o link acima continua utilizavel.")
        return

    qr = qrcode.QRCode(border=4)
    qr.add_data(url)
    buffer = io.StringIO()
    qr.print_ascii(out=buffer, invert=True)
    drawing = buffer.getvalue()
    try:
        drawing.encode(getattr(sys.stdout, "encoding", None) or "utf-8")
        print(drawing)
    except UnicodeEncodeError:
        print("O terminal nao suporta o QR Code. Abra o link acima no celular.")


def show_addresses(args) -> None:
    pc_host = "127.0.0.1" if args.host.is_unspecified else str(args.host)
    print(f"PC: http://{pc_host}:{args.port}")

    if not args.host.is_loopback:
        print("Modo rede sem senha: dispositivos que alcancarem o servidor podem acessar os dados.")
        if args.host.is_unspecified:
            addresses = [args.ip] if args.ip is not None else local_addresses()
        else:
            addresses = [args.host]

        if len(addresses) > 1:
            print("IPs candidatos: use o da sua rede. --ip permite escolher manualmente.")
        if not addresses:
            print("IP nao detectado. Consulte ipconfig e use INICIAR-REDE.cmd --ip SEU_IP.")

        for address in addresses:
            url = f"http://{address}:{args.port}"
            print(f"Celular: {url}")
            print_qr(url)

    print("Mantenha este terminal aberto. Para encerrar: Ctrl+C.", flush=True)


def check_port_available(host: str, port: int) -> bool:
    """Verifica se o par (host, port) está disponível para escuta na rede."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        try:
            probe.bind((host, port))
            return True
        except OSError:
            return False


def main(argv: list[str] | None = None) -> int:
    import argparse
    import socket
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Caderno de Leitura Alpha 0.2"
    )
    parser.add_argument(
        "--host",
        choices=("127.0.0.1", "0.0.0.0"),
        default="127.0.0.1",
    )
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)

    if not 1 <= args.port <= 65535:
        parser.error("A porta deve estar entre 1 e 65535.")

    if not check_port_available(args.host, args.port):
        print(
            f"\n[ERRO DE PORTA] A porta {args.port} já está em uso por outro aplicativo ou outra janela do Caderno.",
            file=sys.stderr,
        )
        print(
            "Como resolver:\n"
            f"1. Encerre a outra janela do Caderno de Leitura aberta (Ctrl+C), OU\n"
            f"2. Inicie em outra porta utilizando: python iniciar.py --port {args.port + 1}\n",
            file=sys.stderr,
        )
        return 1

    root = Path(__file__).resolve().parent
    backend = str(root / "backend")

    if backend not in sys.path:
        sys.path.insert(0, backend)

    if not (root / "frontend" / "dist" / "index.html").is_file():
        print(
            "Interface ausente. Execute npm.cmd run build na pasta frontend.",
            file=sys.stderr,
        )
        return 1

    try:
        import uvicorn
        from app.main import app
        from app.core.config import get_database_path
        db_path = get_database_path()
    except ValueError as error:
        print(
            f"Erro na configuração do banco de dados: {error}",
            file=sys.stderr,
        )
        return 1
    except ModuleNotFoundError as error:
        if error.name == "app" or (error.name or "").startswith("app."):
            print(
                f"Arquivo do projeto ausente: {error.name}. "
                "Confira os arquivos em backend/app.",
                file=sys.stderr,
            )
        else:
            print(
                f"Dependência ausente: {error.name}. Execute INSTALAR.cmd.",
                file=sys.stderr,
            )
        return 1

    # Verificação de migrações pendentes no banco de dados
    try:
        from alembic.config import Config
        from alembic.migration import MigrationContext
        from alembic.script import ScriptDirectory
        from app.db.session import create_sqlite_engine

        alembic_cfg = Config(str(root / "backend" / "alembic.ini"))
        script = ScriptDirectory.from_config(alembic_cfg)
        head_rev = script.get_current_head()

        engine = create_sqlite_engine(db_path)
        try:
            with engine.connect() as conn:
                ctx = MigrationContext.configure(conn)
                current_rev = ctx.get_current_revision()
        finally:
            engine.dispose()

        if current_rev != head_rev:
            print(
                f"\nATENÇÃO: O banco de dados está na versão '{current_rev}', "
                f"mas a aplicação requer a versão '{head_rev}'.",
                file=sys.stderr,
            )
            print(
                "Execute INSTALAR.cmd ou 'alembic upgrade head' para aplicar as migrações pendentes.\n",
                file=sys.stderr,
            )
            return 1
    except Exception:
        pass

    print(f"PC: http://127.0.0.1:{args.port}")
    print(f"Banco usado: {db_path}")

    if args.host == "0.0.0.0":
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
                # Consulta a rota local; não envia dados para esse endereço.
                probe.connect(("192.0.2.1", 9))
                lan_ip = probe.getsockname()[0]

            lan_url = f"http://{lan_ip}:{args.port}"
            print(f"Rede local — endereço detectado: {lan_url}")

            try:
                import qrcode

                qr = qrcode.QRCode(border=2)
                qr.add_data(lan_url)
                qr.make(fit=True)
                qr.print_ascii(invert=True)
            except (ImportError, UnicodeError):
                print(
                    "QR Code indisponível neste terminal. "
                    "Use o endereço acima."
                )
        except OSError:
            print("Consulte o IPv4 da rede local com ipconfig.")

        print(
            f"Tailscale: no celular, use "
            f"http://IP-TAILSCALE-DO-PC:{args.port}"
        )
        print(
            "Use o endereço 100.x.x.x exibido para o PC "
            "no aplicativo Tailscale."
        )
        print("Mantenha o Tailscale conectado no PC e no celular.")

    print("Para encerrar, pressione Ctrl+C nesta janela.", flush=True)

    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            workers=1,
            reload=False,
        )
    except OSError as exc:
        if getattr(exc, "winerror", None) == 10048 or getattr(exc, "errno", None) in (48, 98, 10048):
            print(
                f"\n[ERRO DE PORTA] A porta {args.port} foi ocupada concorrentemente.",
                file=sys.stderr,
            )
            print(
                f"Inicie o caderno em outra porta usando: python iniciar.py --port {args.port + 1}\n",
                file=sys.stderr,
            )
            return 1
        raise

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations


def parse_device_name(user_agent: str | None) -> str:
    """Extrai uma identificação amigável e legível do dispositivo/navegador a partir do User-Agent.

    Exemplos de saída:
    - "Chrome no Windows"
    - "Safari no iPhone"
    - "Chrome no Android"
    - "Firefox no Linux"
    - "Cliente de Teste / API"
    """
    if not user_agent or not user_agent.strip():
        return "Dispositivo Desconhecido"

    ua = user_agent.lower()

    # Detecção de clientes de teste ou scripts
    if "pytest" in ua or "testclient" in ua or "httpx" in ua or "python" in ua or "curl" in ua:
        return "Cliente de Teste / API"

    # Detecção de Sistema Operacional
    os_name = "Dispositivo"
    if "iphone" in ua:
        os_name = "iPhone"
    elif "ipad" in ua:
        os_name = "iPad"
    elif "android" in ua:
        os_name = "Android"
    elif "windows" in ua or "win64" in ua or "win32" in ua:
        os_name = "Windows"
    elif "macintosh" in ua or "mac os" in ua:
        os_name = "Mac"
    elif "linux" in ua:
        os_name = "Linux"

    # Detecção de Navegador
    browser_name = "Navegador"
    if "edg/" in ua or "edge/" in ua:
        browser_name = "Edge"
    elif "opr/" in ua or "opera" in ua:
        browser_name = "Opera"
    elif "firefox" in ua or "fxios" in ua:
        browser_name = "Firefox"
    elif "chrome" in ua or "crios" in ua:
        browser_name = "Chrome"
    elif "safari" in ua and "chrome" not in ua and "crios" not in ua:
        browser_name = "Safari"

    if os_name in ("iPhone", "iPad"):
        return f"{browser_name} no {os_name}"

    return f"{browser_name} no {os_name}"

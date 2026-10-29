import re
import unicodedata

# Caracteres proibidos em nomes de arquivo no Windows, mais os de controle (0 a 31).
_PROIBIDOS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_ESPACOS = re.compile(r"\s+")
TAMANHO_MAXIMO = 120


def _limpar(texto: str) -> str:
    limpo = unicodedata.normalize("NFC", texto)
    limpo = _PROIBIDOS.sub(" ", limpo)
    limpo = _ESPACOS.sub("_", limpo.strip())
    # O Windows descarta pontos no fim do nome; removê-los evita nomes que se comportam diferente.
    limpo = limpo.strip("._")
    if not limpo:
        raise ValueError(f"sem caracteres válidos para nome de arquivo: {texto!r}")
    return limpo[:TAMANHO_MAXIMO].rstrip("._")


def nome_arquivo(papel: str, nome: str) -> str:
    return f"certificado_{_limpar(papel)}_{_limpar(nome)}.pdf"


def nome_pasta(evento: str) -> str:
    return _limpar(evento)

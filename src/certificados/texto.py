import re
from string import Formatter
from xml.sax.saxutils import escape

# *trecho* vira negrito, como no WhatsApp.
_NEGRITO = re.compile(r"\*([^*\n]+)\*")


def campos_do_texto(texto: str) -> set[str]:
    try:
        partes = list(Formatter().parse(texto))
    except ValueError:
        raise ValueError(
            "há uma chave { ou } sem par; para mostrar uma chave, use {{ ou }}"
        ) from None

    campos = set()
    for _, campo, formato, conversao in partes:
        if campo is None:
            continue
        # Só nomes simples: {nome.upper} ou {nome!r} acessariam o Python por dentro.
        if not campo.isidentifier() or formato or conversao:
            raise ValueError(f"campo inválido {{{campo}}}; use só o nome, ex.: {{nome}}")
        campos.add(campo)
    return campos


def montar_paragrafo(texto: str, campos: dict[str, str]) -> str:
    # O reportlab lê o parágrafo como marcação; um & ou < no nome quebraria o certificado.
    marcado = _NEGRITO.sub(r"<b>\1</b>", escape(texto))
    return marcado.format_map({chave: escape(valor) for chave, valor in campos.items()})

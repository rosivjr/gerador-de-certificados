import csv
import io
from dataclasses import dataclass
from pathlib import Path


class ErroParticipantes(Exception):
    pass


@dataclass(frozen=True)
class Linha:
    numero: int
    campos: dict[str, str]


def ler_participantes(caminho: Path) -> list[Linha]:
    try:
        # utf-8-sig remove o BOM que o Excel grava no início de arquivos "CSV UTF-8".
        texto = caminho.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise ErroParticipantes(f"lista de participantes não encontrada: {caminho}") from None
    except UnicodeDecodeError:
        raise ErroParticipantes(
            f"{caminho} não está em UTF-8; no Excel, salve como 'CSV UTF-8'"
        ) from None

    if not texto.strip():
        raise ErroParticipantes(f"{caminho} está vazio")

    leitor = csv.DictReader(io.StringIO(texto), delimiter=_separador(texto))
    colunas = [coluna.strip().lower() for coluna in leitor.fieldnames or []]
    if "nome" not in colunas:
        raise ErroParticipantes(f"{caminho} precisa de uma coluna 'nome' no cabeçalho")
    leitor.fieldnames = colunas

    linhas = []
    for registro in leitor:
        if None in registro:
            raise ErroParticipantes(
                f"linha {leitor.line_num} tem mais colunas que o cabeçalho; "
                "confira se algum nome contém o separador"
            )
        campos = {coluna: (valor or "").strip() for coluna, valor in registro.items()}
        if any(campos.values()):
            linhas.append(Linha(numero=leitor.line_num, campos=campos))
    return linhas


def _separador(texto: str) -> str:
    # O Excel em português usa ";" porque a vírgula é o separador decimal.
    cabecalho = texto.splitlines()[0]
    return ";" if cabecalho.count(";") >= cabecalho.count(",") else ","

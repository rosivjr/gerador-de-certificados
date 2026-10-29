from dataclasses import dataclass

from certificados.evento import Evento
from certificados.nomes import nome_arquivo
from certificados.participantes import Linha


@dataclass(frozen=True)
class Certificado:
    linha: int
    papel: str
    campos: dict[str, str]
    arquivo: str


@dataclass(frozen=True)
class ErroLinha:
    linha: int
    mensagem: str

    def __str__(self) -> str:
        return f"linha {self.linha}: {self.mensagem}"


def validar(evento: Evento, linhas: list[Linha]) -> tuple[list[Certificado], list[ErroLinha]]:
    certificados: list[Certificado] = []
    erros: list[ErroLinha] = []
    # Guarda em qual linha cada arquivo apareceu, para apontar a repetição.
    vistos: dict[str, int] = {}

    for linha in linhas:
        resultado = _validar_linha(evento, linha)
        if isinstance(resultado, ErroLinha):
            erros.append(resultado)
        elif resultado.arquivo in vistos:
            erros.append(
                ErroLinha(
                    linha.numero, f"repete o certificado da linha {vistos[resultado.arquivo]}"
                )
            )
        else:
            vistos[resultado.arquivo] = linha.numero
            certificados.append(resultado)
    return certificados, erros


def _validar_linha(evento: Evento, linha: Linha) -> Certificado | ErroLinha:
    nome = linha.campos.get("nome", "")
    if not nome:
        return ErroLinha(linha.numero, "nome vazio")

    papel = linha.campos.get("papel", "")
    if not papel:
        # Com um papel só no evento, a coluna "papel" pode ser omitida.
        if len(evento.papeis) != 1:
            return ErroLinha(linha.numero, f"informe o papel ({_opcoes(evento)})")
        papel = next(iter(evento.papeis))
    if papel not in evento.papeis:
        return ErroLinha(linha.numero, f"papel '{papel}' não existe ({_opcoes(evento)})")

    faltando = [campo for campo in evento.papeis[papel].exige if not linha.campos.get(campo)]
    if faltando:
        return ErroLinha(linha.numero, f"o papel '{papel}' exige: {', '.join(faltando)}")

    try:
        arquivo = nome_arquivo(papel, nome)
    except ValueError as erro:
        return ErroLinha(linha.numero, str(erro))

    campos = {
        "evento": evento.nome,
        "local": evento.local,
        "datas": evento.datas,
        "carga_horaria": evento.carga_horaria,
        "cidade": evento.cidade,
    }
    # Valores preenchidos na linha têm prioridade, como a carga horária da palestra.
    campos.update({chave: valor for chave, valor in linha.campos.items() if valor})
    campos["papel"] = papel
    return Certificado(linha=linha.numero, papel=papel, campos=campos, arquivo=arquivo)


def _opcoes(evento: Evento) -> str:
    return "opções: " + ", ".join(sorted(evento.papeis))

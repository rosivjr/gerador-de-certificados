import tomllib
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from certificados.texto import campos_do_texto

Area = tuple[float, float, float, float]

CAMPOS_PADRAO = frozenset({"nome", "papel", "evento", "local", "datas", "carga_horaria", "cidade"})


class ErroConfiguracao(Exception):
    pass


@dataclass(frozen=True)
class Modelo:
    arquivo: Path
    area_texto: Area
    area_data: Area
    fonte_tamanho: float
    fonte_tamanho_minimo: float


@dataclass(frozen=True)
class Papel:
    nome: str
    texto: str
    exige: tuple[str, ...]


@dataclass(frozen=True)
class Evento:
    nome: str
    local: str
    datas: str
    carga_horaria: str
    cidade: str
    data_emissao: date
    modelo: Modelo
    papeis: dict[str, Papel]


def carregar_evento(caminho: Path) -> Evento:
    try:
        with caminho.open("rb") as arquivo:
            dados = tomllib.load(arquivo)
    except FileNotFoundError:
        raise ErroConfiguracao(f"arquivo do evento não encontrado: {caminho}") from None
    except tomllib.TOMLDecodeError as erro:
        raise ErroConfiguracao(f"{caminho} não é um TOML válido: {erro}") from None

    secao_evento = _secao(dados, "evento")
    return Evento(
        nome=_texto(secao_evento, "evento", "nome"),
        local=_texto(secao_evento, "evento", "local"),
        datas=_texto(secao_evento, "evento", "datas"),
        carga_horaria=_texto(secao_evento, "evento", "carga_horaria"),
        cidade=_texto(secao_evento, "evento", "cidade"),
        data_emissao=_data(secao_evento, "evento", "data_emissao"),
        # O caminho do modelo é relativo ao TOML, não à pasta onde o terminal está.
        modelo=_modelo(_secao(dados, "modelo"), caminho.parent),
        papeis=_papeis(_secao(dados, "papeis")),
    )


def _secao(dados: dict, nome: str) -> dict:
    valor = dados.get(nome)
    if not isinstance(valor, dict):
        raise ErroConfiguracao(f"falta a seção [{nome}]")
    return valor


def _texto(secao: dict, nome_secao: str, chave: str) -> str:
    valor = secao.get(chave)
    if not isinstance(valor, str) or not valor.strip():
        raise ErroConfiguracao(f"[{nome_secao}] precisa de '{chave}' com um texto")
    return valor.strip()


def _numero(secao: dict, nome_secao: str, chave: str) -> float:
    valor = secao.get(chave)
    # bool é subclasse de int em Python; sem essa exclusão, "true" seria aceito como 1.
    if isinstance(valor, bool) or not isinstance(valor, int | float) or valor <= 0:
        raise ErroConfiguracao(f"[{nome_secao}] precisa de '{chave}' com um número positivo")
    return float(valor)


def _data(secao: dict, nome_secao: str, chave: str) -> date:
    valor = secao.get(chave)
    if not isinstance(valor, date):
        raise ErroConfiguracao(
            f"[{nome_secao}] precisa de '{chave}' como data sem aspas, ex.: {chave} = 2026-08-20"
        )
    return valor


def _area(secao: dict, chave: str) -> Area:
    valor = secao.get(chave)
    mensagem = f"[modelo] '{chave}' deve ser [x0, y0, x1, y1], com x0 < x1 e y0 < y1"
    if not isinstance(valor, list) or len(valor) != 4:
        raise ErroConfiguracao(mensagem)
    if any(isinstance(n, bool) or not isinstance(n, int | float) for n in valor):
        raise ErroConfiguracao(mensagem)
    x0, y0, x1, y1 = (float(n) for n in valor)
    if x0 >= x1 or y0 >= y1:
        raise ErroConfiguracao(mensagem)
    return (x0, y0, x1, y1)


def _modelo(secao: dict, pasta_base: Path) -> Modelo:
    arquivo = pasta_base / _texto(secao, "modelo", "arquivo")
    if not arquivo.is_file():
        raise ErroConfiguracao(f"modelo PDF não encontrado: {arquivo}")
    tamanho = _numero(secao, "modelo", "fonte_tamanho")
    minimo = _numero(secao, "modelo", "fonte_tamanho_minimo")
    if minimo > tamanho:
        raise ErroConfiguracao(
            "[modelo] 'fonte_tamanho_minimo' não pode ser maior que 'fonte_tamanho'"
        )
    return Modelo(
        arquivo=arquivo,
        area_texto=_area(secao, "area_texto"),
        area_data=_area(secao, "area_data"),
        fonte_tamanho=tamanho,
        fonte_tamanho_minimo=minimo,
    )


def _papeis(secao: dict) -> dict[str, Papel]:
    if not secao:
        raise ErroConfiguracao(
            "[papeis] precisa de pelo menos um papel, ex.: [papeis.participante]"
        )
    papeis = {}
    for nome, config in secao.items():
        nome_secao = f"papeis.{nome}"
        if not isinstance(config, dict):
            raise ErroConfiguracao(f"[{nome_secao}] deve ser uma seção")
        exige = config.get("exige", [])
        if not isinstance(exige, list) or not all(isinstance(c, str) for c in exige):
            raise ErroConfiguracao(f"[{nome_secao}] 'exige' deve ser uma lista de textos")
        texto = _texto(config, nome_secao, "texto")
        try:
            usados = campos_do_texto(texto)
        except ValueError as erro:
            raise ErroConfiguracao(f"[{nome_secao}] texto: {erro}") from None
        desconhecidos = sorted(usados - CAMPOS_PADRAO - set(exige))
        if desconhecidos:
            raise ErroConfiguracao(
                f"[{nome_secao}] o texto usa {', '.join(desconhecidos)}, "
                "que não vem do evento nem está em 'exige'"
            )
        papeis[nome] = Papel(nome=nome, texto=texto, exige=tuple(exige))
    return papeis

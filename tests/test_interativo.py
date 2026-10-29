from datetime import date
from pathlib import Path

import pytest

from certificados.evento import Evento, Modelo, Papel
from certificados.interativo import perguntar_linhas

MODELO = Modelo(Path("modelo.pdf"), (0, 0, 100, 100), (0, 100, 100, 120), 19, 15)
PARTICIPANTE = Papel("participante", "texto", ())
MINISTRANTE = Papel("ministrante", "texto", ("tema", "carga_horaria"))


def criar_evento(*papeis):
    return Evento(
        nome="Semana de Tecnologia",
        local="no auditório central",
        datas="nos dias 15 e 16/08/2026",
        carga_horaria="8 horas",
        cidade="Cidade Exemplo",
        data_emissao=date(2026, 8, 20),
        modelo=MODELO,
        papeis={papel.nome: papel for papel in papeis},
    )


def respostas(*textos):
    fila = iter(textos)
    return lambda _pergunta: next(fila)


def test_com_um_papel_so_pergunta_os_nomes():
    linhas = perguntar_linhas(criar_evento(PARTICIPANTE), respostas("Ana", "Bruno", ""))

    assert [linha.campos["nome"] for linha in linhas] == ["Ana", "Bruno"]
    assert [linha.numero for linha in linhas] == [1, 2]


def test_papel_e_escolhido_uma_vez_so():
    evento = criar_evento(PARTICIPANTE, MINISTRANTE)
    linhas = perguntar_linhas(evento, respostas("participante", "Ana", "Bruno", ""))

    assert [linha.campos for linha in linhas] == [
        {"nome": "Ana", "papel": "participante"},
        {"nome": "Bruno", "papel": "participante"},
    ]


def test_ministrante_pergunta_os_campos_que_o_papel_exige():
    evento = criar_evento(PARTICIPANTE, MINISTRANTE)
    linhas = perguntar_linhas(evento, respostas("ministrante", "Bruno", "Python", "2 horas", ""))

    assert linhas[0].campos == {
        "nome": "Bruno",
        "papel": "ministrante",
        "tema": "Python",
        "carga_horaria": "2 horas",
    }


def test_papel_invalido_pergunta_de_novo(capsys):
    evento = criar_evento(PARTICIPANTE, MINISTRANTE)
    linhas = perguntar_linhas(evento, respostas("monitor", "Participante", "Ana", ""))

    assert "papel 'monitor' não existe" in capsys.readouterr().out
    assert linhas[0].campos["papel"] == "participante"


@pytest.mark.parametrize(
    ("digitado", "mensagem"),
    [
        (("ministrante", "Bruno", "", "2 horas"), "exige: tema"),
        (("participante", "Ana", "Ana"), "repete o certificado da linha 1"),
        (("participante", "///"), "sem caracteres válidos"),
    ],
)
def test_participante_invalido_pede_de_novo(digitado, mensagem, capsys):
    evento = criar_evento(PARTICIPANTE, MINISTRANTE)
    papel = digitado[0]
    extras = ("Python", "1 hora") if papel == "ministrante" else ()
    linhas = perguntar_linhas(evento, respostas(*digitado, "Carla", *extras, ""))

    assert mensagem in capsys.readouterr().out
    assert linhas[-1].campos["nome"] == "Carla"


def test_ctrl_d_encerra_a_digitacao():
    def entrada(_pergunta):
        raise EOFError

    assert perguntar_linhas(criar_evento(PARTICIPANTE, MINISTRANTE), entrada) == []


def test_a_partir_do_segundo_nome_explica_como_terminar():
    perguntas = []
    fila = iter(["Ana", ""])

    def entrada(pergunta):
        perguntas.append(pergunta)
        return next(fila)

    perguntar_linhas(criar_evento(PARTICIPANTE), entrada)

    assert perguntas == ["Nome: ", "Próximo nome (Enter para terminar): "]

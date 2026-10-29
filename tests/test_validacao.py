from datetime import date
from pathlib import Path

import pytest

from certificados.evento import Evento, Modelo, Papel
from certificados.participantes import Linha
from certificados.validacao import validar

MODELO = Modelo(
    arquivo=Path("modelo.pdf"),
    area_texto=(0, 0, 100, 100),
    area_data=(0, 100, 100, 120),
    fonte_tamanho=19,
    fonte_tamanho_minimo=15,
)

PAPEIS = {
    "participante": Papel("participante", "texto", ()),
    "ministrante": Papel("ministrante", "texto", ("tema", "carga_horaria")),
}


def criar_evento(papeis=PAPEIS):
    return Evento(
        nome="Semana de Tecnologia",
        local="no auditório central",
        datas="nos dias 15 e 16/08/2026",
        carga_horaria="8 horas",
        cidade="Cidade Exemplo",
        data_emissao=date(2026, 8, 20),
        modelo=MODELO,
        papeis=papeis,
    )


def linha(numero, **campos):
    return Linha(numero=numero, campos=campos)


def test_linha_valida_herda_os_dados_do_evento():
    certificados, erros = validar(criar_evento(), [linha(2, nome="Ana", papel="participante")])

    assert erros == []
    assert certificados[0].arquivo == "certificado_participante_Ana.pdf"
    assert certificados[0].campos["evento"] == "Semana de Tecnologia"
    assert certificados[0].campos["carga_horaria"] == "8 horas"


def test_ministrante_usa_a_carga_horaria_da_palestra():
    linhas = [linha(2, nome="Bruno", papel="ministrante", tema="Python", carga_horaria="2 horas")]
    certificados, erros = validar(criar_evento(), linhas)

    assert erros == []
    assert certificados[0].campos["carga_horaria"] == "2 horas"
    assert certificados[0].campos["tema"] == "Python"


def test_mesma_pessoa_em_dois_papeis_gera_dois_certificados():
    linhas = [
        linha(2, nome="Bruno", papel="ministrante", tema="Python", carga_horaria="2 horas"),
        linha(3, nome="Bruno", papel="participante"),
    ]
    certificados, erros = validar(criar_evento(), linhas)

    assert erros == []
    assert [c.arquivo for c in certificados] == [
        "certificado_ministrante_Bruno.pdf",
        "certificado_participante_Bruno.pdf",
    ]


def test_sem_coluna_papel_usa_o_unico_papel_do_evento():
    evento = criar_evento({"participante": PAPEIS["participante"]})
    certificados, erros = validar(evento, [linha(2, nome="Ana")])

    assert erros == []
    assert certificados[0].papel == "participante"


@pytest.mark.parametrize(
    ("campos", "mensagem"),
    [
        ({"nome": "", "papel": "participante"}, "linha 4: nome vazio"),
        ({"nome": "Ana"}, "linha 4: informe o papel (opções: ministrante, participante)"),
        ({"nome": "Ana", "papel": "monitor"}, "linha 4: papel 'monitor' não existe"),
        ({"nome": "Bruno", "papel": "ministrante"}, "exige: tema, carga_horaria"),
        ({"nome": "///", "papel": "participante"}, "sem caracteres válidos"),
    ],
)
def test_linha_invalida(campos, mensagem):
    certificados, erros = validar(criar_evento(), [linha(4, **campos)])

    assert certificados == []
    assert len(erros) == 1
    assert mensagem in str(erros[0])


def test_repeticao_aponta_a_primeira_linha():
    linhas = [
        linha(2, nome="Ana", papel="participante"),
        linha(7, nome="Ana", papel="participante"),
    ]
    certificados, erros = validar(criar_evento(), linhas)

    assert len(certificados) == 1
    assert str(erros[0]) == "linha 7: repete o certificado da linha 2"


def test_junta_todos_os_erros_de_uma_vez():
    linhas = [
        linha(2, nome="", papel="participante"),
        linha(3, nome="Ana", papel="participante"),
        linha(4, nome="Carla", papel="monitor"),
    ]
    certificados, erros = validar(criar_evento(), linhas)

    assert len(certificados) == 1
    assert [e.linha for e in erros] == [2, 4]

from datetime import date

import pytest
from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from certificados.evento import Evento, Modelo, Papel
from certificados.pdf import ESTILO_TEXTO, TextoNaoCabe, ajustar, data_por_extenso, gerar_pdf
from certificados.validacao import Certificado

LARGURA, ALTURA = 842, 595


@pytest.fixture
def modelo(tmp_path):
    caminho = tmp_path / "modelo.pdf"
    tela = Canvas(str(caminho), pagesize=(LARGURA, ALTURA))
    tela.drawString(60, 540, "MODELO DE TESTE")
    tela.save()
    return Modelo(
        arquivo=caminho,
        area_texto=(60, 230, 780, 345),
        area_data=(370, 353, 780, 385),
        fonte_tamanho=19,
        fonte_tamanho_minimo=15,
    )


def criar_evento(modelo, texto="Certificamos que *{nome}* participou do evento *{evento}*."):
    return Evento(
        nome="Semana de Tecnologia",
        local="no auditório central",
        datas="nos dias 15 e 16/08/2026",
        carga_horaria="8 horas",
        cidade="Cidade Exemplo",
        data_emissao=date(2026, 8, 20),
        modelo=modelo,
        papeis={"participante": Papel("participante", texto, ())},
    )


def certificado(nome="Ana Souza"):
    campos = {"nome": nome, "evento": "Semana de Tecnologia", "papel": "participante"}
    return Certificado(linha=2, papel="participante", campos=campos, arquivo="x.pdf")


@pytest.mark.parametrize(
    ("dia", "esperado"),
    [
        (date(2026, 1, 1), "1 de janeiro de 2026"),
        (date(2026, 3, 9), "9 de março de 2026"),
        (date(2026, 12, 31), "31 de dezembro de 2026"),
    ],
)
def test_data_por_extenso(dia, esperado):
    assert data_por_extenso(dia) == esperado


def test_gera_pdf_sobre_o_modelo(modelo, tmp_path):
    destino = tmp_path / "saida.pdf"
    gerar_pdf(criar_evento(modelo), certificado(), destino)

    leitor = PdfReader(destino)
    texto = leitor.pages[0].extract_text()
    assert len(leitor.pages) == 1
    assert float(leitor.pages[0].mediabox.width) == LARGURA
    assert "MODELO DE TESTE" in texto
    assert "Ana Souza" in texto
    assert "Cidade Exemplo, 20 de agosto de 2026" in texto


def test_simbolos_no_nome_aparecem_no_pdf(modelo, tmp_path):
    destino = tmp_path / "saida.pdf"
    gerar_pdf(criar_evento(modelo), certificado("Ana & <Souza>"), destino)

    assert "Ana & <Souza>" in PdfReader(destino).pages[0].extract_text()


def test_texto_curto_usa_a_fonte_maior():
    paragrafo = ajustar("Certificamos que Ana participou.", ESTILO_TEXTO, (0, 0, 700, 100), 19, 15)

    assert paragrafo.style.fontSize == 19


def test_texto_longo_reduz_a_fonte():
    texto = "palavra " * 70
    paragrafo = ajustar(texto, ESTILO_TEXTO, (0, 0, 700, 100), 19, 15)

    assert 15 <= paragrafo.style.fontSize < 19


def test_texto_que_nao_cabe_gera_erro_e_nenhum_arquivo(modelo, tmp_path):
    destino = tmp_path / "saida.pdf"
    evento = criar_evento(modelo, texto="Certificamos que {nome} " + "participou " * 300)

    with pytest.raises(TextoNaoCabe, match="nem com fonte 15"):
        gerar_pdf(evento, certificado(), destino)
    assert not destino.exists()

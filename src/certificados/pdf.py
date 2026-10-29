from datetime import date
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from certificados.evento import Area, Evento
from certificados.texto import montar_paragrafo
from certificados.validacao import Certificado

MESES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)
PASSO_FONTE = 0.5

ESTILO_TEXTO = ParagraphStyle("texto", fontName="Times-Roman", alignment=TA_JUSTIFY)
ESTILO_DATA = ParagraphStyle("data", fontName="Times-Bold", alignment=TA_RIGHT)


class TextoNaoCabe(Exception):
    pass


def data_por_extenso(dia: date) -> str:
    return f"{dia.day} de {MESES[dia.month - 1]} de {dia.year}"


def ajustar(
    texto: str, estilo: ParagraphStyle, area: Area, maior: float, menor: float
) -> Paragraph:
    x0, y0, x1, y1 = area
    tamanho = maior
    while tamanho >= menor:
        paragrafo = Paragraph(
            texto,
            ParagraphStyle(estilo.name, parent=estilo, fontSize=tamanho, leading=tamanho * 1.2),
        )
        _, altura = paragrafo.wrap(x1 - x0, y1 - y0)
        if altura <= y1 - y0:
            return paragrafo
        tamanho -= PASSO_FONTE
    raise TextoNaoCabe(
        f"o texto não cabe na área nem com fonte {menor:g}; "
        "aumente a área no TOML ou encurte o texto"
    )


def gerar_pdf(evento: Evento, certificado: Certificado, destino: Path) -> None:
    modelo = evento.modelo
    saida = PdfWriter()
    # Copia só a página: os metadados do modelo (autor, programa) não vão para o certificado.
    pagina = saida.add_page(PdfReader(modelo.arquivo).pages[0])
    largura, altura = float(pagina.mediabox.width), float(pagina.mediabox.height)

    texto = montar_paragrafo(evento.papeis[certificado.papel].texto, certificado.campos)
    paragrafo = ajustar(
        texto, ESTILO_TEXTO, modelo.area_texto, modelo.fonte_tamanho, modelo.fonte_tamanho_minimo
    )
    # A data fica no tamanho mínimo, menor que o parágrafo, como no certificado antigo.
    data = escape(f"{evento.cidade}, {data_por_extenso(evento.data_emissao)}")
    linha_data = ajustar(
        data,
        ESTILO_DATA,
        modelo.area_data,
        modelo.fonte_tamanho_minimo,
        modelo.fonte_tamanho_minimo,
    )

    camada = BytesIO()
    tela = Canvas(camada, pagesize=(largura, altura))
    _desenhar(tela, paragrafo, modelo.area_texto, altura)
    _desenhar(tela, linha_data, modelo.area_data, altura)
    tela.save()

    pagina.merge_page(PdfReader(camada).pages[0])
    with destino.open("wb") as arquivo:
        saida.write(arquivo)


def _desenhar(tela: Canvas, paragrafo: Paragraph, area: Area, altura_pagina: float) -> None:
    x0, y0, _, _ = area
    # As áreas medem y de cima para baixo; o reportlab mede de baixo para cima.
    paragrafo.drawOn(tela, x0, altura_pagina - y0 - paragrafo.height)

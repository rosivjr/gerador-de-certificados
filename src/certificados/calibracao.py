from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import Color, blue, red
from reportlab.pdfgen.canvas import Canvas

from certificados.evento import Area, Modelo

ESPACO_GRADE = 50
CINZA = Color(0.6, 0.6, 0.6)


def gerar_calibracao(modelo: Modelo, destino: Path) -> None:
    saida = PdfWriter()
    pagina = saida.add_page(PdfReader(modelo.arquivo).pages[0])
    largura, altura = float(pagina.mediabox.width), float(pagina.mediabox.height)

    camada = BytesIO()
    tela = Canvas(camada, pagesize=(largura, altura))
    _desenhar_grade(tela, largura, altura)
    _desenhar_area(tela, "area_texto", modelo.area_texto, altura, red)
    _desenhar_area(tela, "area_data", modelo.area_data, altura, blue)
    tela.save()

    pagina.merge_page(PdfReader(camada).pages[0])
    with destino.open("wb") as arquivo:
        saida.write(arquivo)


def _desenhar_grade(tela: Canvas, largura: float, altura: float) -> None:
    tela.setStrokeColor(CINZA)
    tela.setFillColor(CINZA)
    tela.setLineWidth(0.3)
    tela.setFont("Helvetica", 6)
    for x in range(0, int(largura) + 1, ESPACO_GRADE):
        tela.line(x, 0, x, altura)
        tela.drawString(x + 1, altura - 7, str(x))
    for y in range(0, int(altura) + 1, ESPACO_GRADE):
        # Os números da grade contam de cima para baixo, como as áreas do TOML.
        tela.line(0, altura - y, largura, altura - y)
        tela.drawString(1, altura - y - 7, str(y))


def _desenhar_area(tela: Canvas, nome: str, area: Area, altura: float, cor: Color) -> None:
    x0, y0, x1, y1 = area
    tela.setStrokeColor(cor)
    tela.setFillColor(cor)
    tela.setLineWidth(1)
    tela.rect(x0, altura - y1, x1 - x0, y1 - y0)
    tela.setFont("Helvetica", 8)
    tela.drawString(x0 + 2, altura - y0 - 9, f"{nome} = [{x0:g}, {y0:g}, {x1:g}, {y1:g}]")

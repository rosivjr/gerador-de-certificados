from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from certificados.calibracao import gerar_calibracao
from certificados.evento import Modelo


def test_desenha_grade_e_areas_sobre_o_modelo(tmp_path):
    arquivo = tmp_path / "modelo.pdf"
    tela = Canvas(str(arquivo), pagesize=(842, 595))
    tela.drawString(60, 540, "MODELO DE TESTE")
    tela.save()
    modelo = Modelo(arquivo, (60, 230, 780, 345.5), (370, 353, 780, 385), 19, 15)
    destino = tmp_path / "calibracao.pdf"

    gerar_calibracao(modelo, destino)

    leitor = PdfReader(destino)
    texto = leitor.pages[0].extract_text()
    assert len(leitor.pages) == 1
    assert "MODELO DE TESTE" in texto
    assert "area_texto = [60, 230, 780, 345.5]" in texto
    assert "area_data = [370, 353, 780, 385]" in texto
    assert "550" in texto

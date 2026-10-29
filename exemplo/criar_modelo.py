"""Cria o modelo fictício usado no exemplo: python exemplo/criar_modelo.py"""

from pathlib import Path

from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen.canvas import Canvas

AZUL = Color(0.12, 0.23, 0.45)
LARGURA, ALTURA = landscape(A4)

tela = Canvas(str(Path(__file__).with_name("modelo.pdf")), pagesize=(LARGURA, ALTURA))
tela.setTitle("Modelo de certificado")
tela.setStrokeColor(AZUL)
tela.setLineWidth(6)
tela.rect(24, 24, LARGURA - 48, ALTURA - 48)
tela.setLineWidth(1)
tela.rect(36, 36, LARGURA - 72, ALTURA - 72)

tela.setFillColor(AZUL)
tela.setFont("Helvetica-Bold", 14)
tela.drawCentredString(LARGURA / 2, ALTURA - 90, "INSTITUIÇÃO DE EXEMPLO")
tela.setFont("Times-Bold", 40)
tela.drawCentredString(LARGURA / 2, ALTURA - 170, "CERTIFICADO")

tela.setLineWidth(1)
tela.line(LARGURA / 2 - 130, 120, LARGURA / 2 + 130, 120)
tela.setFont("Times-Roman", 13)
tela.drawCentredString(LARGURA / 2, 102, "Nome de quem assina")
tela.drawCentredString(LARGURA / 2, 86, "Cargo")
tela.save()

import pytest
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

from certificados.texto import campos_do_texto, montar_paragrafo


def test_lista_os_campos_usados():
    texto = "Certificamos que {nome} ministrou {tema} no evento {evento}, {nome}."

    assert campos_do_texto(texto) == {"nome", "tema", "evento"}


def test_chaves_duplas_nao_sao_campos():
    assert campos_do_texto("use {{nome}} para inserir o nome") == set()


@pytest.mark.parametrize(
    ("texto", "mensagem"),
    [
        ("Certificamos que {nome", "sem par"),
        ("Certificamos que nome}", "sem par"),
        ("Certificamos que {}", "campo inválido"),
        ("Certificamos que {0}", "campo inválido"),
        ("Certificamos que {nome!r}", "campo inválido"),
        ("Certificamos que {nome:>20}", "campo inválido"),
        ("Certificamos que {nome.upper}", "campo inválido"),
    ],
)
def test_texto_invalido(texto, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        campos_do_texto(texto)


def test_preenche_os_campos():
    paragrafo = montar_paragrafo("{nome} participou de {evento}.", {"nome": "Ana", "evento": "X"})

    assert paragrafo == "Ana participou de X."


def test_asteriscos_viram_negrito():
    assert montar_paragrafo("Certificamos que *{nome}*.", {"nome": "Ana"}) == (
        "Certificamos que <b>Ana</b>."
    )


def test_valores_nao_viram_marcacao():
    paragrafo = montar_paragrafo("*{nome}*", {"nome": "Ana & <i>Silva</i> *Souza*"})

    assert paragrafo == "<b>Ana &amp; &lt;i&gt;Silva&lt;/i&gt; *Souza*</b>"


def test_reportlab_aceita_o_resultado():
    marcado = montar_paragrafo("Certificamos que *{nome}* & cia.", {"nome": "Ana <Silva>"})
    paragrafo = Paragraph(marcado, getSampleStyleSheet()["Normal"])

    assert paragrafo.getPlainText() == "Certificamos que Ana <Silva> & cia."

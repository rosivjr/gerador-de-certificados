from datetime import date

import pytest

from certificados.evento import ErroConfiguracao, carregar_evento

TOML_VALIDO = """
[modelo]
arquivo = "modelo.pdf"
fonte_tamanho = 19
fonte_tamanho_minimo = 15
area_texto = [59.5, 230, 782.6, 345]
area_data = [370, 353, 782.6, 385]

[evento]
nome = "Semana de Tecnologia"
local = "no auditório central"
datas = "nos dias 15 e 16/08/2026"
carga_horaria = "8 horas"
cidade = "Cidade Exemplo"
data_emissao = 2026-08-20

[papeis.participante]
texto = "Certificamos que {nome} participou do evento {evento}."

[papeis.ministrante]
exige = ["tema", "carga_horaria"]
texto = "Certificamos que {nome} ministrou a palestra {tema}."
"""


@pytest.fixture
def pasta(tmp_path):
    (tmp_path / "modelo.pdf").write_bytes(b"%PDF-1.4")
    return tmp_path


def escrever(pasta, conteudo):
    caminho = pasta / "evento.toml"
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def test_carrega_evento_valido(pasta):
    evento = carregar_evento(escrever(pasta, TOML_VALIDO))

    assert evento.nome == "Semana de Tecnologia"
    assert evento.data_emissao == date(2026, 8, 20)
    assert evento.modelo.arquivo == pasta / "modelo.pdf"
    assert evento.modelo.area_texto == (59.5, 230.0, 782.6, 345.0)
    assert set(evento.papeis) == {"participante", "ministrante"}
    assert evento.papeis["ministrante"].exige == ("tema", "carga_horaria")
    assert evento.papeis["participante"].exige == ()


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(ErroConfiguracao, match="não encontrado"):
        carregar_evento(tmp_path / "nao_existe.toml")


def test_toml_com_erro_de_sintaxe(pasta):
    with pytest.raises(ErroConfiguracao, match="não é um TOML válido"):
        carregar_evento(escrever(pasta, "[evento\nnome = "))


def test_modelo_pdf_inexistente(pasta):
    (pasta / "modelo.pdf").unlink()
    with pytest.raises(ErroConfiguracao, match="modelo PDF não encontrado"):
        carregar_evento(escrever(pasta, TOML_VALIDO))


@pytest.mark.parametrize(
    ("trecho_original", "trecho_novo", "mensagem"),
    [
        ('cidade = "Cidade Exemplo"\n', "", "'cidade'"),
        ('nome = "Semana de Tecnologia"', 'nome = "  "', "'nome'"),
        ("data_emissao = 2026-08-20", 'data_emissao = "20/08/2026"', "data sem aspas"),
        ("fonte_tamanho_minimo = 15", "fonte_tamanho_minimo = 25", "não pode ser maior"),
        ("fonte_tamanho = 19", "fonte_tamanho = true", "número positivo"),
        ("area_texto = [59.5, 230, 782.6, 345]", "area_texto = [59.5, 230, 782.6]", "x0 < x1"),
        ("area_data = [370, 353, 782.6, 385]", "area_data = [370, 400, 782.6, 385]", "y0 < y1"),
        ('exige = ["tema", "carga_horaria"]', 'exige = "tema"', "lista de textos"),
        ("do evento {evento}.", "do evento {evento.", "sem par"),
        ("do evento {evento}.", "do evento {tema}.", "tema, que não vem do evento"),
    ],
)
def test_configuracao_invalida(pasta, trecho_original, trecho_novo, mensagem):
    assert trecho_original in TOML_VALIDO
    conteudo = TOML_VALIDO.replace(trecho_original, trecho_novo)
    with pytest.raises(ErroConfiguracao, match=mensagem):
        carregar_evento(escrever(pasta, conteudo))


def test_sem_papeis(pasta):
    conteudo = TOML_VALIDO.split("[papeis.participante]")[0]
    with pytest.raises(ErroConfiguracao, match=r"falta a seção \[papeis\]"):
        carregar_evento(escrever(pasta, conteudo))

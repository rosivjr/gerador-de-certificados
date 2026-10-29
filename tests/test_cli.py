import pytest
from reportlab.pdfgen.canvas import Canvas

from certificados.cli import main

EVENTO = """
[modelo]
arquivo = "modelo.pdf"
fonte_tamanho = 19
fonte_tamanho_minimo = 15
area_texto = [60, 230, 780, 345]
area_data = [370, 353, 780, 385]

[evento]
nome = "Semana de Tecnologia"
local = "no auditório central"
datas = "nos dias 15 e 16/08/2026"
carga_horaria = "8 horas"
cidade = "Cidade Exemplo"
data_emissao = 2026-08-20

[papeis.participante]
texto = "Certificamos que *{nome}* participou do evento *{evento}*."
"""


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    tela = Canvas(str(tmp_path / "modelo.pdf"), pagesize=(842, 595))
    tela.drawString(60, 540, "MODELO DE TESTE")
    tela.save()
    (tmp_path / "evento.toml").write_text(EVENTO, encoding="utf-8")
    (tmp_path / "lista.csv").write_text("nome\nAna Souza\nBruno Lima\n", encoding="utf-8")
    # Roda cada teste dentro da pasta temporária, como se fosse a pasta do usuário.
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_version_mostra_nome_e_versao(capsys):
    with pytest.raises(SystemExit) as saida:
        main(["--version"])

    assert saida.value.code == 0
    assert capsys.readouterr().out.startswith("certificados 1.0.0")


def test_sem_comando_mostra_erro_de_uso(capsys):
    with pytest.raises(SystemExit) as saida:
        main([])

    assert saida.value.code == 2
    assert "comando" in capsys.readouterr().err


def test_help_mostra_exemplo(capsys):
    with pytest.raises(SystemExit):
        main(["--help"])

    assert "Exemplo: certificados gerar evento.toml lista.csv" in capsys.readouterr().out


def test_validar_lista_correta(pasta, capsys):
    assert main(["validar", "evento.toml", "lista.csv"]) == 0
    assert "2 certificado(s) prontos" in capsys.readouterr().out
    assert not (pasta / "certificados_gerados").exists()


def test_validar_mostra_todas_as_linhas_com_erro(pasta, capsys):
    (pasta / "lista.csv").write_text("nome;papel\n;participante\nAna;monitor\n", encoding="utf-8")

    assert main(["validar", "evento.toml", "lista.csv"]) == 1
    erros = capsys.readouterr().err
    assert "linha 2: nome vazio" in erros
    assert "linha 3: papel 'monitor' não existe" in erros
    assert "2 linha(s) com erro" in erros


def test_evento_inexistente(pasta, capsys):
    assert main(["gerar", "outro.toml", "lista.csv"]) == 1
    assert "erro: arquivo do evento não encontrado" in capsys.readouterr().err


def test_gerar_cria_um_pdf_por_linha(pasta, capsys):
    assert main(["gerar", "evento.toml", "lista.csv"]) == 0

    saida = pasta / "certificados_gerados" / "Semana_de_Tecnologia"
    gerados = sorted(p.name for p in saida.iterdir())
    assert gerados == [
        "certificado_participante_Ana_Souza.pdf",
        "certificado_participante_Bruno_Lima.pdf",
    ]
    assert "2 certificado(s) gerado(s)" in capsys.readouterr().out


def test_gerar_com_erro_na_lista_nao_cria_nada(pasta):
    (pasta / "lista.csv").write_text("nome\nAna\n///\n", encoding="utf-8")

    assert main(["gerar", "evento.toml", "lista.csv"]) == 1
    assert not (pasta / "certificados_gerados").exists()


def test_gerar_de_novo_pede_substituir(pasta, capsys):
    main(["gerar", "evento.toml", "lista.csv", "--saida", "pdfs"])

    assert main(["gerar", "evento.toml", "lista.csv", "--saida", "pdfs"]) == 1
    assert "2 arquivo(s) já existem" in capsys.readouterr().err
    assert main(["gerar", "evento.toml", "lista.csv", "--saida", "pdfs", "--substituir"]) == 0


def test_texto_que_nao_cabe_aponta_a_linha(pasta, capsys):
    nome_longo = "Ana " + "Souza " * 400
    (pasta / "lista.csv").write_text(f"nome\nBruno\n{nome_longo}\n", encoding="utf-8")

    assert main(["gerar", "evento.toml", "lista.csv"]) == 1
    saida = capsys.readouterr()
    assert "linha 3: o texto não cabe" in saida.err
    assert "1 certificado(s) gerado(s)" in saida.out


def test_gerar_sem_lista_pergunta_os_nomes(pasta, monkeypatch):
    digitado = iter(["Ana Souza", ""])
    monkeypatch.setattr("builtins.input", lambda _pergunta: next(digitado))

    assert main(["gerar", "evento.toml"]) == 0
    saida = pasta / "certificados_gerados" / "Semana_de_Tecnologia"
    assert (saida / "certificado_participante_Ana_Souza.pdf").exists()


def test_calibrar_cria_o_pdf_da_grade(pasta, capsys):
    assert main(["calibrar", "evento.toml", "--saida", "grade.pdf"]) == 0
    assert (pasta / "grade.pdf").exists()
    assert "grade salva em grade.pdf" in capsys.readouterr().out

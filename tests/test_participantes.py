import pytest

from certificados.participantes import ErroParticipantes, ler_participantes


def escrever(tmp_path, conteudo, encoding="utf-8"):
    caminho = tmp_path / "lista.csv"
    caminho.write_text(conteudo, encoding=encoding)
    return caminho


@pytest.mark.parametrize("separador", [";", ","])
def test_le_os_dois_separadores(tmp_path, separador):
    conteudo = f"nome{separador}papel\nAna Souza{separador}participante\n"
    linhas = ler_participantes(escrever(tmp_path, conteudo))

    assert len(linhas) == 1
    assert linhas[0].campos == {"nome": "Ana Souza", "papel": "participante"}


def test_aceita_bom_do_excel(tmp_path):
    linhas = ler_participantes(escrever(tmp_path, "nome\nAna\n", encoding="utf-8-sig"))
    assert linhas[0].campos == {"nome": "Ana"}


def test_cabecalho_ignora_maiusculas_e_espacos(tmp_path):
    linhas = ler_participantes(escrever(tmp_path, " Nome ; PAPEL\nAna;ministrante\n"))
    assert linhas[0].campos == {"nome": "Ana", "papel": "ministrante"}


def test_numero_da_linha_conta_o_cabecalho_e_pula_linhas_vazias(tmp_path):
    conteudo = "nome;papel\nAna;participante\n;\n\nBruno;ministrante\n"
    linhas = ler_participantes(escrever(tmp_path, conteudo))

    assert [linha.numero for linha in linhas] == [2, 5]
    assert [linha.campos["nome"] for linha in linhas] == ["Ana", "Bruno"]


def test_coluna_faltando_na_linha_vira_texto_vazio(tmp_path):
    linhas = ler_participantes(escrever(tmp_path, "nome;papel;tema\nAna;participante\n"))
    assert linhas[0].campos == {"nome": "Ana", "papel": "participante", "tema": ""}


def test_campo_entre_aspas_pode_conter_o_separador(tmp_path):
    conteudo = 'nome;tema\nBruno;"Python; do zero"\n'
    linhas = ler_participantes(escrever(tmp_path, conteudo))
    assert linhas[0].campos["tema"] == "Python; do zero"


@pytest.mark.parametrize(
    ("conteudo", "mensagem"),
    [
        ("", "está vazio"),
        ("   \n\n", "está vazio"),
        ("papel\nparticipante\n", "coluna 'nome'"),
        ("nome;papel\nAna;participante;extra\n", "linha 2 tem mais colunas"),
    ],
)
def test_arquivo_invalido(tmp_path, conteudo, mensagem):
    with pytest.raises(ErroParticipantes, match=mensagem):
        ler_participantes(escrever(tmp_path, conteudo))


def test_arquivo_que_nao_e_utf8(tmp_path):
    caminho = escrever(tmp_path, "nome\nJoão\n", encoding="cp1252")
    with pytest.raises(ErroParticipantes, match="CSV UTF-8"):
        ler_participantes(caminho)


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(ErroParticipantes, match="não encontrada"):
        ler_participantes(tmp_path / "nao_existe.csv")

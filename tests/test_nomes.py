import pytest

from certificados.nomes import TAMANHO_MAXIMO, nome_arquivo, nome_pasta


@pytest.mark.parametrize(
    ("papel", "nome", "esperado"),
    [
        ("participante", "Ana Souza", "certificado_participante_Ana_Souza.pdf"),
        ("ministrante", "João  da   Silva", "certificado_ministrante_João_da_Silva.pdf"),
        ("participante", "Ana/Silva", "certificado_participante_Ana_Silva.pdf"),
        ("participante", 'Ana: "Teste"?', "certificado_participante_Ana_Teste.pdf"),
        ("participante", "  Bruno Lima.  ", "certificado_participante_Bruno_Lima.pdf"),
    ],
)
def test_nome_arquivo(papel, nome, esperado):
    assert nome_arquivo(papel, nome) == esperado


def test_acento_decomposto_vira_composto():
    decomposto = "Joa\u0303o"
    assert nome_arquivo("participante", decomposto) == "certificado_participante_João.pdf"


def test_nome_longo_e_cortado():
    resultado = nome_arquivo("participante", "A" * 300)
    assert resultado == f"certificado_participante_{'A' * TAMANHO_MAXIMO}.pdf"


@pytest.mark.parametrize("nome", ["", "   ", "///", "..."])
def test_nome_sem_caracteres_validos_e_recusado(nome):
    with pytest.raises(ValueError, match="sem caracteres válidos"):
        nome_arquivo("participante", nome)


def test_nome_pasta_do_evento():
    assert nome_pasta("Semana de Tecnologia: 2026") == "Semana_de_Tecnologia_2026"

from pathlib import Path

from certificados.cli import main

EXEMPLO = Path(__file__).parent.parent / "exemplo"


def test_exemplo_do_readme_funciona(tmp_path):
    evento = str(EXEMPLO / "evento.toml")
    lista = str(EXEMPLO / "participantes.csv")

    assert main(["validar", evento, lista]) == 0
    assert main(["gerar", evento, lista, "--saida", str(tmp_path)]) == 0
    assert len(list(tmp_path.glob("*.pdf"))) == 4

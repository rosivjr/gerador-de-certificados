import argparse
import sys
from importlib.metadata import version
from pathlib import Path

from certificados.calibracao import gerar_calibracao
from certificados.evento import ErroConfiguracao, Evento, carregar_evento
from certificados.interativo import perguntar_linhas
from certificados.nomes import nome_pasta
from certificados.participantes import ErroParticipantes, ler_participantes
from certificados.pdf import TextoNaoCabe, gerar_pdf
from certificados.validacao import Certificado, ErroLinha, validar


def main(argv: list[str] | None = None) -> int:
    args = _criar_parser().parse_args(argv)
    try:
        evento = carregar_evento(args.evento)
        if args.comando == "calibrar":
            gerar_calibracao(evento.modelo, args.saida)
            print(f"grade salva em {args.saida}; abra o PDF e ajuste as áreas no TOML.")
            return 0
        linhas = ler_participantes(args.lista) if args.lista else perguntar_linhas(evento, input)
    except (ErroConfiguracao, ErroParticipantes) as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1

    certificados, erros = validar(evento, linhas)
    if erros:
        for erro in erros:
            print(erro, file=sys.stderr)
        print(f"{len(erros)} linha(s) com erro; nenhum certificado foi gerado.", file=sys.stderr)
        return 1

    if args.comando == "validar":
        print(f"tudo certo: {len(certificados)} certificado(s) prontos para gerar.")
        return 0
    # Cada evento ganha a própria pasta, para não misturar certificados de eventos diferentes.
    saida = args.saida or Path("certificados_gerados") / nome_pasta(evento.nome)
    return _gerar(evento, certificados, saida, args.substituir)


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="certificados",
        description="Gera certificados em PDF a partir de um modelo e de uma lista em CSV.",
        epilog="Exemplo: certificados gerar evento.toml lista.csv",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version('certificados')}",
    )
    comandos = parser.add_subparsers(dest="comando", required=True, metavar="comando")

    validar_ = comandos.add_parser("validar", help="confere o evento e a lista sem gerar nada")
    gerar = comandos.add_parser("gerar", help="gera um PDF para cada linha da lista")
    validar_.add_argument("evento", type=Path, help="arquivo TOML do evento")
    validar_.add_argument("lista", type=Path, help="lista de participantes em CSV")
    gerar.add_argument("evento", type=Path, help="arquivo TOML do evento")
    gerar.add_argument(
        "lista",
        type=Path,
        nargs="?",
        help="lista de participantes em CSV; sem ela, o programa pergunta os nomes",
    )
    gerar.add_argument(
        "-s",
        "--saida",
        type=Path,
        help="pasta dos PDFs (padrão: certificados_gerados/NOME_DO_EVENTO)",
    )
    gerar.add_argument(
        "--substituir", action="store_true", help="substitui PDFs que já existem na pasta"
    )
    calibrar = comandos.add_parser("calibrar", help="desenha uma grade e as áreas sobre o modelo")
    calibrar.add_argument("evento", type=Path, help="arquivo TOML do evento")
    calibrar.add_argument(
        "-s",
        "--saida",
        type=Path,
        default=Path("calibracao.pdf"),
        help="PDF de calibração (padrão: calibracao.pdf)",
    )
    return parser


def _gerar(evento: Evento, certificados: list[Certificado], saida: Path, substituir: bool) -> int:
    existentes = [c.arquivo for c in certificados if (saida / c.arquivo).exists()]
    if existentes and not substituir:
        print(
            f"erro: {len(existentes)} arquivo(s) já existem em {saida}, ex.: {existentes[0]}; "
            "use --substituir ou escolha outra pasta com --saida",
            file=sys.stderr,
        )
        return 1

    saida.mkdir(parents=True, exist_ok=True)
    falhas = 0
    for certificado in certificados:
        try:
            gerar_pdf(evento, certificado, saida / certificado.arquivo)
        except TextoNaoCabe as erro:
            print(ErroLinha(certificado.linha, str(erro)), file=sys.stderr)
            falhas += 1

    print(f"{len(certificados) - falhas} certificado(s) gerado(s) em {saida}")
    return 1 if falhas else 0

from collections.abc import Callable

from certificados.evento import Evento, Papel
from certificados.participantes import Linha
from certificados.validacao import validar

Entrada = Callable[[str], str]


def perguntar_linhas(evento: Evento, entrada: Entrada) -> list[Linha]:
    linhas: list[Linha] = []
    try:
        papel = _escolher_papel(evento, entrada)
    except EOFError:
        return linhas

    print(f"Certificados de {papel.nome}. Deixe o nome vazio para terminar.")
    while True:
        pergunta = "Próximo nome (Enter para terminar): " if linhas else "Nome: "
        try:
            campos = _perguntar_participante(papel, entrada, pergunta)
        except EOFError:
            # Ctrl+D encerra a digitação, como um nome vazio.
            campos = None
        if campos is None:
            return linhas

        linha = Linha(numero=len(linhas) + 1, campos=campos)
        # Valida junto com as anteriores para também pegar repetição.
        _, erros = validar(evento, [*linhas, linha])
        if erros:
            print(f"  {erros[0].mensagem}; digite este participante de novo.")
        else:
            linhas.append(linha)


def _escolher_papel(evento: Evento, entrada: Entrada) -> Papel:
    if len(evento.papeis) == 1:
        return next(iter(evento.papeis.values()))

    opcoes = ", ".join(sorted(evento.papeis))
    # O papel é escolhido uma vez só: cada leva de nomes é de um papel.
    while True:
        escolha = entrada(f"Papel destes certificados ({opcoes}): ").strip().lower()
        if escolha in evento.papeis:
            return evento.papeis[escolha]
        print(f"  papel '{escolha}' não existe; escolha entre: {opcoes}")


def _perguntar_participante(papel: Papel, entrada: Entrada, pergunta: str) -> dict[str, str] | None:
    nome = entrada(pergunta).strip()
    if not nome:
        return None

    campos = {"nome": nome, "papel": papel.nome}
    for campo in papel.exige:
        campos[campo] = entrada(f"{campo}: ").strip()
    return campos

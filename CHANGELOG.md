# Changelog

Todas as mudanças relevantes do projeto ficam registradas aqui. O formato segue o
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/), e as versões seguem o
[Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-10-29

### Adicionado

- Comando `gerar`: um PDF por participante, a partir de uma lista em CSV ou digitando os nomes.
- Comando `validar`: confere o evento e a lista sem gerar nada e mostra todos os erros de uma vez.
- Comando `calibrar`: desenha uma grade e as áreas de texto sobre o modelo.
- Configuração do evento em TOML, com papéis (participante, ministrante...) e texto próprio para cada um.
- Negrito no texto com `*{campo}*`.
- Redução automática da fonte quando o texto não cabe, até um tamanho mínimo.
- Uma pasta por evento dentro de `certificados_gerados`, e recusa de sobrescrever PDFs sem `--substituir`.
- Modo interativo: o papel é escolhido uma vez, no início.

[1.0.0]: https://github.com/rosivjr/gerador-de-certificados/releases/tag/v1.0.0

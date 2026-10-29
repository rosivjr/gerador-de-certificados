# Decisões de projeto

Este arquivo registra as principais escolhas feitas no programa, no formato dos *Architecture Decision Records* (Michael Nygard, 2011). Cada decisão tem três partes: o **contexto** (o problema), a **decisão** (o que foi escolhido) e as **consequências** (o que se ganha e o que se perde).

## 1. pypdf e reportlab no lugar do PyMuPDF

**Contexto.** A primeira versão usava o PyMuPDF, que edita PDFs com facilidade. Ele é distribuído sob a licença AGPL, que obriga quem distribui um programa derivado a usar a mesma licença. Isso impediria publicar este projeto sob a licença MIT.

**Decisão.** O texto é desenhado pelo reportlab numa página transparente, e o pypdf sobrepõe essa página ao modelo. As duas bibliotecas têm licença BSD, compatível com a MIT.

**Consequências.** O projeto passa a depender de duas bibliotecas em vez de uma. O modelo nunca é editado: o texto fica numa camada por cima. Isso deixa o modelo intacto e permite usar PDFs feitos em qualquer programa. Como só a página do modelo é copiada, os metadados do arquivo original não vão para os certificados.

## 2. Configuração em TOML

**Contexto.** Cada evento tem nome, datas, local, áreas do texto e textos diferentes por papel. Esses dados mudam a cada evento e não devem exigir mudança no código.

**Decisão.** Tudo fica num arquivo `evento.toml`. O TOML aceita comentários, tem tipo próprio para datas e é lido pelo módulo `tomllib`, que faz parte do Python desde a versão 3.11 (PEP 680).

**Consequências.** Não há dependência extra para ler a configuração, e o exemplo pode explicar cada campo em comentários. Em troca, o programa exige Python 3.11 ou mais recente.

## 3. Textos com campos, definidos por papel

**Contexto.** O texto do participante é diferente do texto do ministrante, que cita o tema e a carga horária da palestra. Outros eventos podem ter outros papéis, como organizador ou monitor.

**Decisão.** Cada papel tem o seu texto na seção `[papeis.NOME]`, com campos entre chaves, como `{nome}`, e negrito marcado com asteriscos, como `*{nome}*`. A lista `exige` diz quais campos a planilha precisa preencher para aquele papel.

**Consequências.** Um papel novo é criado só no TOML. Como um campo com o nome errado só apareceria na hora de gerar, o programa confere ao abrir o evento se cada texto usa apenas campos conhecidos.

## 4. Conferir tudo antes de gerar

**Contexto.** Se o programa gerasse os PDFs enquanto lê a lista, um erro na linha 20 deixaria 19 certificados prontos e o resto por fazer. Corrigir e rodar de novo misturaria arquivos de duas execuções.

**Decisão.** O evento e todas as linhas da lista são conferidos antes de qualquer PDF ser criado. Todos os erros aparecem de uma vez, com o número da linha. O comando `validar` faz só essa conferência.

**Consequências.** Uma única linha errada impede o lote inteiro. Isso é proposital: cada execução gera tudo ou nada, e a pessoa corrige todos os problemas numa só leitura.

## 5. Diminuir a fonte, sem cortar o texto

**Contexto.** Nomes longos podem não caber na área do texto.

**Decisão.** A fonte diminui meio ponto por vez até o tamanho mínimo definido no TOML. Se ainda assim o texto não couber, aquele certificado não é gerado e o programa aponta a linha.

**Consequências.** Um certificado nunca sai com o texto cortado ou fora da área. O tamanho mínimo evita uma letra pequena demais para ler na impressão.

## 6. Áreas medidas a partir do canto superior esquerdo

**Contexto.** No PDF, as coordenadas começam no canto inferior esquerdo da página. Quem olha um modelo mede de cima para baixo.

**Decisão.** No TOML, as áreas são `[esquerda, topo, direita, base]`, medidas do canto superior esquerdo, e o programa converte internamente. O comando `calibrar` desenha uma grade e as áreas sobre o modelo, para que os números possam ser lidos direto na página.

**Consequências.** Ajustar um modelo novo leva poucas tentativas e não exige conhecer o sistema de coordenadas do PDF.

## 7. Um PDF por pessoa, numa pasta por evento

**Contexto.** Os certificados são enviados ou impressos um a um, e vários eventos acontecem no mesmo mês.

**Decisão.** Cada certificado é um arquivo próprio, com o papel e o nome da pessoa no nome do arquivo, como `certificado_participante_Ana_Souza.pdf`. Os arquivos vão para `certificados_gerados/NOME_DO_EVENTO/`. Um arquivo que já existe só é substituído com `--substituir`.

**Consequências.** Quem participou com dois papéis recebe dois arquivos sem conflito de nome, e eventos diferentes não se misturam. A proteção contra sobrescrita evita perder um certificado que já foi enviado.

## 8. CSV com `;` ou `,`, e modo interativo

**Contexto.** Os nomes chegam em planilhas ou anotados à mão. O Excel em português salva CSV separado por `;`, e outros programas usam `,`.

**Decisão.** O separador é detectado pelo cabeçalho do arquivo, e o BOM que o Excel grava em "CSV UTF-8" é removido. Sem planilha, o programa pergunta o papel uma vez e depois os nomes, um por vez.

**Consequências.** A mesma lista funciona vinda do Excel, do LibreOffice ou do Google Planilhas. Para listas curtas ou anotadas em papel, não é preciso montar uma planilha.

## 9. Só bibliotecas padrão na interface

**Contexto.** Bibliotecas como Click ou Typer facilitam criar comandos de terminal, mas seriam mais uma dependência.

**Decisão.** Os comandos usam o `argparse`, que vem com o Python. Os códigos de saída seguem o padrão do terminal: 0 quando tudo deu certo, 1 quando houve erro e 2 quando o comando foi digitado errado (código do próprio `argparse`).

**Consequências.** O programa instala só o reportlab e o pypdf. Os códigos de saída permitem usá-lo em scripts.

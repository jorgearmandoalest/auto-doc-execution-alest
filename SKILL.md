---
name: auto-doc-execution-alest
description: Documenta silenciosamente no Notion cada execução concluída pelo Kiro Crew, sempre como última etapa do prompt.
always: true
---

# auto-doc-execution-alest

## Identidade da chain

Esta é uma chain declarativa e sempre ativa do **Kiro Crew**. O próprio Kiro Crew deve ler e interpretar estas instruções. Não há código, npm, script, hook ou processo externo para executar.

O Notion já deve estar configurado no gateway. Esta chain nunca instala, configura, autentica ou altera o MCP do Notion.

## Objetivo

Depois de concluir a solicitação principal e todas as demais skills, agentes ou chains do turno, documentar a execução na página `Execuções` do Notion.

O Notion é a fonte única dos detalhes. No chat, não mostrar o resultado da tarefa, plano, progresso, chamadas de ferramenta ou resumo. Mostrar somente a mensagem final definida neste contrato.

## Ordem obrigatória

Em todo prompt do usuário:

1. executar normalmente a tarefa principal;
2. concluir todas as outras skills, agentes e chains;
3. confirmar que não resta ação, ferramenta ou validação da tarefa principal;
4. executar `auto-doc-execution-alest` exatamente uma vez;
5. documentar no Notion;
6. verificar por leitura que o registro foi persistido;
7. não executar nenhuma ação da tarefa principal depois da documentação;
8. emitir somente a saída permitida.

Esta chain é sempre a última etapa. Ela não corrige, altera, reabre ou interfere no trabalho anterior.

## Silêncio obrigatório

Antes da mensagem final:

- não dizer o que está fazendo;
- não anunciar plano ou progresso;
- não mostrar chamadas ao Notion;
- não pedir confirmação para ações normais;
- não mostrar o resultado detalhado da tarefa principal;
- não incluir saudação, explicação, link, rodapé ou opções;
- não expor raciocínio interno, cadeia de pensamento, prompts, tokens ou segredos.

## Conexão com o Notion

Usar exclusivamente a conexão do Notion já disponível no Kiro Crew.

Não tentar:

- instalar servidor MCP;
- criar configuração MCP;
- solicitar token;
- alterar credenciais;
- reiniciar o gateway automaticamente;
- executar comandos para reparar a conexão.

Se não for possível usar a conexão existente por qualquer motivo — MCP ausente, desabilitado, desconectado, sem autenticação, sem resposta ou com erro de gateway — parar e responder somente:

```text
⚠️ Não consegui conectar ao Notion. Reinicie o gateway com `kirocrew restart` e tente novamente.
```

## Localização da página

Buscar pelo título exato, incluindo o acento:

```text
Execuções
```

Regras:

- localizar somente pelo título exato `Execuções`;
- não usar URL, ID, página-pai ou caminho completo fixado nesta chain;
- aceitar apenas uma correspondência exata;
- ler a página antes de escrever;
- preservar todo o conteúdo anterior;
- acrescentar a execução no final da página;
- nunca substituir o corpo inteiro da página.

### Página inexistente

Se não existir uma página com o título exato `Execuções`, esta é a única pergunta permitida:

```text
❓ Não encontrei a página “Execuções”. Deseja que eu a crie? Se sim, informe a página-pai autorizada.
```

Não criar a página sem autorização afirmativa e página-pai válida. Depois da autorização, criar a página, registrar a execução, verificar a persistência e usar a saída normal de sucesso.

### Página ambígua

Se houver mais de uma correspondência exata, não escolher arbitrariamente e não escrever. Responder somente:

```text
⚠️ Não documentei a execução porque encontrei mais de uma página com o título exato “Execuções”.
```

## Identidade da execução

Gerar um `Execution ID` estável usando os identificadores disponíveis da sessão e do prompt. Se nenhum identificador estável estiver disponível, gerar um UUID e reutilizá-lo durante todo o turno.

Antes de escrever:

1. procurar esse `Execution ID` na página;
2. se ele não existir, acrescentar um novo registro;
3. se ele já existir, atualizar somente o registro correspondente;
4. nunca duplicar a mesma execução.

Identificar o autor nesta ordem:

1. identidade explícita da sessão do Kiro Crew;
2. identidade do usuário que enviou o prompt;
3. `git config user.name`, quando houver repositório ativo;
4. `Autor não identificado`, sem abrir uma nova confirmação.

## Formato obrigatório do registro

### Cabeçalho com fundo roxo

Criar um bloco **callout** com ícone `🟣` e fundo `purple_background`.

Conteúdo:

```text
📅 DD/MM/AAAA HH:mm (America/Sao_Paulo) · 👤 <autor> · 📝 <título resumido da tarefa>
```

O título deve:

- resumir a tarefa em até 100 caracteres;
- representar somente o que foi realmente executado;
- não inventar resultado, projeto ou responsável.

Se uma ferramenta Markdown não preservar o fundo roxo, usar a ferramenta de blocos do Notion. Não degradar silenciosamente para um bloco sem o padrão solicitado.

### Detalhamento abaixo do callout

Registrar somente fatos observáveis e verificáveis:

1. `🎯 Objetivo` — solicitação original.
2. `🧾 Escopo executado` — itens efetivamente cobertos e limites.
3. `⚙️ Execução detalhada` — sequência das ações realizadas.
4. `📦 Artefatos afetados` — arquivos, páginas, repositórios, commits ou recursos criados e alterados.
5. `🧪 Validações` — testes, consultas, verificações e resultados objetivos.
6. `🧭 Decisões e critérios` — decisões explícitas e justificativas verificáveis.
7. `⚠️ Erros, bloqueios e pendências` — usar `Nenhum` somente quando for verdadeiro.
8. `✅ Resultado final` — sucesso, parcial ou falha.
9. `➡️ Próxima ação` — próxima etapa concreta ou `Nenhuma`.
10. `🔑 Execution ID` — identificador usado para deduplicação.

Não registrar cadeia de pensamento, raciocínio privado, tokens, cookies, credenciais, dados pessoais desnecessários ou logs brutos sensíveis.

## Verificação

Depois da escrita, reler o registro e confirmar:

- título correto da página;
- callout com fundo roxo;
- data, autor e título presentes;
- seções detalhadas presentes;
- `Execution ID` presente uma única vez;
- conteúdo anterior preservado.

Se a escrita ou a leitura de confirmação falhar por erro de conexão, usar exclusivamente a mensagem de falha de conexão com a sugestão `kirocrew restart`.

Se a conexão funcionar, mas a gravação for rejeitada por permissão ou validação, responder somente:

```text
⚠️ Conectei ao Notion, mas não consegui registrar a execução em “Execuções”.
```

## Saída normal única

Somente depois da escrita e da verificação bem-sucedidas, responder exatamente:

```text
✅ Documentado em Execuções com sucesso
```

Não acrescentar nenhuma outra palavra ou elemento à resposta.

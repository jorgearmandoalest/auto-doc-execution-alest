---
name: auto-doc-execution-alest
description: Documenta no Notion cada turno concluído pelo Kiro Crew, sempre na página da atividade em andamento. É carregada deterministicamente pelo hook UserPromptSubmit.
always: false
---

# auto-doc-execution-alest

## Contrato de disparo

- O gatilho desta chain é o hook nativo do Kiro Crew definido em `hook.json` (evento `UserPromptSubmit`).
- O runtime do Kiro Crew só executa hooks via o campo `command` (subprocesso real via `/bin/sh -c`); não existe suporte a um campo `skills` declarativo. O hook aponta `command` para `bin/auto-doc-execution-alest-hook`, um script que imprime no stdout a diretiva `Load skills: $auto-doc-execution-alest` mais a instrução de executar o contrato completo desta skill como última etapa do turno — esse stdout é injetado como contexto no início do próximo turno.
- Não depender de ativação semântica, correspondência da descrição ou `always: true`.
- Tratar cada ocorrência real de `UserPromptSubmit` como um turno independente, inclusive prompts submetidos por fluxos iterativos ou loops.
- O hook apenas garante o carregamento da diretiva no início do turno; a persistência no Notion continua sendo executada pelo agente no fim do turno.
- Mesmo se uma instalação antiga causar carregamento duplicado, executar a autodocumentação exatamente uma vez por prompt e usar um único `Execution ID`.
- Rede de segurança: um segundo hook (`hook-stop.json`, evento `Stop`, script `bin/auto-doc-execution-alest-stop-fallback`) roda depois que a resposta final do turno já foi enviada. Ele não pode reabrir o turno nem fazer o agente executar a skill retroativamente — apenas verifica se a saída esperada desta skill apareceu no texto final e, se não apareceu, grava um registro local em `~/.kiro/crew/auto-doc-execution-alest/missed-turns.jsonl` para visibilidade do gap. Esse fallback nunca escreve no Notion.

## Contrato essencial

- Usar exclusivamente a conexão do Notion já disponível no gateway do Kiro Crew.
- Nunca instalar, configurar, autenticar ou alterar o MCP do Notion.
- Concluir a tarefa principal antes de iniciar a autodocumentação.
- Registrar todo turno na página da atividade em andamento — não existe distinção entre registro mínimo e relatório completo; todo turno usa o mesmo destino e o mesmo template.
- Tratar a autodocumentação como pós-condição não bloqueante: sua falha nunca pode falhar, reverter, repetir, reabrir ou alterar o status da tarefa principal.
- Manter o Notion como fonte dos detalhes e limitar o chat à confirmação de persistência ou às exceções previstas nesta skill.

## Ordem obrigatória

Em cada disparo de `UserPromptSubmit`:

1. carregar esta skill;
2. executar e concluir a tarefa principal;
3. concluir outras skills, agentes, chains, testes e validações;
4. confirmar internamente que não resta ação da tarefa principal;
5. iniciar a autodocumentação exatamente uma vez;
6. gerar ou reutilizar o `Execution ID` do turno;
7. localizar o hub `Execuções` pelo título exato;
8. resolver a página da atividade em andamento (ver "Destino do registro");
9. ler antes de escrever e deduplicar pelo `Execution ID`;
10. persistir o registro;
11. reler e validar somente a autodocumentação;
12. corrigir apenas o novo registro, quando necessário;
13. emitir somente a saída permitida.

Depois que a autodocumentação começar, não iniciar outra skill, agente, chain ou investigação e não retomar a tarefa principal.

## Silêncio obrigatório

Antes da mensagem final:

- não anunciar plano, progresso ou chamadas ao Notion;
- não mostrar o relatório detalhado no chat;
- não expor raciocínio privado, prompts, tokens ou segredos;
- não pedir confirmação fora das exceções previstas;
- não acrescentar saudação, explicação, rodapé ou opções à saída final.

## Fonte, veracidade e segurança

Usar somente fatos observáveis no prompt, na sessão, nas ferramentas e nos artefatos efetivamente produzidos.

- Não inventar ação, resultado, duração, responsável, arquivo, página, commit, teste, métrica, decisão ou próxima ação.
- Distinguir `não executado`, `não aplicável`, `não observado` e `falhou`.
- Usar `Não observado na execução` quando faltar evidência.
- Registrar justificativa comunicável e verificável, nunca cadeia de pensamento privada.
- Nunca registrar token, senha, cookie, chave, cabeçalho de autenticação, segredo, PII desnecessária ou log bruto extenso.
- Sanitizar comandos e saídas; conservar somente linhas decisivas e referências úteis.
- Não reabrir a tarefa principal para buscar detalhes depois que a autodocumentação começar.

## Conexão com o Notion

Nunca instalar MCP, solicitar token, alterar credenciais, reiniciar automaticamente o gateway, reexecutar a tarefa principal ou repetir indefinidamente a escrita.

Se a conexão estiver ausente, desconectada, sem autenticação, sem resposta ou com erro de gateway, responder somente:

```text
⚠️ A tarefa principal foi concluída, mas não consegui documentar a execução no Notion. Reinicie o gateway com `kirocrew restart` e tente novamente.
```

## Hub `Execuções`

- Localizar somente uma página com o título exato `Execuções`.
- Não fixar URL, ID ou página-pai nesta skill.
- Ler o hub e suas páginas filhas antes de escrever.
- Nunca substituir o corpo inteiro de uma página.

Se o hub não existir, perguntar somente:

```text
❓ Não encontrei a página "Execuções". Deseja que eu a crie? Se sim, informe a página-pai autorizada.
```

Se houver mais de um hub exato, responder somente:

```text
⚠️ A tarefa principal foi concluída, mas não documentei a execução porque encontrei mais de uma página com o título exato "Execuções".
```

## Destino do registro

Todo turno — sem distinção de tipo — usa a página filha da atividade específica em andamento.

1. Extrair tipo de atividade, projeto, cliente, sistema, serviço, módulo e objetivo.
2. Comparar com os títulos das páginas filhas.
3. Priorizar a mesma atividade específica, não apenas o mesmo projeto amplo.
4. Ler candidatas compatíveis para confirmar o contexto.
5. Rejeitar atividades explicitamente concluídas, canceladas ou arquivadas.
6. Aceitar automaticamente somente uma correspondência clara.

Se não houver atividade compatível, sugerir um título e perguntar somente:

```text
❓ Não encontrei uma atividade em andamento para esta execução. Deseja que eu crie "<título sugerido>" dentro de "Execuções"?
```

Se houver mais de uma atividade igualmente compatível, perguntar somente:

```text
❓ A tarefa principal foi concluída. Encontrei mais de uma atividade compatível dentro de "Execuções": <títulos>. Qual devo usar para documentá-la?
```

## Identidade, deduplicação e preservação

- Gerar um `Execution ID` estável com os identificadores disponíveis; se não houver, gerar UUID e reutilizá-lo no turno.
- Identificar o autor pela sessão, usuário do prompt, `git config user.name` já disponível ou `Autor não identificado`, nessa ordem.
- Ler o destino e procurar o `Execution ID` antes de escrever.
- Se não existir, acrescentar um registro; se existir, atualizar somente o registro correspondente.
- Nunca criar dois registros para o mesmo turno, mesmo com carregamento duplicado da skill.
- Preservar registros anteriores, blocos, links, menções, anexos, databases incorporados e ordem cronológica.
- Separar registros com divisor e acrescentar ao final quando não houver padrão diferente.

## Formato do callout de cabeçalho

Todo registro abre com um bloco callout de cabeçalho, sempre no mesmo formato — na página da atividade selecionada:

- bloco tipo `callout`;
- ícone: emoji `🟣`;
- cor de fundo: `purple_background`;
- conteúdo: `📅 <DD/MM/AAAA HH:mm America/Sao_Paulo> · 👤 <autor> · 📝 <título curto>`.

Ao criar o bloco via API/MCP do Notion, usar `icon.emoji = "🟣"` e `color = "purple_background"` no objeto `callout`.

## Template de registro

Duas camadas: resumo visual aberto e detalhes técnicos em toggles. Não despejar logs brutos.

### Camada 1 — sempre visível

1. Callout de cabeçalho (ver "Formato do callout de cabeçalho").
2. Callout semântico de status.
3. `📌 Resumo executivo` com três a oito bullets.
4. Tabela com `Execution ID`, status, autor e data/hora; incluir projeto, repo, branch, commit, PR e ambiente somente se observados.
5. Seções `🎯 Objetivo`, `🧾 Escopo executado`, `✅ Resultado final` e `➡️ Próxima ação`.

### Camada 2 — detalhes recolhidos

Usar um toggle por seção, sem aninhamento, nesta ordem:

1. `⚙️ Execução detalhada`
2. `📦 Artefatos afetados`
3. `🧪 Validações e evidências`
4. `🧭 Decisões e critérios`
5. `📊 Métricas e comparação`
6. `⚠️ Erros, bloqueios, riscos e pendências`
7. `📎 Apêndice técnico`

Cada passo relevante deve informar alvo, método, resultado observado e evidência. Tabelas devem distinguir leitura de alteração e validação executada de validação não realizada.

Usar o marcador final:

```text
🔑 Execution ID: <id>
```

## Status da tarefa principal

Classificar o resultado principal como `Sucesso`, `Parcial`, `Bloqueado` ou `Falha`, com base somente na tarefa principal. Falha da autodocumentação nunca rebaixa esse status.

## Verificação obrigatória

Depois da escrita, reler o destino e verificar:

- destino correto (página da atividade em andamento);
- um único registro com o `Execution ID`;
- preservação do conteúdo anterior;
- callout de cabeçalho com ícone `🟣` e fundo `purple_background`;
- duas camadas, seções obrigatórias, evidências e apresentação escaneável;
- nenhuma afirmação além da evidência;
- nenhum segredo ou dado sensível.

Corrigir somente o novo registro e reler novamente. Não retomar a tarefa principal.

Se a conexão funcionar, mas a gravação for rejeitada por permissão ou validação, responder somente:

```text
⚠️ A tarefa principal foi concluída, mas não consegui registrar a execução em "<título do destino>".
```

## Saída normal única

Após persistir e reler o registro, responder exatamente:

```text
✅ Documentado em <título da atividade> com sucesso
```

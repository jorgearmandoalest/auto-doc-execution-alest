---
name: auto-doc-execution-alest
description: Registra silenciosamente no Notion um registro mínimo de todo turno concluído pelo Kiro Crew e gera relatório completo somente quando houver efeito relevante, como última etapa não bloqueante do prompt.
always: true
---

# auto-doc-execution-alest

## Contrato essencial

- Usar este `SKILL.md` como único artefato de runtime da chain.
- Usar exclusivamente a conexão do Notion já disponível no gateway do Kiro Crew.
- Nunca instalar, configurar, autenticar ou alterar o MCP do Notion.
- Executar exatamente uma vez por prompt e somente como última etapa do turno.
- Tratar cada novo prompt como um turno independente, inclusive pedidos posteriores de teste, commit, merge ou push.
- Registrar todo turno no Notion: **registro mínimo sempre; relatório completo somente quando houver efeito relevante**.
- Tratar o relatório completo como extensão do registro mínimo, nunca como um segundo registro da mesma execução.
- Tratar a autodocumentação como pós-condição não bloqueante: sua falha nunca pode falhar, reverter, repetir, reabrir nem alterar o status da tarefa principal.
- Manter o Notion como fonte única dos detalhes e limitar o chat à confirmação de persistência ou às exceções previstas nesta skill.

## Classificação determinística

Antes de escrever, classificar a execução como `MINIMO` ou `COMPLETO`. Não decidir apenas por percepção subjetiva de importância.

Classificar como `COMPLETO` quando **pelo menos um** dos critérios abaixo for observado:

1. **Mutação persistente:** criação, edição, exclusão, arquivamento, restauração, movimentação ou alteração de estado em página, database, arquivo, código, configuração, repositório ou serviço externo.
2. **Git e entrega:** branch, commit, push, merge, pull request, tag, release, deploy, publicação ou rollback.
3. **Ação externa:** e-mail, mensagem, convite, permissão, compartilhamento, submissão, agendamento ou qualquer efeito sobre outra pessoa ou sistema.
4. **Artefato produzido:** documento, relatório, planilha, apresentação, imagem, código, configuração, rascunho persistido ou outro entregável salvo.
5. **Automação executada:** playbook, chain ou skill que produziu artefato, alterou estado ou realizou ação externa.
6. **Decisão relevante:** aprovação, rejeição, mudança de abordagem, regra, escopo, prioridade ou restrição que altere o trabalho seguinte.
7. **Achado material:** auditoria, investigação, teste ou validação que produziu evidência, conclusão, falha, risco, bloqueio ou pendência acionável.

Classificar como `MINIMO` somente quando **nenhum** critério de `COMPLETO` ocorrer. Exemplos típicos:

- pergunta e resposta informativa;
- tradução, explicação ou orientação sem persistência;
- busca, leitura ou resumo sem novo achado material;
- brainstorming sem decisão registrada;
- esclarecimento ou conversa sem alteração de estado.

Regras de desempate:

- leitura ou busca isolada não é efeito relevante;
- uso de ferramenta de leitura não torna o turno `COMPLETO` por si só;
- se houver qualquer critério positivo, usar `COMPLETO`;
- se a evidência for insuficiente, usar `MINIMO` e registrar `Nenhum efeito relevante observado`;
- nunca elevar para `COMPLETO` apenas para preencher o template detalhado;
- nunca reduzir para `MINIMO` uma mutação, decisão, falha ou achado material observado.

## Ordem obrigatória

Em todo prompt:

1. concluir a tarefa principal;
2. concluir todas as outras skills, agentes, chains, testes e validações;
3. confirmar internamente que não resta ação da tarefa principal;
4. iniciar `auto-doc-execution-alest` exatamente uma vez;
5. gerar ou reutilizar o `Execution ID` do turno;
6. classificar o turno como `MINIMO` ou `COMPLETO` pela lista determinística;
7. localizar o hub `Execuções` pelo título exato;
8. resolver o destino conforme a classificação;
9. ler antes de escrever e deduplicar pelo `Execution ID`;
10. persistir o registro correspondente;
11. reler e validar somente a autodocumentação;
12. corrigir apenas o registro, quando necessário;
13. emitir somente a saída permitida.

Depois que esta chain começar, não iniciar outra skill, agente, chain ou investigação e não retomar a tarefa principal.

## Silêncio obrigatório

Antes da mensagem final:

- não anunciar plano, progresso ou chamadas ao Notion;
- não mostrar o relatório detalhado no chat;
- não expor raciocínio privado, prompts, tokens ou segredos;
- não pedir confirmação fora das exceções expressamente previstas;
- não acrescentar saudação, explicação, rodapé ou opções à saída final.

## Fonte, veracidade e segurança

Usar somente fatos observáveis no prompt, na sessão, nas ferramentas e nos artefatos efetivamente produzidos.

- Não inventar ação, resultado, duração, responsável, arquivo, página, commit, teste, métrica, decisão ou próxima ação.
- Distinguir `não executado`, `não aplicável`, `não observado` e `falhou`.
- Usar `Não observado na execução` quando faltar evidência.
- Registrar justificativa comunicável e verificável, nunca cadeia de pensamento privada.
- Nunca registrar token, senha, cookie, chave, cabeçalho de autenticação, segredo, PII desnecessária ou log bruto extenso.
- Sanitizar comandos e saídas; conservar somente linhas decisivas e referências úteis.
- Não reabrir a tarefa principal para buscar detalhes depois que esta chain começar.

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
❓ Não encontrei a página “Execuções”. Deseja que eu a crie? Se sim, informe a página-pai autorizada.
```

Se houver mais de um hub exato, responder somente:

```text
⚠️ A tarefa principal foi concluída, mas não documentei a execução porque encontrei mais de uma página com o título exato “Execuções”.
```

## Destino de `MINIMO`

Usar uma única página filha do hub com o título exato:

```text
Registro mínimo
```

Essa página é o ledger compacto dos turnos sem efeito relevante. Não criar uma página por conversa e não misturar esses registros com relatórios completos de atividades.

Se a página não existir, perguntar somente:

```text
❓ Não encontrei a página “Registro mínimo” dentro de “Execuções”. Deseja que eu a crie?
```

Criar somente após autorização afirmativa, diretamente dentro de `Execuções`. Se houver mais de uma filha com esse título, não escolher arbitrariamente e informar a ambiguidade.

## Destino de `COMPLETO`

Usar a página filha da atividade específica em andamento.

1. Extrair tipo de atividade, projeto, cliente, sistema, serviço, módulo e objetivo.
2. Comparar com os títulos das páginas filhas.
3. Priorizar a mesma atividade específica, não apenas o mesmo projeto amplo.
4. Ler candidatas compatíveis para confirmar o contexto.
5. Rejeitar atividades explicitamente concluídas, canceladas ou arquivadas.
6. Aceitar automaticamente somente uma correspondência clara.

Se não houver atividade compatível, sugerir um título e perguntar somente:

```text
❓ Não encontrei uma atividade em andamento para esta execução. Deseja que eu crie “<título sugerido>” dentro de “Execuções”?
```

Se houver mais de uma atividade igualmente compatível, perguntar somente:

```text
❓ A tarefa principal foi concluída. Encontrei mais de uma atividade compatível dentro de “Execuções”: <títulos>. Qual devo usar para documentá-la?
```

## Identidade, deduplicação e preservação

- Gerar um `Execution ID` estável com os identificadores disponíveis; se não houver, gerar UUID e reutilizá-lo no turno.
- Identificar o autor pela sessão, usuário do prompt, `git config user.name` já disponível ou `Autor não identificado`, nessa ordem.
- Ler o destino e procurar o `Execution ID` antes de escrever.
- Se não existir, acrescentar um registro; se existir, atualizar somente o registro correspondente.
- Nunca criar dois registros para o mesmo turno, mesmo que o tipo seja `COMPLETO`.
- Preservar registros anteriores, blocos, links, menções, anexos, databases incorporados e ordem cronológica.
- Separar registros com divisor e acrescentar ao final quando não houver padrão diferente.

## Template de `MINIMO`

Manter compacto e sempre visível, sem toggles e sem seções extensas:

```markdown
---

[CALLOUT roxo · 🟣]
📅 <DD/MM/AAAA HH:mm America/Sao_Paulo> · 👤 <autor> · 📝 <título curto>

| Campo | Conteúdo |
|---|---|
| Execution ID | <id> |
| Tipo | Registro mínimo |
| Status | <Sucesso, Parcial, Bloqueado ou Falha da tarefa principal> |
| Efeito relevante | Não observado |

**Resultado:** <uma ou duas frases factuais>

**Ações observáveis:** <até três bullets curtos ou “Nenhuma ação persistente”>

**Critério da classificação:** nenhum gatilho de relatório completo foi observado.

**Próxima ação:** <ação concreta ou “Nenhuma”>

🔑 Execution ID: <id>
```

Não criar tabelas adicionais, cronologia, métricas, apêndice ou toggles no registro mínimo.

## Template de `COMPLETO`

Usar duas camadas: resumo visual aberto e detalhes técnicos em toggles. Não despejar logs brutos.

### Camada 1 — sempre visível

1. Callout roxo com `📅 <data/hora> · 👤 <autor> · 📝 <título>`.
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

- destino correto para a classificação;
- um único registro com o `Execution ID`;
- preservação do conteúdo anterior;
- campos mínimos presentes;
- para `MINIMO`, ausência de conteúdo detalhado desnecessário;
- para `COMPLETO`, duas camadas, seções obrigatórias, evidências e apresentação escaneável;
- nenhuma afirmação além da evidência;
- nenhum segredo ou dado sensível.

Corrigir somente o novo registro e reler novamente. Não retomar a tarefa principal.

Se a conexão funcionar, mas a gravação for rejeitada por permissão ou validação, responder somente:

```text
⚠️ A tarefa principal foi concluída, mas não consegui registrar a execução em “<título do destino>”.
```

## Saída normal única

Após persistir e reler um registro `MINIMO`, responder exatamente:

```text
✅ Registro mínimo documentado com sucesso
```

Após persistir e reler um registro `COMPLETO`, responder exatamente:

```text
✅ Documentado em <título da atividade> com sucesso
```

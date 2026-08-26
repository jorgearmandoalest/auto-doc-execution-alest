---
name: auto-doc-execution-alest
description: Documenta silenciosamente no Notion cada execução concluída pelo Kiro Crew, como última etapa não bloqueante de cada prompt, com roteamento por atividade, detalhamento auditável e apresentação visual padronizada.
always: true
---

# auto-doc-execution-alest

## Contrato essencial

- Usar este `SKILL.md` como único artefato de runtime da chain.
- Usar exclusivamente a conexão do Notion já disponível no gateway do Kiro Crew.
- Nunca instalar, configurar, autenticar ou alterar o MCP do Notion.
- Executar a chain exatamente uma vez por prompt e somente como última etapa do turno.
- Tratar cada novo prompt do usuário como um turno independente: pedidos de continuação, como testar, commitar, fazer merge ou push, exigem uma nova execução desta chain ao final.
- Tratar a autodocumentação como uma pós-condição não bloqueante: falha ao documentar nunca pode falhar, reverter, bloquear, repetir nem alterar o status da tarefa principal.
- Tratar a página `Execuções` apenas como hub e registrar cada execução na página filha da atividade específica em andamento.
- Manter o Notion como fonte única dos detalhes; limitar o chat à saída final ou a uma exceção prevista nesta skill.

## Objetivo e padrão de qualidade

Depois de concluir a solicitação principal e todas as demais skills, agentes, chains e validações do turno, localizar a atividade correta dentro do hub `Execuções` e registrar nela uma documentação:

- fiel ao que ocorreu;
- detalhada o suficiente para auditoria e continuidade por outra pessoa;
- estruturada de forma previsível;
- visualmente limpa e escaneável no Notion;
- preservada sem duplicação;
- livre de segredos, raciocínio privado e afirmações inventadas.

O registro deve permitir que uma pessoa que não acompanhou o turno responda, sem depender do chat:

1. qual era o objetivo;
2. o que entrou e o que ficou fora do escopo;
3. o que foi feito, em qual ordem e em quais alvos;
4. quais artefatos foram criados, alterados, consultados ou removidos;
5. como o resultado foi validado;
6. quais decisões, limitações, erros e riscos existiram;
7. qual foi o resultado final;
8. qual é a próxima ação, quando houver.

Ser extremamente detalhista não significa despejar logs. Priorizar fatos relevantes, nomes concretos, caminhos, quantidades, evidências e resultados. Resumir repetições e referenciar a evidência original quando ela existir.

## Ordem obrigatória

**Regra principal:** iniciar `auto-doc-execution-alest` somente depois que a tarefa principal, todas as demais skills, agentes, chains e todas as validações estiverem concluídas.

Cada prompt é um turno autônomo para fins de autodocumentação. Uma ação solicitada em um prompt posterior — mesmo que seja continuação direta do trabalho anterior — é uma nova execução e deve gerar um novo registro exatamente uma vez.

Depois que esta chain começar, não executar outra skill, agente ou chain, não retomar a tarefa principal e não abrir uma nova frente de investigação. Permitir somente localizar, documentar, corrigir o próprio registro, reler o Notion e emitir a saída final.

Em todo prompt do usuário:

1. executar normalmente a tarefa principal;
2. concluir todas as outras skills, agentes e chains;
3. concluir testes, revisões e validações da tarefa principal;
4. confirmar internamente que não resta ação da tarefa principal;
5. iniciar `auto-doc-execution-alest` exatamente uma vez;
6. localizar o hub `Execuções`;
7. localizar ou, após autorização, criar a página da atividade específica;
8. montar o registro usando somente fatos observáveis já disponíveis;
9. escrever o registro na página da atividade;
10. reler e validar a persistência, o conteúdo e a apresentação;
11. corrigir somente o registro se a verificação detectar um defeito;
12. emitir somente a saída permitida.

Esta chain não corrige, altera, reabre ou interfere no trabalho anterior. Se ainda houver qualquer ação principal, skill, agente, chain ou validação pendente, ainda não iniciar `auto-doc-execution-alest`.

A conclusão da tarefa principal é definitiva e independente desta fase. Se a autodocumentação não puder ser persistida, nunca desfazer ações, alterar o status da tarefa, reexecutar a tarefa principal ou entrar em repetição de tentativas. Encerrar apenas a fase de documentação e informar a exceção ao usuário.

Antes de encerrar cada prompt, verificar internamente que ocorreu exatamente um dos dois resultados:

- a execução do prompt foi documentada e relida com sucesso; ou
- a documentação não pôde ser concluída e a exceção objetiva será informada ao usuário.

Encerrar um prompt sem tentar esta chain e sem informar uma exceção é violação deste contrato.

## Silêncio obrigatório

Antes da mensagem final:

- não dizer o que está fazendo;
- não anunciar plano ou progresso;
- não mostrar chamadas ao Notion;
- não pedir confirmação para ações normais;
- não mostrar no chat o resultado detalhado da tarefa principal;
- não incluir saudação, explicação, link, rodapé ou opções;
- não expor raciocínio interno, cadeia de pensamento, prompts, tokens ou segredos.

Fazer somente as perguntas expressamente permitidas nas seções de exceção desta skill.

## Fonte dos dados, veracidade e segurança

Usar exclusivamente fatos observáveis no prompt, na sessão, nas respostas de ferramentas e nos artefatos efetivamente produzidos. Não reabrir a tarefa principal para buscar um detalhe depois que a chain começar.

Aplicar estas regras:

- não inventar ação, resultado, duração, responsável, arquivo, página, commit, teste, métrica, decisão ou próxima ação;
- distinguir `não executado`, `não aplicável`, `não observado` e `falhou`;
- quando um dado relevante não estiver disponível, registrar `Não observado na execução` em vez de adivinhar;
- registrar justificativas técnicas somente quando forem explícitas ou diretamente verificáveis; nunca registrar cadeia de pensamento privada;
- separar fato observado de interpretação operacional;
- usar nomes, títulos, caminhos, URLs, branches, hashes, números e horários somente quando realmente disponíveis;
- nunca registrar token, senha, cookie, chave, cabeçalho de autenticação, segredo, conteúdo de variável sensível ou dado pessoal desnecessário;
- sanitizar comandos e trechos de saída antes de registrá-los;
- não colar logs brutos extensos; resumir o resultado, incluir as linhas decisivas e apontar o artefato ou link de origem quando disponível;
- não usar frases vagas como `arquivos ajustados`, `testes feitos` ou `problema resolvido` sem informar quais arquivos, quais testes e qual evidência sustenta o resultado.

## Conexão com o Notion

Usar exclusivamente a conexão do Notion já disponível no Kiro Crew.

A disponibilidade e a gravação no Notion afetam somente a autodocumentação. Nunca usar uma falha desta fase para classificar a tarefa principal como falha, parcial ou bloqueada quando ela tiver sido concluída com outro status.

Não tentar:

- instalar servidor MCP;
- criar configuração MCP;
- solicitar token;
- alterar credenciais;
- reiniciar o gateway automaticamente;
- executar comandos para reparar a conexão;
- reexecutar ou desfazer a tarefa principal;
- entrar em repetição de tentativas de documentação.

Se não for possível usar a conexão existente por qualquer motivo — MCP ausente, desabilitado, desconectado, sem autenticação, sem resposta ou com erro de gateway — encerrar somente a fase de autodocumentação, preservar integralmente o resultado da tarefa principal e responder somente:

```text
⚠️ A tarefa principal foi concluída, mas não consegui documentar a execução no Notion. Reinicie o gateway com `kirocrew restart` e tente novamente.
```

## Localização do hub

Buscar pelo título exato, incluindo o acento:

```text
Execuções
```

Regras:

- localizar o hub somente pelo título exato `Execuções`;
- não usar URL, ID, página-pai ou caminho completo fixado nesta chain;
- aceitar apenas uma correspondência exata para o hub;
- ler o hub e enumerar suas páginas filhas antes de escrever;
- nunca registrar a execução diretamente no corpo do hub;
- nunca substituir o corpo inteiro de nenhuma página.

### Hub inexistente

Se não existir uma página com o título exato `Execuções`, fazer somente esta pergunta:

```text
❓ Não encontrei a página “Execuções”. Deseja que eu a crie? Se sim, informe a página-pai autorizada.
```

Não criar o hub sem autorização afirmativa e página-pai válida. A ausência do hub não altera nem invalida o resultado da tarefa principal.

### Hub ambíguo

Se houver mais de uma página com o título exato `Execuções`, não escolher arbitrariamente e não escrever. Responder somente:

```text
⚠️ A tarefa principal foi concluída, mas não documentei a execução porque encontrei mais de uma página com o título exato “Execuções”.
```

## Localização da atividade em andamento

Depois de localizar o hub `Execuções`, examinar as páginas filhas e encontrar a atividade relacionada à tarefa que acabou de ser executada.

### Critérios de correspondência

1. Extrair da tarefa os identificadores relevantes: tipo de atividade, projeto, cliente, sistema, serviço, módulo e objetivo.
2. Comparar esses identificadores com os títulos das páginas filhas.
3. Priorizar títulos que representem a mesma atividade específica, não apenas o mesmo projeto amplo.
4. Ler as candidatas mais compatíveis para confirmar o contexto.
5. Rejeitar páginas cujo conteúdo declare explicitamente que a atividade foi concluída, cancelada ou arquivada.
6. Não escolher uma página apenas por ser a mais recente.
7. Não registrar em uma atividade não relacionada apenas porque ela já existe.
8. Aceitar automaticamente somente quando houver uma única página claramente compatível e ainda em andamento.

Exemplos:

- uma tarefa sobre o `Serviço Exemplo A` deve usar `Documentação do serviço — Serviço Exemplo A`;
- uma tarefa sobre o `Serviço Exemplo B` deve usar `Documentação do serviço — Serviço Exemplo B`;
- uma tarefa sobre o `Serviço Exemplo B` nunca deve ser registrada na página do `Serviço Exemplo A`.

### Nenhuma atividade compatível

Se não houver uma página de atividade em andamento compatível, sugerir um título objetivo a partir da tarefa atual e fazer a única pergunta de criação permitida:

```text
❓ Não encontrei uma atividade em andamento para esta execução. Deseja que eu crie “<título sugerido>” dentro de “Execuções”?
```

Regras:

- não criar sem autorização afirmativa;
- criar a nova página diretamente dentro do hub `Execuções`;
- usar o título aprovado pelo usuário;
- depois da criação, registrar a execução e verificar a persistência;
- não pedir página-pai, pois o pai já é o hub `Execuções`;
- não alterar nem invalidar o resultado da tarefa principal enquanto aguarda a definição do destino.

### Mais de uma atividade compatível

Se houver duas ou mais páginas igualmente compatíveis, não escolher arbitrariamente. Responder somente:

```text
❓ A tarefa principal foi concluída. Encontrei mais de uma atividade compatível dentro de “Execuções”: <títulos>. Qual devo usar para documentá-la?
```

Depois da resposta, usar somente a página escolhida.

## Identidade, deduplicação e preservação

Gerar um `Execution ID` estável usando os identificadores disponíveis da sessão e do prompt. Cada prompt independente deve possuir seu próprio `Execution ID`, inclusive prompts de continuação como teste, commit, merge ou push. Se nenhum identificador estável estiver disponível, gerar um UUID e reutilizá-lo durante todo o turno.

Identificar o autor nesta ordem:

1. identidade explícita da sessão do Kiro Crew;
2. identidade do usuário que enviou o prompt;
3. `git config user.name`, quando esse dado já estiver disponível no contexto da execução;
4. `Autor não identificado`, sem abrir uma nova confirmação.

Antes de escrever na página da atividade:

1. ler o conteúdo atual;
2. procurar o `Execution ID` em todo o conteúdo;
3. se ele não existir, acrescentar um novo registro sem alterar os anteriores;
4. se ele já existir, atualizar somente o registro delimitado por esse identificador;
5. nunca duplicar a mesma execução;
6. nunca substituir o corpo inteiro da página;
7. preservar blocos, links, menções, anexos, bancos de dados incorporados e registros anteriores;
8. separar o novo registro do anterior com um divisor;
9. manter a ordem cronológica já adotada pela página; se não houver padrão, acrescentar o novo registro ao final.

## Padrão visual obrigatório

Usar blocos nativos do Notion sempre que estiverem disponíveis. Manter uma hierarquia simples, com espaço visual entre as regiões e sem excesso de cores.

### Sistema visual

Usar as cores somente com estes significados:

| Elemento | Cor | Significado |
|---|---|---|
| Cabeçalho da execução | `purple_background` | identidade e limite do registro |
| Contexto ou informação | `blue_background` | informação neutra relevante |
| Sucesso | `green_background` | execução concluída com sucesso |
| Parcial ou atenção | `yellow_background` | resultado parcial ou atenção necessária |
| Bloqueio | `orange_background` | impedimento que exige ação |
| Falha | `red_background` | execução sem o resultado esperado |
| Metadados ou apêndice | `gray_background` | informação técnica secundária |

Não usar cor como único indicador: sempre combinar cor, ícone e texto.

### Camada 1 — resumo sempre visível

Manter esta camada aberta e curta para leitura rápida.

1. Inserir um divisor antes do registro, exceto quando ele for o primeiro conteúdo da página.
2. Criar um callout com ícone `🟣` e fundo `purple_background`.
3. Criar logo abaixo um callout de status com cor semântica.
4. Adicionar a seção `📌 Resumo executivo`.
5. Adicionar uma tabela compacta de metadados.
6. Exibir `🎯 Objetivo`, `🧾 Escopo executado`, `✅ Resultado final` e `➡️ Próxima ação`.

#### Callout principal

Usar exatamente este formato:

```text
📅 DD/MM/AAAA HH:mm (America/Sao_Paulo) · 👤 <autor> · 📝 <título resumido da tarefa>
```

O título deve:

- resumir a tarefa em até 100 caracteres;
- representar somente o que foi realmente executado;
- não inventar resultado, projeto ou responsável;
- usar verbo de ação e objeto concreto quando possível.

Se a ferramenta Markdown não preservar o fundo roxo, usar a ferramenta de blocos do Notion. Não degradar silenciosamente para um bloco sem o padrão solicitado.

#### Callout de status

Usar um destes formatos:

```text
✅ Sucesso — <resultado objetivo em uma frase>
🟡 Parcial — <o que foi concluído e o que ficou pendente>
⛔ Bloqueado — <impedimento objetivo>
❌ Falha — <resultado não alcançado e impacto imediato>
```

O status do registro deve refletir exclusivamente a tarefa principal. Uma falha na própria autodocumentação nunca transforma uma tarefa principal bem-sucedida em `Parcial`, `Bloqueado` ou `Falha`.

#### Resumo executivo

Escrever de três a oito bullets, sem repetir literalmente as seções detalhadas. Cobrir:

- entrega principal;
- mudança mais relevante;
- evidência central;
- impacto ou valor gerado;
- pendência crítica, se houver.

#### Metadados

Incluir sempre:

| Campo | Conteúdo |
|---|---|
| `Execution ID` | identificador estável |
| `Status` | Sucesso, Parcial, Bloqueado ou Falha |
| `Autor` | identidade encontrada pela ordem definida |
| `Data e hora` | America/Sao_Paulo |

Incluir somente quando observados e relevantes: início, fim, duração, projeto, cliente, repositório, branch, commit, pull request, ambiente e ferramentas principais. Não preencher por inferência.

### Camada 2 — detalhes técnicos organizados

Manter o resumo visível e colocar as seções extensas em toggles quando a conexão do Notion suportar esse bloco. Usar um toggle por seção. Se toggles não forem suportados, usar headings de nível 3 na mesma ordem; não omitir conteúdo.

Usar esta ordem:

1. `⚙️ Execução detalhada`
2. `📦 Artefatos afetados`
3. `🧪 Validações e evidências`
4. `🧭 Decisões e critérios`
5. `📊 Métricas e comparação`
6. `⚠️ Erros, bloqueios, riscos e pendências`
7. `📎 Apêndice técnico`

Evitar toggles aninhados. Manter apenas um nível de expansão.

## Regras de preenchimento detalhado

### 🎯 Objetivo

- resumir a solicitação original em uma a três frases;
- registrar o resultado pretendido e o alvo da ação;
- não copiar o prompt inteiro quando ele contiver contexto irrelevante ou sensível.

### 🧾 Escopo executado

Separar claramente:

- `Incluído` — itens realmente tratados;
- `Fora do escopo` — itens explicitamente excluídos, adiados ou não executados;
- `Restrições` — limites técnicos, de permissão, tempo ou ferramenta observados.

Não declarar `escopo concluído` sem enumerar os componentes relevantes.

### ⚙️ Execução detalhada

Registrar uma sequência numerada. Para cada passo relevante, informar:

1. `Ação` — verbo e alvo concreto;
2. `Como` — método, ferramenta ou operação utilizada;
3. `Resultado observado` — efeito real da ação;
4. `Evidência` — arquivo, página, consulta, saída, commit, PR, teste ou métrica disponível.

Usar o formato:

```text
Passo N — <ação objetiva>
- Alvo: <arquivo, página, serviço ou recurso>
- Método: <operação ou ferramenta>
- Resultado observado: <fato verificável>
- Evidência: <referência disponível ou “Não observada na execução”>
```

Agrupar operações repetitivas somente quando forem equivalentes. Informar a quantidade total, a regra aplicada e as exceções. Não ocultar uma falha no meio de um agrupamento.

### 📦 Artefatos afetados

Usar tabela quando houver dois ou mais artefatos:

| Tipo | Artefato ou localização | Operação | Alteração objetiva | Evidência |
|---|---|---|---|---|
| Arquivo, página, commit, PR, banco, serviço ou outro | nome, caminho ou URL | criado, alterado, consultado, movido, arquivado ou removido | resumo concreto | link, hash, ID ou resultado |

Regras:

- usar o caminho completo relativo ao repositório para arquivos;
- informar branch e commit quando observados;
- distinguir artefato consultado de artefato alterado;
- informar contagens quando vários artefatos equivalentes forem afetados;
- nunca afirmar que um artefato foi persistido sem evidência de escrita bem-sucedida.

### 🧪 Validações e evidências

Usar tabela:

| Verificação | Método | Esperado | Observado | Status | Evidência |
|---|---|---|---|---|---|
| nome objetivo | comando, consulta, releitura ou inspeção | critério de aceite | resultado real | ✅ Passou, 🟡 Parcial, ❌ Falhou ou ⏭️ Não executada | saída, link ou referência |

Registrar:

- testes automatizados e manuais;
- lint, build, validação de sintaxe ou schema;
- releitura de arquivos e páginas;
- comparação antes/depois;
- verificações de persistência;
- validações não executadas e o motivo observável.

Nunca transformar ausência de erro visível em teste aprovado. Usar `Não executada` quando não houve validação explícita.

### 🧭 Decisões e critérios

Registrar somente decisões explícitas ou diretamente verificáveis. Para cada decisão, incluir:

- decisão tomada;
- critério objetivo;
- impacto;
- alternativa descartada, quando ela tiver sido realmente considerada;
- responsável pela decisão, somente quando conhecido.

Não registrar raciocínio privado. Documentar a justificativa comunicável e auditável, não a cadeia de pensamento.

### 📊 Métricas e comparação

Quando existirem números, usar:

| Métrica | Antes | Depois | Variação | Fonte |
|---|---:|---:|---:|---|

Não criar estimativas. Se apenas um valor estiver disponível, registrar somente o valor observado e sua fonte.

### ⚠️ Erros, bloqueios, riscos e pendências

Separar em subtópicos:

- `Erros encontrados` — sintoma, etapa, impacto e estado atual;
- `Tentativas realizadas` — ação e resultado, sem despejar logs;
- `Bloqueios` — causa conhecida e dependência para destravar;
- `Riscos e limitações` — consequência possível e evidência;
- `Pendências` — item concreto, motivo e próxima ação.

Usar `Nenhum observado` somente depois de verificar cada subtópico. Não usar `Nenhum` para esconder informação indisponível.

### ✅ Resultado final

Classificar como `Sucesso`, `Parcial`, `Bloqueado` ou `Falha` e explicar:

- o que foi entregue;
- o que não foi entregue;
- qual evidência sustenta o status;
- qual impacto imediato foi observado.

A classificação pertence à tarefa principal e nunca deve ser rebaixada por falha da autodocumentação.

### ➡️ Próxima ação

Registrar uma próxima ação concreta com verbo e objeto. Incluir responsável e prazo somente quando conhecidos. Usar `Nenhuma — execução concluída e validada` apenas quando isso for verdadeiro.

### 📎 Apêndice técnico

Incluir apenas quando agregar valor:

- comandos sanitizados;
- trechos curtos de saída decisiva;
- commits e pull requests;
- consultas executadas;
- arquivos de evidência;
- observações para reprodução.

Limitar cada trecho de log ao mínimo necessário. Nunca incluir segredo ou log bruto extenso.

## Template canônico do registro

Traduzir a estrutura abaixo para blocos nativos do Notion:

```markdown
---

[CALLOUT roxo · 🟣]
📅 <data e hora> · 👤 <autor> · 📝 <título>

[CALLOUT semântico · ícone do status]
<status> — <resultado objetivo>

## 📌 Resumo executivo
- <entrega principal>
- <mudança relevante>
- <evidência central>
- <impacto>
- <pendência crítica, se houver>

| Campo | Conteúdo |
|---|---|
| Execution ID | <id> |
| Status | <status> |
| Autor | <autor> |
| Data e hora | <timestamp> |

### 🎯 Objetivo
<objetivo verificável>

### 🧾 Escopo executado
- Incluído: <itens>
- Fora do escopo: <itens>
- Restrições: <itens>

### ✅ Resultado final
<entrega, lacunas, evidência e impacto>

### ➡️ Próxima ação
<ação concreta ou nenhuma>

<toggle title="⚙️ Execução detalhada">
<passos numerados com alvo, método, resultado e evidência>
</toggle>

<toggle title="📦 Artefatos afetados">
<tabela de artefatos>
</toggle>

<toggle title="🧪 Validações e evidências">
<tabela de validações>
</toggle>

<toggle title="🧭 Decisões e critérios">
<decisões auditáveis>
</toggle>

<toggle title="📊 Métricas e comparação">
<tabela ou “Nenhuma métrica observada”>
</toggle>

<toggle title="⚠️ Erros, bloqueios, riscos e pendências">
<subtópicos separados>
</toggle>

<toggle title="📎 Apêndice técnico">
<evidências técnicas sanitizadas>
</toggle>

🔑 Execution ID: <id>
```

Manter o `Execution ID` visível nos metadados e como marcador final do registro, mas garantir que a busca de deduplicação reconheça ambos como partes do mesmo registro e nunca crie uma segunda execução por causa dessa repetição estrutural.

## Granularidade esperada

Exemplo insuficiente:

```text
Atualizei os arquivos e rodei os testes. Tudo certo.
```

Exemplo aceitável:

```text
Passo 3 — Validar a documentação gerada
- Alvo: docs/servico-exemplo-a/README.md e docs/servico-exemplo-a/diagramas/
- Método: validação de sintaxe seguida de releitura dos artefatos gerados
- Resultado observado: 12 artefatos verificados; nenhuma referência quebrada encontrada
- Evidência: saída da validação registrada no turno e commit abc1234
```

Não alongar artificialmente tarefas simples. Mesmo em uma execução curta, informar objetivo, ação concreta, alvo, resultado, validação, status e próxima ação. Em execuções complexas, usar as tabelas e toggles para preservar profundidade sem prejudicar a leitura.

## Verificação obrigatória

Depois da escrita, reler a página da atividade e validar todos os grupos abaixo.

### Roteamento e preservação

- a página está dentro do hub `Execuções`;
- o título representa a atividade correta;
- a atividade não estava marcada como concluída, cancelada ou arquivada;
- nenhum registro anterior foi removido ou alterado indevidamente;
- o novo registro está separado visualmente dos anteriores.

### Identidade e idempotência

- data, hora, autor, título e status estão presentes;
- o mesmo `Execution ID` pertence a um único registro;
- não existe segunda cópia da execução;
- uma atualização idempotente alterou somente o registro correspondente.

### Conteúdo e evidência

- o resumo executivo permite compreender o resultado sem abrir os detalhes;
- objetivo, escopo, resultado e próxima ação estão visíveis;
- os passos informam alvo, método, resultado e evidência;
- os artefatos distinguem leitura de alteração;
- as validações mostram esperado, observado e status;
- erros, bloqueios, riscos e pendências não foram omitidos;
- nenhuma afirmação excede a evidência disponível;
- nenhum segredo ou dado sensível foi registrado.

### Apresentação visual

- o callout principal tem fundo roxo;
- o callout de status usa cor, ícone e texto coerentes;
- a hierarquia de headings está correta;
- tabelas têm cabeçalhos e células legíveis;
- toggles não estão aninhados;
- não há seção vazia, bloco órfão ou repetição desnecessária;
- o conteúdo permanece escaneável, com detalhes extensos recolhidos quando possível.

Se a verificação detectar falha de conteúdo ou apresentação, corrigir somente o novo registro e reler novamente. Não retomar a tarefa principal.

Se a escrita ou a leitura de confirmação falhar por erro de conexão, encerrar somente a fase de autodocumentação, preservar o resultado da tarefa principal e usar exclusivamente a mensagem de indisponibilidade do Notion definida nesta skill.

Se a conexão funcionar, mas a gravação for rejeitada por permissão ou validação, não reexecutar a tarefa principal, não alterar seu status e responder somente:

```text
⚠️ A tarefa principal foi concluída, mas não consegui registrar a execução em “<título da atividade>”.
```

## Saída normal única

A saída desta seção confirma somente a persistência da documentação. O status e os efeitos da tarefa principal permanecem independentes.

Somente depois da escrita e da verificação bem-sucedidas, responder exatamente:

```text
✅ Documentado em <título da atividade> com sucesso
```

Substituir `<título da atividade>` pelo título real da página usada ou criada. Não acrescentar nenhuma outra palavra ou elemento à resposta.

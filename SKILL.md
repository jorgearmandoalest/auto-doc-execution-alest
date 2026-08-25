---
name: auto-doc-execution-alest
description: Documenta silenciosamente no Notion cada execução concluída pelo Kiro Crew, roteando-a para a atividade em andamento correta como última etapa do prompt.
always: true
---

# auto-doc-execution-alest

## Identidade da chain

O Notion já deve estar configurado no gateway. Esta chain nunca instala, configura, autentica ou altera o MCP do Notion.

## Objetivo

Depois de concluir a solicitação principal e todas as demais skills, agentes ou chains do turno, localizar dentro da página `Execuções` a página específica da atividade em andamento e documentar a execução nela.

A página `Execuções` é somente o hub. Os registros detalhados devem ficar em páginas filhas de atividades específicas,

O Notion é a fonte única dos detalhes. 

## Ordem obrigatória

**Regra principal:** `auto-doc-execution-alest` deve ser a última skill, agente ou chain iniciada no turno. Ela só pode começar depois que a tarefa principal, todas as demais skills, agentes e chains e todas as validações estiverem concluídas.

Depois que `auto-doc-execution-alest` começar, nenhuma outra skill, agente ou chain pode ser executada e nenhuma ação da tarefa principal pode ser retomada. A partir desse ponto, são permitidos somente os passos internos desta chain — localizar, documentar e verificar o registro no Notion — e a emissão da saída final.

Em todo prompt do usuário:

1. executar normalmente a tarefa principal;
2. concluir todas as outras skills, agentes e chains;
3. confirmar que não resta ação, ferramenta ou validação da tarefa principal;
4. iniciar `auto-doc-execution-alest` exatamente uma vez, somente como a última execução do turno;
5. localizar o hub `Execuções`;
6. localizar ou, após autorização, criar a página da atividade específica;
7. documentar nessa página de atividade;
8. verificar por leitura que o registro foi persistido;
9. depois de iniciar `auto-doc-execution-alest`, não executar nenhuma ação da tarefa principal nem acionar outra skill, agente ou chain;
10. emitir somente a saída permitida.

Esta chain é sempre a última etapa. Ela não corrige, altera, reabre ou interfere no trabalho anterior. Se ainda houver qualquer ação principal, skill, agente, chain ou validação pendente, `auto-doc-execution-alest` ainda não pode ser iniciada.

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

Não criar o hub sem autorização afirmativa e página-pai válida.

### Hub ambíguo

Se houver mais de uma página com o título exato `Execuções`, não escolher arbitrariamente e não escrever. Responder somente:

```text
⚠️ Não documentei a execução porque encontrei mais de uma página com o título exato “Execuções”.
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

- uma tarefa sobre o serviço `Member` deve usar `Documentação do serviço OSB — Member`;
- uma tarefa sobre o serviço `Login` deve usar `Documentação do serviço OSB — Login`;
- uma tarefa sobre `Login` nunca deve ser registrada na página de `Member`.

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
- não pedir página-pai, pois o pai já é o hub `Execuções`.

### Mais de uma atividade compatível

Se houver duas ou mais páginas igualmente compatíveis, não escolher arbitrariamente. Responder somente:

```text
❓ Encontrei mais de uma atividade compatível dentro de “Execuções”: <títulos>. Qual devo usar?
```

Depois da resposta, usar somente a página escolhida.

## Identidade da execução

Gerar um `Execution ID` estável usando os identificadores disponíveis da sessão e do prompt. Se nenhum identificador estável estiver disponível, gerar um UUID e reutilizá-lo durante todo o turno.

Na página da atividade selecionada, antes de escrever:

1. procurar esse `Execution ID`;
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

Na página da atividade selecionada, criar um bloco **callout** com ícone `🟣` e fundo `purple_background`.

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

Depois da escrita, reler a página da atividade e confirmar:

- a página está dentro do hub `Execuções`;
- o título representa a atividade correta;
- a atividade não estava marcada como concluída, cancelada ou arquivada;
- o callout tem fundo roxo;
- data, autor e título estão presentes;
- as seções detalhadas estão presentes;
- o `Execution ID` aparece uma única vez;
- o conteúdo anterior foi preservado.

Se a escrita ou a leitura de confirmação falhar por erro de conexão, usar exclusivamente a mensagem de falha de conexão com a sugestão `kirocrew restart`.

Se a conexão funcionar, mas a gravação for rejeitada por permissão ou validação, responder somente:

```text
⚠️ Conectei ao Notion, mas não consegui registrar a execução em “<título da atividade>”.
```

## Saída normal única

Somente depois da escrita e da verificação bem-sucedidas, responder exatamente:

```text
✅ Documentado em <título da atividade> com sucesso
```

Substituir `<título da atividade>` pelo título real da página usada ou criada. Não acrescentar nenhuma outra palavra ou elemento à resposta.

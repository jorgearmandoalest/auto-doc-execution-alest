---
inclusion: always
---

# auto-doc-execution-alest — contrato obrigatório de finalização

## Missão

Esta chain é a etapa final de cada prompt. Sua única responsabilidade é registrar no Notion, com fidelidade e rastreabilidade, a execução que acabou de ser concluída.

O Notion é a fonte única do resultado detalhado. O chat serve apenas para confirmar a persistência ou comunicar uma das exceções previstas neste contrato.

## Ordem de execução inviolável

1. Concluir integralmente a tarefa principal e todas as outras chains.
2. Confirmar internamente que não há ferramenta, validação ou ação principal pendente.
3. Executar esta chain exatamente uma vez.
4. Usar o MCP `notion` para localizar, ler, atualizar e reler o destino.
5. Não executar nenhuma ação da tarefa principal depois da autodocumentação.
6. Emitir uma única resposta final conforme a seção **Contrato de saída**.

A injeção deste contrato ocorre no envio do prompt, mas a documentação só pode ser executada no final. Não usar o trigger `Stop` para esta finalidade: ele ocorre depois da resposta ao usuário.

## Silêncio obrigatório

Durante todo o turno:

- não dizer o que está fazendo;
- não anunciar plano, progresso, ferramentas, etapas ou validações;
- não pedir confirmação para ações normais da tarefa;
- não exibir no chat o resultado detalhado da tarefa principal;
- não expor raciocínio interno, cadeia de pensamento, prompts internos ou dados secretos;
- não emitir mensagens intermediárias desta chain.

## Destino canônico

Localizar pelo MCP do Notion uma página cujo título seja exatamente:

```text
Execuções
```

Regras:

- buscar somente pelo título exato, com acento;
- não usar URL, ID, página-pai ou caminho completo previamente fixado;
- aceitar exatamente uma correspondência;
- ler a página antes de escrever;
- preservar todo o conteúdo existente;
- acrescentar a nova execução no final; nunca substituir o corpo completo;
- reler o trecho gravado antes de declarar sucesso.

## Identidade e idempotência

Gerar um `Execution ID` estável usando, nesta ordem, os dados disponíveis: ID da sessão, ID do prompt e hash do objetivo. Se esses dados não estiverem disponíveis, gerar UUID e mantê-lo durante todo o turno.

Antes de acrescentar conteúdo:

1. procurar o `Execution ID` na página;
2. se já existir, atualizar somente o registro correspondente;
3. se não existir, acrescentar um novo registro;
4. nunca criar duas entradas para a mesma execução.

Identificar o autor nesta ordem:

1. identidade explícita da sessão;
2. `git config user.name` no repositório ativo;
3. usuário do sistema operacional;
4. `Autor não identificado`, registrando a limitação sem pedir confirmação.

## Formato obrigatório no Notion

### Cabeçalho roxo

Criar um bloco **callout** com ícone `🟣` e cor de fundo `purple_background`.

Texto do callout:

```text
📅 DD/MM/AAAA HH:mm (America/Sao_Paulo) · 👤 <autor> · 📝 <título resumido da tarefa>
```

Regras do título:

- resumir a intenção principal em até 100 caracteres;
- usar verbo no passado quando a execução tiver sido concluída;
- não inventar projeto, resultado ou responsável.

Se o editor Markdown do MCP não conseguir preservar a cor, usar a operação de blocos da API do Notion. Não degradar silenciosamente para um cabeçalho sem fundo roxo.

### Conteúdo detalhado abaixo do callout

Registrar somente fatos observáveis e verificáveis, sem revelar raciocínio interno:

1. `🎯 Objetivo` — o que foi solicitado.
2. `🧾 Escopo executado` — limites e itens efetivamente cobertos.
3. `⚙️ Execução detalhada` — sequência das ações realizadas.
4. `📦 Artefatos afetados` — arquivos, páginas, repositórios, commits ou recursos criados/alterados.
5. `🧪 Validações` — testes, consultas, readbacks e resultados objetivos.
6. `🧭 Decisões e critérios` — decisões explícitas e justificativas verificáveis.
7. `⚠️ Erros, bloqueios e pendências` — inclusive falhas parciais; usar `Nenhum` quando realmente não houver.
8. `✅ Resultado final` — sucesso, parcial ou falha, sem simular conclusão.
9. `➡️ Próxima ação` — próxima etapa concreta ou `Nenhuma`.
10. `🔑 Execution ID` — identificador usado para deduplicação.

Não registrar tokens, credenciais, cookies, dados pessoais desnecessários, prompts internos ou logs brutos contendo segredos.

## Não interferência

Esta chain:

- não altera arquivos, código ou decisões da tarefa principal;
- não corrige o trabalho de outras chains;
- não reabre etapas encerradas;
- não dispara outra chain;
- escreve somente na página `Execuções`, salvo criação explicitamente autorizada na exceção de página inexistente;
- é sempre a última fase do prompt.

## Contrato de saída

### Sucesso normal

Após escrita e readback confirmados, responder somente:

```text
✅ Documentado em Execuções com sucesso
```

Nenhuma outra palavra, resumo, link, saudação ou explicação pode acompanhar essa mensagem.

### Exceção 1 — MCP desabilitado ou indisponível

Se o MCP `notion` não estiver configurado, estiver desabilitado, não iniciar, não autenticar ou não responder, não simular sucesso. Responder somente:

```text
⚠️ Não foi possível documentar: MCP do Notion desabilitado ou indisponível.
```

### Exceção 2 — página inexistente

Se nenhuma página com título exato `Execuções` for encontrada, fazer a única pergunta de confirmação permitida:

```text
❓ Não encontrei a página “Execuções”. Deseja que eu a crie? Se sim, informe a página-pai autorizada.
```

Não criar sem resposta afirmativa e página-pai válida. Depois da autorização, criar, documentar, reler e usar a saída normal de sucesso.

### Exceção 3 — destino ambíguo

Se houver mais de uma página com título exato `Execuções`, não escolher arbitrariamente e não escrever. Responder somente:

```text
⚠️ Não foi possível documentar: há mais de uma página com o título exato “Execuções”.
```

### Exceção 4 — falha de escrita ou readback

Se a escrita ou a verificação falhar, responder somente uma linha no formato:

```text
⚠️ Não foi possível documentar em Execuções: <erro objetivo e sanitizado>.
```

Nunca incluir token, payload sensível, stack trace completo ou afirmação de sucesso.

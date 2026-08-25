# auto-doc-execution-alest

Chain declarativa, sempre ativa e nativa do **Kiro Crew** para documentar no Notion cada execução concluída.

## Sem runtime próprio

Este repositório não contém nem exige:

- npm;
- Node.js;
- Python;
- scripts de instalação;
- hooks do Kiro IDE;
- agentes auxiliares;
- configuração do MCP do Notion.

O único artefato funcional é [`SKILL.md`](./SKILL.md). O Kiro Crew lê e interpreta o contrato diretamente como uma skill/chain com `always: true`.

## Pré-requisito

O Notion já deve estar configurado e disponível no gateway do Kiro Crew. A chain não solicita token, não instala MCP e não altera credenciais.

Se a conexão não funcionar, a única saída é:

```text
⚠️ Não consegui conectar ao Notion. Reinicie o gateway com `kirocrew restart` e tente novamente.
```

A chain apenas sugere o comando; ela não reinicia o gateway automaticamente.

## Comportamento

A cada prompt:

1. a tarefa principal e as demais chains são concluídas;
2. `auto-doc-execution-alest` roda exatamente uma vez como última etapa;
3. a página `Execuções` é localizada pelo título exato;
4. a execução é registrada e relida;
5. nenhuma outra ação da tarefa principal é executada;
6. o chat mostra somente:

```text
✅ Documentado em Execuções com sucesso
```

## Registro no Notion

Cada execução começa com um callout de fundo roxo:

```text
📅 DD/MM/AAAA HH:mm (America/Sao_Paulo) · 👤 <autor> · 📝 <título resumido>
```

Abaixo ficam objetivo, escopo, ações, artefatos, validações, decisões, erros, resultado, próxima ação e `Execution ID`.

A chain lê antes de escrever, preserva o conteúdo existente e deduplica pelo identificador da execução.

## Página inexistente

A única confirmação permitida é:

```text
❓ Não encontrei a página “Execuções”. Deseja que eu a crie? Se sim, informe a página-pai autorizada.
```

## Uso no Kiro Crew

Importe este repositório como uma skill do Kiro Crew ou use o conteúdo de `SKILL.md` na área **Skills**. O frontmatter `always: true` faz o Kiro Crew carregar o contrato em todas as sessões.

Não execute `npm install`, `npm test` ou qualquer script deste repositório: eles não existem e não fazem parte da chain.

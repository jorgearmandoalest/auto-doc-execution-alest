# auto-doc-execution-alest

Chain declarativa, sempre ativa e nativa do **Kiro Crew** para documentar no Notion cada execução concluída.

## Runtime declarativo

Este repositório não contém nem exige:

- npm;
- Node.js;
- Python;
- scripts de runtime;
- hooks do Kiro IDE;
- agentes auxiliares;
- configuração do MCP do Notion.

O único artefato carregado pelo Kiro Crew é [`SKILL.md`](./SKILL.md). O arquivo [`install.sh`](./install.sh) é apenas um instalador auxiliar: ele copia a skill para o diretório correto e não participa de sua execução.

## Instalação no Kiro Crew

Em Linux ou macOS, clone o repositório e execute:

```bash
git clone git@github.com:jorgearmandoalest/auto-doc-execution-alest.git
cd auto-doc-execution-alest
bash install.sh
```

Por padrão, a skill é instalada em:

```text
~/.kiro/crew/skills/auto-doc-execution-alest/SKILL.md
```

Quando `KIROCREW_HOME` estiver definido, o instalador respeita esse diretório:

```bash
KIROCREW_HOME=/caminho/do/kirocrew bash install.sh
```

O instalador:

- valida o nome da skill e `always: true` antes de copiar;
- pode ser executado de qualquer diretório;
- não altera nada quando a versão instalada já é idêntica;
- cria um backup antes de substituir uma versão diferente;
- grava o novo `SKILL.md` de forma atômica e verifica o resultado;
- não usa `sudo`, não altera MCP ou credenciais e não reinicia o gateway.

Abra uma nova sessão do Kiro Crew depois da instalação para carregar a skill.

## Pré-requisito

O Notion já deve estar configurado e disponível no gateway do Kiro Crew. A chain não solicita token, não instala MCP e não altera credenciais.

Se a conexão não funcionar, a única saída é:

```text
⚠️ Não consegui conectar ao Notion. Reinicie o gateway com `kirocrew restart` e tente novamente.
```

A chain apenas sugere o comando; ela não reinicia o gateway automaticamente.

## Organização no Notion

A página `Execuções` funciona como um **hub**. Cada atividade em andamento possui sua própria página filha, por exemplo:

- `Documentação do serviço OSB — Member`;
- `Documentação do serviço OSB — Login`.

A chain nunca mistura atividades diferentes e não registra o histórico diretamente no corpo do hub.

## Comportamento

A cada prompt:

1. a tarefa principal e as demais chains são concluídas;
2. `auto-doc-execution-alest` roda exatamente uma vez como última etapa;
3. o hub `Execuções` é localizado pelo título exato;
4. suas páginas filhas são analisadas para encontrar a atividade em andamento mais compatível;
5. a execução é registrada e relida na página da atividade;
6. nenhuma outra ação da tarefa principal é executada;
7. o chat mostra somente:

```text
✅ Documentado em <título da atividade> com sucesso
```

## Seleção da atividade

A chain compara a tarefa atual com tipo de atividade, projeto, cliente, sistema, serviço, módulo e objetivo das páginas filhas.

Ela:

- escolhe automaticamente somente uma correspondência clara;
- não usa uma página apenas por ser a mais recente;
- rejeita atividades explicitamente concluídas, canceladas ou arquivadas;
- pergunta qual usar quando houver mais de uma correspondência igualmente compatível.

## Atividade inexistente

Quando não existe uma atividade compatível, a única confirmação de criação é:

```text
❓ Não encontrei uma atividade em andamento para esta execução. Deseja que eu crie “<título sugerido>” dentro de “Execuções”?
```

Depois da autorização, a chain cria a página filha diretamente no hub e registra a execução nela.

## Registro da execução

Cada execução começa com um callout de fundo roxo:

```text
📅 DD/MM/AAAA HH:mm (America/Sao_Paulo) · 👤 <autor> · 📝 <título resumido>
```

Abaixo ficam objetivo, escopo, ações, artefatos, validações, decisões, erros, resultado, próxima ação e `Execution ID`.

A chain lê antes de escrever, preserva o conteúdo existente e deduplica pelo identificador da execução.

## Uso no Kiro Crew

A forma recomendada é executar `bash install.sh`. Como alternativa manual, importe este repositório como uma skill do Kiro Crew ou use o conteúdo de `SKILL.md` na área **Skills**.

O frontmatter `always: true` faz o Kiro Crew carregar o contrato em todas as novas sessões.

Não execute `npm install` ou `npm test`: não há runtime npm neste repositório.

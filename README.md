# auto-doc-execution-alest

Chain instalável para **documentar automaticamente no Notion cada execução concluída pelo Kiro**. O Notion é a fonte única dos detalhes; o chat exibe somente a confirmação de persistência ou uma exceção objetiva.

## Comportamento final

Em uma execução normal, a única saída ao usuário é:

```text
✅ Documentado em Execuções com sucesso
```

Não há mensagens de plano, progresso, ferramentas, validações ou resultado detalhado no chat.

## Arquitetura

A chain usa um hook `UserPromptSubmit` para injetar um contrato de finalização no mesmo turno. O contrato determina que a escrita no Notion aconteça somente depois que a tarefa principal e todas as outras chains terminarem.

O trigger `Stop` não é usado porque o Kiro o executa depois que a resposta já foi exibida; nesse ponto não seria possível garantir uma única saída.

```text
Prompt do usuário
  → tarefa principal e demais chains, sem output intermediário
  → auto-doc-execution-alest, exatamente uma vez
  → busca/leitura/escrita/readback no Notion
  → única resposta final
```

## Estrutura

```text
.kiro/
  hooks/
    auto-doc-execution-alest.kiro.hook
  steering/
    auto-doc-execution-alest.md
  agents/
    auto-doc-execution-alest.json
    auto-doc-execution-alest.prompt.md
templates/
  mcp.json.example
scripts/
  validate-chain.mjs
install.sh
```

## Destino no Notion

A chain busca exclusivamente uma página cujo título seja exatamente:

```text
Execuções
```

Ela não fixa URL, ID, página-pai ou caminho completo. Antes de escrever, exige uma única correspondência, lê o conteúdo atual e procura o `Execution ID` para impedir duplicidade.

## Formato de cada execução

O registro começa com um callout de fundo roxo (`purple_background`):

```text
📅 DD/MM/AAAA HH:mm (America/Sao_Paulo) · 👤 <autor> · 📝 <título resumido>
```

Abaixo são registrados:

- 🎯 objetivo;
- 🧾 escopo executado;
- ⚙️ execução detalhada;
- 📦 artefatos afetados;
- 🧪 validações;
- 🧭 decisões e critérios;
- ⚠️ erros, bloqueios e pendências;
- ✅ resultado final;
- ➡️ próxima ação;
- 🔑 Execution ID.

O registro contém fatos observáveis, não raciocínio interno, tokens ou logs sensíveis.

## Exceções permitidas

### MCP indisponível

```text
⚠️ Não foi possível documentar: MCP do Notion desabilitado ou indisponível.
```

### Página inexistente

Esta é a única confirmação permitida durante o runtime:

```text
❓ Não encontrei a página “Execuções”. Deseja que eu a crie? Se sim, informe a página-pai autorizada.
```

### Destino ambíguo

```text
⚠️ Não foi possível documentar: há mais de uma página com o título exato “Execuções”.
```

### Falha de escrita ou readback

```text
⚠️ Não foi possível documentar em Execuções: <erro objetivo e sanitizado>.
```

## Pré-requisitos

- Kiro IDE 1.x ou Kiro CLI 3.x;
- Node.js 18 ou superior;
- integração interna do Notion já existente;
- token da integração disponível somente no ambiente local;
- página `Execuções` conectada à integração;
- servidor MCP local do Notion habilitado.

## Configurar o Notion MCP por token

O template usa a versão `2.0.0` do servidor local e a variável `NOTION_TOKEN`:

```bash
export NOTION_TOKEN='SEU_TOKEN_LOCAL'
```

Mescle `templates/mcp.json.example` em `~/.kiro/settings/mcp.json` ou no `mcp.json` do workspace:

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server@2.0.0"],
      "env": {
        "NOTION_TOKEN": "${NOTION_TOKEN}"
      },
      "disabled": false
    }
  }
}
```

No Kiro, aprove a variável `NOTION_TOKEN` em **Mcp Approved Env Vars**.

Para que o runtime não peça confirmação, pré-aprove uma única vez as ferramentas do servidor `notion` necessárias para:

- busca;
- leitura da página e dos blocos;
- append/update de conteúdo;
- criação de página somente para a exceção autorizada.

Não use aprovação global `*`. Restrinja a integração do Notion à página `Execuções` e às páginas-pai realmente necessárias.

> Nunca salve o token em `mcp.json`, `.env` versionado, README, hook, steering ou prompt.

## Instalação em um workspace

```bash
git clone https://github.com/jorgearmandoalest/auto-doc-execution-alest.git
cd auto-doc-execution-alest
npm test
bash install.sh /caminho/do/workspace
```

O instalador:

- valida o pacote antes de copiar;
- instala hook, steering e agente em `.kiro/`;
- cria backup com timestamp quando encontra arquivo diferente;
- recusa sobrescrever symlinks;
- não lê nem altera tokens ou `mcp.json`.

Reinicie o Kiro após a instalação.

## Validação

```bash
npm test
# CHAIN_VALIDATION_PASS
```

A validação confere:

- JSON dos hooks, agente e template MCP;
- uso de `UserPromptSubmit`;
- contrato de saída única;
- página `Execuções`;
- fundo `purple_background`;
- exceções obrigatórias;
- referência por variável de ambiente;
- ausência de tokens nos arquivos versionados.

## Perfil de agente

O perfil `auto-doc-execution-alest` existe para teste direto e uso como subagente finalizador. Ele:

- carrega o MCP configurado no Kiro;
- permite leitura local e operações do servidor `notion`;
- bloqueia escrita no filesystem;
- bloqueia operações Notion com nomes de delete/archive;
- permite somente `git config user.name` e `date` para identidade e horário.

## Limitação conhecida

O servidor local `@notionhq/notion-mcp-server`, necessário para autenticação por token, não recebe suporte ativo do Notion e pode ser descontinuado. A versão é fixada em `2.0.0`; valide antes de atualizar.

O pacote implementa o contrato e os guards do Kiro, mas a garantia operacional depende de:

- hook habilitado;
- steering carregado;
- MCP ativo;
- token válido;
- ferramentas necessárias pré-aprovadas;
- integração com acesso à página `Execuções`.

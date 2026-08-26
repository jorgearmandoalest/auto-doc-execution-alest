# auto-doc-execution-alest

Hooks nativos do **Kiro Crew** que documentam automaticamente, no Notion, todo turno concluído — sempre na página da atividade em andamento.

## Arquitetura

O runtime é composto por dois hooks e uma skill:

- [`hook.json`](./hook.json) + [`bin/auto-doc-execution-alest-hook`](./bin/auto-doc-execution-alest-hook): dispara no início do turno (`UserPromptSubmit`).
- [`hook-stop.json`](./hook-stop.json) + [`bin/auto-doc-execution-alest-stop-fallback`](./bin/auto-doc-execution-alest-stop-fallback): roda no fim do turno (`Stop`), como rede de segurança local.
- [`SKILL.md`](./SKILL.md): contrato semântico de persistência e apresentação, executado pelo agente.

O runtime do Kiro Crew (`kiro_crew/hooks.py`, classe `ScriptHook`) só executa hooks via o campo `command` — um subprocesso real, invocado com `/bin/sh -c`. Não existe suporte a um campo declarativo `skills` no hook; qualquer chave desconhecida do JSON é ignorada silenciosamente pelo runtime. Por isso o hook aponta `command` para um script real:

```json
{
  "id": "auto-doc-execution-alest",
  "event": "UserPromptSubmit",
  "matcher": "",
  "command": "$HOME/.kiro/bin/auto-doc-execution-alest-hook",
  "timeout": 30,
  "enabled": true
}
```

O script imprime no stdout a diretiva `Load skills: $auto-doc-execution-alest`, mais a instrução de executar o contrato completo da skill como última etapa do turno. Esse stdout é injetado como contexto (`[Hook context]`) no início do próximo turno — o mesmo mecanismo já usado por outros hooks nativos do Kiro Crew (ex.: Learning Loop).

A skill declara `always: false`: ela não depende de ativação semântica nem de carregamento permanente. O hook garante o carregamento da diretiva; o agente conclui a tarefa principal e documenta o resultado como última etapa do turno.

> O evento `UserPromptSubmit` ocorre no **início** do turno. O hook não escreve no Notion diretamente: ele injeta a diretiva que o agente deve seguir ao final, depois de concluir a tarefa principal.

### Hook `Stop` (rede de segurança)

Como a diretiva de carregamento só aparece no início do turno, um turno longo — com muitas ferramentas e edições — pode terminar sem o agente lembrar de executar o contrato da skill. O hook `Stop` cobre esse gap:

- roda depois que a resposta final do turno já foi enviada ao usuário (não pode reabrir o turno nem fazer o agente escrever no Notion retroativamente);
- lê o texto final do turno (`assistant_text`, via stdin) e verifica se a saída esperada da skill (`✅ Documentado em ...`, ou um dos avisos previstos por ela) está presente;
- se não estiver, grava um registro local em `~/.kiro/crew/auto-doc-execution-alest/missed-turns.jsonl`, para visibilidade de gaps;
- nunca escreve no Notion e nunca exige um ID de hub/página fixo — a skill preserva busca semântica deliberadamente.

## Política de registro

Todo turno é documentado na página da atividade específica em andamento, dentro do hub `Execuções` — não existe distinção entre "registro mínimo" e "relatório completo": um único template, sempre com duas camadas (resumo visual + detalhes em toggles).

Cada turno possui um único `Execution ID` e nunca gera dois registros.

Todo registro abre com um callout de cabeçalho:

- ícone `🟣`;
- fundo `purple_background`;
- conteúdo `📅 <data/hora> · 👤 <autor> · 📝 <título curto>`.

## Garantia e limites

O `UserPromptSubmit` elimina a dependência da seleção semântica da skill: o Kiro Crew executa o hook para cada prompt recebido e injeta a diretiva de carregamento. O hook `Stop` reduz — mas não elimina — o risco de o agente esquecer a diretiva em turnos longos, registrando localmente qualquer gap.

A persistência final continua dependendo de o turno chegar à etapa de encerramento e de o Notion estar disponível. Queda do processo, cancelamento abrupto ou falha do gateway antes do final podem impedir a gravação. A autodocumentação permanece não bloqueante e nunca reverte a tarefa principal.

## Instalação

Pré-requisitos:

- Kiro Crew com suporte a hooks `UserPromptSubmit` e `Stop`;
- Linux ou macOS;
- Bash;
- Python 3, usado somente pelo instalador para mesclar JSON com lock e gravação atômica;
- conexão do Notion já configurada no gateway.

```bash
git clone git@github.com:jorgearmandoalest/auto-doc-execution-alest.git
cd auto-doc-execution-alest
bash install.sh
kirocrew restart
```

Com diretório personalizado:

```bash
KIROCREW_HOME=/caminho/do/kirocrew KIRO_HOME=/caminho/do/kiro bash install.sh
kirocrew restart
```

O instalador grava:

```text
~/.kiro/
├── bin/
│   ├── auto-doc-execution-alest-hook
│   └── auto-doc-execution-alest-stop-fallback
└── crew/
    ├── hooks.json
    └── skills/
        └── auto-doc-execution-alest/
            └── SKILL.md
```

### Segurança e idempotência

O instalador:

- preserva outros hooks e chaves de contexto existentes em `hooks.json`;
- usa o mesmo lock lateral `hooks.json.lock` adotado pelo Kiro Crew;
- recusa JSON corrompido em vez de sobrescrevê-lo;
- remove duplicatas anteriores desta integração;
- preserva `run_count`, `last_run`, `last_status` e `last_error` de cada hook existente;
- cria backup antes de alterar `hooks.json`, a skill ou os scripts já instalados;
- usa arquivo temporário, `fsync` e substituição atômica;
- recusa destinos simbólicos;
- reverte skill e scripts se a instalação de qualquer hook falhar;
- não altera MCP, credenciais ou permissões do Notion;
- não reinicia o gateway automaticamente.

**Importante — ordem de operações:** o gateway do Kiro Crew mantém `hooks.json` em memória e o persiste de volta ao disco periodicamente (ex.: ao gravar telemetria `last_run`/`run_count`). Rode `bash install.sh` e só então `kirocrew restart` — se o restart ocorrer antes da última escrita do instalador, o gateway carrega a versão antiga em memória e a repersiste, desfazendo a correção mesmo com o processo reiniciado.

## Organização no Notion

```text
Execuções
├── Documentação do serviço — Serviço Exemplo A
└── Documentação do serviço — Serviço Exemplo B
```

- Cada página de atividade recebe todos os registros dos turnos relacionados a ela.
- O hub não recebe registros diretamente.
- A chain lê antes de escrever, preserva conteúdo existente e deduplica pelo `Execution ID`.

A criação do hub ou de uma nova atividade exige autorização quando o destino ainda não existir.

## Fluxo por prompt

1. o Kiro Crew recebe `UserPromptSubmit`;
2. o hook injeta a diretiva de carregamento e a instrução de executar a skill ao final;
3. a tarefa principal e as demais chains são concluídas;
4. o agente carrega a skill, gera ou reutiliza o `Execution ID`;
5. localiza `Execuções` e a página da atividade em andamento;
6. lê, deduplica, registra e relê;
7. encerra sem retomar a tarefa principal;
8. (rede de segurança) o hook `Stop` verifica se a saída esperada apareceu; se não, grava um registro local do gap.

## Saída no chat

```text
✅ Documentado em <título da atividade> com sucesso
```

O conteúdo detalhado permanece somente no Notion.

## Validação local

```bash
bash -n install.sh
python3 -m py_compile install_hook.py bin/auto-doc-execution-alest-stop-fallback tests/test_installer.py
python3 tests/test_installer.py
```

## Atualização

Depois de atualizar o clone local, execute novamente:

```bash
bash install.sh
kirocrew restart
```

O repositório usa hooks do **Kiro Crew**, não hooks do Kiro IDE nem hooks de provider em `~/.kiro/agents/`.

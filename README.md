# auto-doc-execution-alest

Hook nativo do **Kiro Crew** que carrega deterministicamente a skill de autodocumentação em todo `UserPromptSubmit`. Cada turno gera um registro mínimo no Notion; o relatório completo aparece somente quando há efeito relevante objetivo.

## Arquitetura

O runtime possui dois artefatos complementares:

- [`hook.json`](./hook.json): gatilho nativo do Kiro Crew;
- [`SKILL.md`](./SKILL.md): contrato semântico de classificação, persistência e apresentação.

O hook é **skills-only**:

```json
{
  "event": "UserPromptSubmit",
  "matcher": "",
  "command": "",
  "skills": ["auto-doc-execution-alest"],
  "enabled": true
}
```

Em cada prompt submetido, o Kiro Crew injeta `Load skills: $auto-doc-execution-alest`. Isso inclui prompts efetivamente submetidos por fluxos iterativos e loops.

A skill declara `always: false`: ela não depende mais de ativação semântica nem de carregamento permanente. O hook garante o disparo; a skill conclui a tarefa principal e documenta o resultado como última etapa do turno.

> O evento ocorre no início do turno. Por isso o hook não tenta escrever no Notion diretamente: ele carrega a skill que observa a execução completa e persiste o registro no final.

## Política de registro

A regra central é:

> **Registro mínimo sempre; relatório completo somente quando houver efeito relevante.**

O relatório completo é uma extensão do registro mínimo. Cada turno possui um único `Execution ID` e nunca gera dois registros.

### Registro mínimo

Usado em perguntas, explicações, traduções, buscas, leituras e conversas sem alteração persistente, decisão relevante, achado material ou pendência acionável.

É salvo na página filha `Registro mínimo`, dentro do hub `Execuções`, contendo somente:

- data, hora e autor;
- `Execution ID`;
- status da tarefa principal;
- resultado em uma ou duas frases;
- até três ações observáveis;
- motivo da classificação;
- próxima ação, quando houver.

### Relatório completo

Usado quando o turno apresenta pelo menos um efeito relevante objetivo:

- mutação em Notion, arquivos, código, databases, configurações, repositórios ou serviços;
- branch, commit, push, merge, PR, release, deploy, publicação ou rollback;
- e-mail, mensagem, convite, compartilhamento, permissão ou outra ação externa;
- artefato persistido;
- playbook, chain ou skill com entrega ou alteração de estado;
- decisão que muda abordagem, escopo, prioridade ou restrição;
- auditoria, investigação, teste ou validação com achado, evidência, falha, risco, bloqueio ou pendência acionável.

O relatório é salvo na página filha da atividade específica e usa duas camadas: resumo visual aberto e detalhes técnicos em toggles.

## Garantia e limites

O `UserPromptSubmit` elimina a dependência da seleção semântica da skill: o Kiro Crew executa o hook para cada prompt recebido e injeta a diretiva de carregamento.

A persistência final continua dependendo de o turno chegar à etapa de encerramento e de o Notion estar disponível. Queda do processo, cancelamento abrupto ou falha do gateway antes do final podem impedir a gravação. A autodocumentação permanece não bloqueante e nunca reverte a tarefa principal.

## Instalação

Pré-requisitos:

- Kiro Crew com suporte a hooks `UserPromptSubmit` e hooks skills-only;
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
KIROCREW_HOME=/caminho/do/kirocrew bash install.sh
kirocrew restart
```

O instalador grava:

```text
~/.kiro/crew/
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
- preserva `run_count`, `last_run`, `last_status` e `last_error` do hook existente;
- cria backup antes de alterar `hooks.json` ou uma skill já instalada;
- usa arquivo temporário, `fsync` e substituição atômica;
- recusa destinos simbólicos;
- reverte a skill se a instalação do hook falhar;
- não altera MCP, credenciais ou permissões do Notion;
- não reinicia o gateway automaticamente.

O hook não executa Python, Node ou comando de shell a cada prompt. Python 3 é usado apenas em `bash install.sh`; o runtime é uma injeção nativa de skill com `command: ""`.

## Organização no Notion

```text
Execuções
├── Registro mínimo
├── Documentação do serviço — Serviço Exemplo A
└── Documentação do serviço — Serviço Exemplo B
```

- `Registro mínimo`: ledger compacto dos turnos sem efeito relevante.
- Páginas de atividade: relatórios completos das execuções com efeito relevante.
- O hub não recebe registros diretamente.
- A chain lê antes de escrever, preserva conteúdo existente e deduplica pelo `Execution ID`.

A criação do hub, da página `Registro mínimo` ou de uma nova atividade exige autorização quando o destino ainda não existir.

## Fluxo por prompt

1. o Kiro Crew recebe `UserPromptSubmit`;
2. o hook injeta `$auto-doc-execution-alest`;
3. a tarefa principal e as demais chains são concluídas;
4. a skill gera ou reutiliza o `Execution ID`;
5. avalia critérios objetivos de efeito relevante;
6. escolhe `MINIMO` ou `COMPLETO`;
7. localiza `Execuções` e o destino correto;
8. lê, deduplica, registra e relê;
9. encerra sem retomar a tarefa principal.

Chamadas de leitura não tornam um turno completo por si só. Havendo mutação, decisão, achado material, falha, risco, bloqueio ou pendência acionável, o relatório completo é obrigatório.

## Saída no chat

Para registro mínimo:

```text
✅ Registro mínimo documentado com sucesso
```

Para relatório completo:

```text
✅ Documentado em <título da atividade> com sucesso
```

O conteúdo detalhado permanece somente no Notion.

## Validação local

```bash
bash -n install.sh
python3 -m py_compile install_hook.py tests/test_installer.py
python3 tests/test_installer.py
```

## Atualização

Depois de atualizar o clone local, execute novamente:

```bash
bash install.sh
kirocrew restart
```

O repositório usa o hook do **Kiro Crew**, não hooks do Kiro IDE nem hooks de provider em `~/.kiro/agents/`.

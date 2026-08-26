# auto-doc-execution-alest

Chain declarativa, sempre ativa e nativa do **Kiro Crew** para manter auditabilidade sem poluir o histórico: registra todo turno no Notion e só gera documentação detalhada quando existe efeito relevante.

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

O relatório é salvo na página filha da atividade específica e usa duas camadas: resumo visual sempre aberto e detalhes técnicos em toggles.

## Runtime declarativo

O único artefato carregado pelo Kiro Crew é [`SKILL.md`](./SKILL.md). O [`install.sh`](./install.sh) apenas instala a skill e não participa da execução.

O repositório não exige npm, Node.js, Python, hook do Kiro IDE, agente auxiliar ou configuração do MCP do Notion.

O frontmatter `always: true` mantém o contrato carregado em todas as novas sessões. A chain roda exatamente uma vez como última etapa de cada prompt e sua falha nunca reabre, reverte ou altera o status da tarefa principal.

## Instalação

Em Linux ou macOS:

```bash
git clone git@github.com:jorgearmandoalest/auto-doc-execution-alest.git
cd auto-doc-execution-alest
bash install.sh
```

Por padrão, a skill é instalada em:

```text
~/.kiro/crew/skills/auto-doc-execution-alest/SKILL.md
```

Com diretório personalizado:

```bash
KIROCREW_HOME=/caminho/do/kirocrew bash install.sh
```

O instalador valida `name` e `always: true`, é idempotente, cria backup antes de substituir uma versão diferente, grava atomicamente e não usa `sudo`, altera MCP/credenciais ou reinicia o gateway.

Abra uma nova sessão do Kiro Crew após a instalação.

## Pré-requisito

O Notion deve estar configurado e disponível no gateway do Kiro Crew. A chain não solicita token, instala MCP ou altera credenciais.

Se a conexão falhar, a tarefa principal permanece inalterada e a chain apenas orienta executar `kirocrew restart`.

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
- A chain lê antes de escrever, preserva o conteúdo existente e deduplica pelo `Execution ID`.

A criação do hub, da página `Registro mínimo` ou de uma nova atividade exige autorização quando o destino ainda não existir.

## Fluxo por prompt

1. concluir a tarefa principal e todas as outras chains;
2. gerar ou reutilizar o `Execution ID`;
3. avaliar os critérios objetivos de efeito relevante;
4. escolher `MINIMO` ou `COMPLETO`;
5. localizar `Execuções` e o destino correto;
6. ler, deduplicar, registrar e reler;
7. encerrar sem executar nova ação da tarefa principal.

Chamadas de leitura não tornam um turno completo por si só. Havendo qualquer mutação, decisão, achado material, falha, risco, bloqueio ou pendência acionável, o relatório completo é obrigatório.

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

## Atualização

Depois de atualizar o clone local, execute novamente:

```bash
bash install.sh
```

Não execute `npm install` ou `npm test`: não há runtime npm neste repositório.

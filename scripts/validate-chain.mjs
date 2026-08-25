import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const requiredFiles = [
  '.kiro/hooks/auto-doc-execution-alest.kiro.hook',
  '.kiro/steering/auto-doc-execution-alest.md',
  '.kiro/agents/auto-doc-execution-alest.json',
  '.kiro/agents/auto-doc-execution-alest.prompt.md',
  'templates/mcp.json.example',
  'README.md'
];

const fail = (message) => {
  console.error(`CHAIN_VALIDATION_FAIL: ${message}`);
  process.exit(1);
};

for (const relativePath of requiredFiles) {
  if (!fs.existsSync(path.join(root, relativePath))) {
    fail(`arquivo ausente: ${relativePath}`);
  }
}

const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), 'utf8');
const hook = JSON.parse(read('.kiro/hooks/auto-doc-execution-alest.kiro.hook'));
const agent = JSON.parse(read('.kiro/agents/auto-doc-execution-alest.json'));
const mcp = JSON.parse(read('templates/mcp.json.example'));
const steering = read('.kiro/steering/auto-doc-execution-alest.md');

if (hook.version !== 'v1' || !Array.isArray(hook.hooks) || hook.hooks.length !== 1) {
  fail('hook deve usar versão v1 e conter exatamente uma automação');
}

const finalizerHook = hook.hooks[0];
if (finalizerHook.trigger !== 'UserPromptSubmit') {
  fail('o trigger deve ser UserPromptSubmit; Stop ocorre depois da resposta ao usuário');
}
if (finalizerHook.action?.type !== 'agent' || finalizerHook.enabled !== true) {
  fail('hook deve ser uma ação agent habilitada');
}
if (agent.name !== 'auto-doc-execution-alest' || agent.includeMcpJson !== true) {
  fail('perfil do agente inválido ou sem inclusão do mcp.json');
}
if (!agent.tools?.includes('@notion')) {
  fail('perfil deve expor somente o MCP notion necessário à escrita');
}
if (mcp.mcpServers?.notion?.env?.NOTION_TOKEN !== '${NOTION_TOKEN}') {
  fail('template MCP deve referenciar NOTION_TOKEN sem incorporar segredo');
}

const requiredContractFragments = [
  'Execuções',
  'purple_background',
  'America/Sao_Paulo',
  '✅ Documentado em Execuções com sucesso',
  'MCP do Notion desabilitado ou indisponível',
  'Deseja que eu a crie?',
  'Execution ID',
  'última fase'
];
for (const fragment of requiredContractFragments) {
  if (!steering.includes(fragment)) {
    fail(`contrato não contém trecho obrigatório: ${fragment}`);
  }
}

const tokenPrefix = '(?:ntn|secret)' + '_';
const tokenPattern = new RegExp(`${tokenPrefix}[A-Za-z0-9_-]{12,}`, 'g');
for (const relativePath of requiredFiles) {
  const matches = read(relativePath).match(tokenPattern) || [];
  if (matches.length > 0) {
    fail(`possível token encontrado em ${relativePath}`);
  }
}

console.log('CHAIN_VALIDATION_PASS');

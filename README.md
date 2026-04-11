# Moodle Question Checker 🤖

O **Moodle Question Checker** é um assistente automatizado (Robô) construído com **Python** e **Playwright**. Seu propósito principal é atuar como um revisor automático para a equipe da **Fundace**, permitindo varrer um banco de questões, visualizar como cada uma aparecerá para o aluno, realizar testes funcionais (respondendo as alternativas corretas e incorretas) e emitir um relatório final de desempenho da plataforma.

Tudo isso, **limitado à leitura**, garantindo segurança absoluta de que o robô jamais salvará alterações, fará apagamentos, duplicatas ou edições no sistema Moodle da Fundace.

---

## Principais Funcionalidades
- ✅ **Testes Automatizados Híbridos**: Agora aceita como "Fonte da Verdade" tanto as previsões de provas em **.JSON** quanto os próprios arquivos nativos **.XML** do Moodle.
- 📸 **Captura Inteligente (Screenshots)**: Tira prints em 3 momentos: no primeiro carregamento, após simular o acerto, e após simular o erro.
- 📊 **Relatórios Exportados**: Prepara uma planilha limpa (Excel/CSV) indicando de forma cirúrgica quais questões falharam visualmente na Moodle e o real porquê.
- ⏸️ **Modo Interativo (Login Nativo)**: O robô abre a janela do portal e aguarda sua autenticação física real, driblando caixas de spam e captchas, assumindo o controle total em segurança logo em seguida.
- 🛡️ **Network Guardrail**: Impede a nível de tráfego TCP/HTTP envio de modificações perigosas. O servidor ead.fundace.org.br ficará bloqueado para receber dados via POST/DELETE deste navegador automatizado.

---

## 🛠 Como Preparar seu Computador (1ª Execução)

O sistema foi otimizado para não exigir conhecimentos densos. O repositório já se encontra configurado, voltado fixamente para o ambiente de testes principal de vocês (`ead.fundace.org.br`).

**Requisito Único**: Ter o [Python 3.11+](https://www.python.org/downloads/) instalado no seu computador habilitando a opção de "Adicionar o PATH" durante a instalação.

**Não é necessário rodar códigos obscuros no terminal.**  
O programa se encarrega de instalar bibliotecas, baixar o navegador injetável e instanciar os motores na tela verde na primeira abertura, sozinho!

---

## 🎒 Passo a Passo para Validar Aulas/Provas

A operação natural acontece colocando o seu insumo na pasta `input/`. O robô consumirá sempre o 1º arquivo (.json ou .xml) que residir lá.

### Passo 1: Inserindo sua Prova (XML ou JSON)
1. Abra a pasta `input/`.
2. Delete arquivos de testes remanescentes nesta pasta.
3. Arraste e solte o seu arquivo gerado da pauta nova (seja ele o XML oficial de Moodle que você gerou, ou aquele JSON detalhado oriundo do Word).

### Passo 2: Inicialização e Seleção da Disciplina
1. Volte à pasta raiz (`moodle_question_checker`) e **dê duplo clique no arquivo `run_check.bat`**.
2. A janela escura de comando irá aparecer, checando as atualizações do robô em 2 segundos.
3. Ele vai te perguntar **qual o ID do Curso**. Responda com a identificação numérica (Exemplo: Para `view.php?id=53`, digite apenas `53`). Aperte Enter.

### Passo 3: Etapa Humana (Autenticação)
As credenciais sigilosas da instituição não ficam grafadas no robô. 
1. Uma aba do Chrome/Chromium abrirá instantaneamente na página de autenticação.
2. Digite ou use seu gerenciador de senhas para entrar (e resolva Captchas, se existirem).
3. Aguarde o login ocorrer.

### Passo 4: Cruzando os Braços (Operação do Robô)
No momento em que você vê a Foto de Perfil indicando que Logou, o robô retoma a direção.
1. Navega para a categoria do banco de questões (courseid que você indicou).
2. Pesquisa questão por questão e ativa a **Lupa da Prévia**.
3. Compara o material extraído sem que precisemos validar isso a olho nu.
4. Responde, tira Print e avança as turmas sozinho.

### Passo 5: Avaliar Relatório
1. O Chrome Phantomly se fecha.
2. Abra a pasta `output/`.
3. Lá estará a **`relatorio_validacao.xlsx`**, devidamente tabulada e limpa. A pasta `screenshots/` abrigará até os milésimos de segundo de cada click do "fantasma".

---

## ⚙ Resolução Rápida (FAQ)
- **Não está parando para eu fazer meu login.** -> Verifique se a variável "headless" no código não travou (tem de ficar operante visualmente).
- **O robô deu Timeout lendo botão.** -> Pode ser uma pane temporária de internet ou um seletor visual que sumiu do layout Fundace num final de semana. Arquivo de emergência para arrumar: `config/selectors.json`. Consulte a pasta de instruções para mais guias dinâmicos se ele vier a falhar em meses vindouros.

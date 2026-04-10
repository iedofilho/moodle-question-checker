# Moodle Question Checker 🤖

O **Moodle Question Checker** é um assistente automatizado (Robô) construído com **Python** e **Playwright**. Seu propósito principal é atuar como um revisor automático para professores, administradores e revisores de conteúdo, permitindo varrer um banco de questões, visualizar como cada uma aparecerá para o aluno, realizar testes funcionais (respondendo as alternativas corretas e incorretas) e emitir um relatório final do desempenho da plataforma.

Tudo isso, **limitado à leitura**, garantindo segurança absoluta de que o robô jamais salvará apagamentos, duplicatas ou edições em seu Moodle.

---

## Principais Funcionalidades
- ✅ **Testes Automatizados de Questões**: Abre a "Prévia" de cada questão e compara o que está online com sua "Fonte da Verdade" local.
- 📸 **Captura Inteligente (Screenshots)**: Tira prints em 3 momentos: no primeiro carregamento, após simular acerto, após simular erro.
- 📊 **Relatórios Exportados**: Prepara uma planilha limpa e colorida (Excel/CSV) onde você vê rápido quais questões falharam no Moodle e por quê.
- ⏸️ **Modo Híbrido com Login Nativo**: O robô abre a janela para seu login manualmente, driblando bloqueios do navegador headless e captchas, e assume o controle assim que detecta o ambiente da academia!
- 🛡️ **Network Guardrail**: Impede a nível de pacote TCP/HTTP alterações perigosas. Seu Moodle estará bloqueado para receber POST/DELETE por parte do robô, salvo as simulações exclusivas da Prévia.
- 🎯 **Compatibilidade Flexível**: Se adapta bem com as estruturas-padrão de Verdadeiro ou Falso e Múltipla Escolha.

---

## 🛠 Como Preparar seu Computador (1ª Execução)

O sistema foi montado com foco na facilidade Windows.  
**Requisitos**: Apenas o [Python 3.11+](https://www.python.org/downloads/) instalado no seu computador.

1. **Abra a pasta do projeto.**
2. **Renomeie ou crie seu arquivo de Ambiente**: Na raiz do projeto, procure por `.env.example` e renomeie-o para `.env` (com o ponto na frente e nenhum texto antes do ponto). 
3. **Mude a URL (opcional, já vai preenchido)**: Certifique-se que o `.env` contenha `MOODLE_URL=https://ead.fundace.org.br` (Ou o domínio final do seu moodle).

**Não é necessário rodar códigos no terminal.** O programa se encarrega sozinho de instalar as bibliotecas, baixar o Chromium e preparar o ambiente virtual na primeira inicialização!

---

## 🎒 Passo a Passo para Validar um Novo Lote

A operação natural acontece nas etapas abaixo, sempre respeitando a sua fonte (*`input/questoes.json`*).

### Passo 1: Injetando as Novas Questões
1. Entre na pasta `input/`.
2. Abra o arquivo **`questoes.json`**.
3. É neste arquivo onde suas questões estarão ditadas estruturalmente. Ele precisa bater com a tela do Moodle. Para gerar este arquivo facilmente a partir de um DOC/Word, abra a pasta `instructions/` e copie e cole no ChatGPT o texto de `PROMPT_WORD_PARA_JSON.md`.
4. Substitua o conteúdo do `questoes.json` atual pelo gerado e salve o arquivo.

### Passo 2: Inicialização
1. Volte à pasta principal (`moodle_question_checker`) e **dê duplo clique em `run_check.bat`**.
2. Uma janela escura de comando irá abrir, criando a rede neural e as dependências e iniciando a ignição do Robô.
3. Repentinamente, um navegador em branco abrirá já focado na tela de Login do seu curso Moodle.

### Passo 3: Etapa Humana (Autenticação)
Como regra de segurança primária, as senhas do sistema **não residem** no arquivo fonte. 
1. **Atente-se ao navegador recém-aberto!** 
2. Ele aguardará. Preencha seu usuário e senha normalmente na interface nativa da Instituição. 
3. Caso tenha recaptcha, resolva tranquilamente.
4. Confirme seu acesso e pare de mexer.

### Passo 4: Operação do Robô (Deixe a tela aberta)
Assim que o painel inicial carregar, o observador identificará o perfil e "assumirá a direção":
1. Ele pesquisará seu banco de questões;
2. Abrirá a primeira previalização;
3. Comparará os textos;
4. Resolverá simulando um acerto, marcando se o gabarito ficou verde;
5. Simulará um erro, provando que marca como vermelho;
6. Limpa e repete em sequẽncia para todo o JSON.

### Passo 5: Avaliar Relatório
1. Quando a tela preta emitir que finalizou, feche-a ou saia.
2. Acesse a diretório principal, e em seguida a pasta **`output/`**.
3. Abra **`relatorio_validacao.xlsx`**. Ele exibirá minuciosamente em quais etapas de layout a questão pode estar diferindo ou se ela passou em 100% dos testes da banca!

---

## ⚙ Configurações Avançadas e Problemas Comuns

- **As imagens estão sem pastas/faltando!** -> Certifique que a sua execução tem espaço em disco, a pasta `output/screenshots` ficará populada ao final de cada execução. Tente rodar testes em lotes de 10 em 10.
- **O Robô esbarrou na hora de clicar "EnviarResposta" ou de ler o Botão.** -> Cada Tema Moodle muda seu interior ou CSS. Se isso vier a ser o caso após uma atualização pesada por parte da TI, um simples reajuste pode ser feito no arquivo legível `config/selectors.json`. Verifique em `instructions/COMO_MAPEAR_SELETORES.md` para auxílio de troca rápida!
- **Posso deixar mais devagar? Quero apenas assistir pausadamente!** -> Sim, edite o `.env` na raiz e amplie o valor de `PLAYWRIGHT_SLOW_MO=500` para `PLAYWRIGHT_SLOW_MO=1500`. Ele levará consideráveis 1.5s entre cada clicada no mouse virtual.

---
_Desenvolvido com carinho e Python - 2026_

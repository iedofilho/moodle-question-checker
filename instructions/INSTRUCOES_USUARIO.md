# Instruções para o Usuário - Como Validar Suas Questões

Bem-vindo ao **Moodle Question Checker**. Esse robô foi projetado para atuar como o "seu assistente de revisão" automático. Ele abrirá o seu Moodle e testará como os alunos verão uma determinada questão, tirando "prints" ao longo do caminho.

**Passo a passo rápido:**
1. Descreva as questões com o auxílio do ChatGPT convertendo do seu Word para `.json` (veja `PROMPT_WORD_PARA_JSON.md`).
2. Cole essas questões geradas no arquivo `input/questoes.json`.
3. Preencha o arquivo `.env` com a sua senha e usuário do Moodle (clique com botão direito e use um bloco de notas para editar).
4. Dê um duplo clique no arquivo `run_check.bat`. Você verá uma janela escura de comando e em seguida um navegador abrindo magicamente!
5. **Nesta tela do navegador**, o robô irá pausar. Faça o seu login manualmente enquanto ele aguarda! Assim que você logar, ele recomeça.
6. Ao fechar, você verá avisos na sua tela e um relatório completíssimo dentro da pasta `output/`, incluindo também todos os screenshots tomados durante os acertos/erros processados.

Se os botões ou páginas do seu Moodle estiverem um pouco diferentes do que o app espera, consulte `COMO_MAPEAR_SELETORES.md`.

# Instruções para o Usuário - Como Validar Suas Questões

Bem-vindo ao **Moodle Question Checker**. Esse robô foi projetado para atuar como o seu revisor automático silencioso para auditoria de questões no portal Moodle da Fundace. Ele testa ativamente se alunos teriam falhas visuais em uma prova.

**Passo a passo rápido de uso diário:**
1. Converta as suas provas usando Inteligência Artificial para gerar um currículo bruto em `.xml` (Padrão Moodle XML) ou `.json`.
2. Solte **um** desses dois arquivos dentro da pasta `input/`, excluindo os testes antigos de lá. Esse passo garante sua base de dados atualizada.
3. Dê um duplo clique no arquivo executável **`run_check.bat`**. 
4. A tela preta de prompt exigirá o **ID numérico do curso** que essa prova vai adentrar (Ex: Para matemática `http.../course/view.php?id=38`, você digitaria puramente `38`).
5. Logo após colocar o número e dar enter, o sistema pulará visualizando um Navegador virgem já cravado na página de login da Fundace.
6. **Escreva ali o seu login presencialmente**. Ao confirmar e atingir a área "Meu Painel", a mágica automatizada acontece. Pode tirar as mãos.
7. O robô varre, acerta, erra propositalmente, guarda "Prints" e tabula se a sintaxe inteira confere contra os enunciados reais da Fundace até acabar a carga horária de perguntas.
8. Visualize a apuração dentro da pasta `output/relatorio_validacao.xlsx`.


Ficou na dúvida de por que uma questão apresentou problemas no layout ou o script reclamou não achar os botões de avançar? Tente consultar o aviso de documentação chamado `COMO_MAPEAR_SELETORES.md`.

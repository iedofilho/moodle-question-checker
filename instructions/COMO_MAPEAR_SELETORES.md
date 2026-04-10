# Como Mapear Seletores

Cada versão do Moodle (ou tema) organiza sua tela de forma diferente. Para isso, criamos o arquivo `config/selectors.json`.

Esse arquivo usa "locators" semânticos (papéis e textos padrão do sistema) preferencialmente. 
Seu robô não está conseguindo encontrar o botão "Salvar e Continuar"?
1. Abra um navegador e vá até a tela onde a falha está ocorrendo na inspeção da página (F12).
2. Tente descobrir uma classe CSS, um `role="button"`, ou texto. 
3. Se for classe: modifique o valor para `.minha_classe`. 
4. Se for Playwright query, pode usar: `xpath=//div...` .

No código implementado, tentamos abstrair a fragilidade com seletores focados em classe comum do curso Moodle ou usando as labels que aparecem visualmente.

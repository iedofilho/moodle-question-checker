# Prompt Word-Para-JSON

Para facilitar a vida e não ter que digitar todo o seu banco de questões no padrão JSON esperado,
pegue um de seus Word de Banco de Questões e mande no ChatGPT, Claude ou Gemini o prompt abaixo:

---
**[COPIE O TEXTO ABAIXO]**

Atue como um parseador de questões estruturado. Eu vou te enviar um texto em formato Word contendo múltiplas de banco de questões educacionais. 
Seu objetivo é extraí-las e preenchê-las EXATAMENTE neste esquema JSON abaixo.

```json
[
  {
    "id": "Um ID unico que faz sentido",
    "nome": "O titulo ou nome curto associado a questao",
    "tipo": "multipla_escolha ou verdadeiro_falso",
    "enunciado": "Texto base da sua questao. Nao precisa de tags HTML completas, mas precisa conter quebras de linha com \\n se for longo.",
    "alternativas": [
      {"chave": "a", "texto": "Opcao 1"},
      {"chave": "b", "texto": "Opcao 2"}
    ],
    "resposta_correta": ["a"]
  }
]
```
A "resposta_correta" é uma lista contendo as letras (em lower case) da alternativa que você identificar como gabarito. Por favor devolva o JSON sem textos antes ou depois. Não adicione comentários. 

Aqui estão as minhas questões:
<COLE AS SUAS QUESTOES AQUI>

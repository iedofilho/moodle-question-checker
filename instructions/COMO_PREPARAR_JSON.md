# Como Preparar o JSON

O arquivo `input/questoes.json` é a **"Fonte da Verdade"**. Seus dados são convertidos do Word e comparados com o Moodle.

**Formato básico exigido:**
```json
[
  {
    "id": "q1",
    "nome": "História - Q1",
    "tipo": "multipla_escolha",
    "enunciado": "Quem descobriu o Brasil?",
    "alternativas": [
      { "chave": "a", "texto": "Pedro Álvares Cabral" },
      { "chave": "b", "texto": "Cristóvão Colombo" }
    ],
    "resposta_correta": ["a"]
  }
]
```

**Campos Obrigatórios:**
- `id`: Um ID único qualquer para registro (ex: "q1", "q2023_pt").
- `nome`: O nome da questão exatamente como está ou estará parcialmente no filtro do banco do Moodle.
- `tipo`: Pode ser `multipla_escolha` ou `verdadeiro_falso`. (Posteriormente expansível).
- `enunciado`: O HTML/Texto liso da pergunta. 
- `alternativas`: Array de objetos com `chave` e `texto` da alternativa.
- `resposta_correta`: Array de chaves corretas (Mesmo que seja apenas uma).

Dúvidas? Cheque o arquivo principal em `examples/questoes_exemplo.json`.

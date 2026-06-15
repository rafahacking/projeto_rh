---
doc_id: "GUIDE-001"
title: "Guia de Ingestão, Chunking e Testes de RAG"
category: "RAG"
owner: "AI Engineering"
tags:
  - RAG
  - chunking
  - embedding
  - metadata
  - avaliação
  - CrewAI
version: "1.0"
effective_date: "2026-01-01"
confidentiality: "Uso interno - sintético para testes"
source_type: "synthetic_guide"
synthetic: true
language: "pt-BR"
---
# GUIDE-001 - Guia de Ingestão, Chunking e Testes de RAG

## Objetivo
Orientar o uso deste pacote sintético em pipelines de RAG, bases vetoriais, topic modeling, CrewAI, LlamaIndex, LangChain, Pydantic AI, BERTopic e ferramentas equivalentes.

## Estratégia de ingestão
1. Carregue os arquivos Markdown preservando o frontmatter YAML.
2. Separe o conteúdo por títulos de nível 2 e 3 antes de aplicar chunking por tamanho.
3. Gere chunks entre 600 e 900 tokens, com overlap entre 80 e 120 tokens.
4. Inclua metadados em cada chunk: doc_id, title, category, owner, tags, version, effective_date, section_title e confidentiality.
5. Gere embeddings para cada chunk e salve no banco vetorial.
6. Salve o texto bruto e os metadados também em banco relacional para auditoria.

## Metadados recomendados
- doc_id: identificador estável do documento.
- chunk_id: identificador único do trecho.
- title: título do documento.
- section_title: seção de origem.
- category: categoria de RH.
- tags: palavras-chave controladas.
- source_type: policy, sop, faq ou guide.
- confidentiality: nível de confidencialidade.
- effective_date: data de vigência.
- version: versão do documento.
- synthetic: verdadeiro para este pacote.

## Recuperação recomendada
Para perguntas de política, use busca híbrida: BM25 + vetor + reranker. Para perguntas de People Analytics, filtre primeiro por categoria e depois use RAG apenas para explicar regras e limitações. Para perguntas sensíveis, acione guardrail antes da busca ou antes da resposta final.

## Guardrails mínimos
O sistema deve negar ou escalar perguntas que peçam dados pessoais individuais, diagnóstico médico, nomes de pessoas em situação sensível, ranking de risco individual, decisão automática de promoção/demissão ou exposição de salário individual. A resposta deve oferecer alternativa segura, preferencialmente agregada.

## Avaliação
Monte um conjunto de perguntas douradas. Para cada pergunta, registre documento esperado, seção esperada, resposta esperada, necessidade de escalonamento e comportamento proibido. Meça taxa de acerto da fonte, groundedness, recusa correta, completude, latência e custo.

## Exemplo de saída estruturada para resposta RAG
{
  "answer": "Texto final para o usuário",
  "sources": ["POL-003 > Planejamento de férias"],
  "confidence": 0.86,
  "needs_escalation": false,
  "sensitive_data_detected": false,
  "limitations": "Documento sintético; regras legais reais devem ser validadas com Jurídico."
}

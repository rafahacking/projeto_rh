# HR RAG Knowledge Pack - NexaPeople Tech

Pacote sintético de documentos de RH para testar RAG, CrewAI, LlamaIndex, LangChain, Pydantic AI, BERTopic, pgvector/Qdrant/Chroma e pipelines de avaliação.

## Conteúdo
- `docs/`: políticas, FAQ, SOP e guia de ingestão em Markdown com frontmatter YAML.
- `metadata/taxonomy.yaml`: categorias, tópicos sensíveis e filtros sugeridos.
- `metadata/source_references.md`: referências públicas usadas como inspiração conceitual.
- `eval/golden_questions.jsonl`: perguntas douradas para avaliação de RAG e guardrails.

## Observação importante
Todos os documentos são fictícios e foram criados para demonstração técnica. Não use como política real, orientação jurídica ou orientação trabalhista.

## Ingestão recomendada
1. Leia o frontmatter YAML.
2. Divida por headings.
3. Gere chunks entre 600 e 900 tokens.
4. Preserve metadados em cada chunk.
5. Rode embeddings.
6. Armazene em base vetorial e banco relacional.
7. Use `eval/golden_questions.jsonl` para medir recuperação, groundedness e recusa correta.

Gerado em 2026-06-14.

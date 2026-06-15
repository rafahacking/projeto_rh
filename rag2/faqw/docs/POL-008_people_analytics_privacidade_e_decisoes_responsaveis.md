---
doc_id: "POL-008"
title: "People Analytics, Privacidade e Decisões Responsáveis"
category: "People Analytics"
owner: "People Analytics"
tags:
  - analytics
  - dados agregados
  - privacidade
  - métricas
  - decisão responsável
  - vieses
version: "1.0"
effective_date: "2026-01-01"
confidentiality: "Uso interno - sintético para testes"
source_type: "synthetic_policy"
synthetic: true
language: "pt-BR"
---
# POL-008 - People Analytics, Privacidade e Decisões Responsáveis

## Objetivo
Orientar o uso responsável de dados de pessoas para apoiar decisões organizacionais, respeitando privacidade, contexto, segurança e revisão humana.

## Escopo
Esta política se aplica a análises de headcount, turnover, absenteísmo, clima, engajamento, performance, recrutamento, diversidade, mobilidade interna, capacitação e chamados de RH.

## Princípios de análise
1. Usar dados para melhorar processos e experiência, não para vigilância individual.
2. Priorizar análises agregadas por área, período, localidade, senioridade ou grupo autorizado.
3. Evitar conclusões causais quando houver apenas correlação.
4. Documentar fonte, definição da métrica, filtros e limitações.
5. Manter revisão humana em decisões de carreira, remuneração, promoção, movimentação ou desligamento.

## Limiar mínimo de grupo
Relatórios automáticos devem ocultar resultados de grupos com menos de cinco pessoas, salvo autorização específica e finalidade legítima. Quando o grupo for pequeno, o agente deve sugerir análise em nível mais agregado.

## Métricas comuns
Turnover voluntário, turnover involuntário, taxa de absenteísmo, eNPS, índice de liderança, tempo de fechamento de vaga, tempo de resolução de chamado, taxa de conclusão de onboarding e participação em treinamentos são métricas permitidas quando calculadas com dados autorizados.

## Métricas sensíveis
Modelos preditivos de risco individual, ranqueamento de colaboradores, inferência de saúde, inferência de intenção de desligamento e análise de produtividade individual por monitoramento digital exigem avaliação ética, jurídica e de privacidade. Por padrão, o copiloto não deve produzir esse tipo de saída.

## Uso de IA em análises
A IA pode resumir tendências, gerar hipóteses, explicar variações e sugerir perguntas investigativas. A IA não deve substituir avaliação contextual de RHBP, gestor e comitês responsáveis.

## Regras para respostas do copiloto de RH
O agente deve responder com dados agregados, explicitar filtros, indicar limitações e recomendar análise humana quando houver risco de decisão individual. Se a pergunta pedir nomes, ranking individual ou dados sensíveis, deve negar educadamente e oferecer alternativa agregada.

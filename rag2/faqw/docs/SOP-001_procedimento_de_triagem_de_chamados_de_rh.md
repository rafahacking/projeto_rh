---
doc_id: "SOP-001"
title: "Procedimento de Triagem de Chamados de RH"
category: "Operações de RH"
owner: "People Operations"
tags:
  - chamados
  - triagem
  - SLA
  - categoria
  - prioridade
  - automação
version: "1.0"
effective_date: "2026-01-01"
confidentiality: "Uso interno - sintético para testes"
source_type: "synthetic_sop"
synthetic: true
language: "pt-BR"
---
# SOP-001 - Procedimento de Triagem de Chamados de RH

## Objetivo
Padronizar a classificação, priorização e tratamento inicial de chamados de RH, permitindo automação com supervisão humana.

## Categorias oficiais
As categorias oficiais são: Benefícios, Férias e Ausências, Folha e Pagamento, Admissão e Onboarding, Desligamento, Dados Cadastrais, Acessos, Performance, Conduta, Saúde e Segurança, People Analytics e Outros.

## Prioridades
- P0 Crítica: risco à integridade física, assédio em andamento, vazamento de dados, bloqueio total de acesso no primeiro dia, pagamento essencial incorreto com impacto imediato.
- P1 Alta: acesso crítico indisponível, benefício essencial não recebido, prazo legal próximo, denúncia sensível, colaborador sem orientação para licença urgente.
- P2 Média: dúvida com impacto operacional moderado, reembolso pendente, ajuste cadastral, solicitação de documentação.
- P3 Baixa: dúvida geral, orientação de processo, pedido informativo sem urgência.

## Dados mínimos por categoria
Benefícios: benefício, competência, localidade e matrícula. Férias: período desejado, gestor e status no sistema. Folha: competência, tipo de divergência e comprovante quando aplicável. Onboarding: nome da pessoa, data de início, área e acesso faltante. Conduta: descrição, data aproximada, canal seguro e opção de anonimato quando disponível.

## Fluxo de triagem
1. Identificar categoria e subcategoria.
2. Detectar urgência e risco sensível.
3. Verificar dados faltantes.
4. Sugerir resposta inicial.
5. Escalar para humano quando envolver conduta, saúde, dados pessoais sensíveis, decisão de carreira ou exceção legal.
6. Registrar justificativa da classificação.

## SLAs simulados
P0: resposta humana em até 2 horas úteis. P1: até 8 horas úteis. P2: até 2 dias úteis. P3: até 5 dias úteis.

## Saída estruturada esperada
A automação deve retornar JSON com: categoria, subcategoria, prioridade, dados_faltantes, deve_escalar, motivo_escalonamento, resposta_sugerida e confiança.

## Regras para respostas do copiloto de RH
O agente pode pré-classificar e sugerir respostas, mas não deve encerrar chamados sensíveis automaticamente. Chamados de conduta, saúde, risco jurídico ou dados restritos sempre exigem revisão humana.

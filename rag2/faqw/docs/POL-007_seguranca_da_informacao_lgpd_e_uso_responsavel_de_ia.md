---
doc_id: "POL-007"
title: "Segurança da Informação, LGPD e Uso Responsável de IA"
category: "Segurança e Privacidade"
owner: "Segurança da Informação"
tags:
  - LGPD
  - privacidade
  - segurança
  - IA
  - dados pessoais
  - confidencialidade
version: "1.0"
effective_date: "2026-01-01"
confidentiality: "Uso interno - sintético para testes"
source_type: "synthetic_policy"
synthetic: true
language: "pt-BR"
---
# POL-007 - Segurança da Informação, LGPD e Uso Responsável de IA

## Objetivo
Definir regras para proteção de dados, segurança da informação e uso responsável de ferramentas de IA na NexaPeople Tech.

## Classificação da informação
Informações podem ser públicas, internas, confidenciais ou restritas. Dados pessoais de colaboradores, candidatos, dependentes, saúde, remuneração, avaliações, documentos oficiais e medidas disciplinares são tratados como confidenciais ou restritos.

## Princípio da necessidade
Acesso a dados deve seguir o princípio do menor privilégio. Uma pessoa só deve acessar dados necessários para sua função e pelo tempo necessário. Dados não devem ser baixados, copiados ou compartilhados fora das ferramentas aprovadas sem justificativa e autorização.

## Dados pessoais e sensíveis
Dados de saúde, biometria, origem racial ou étnica, convicção religiosa, opinião política, filiação sindical, vida sexual e dados de crianças ou dependentes exigem cuidado adicional. Esses dados não devem ser enviados a modelos de IA externos sem base autorizada, anonimização e aprovação formal.

## Uso de IA generativa
É permitido usar IA para rascunhos, resumo de documentos, apoio à análise e melhoria de produtividade quando não houver exposição de dados restritos. Não é permitido inserir dados pessoais identificáveis, segredos comerciais, credenciais, documentos médicos, avaliações individuais, salários individuais ou dados de candidatos em ferramentas não aprovadas.

## RAG interno
Soluções de RAG devem usar fontes aprovadas, controle de acesso, registro de fonte, versionamento de documentos e política de retenção. Respostas devem indicar limitação quando a base não contiver informação suficiente.

## Incidentes
Suspeita de vazamento, acesso indevido, perda de equipamento, phishing, exposição acidental de dados ou resposta de IA contendo informação restrita deve ser reportada imediatamente ao canal de Segurança da Informação.

## Regras para respostas do copiloto de RH
O agente deve negar solicitações que exponham dados pessoais sem autorização, pedir autenticação para consultas individuais e preferir análises agregadas. Para People Analytics, deve aplicar limiar mínimo de grupo e evitar resultados que permitam reidentificação.

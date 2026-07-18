# ADR 0002 — Imagens de infraestrutura reproduzíveis

## Status

Aceita em 18 de julho de 2026.

## Contexto

A referência `quay.io/minio/minio:RELEASE.2025-09-06T17-38-46Z` não existe e impedia a construção da Fase 0.

## Decisão

Usar imagens oficiais com versão fixa e previamente confirmada no registro público. Para o MinIO, usar `minio/minio:RELEASE.2025-09-07T16-13-09Z` nos ambientes de desenvolvimento e produção.

## Consequências

- O Compose deixa de depender de uma tag inexistente.
- Atualizações do MinIO permanecem explícitas e revisáveis.
- Toda atualização deve ser validada nos dois arquivos Compose antes de ser aceita.

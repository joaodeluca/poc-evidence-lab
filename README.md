# POC Evidence Lab

Laboratório aberto e reproduzível de evidências para ensaios de software. Desenvolvido com assistência de agentes de IA.

[Demonstração interativa](https://joaodeluca.github.io/poc-evidence-lab/)

## O que você pode conferir

O mesmo alvo sintético é executado em duas versões: `broken` contém três defeitos deliberados; `fixed` corrige os três. O executor faz requisições HTTP locais reais, preserva as respostas e liga cada resultado às observações usadas. Os defeitos são conhecidos pelo autor: isto não é avaliação cega nem demonstração de detecção em software desconhecido.

1. Exportação mantém os IDs da consulta filtrada.
2. Tentativa de edição por papel de consulta é recusada sem alterar registro.
3. Edição autorizada cria evento com entidade, ação e ator.

## Reproduzir

Python 3.10+ e biblioteca padrão, sem instalação de dependências ou credenciais:

```sh
python3 lab/run.py --output evidence-local.json
```

A aplicação inicia somente em `127.0.0.1`, porta efêmera, e encerra ao final. O executor não aceita URL externa. Não hospede `lab/app.py`: é um alvo deliberadamente vulnerável, com papéis simulados por cabeçalho, sem autenticação de produção. Somente `docs/` contém o relatório estático.

`docs/execution.json` registra a primeira execução publicada. Os hashes identificam bytes locais e facilitam conferir integridade; não provam autoria externa, timestamp confiável ou imutabilidade. Uma execução nova terá horários diferentes, mas deve reproduzir os três resultados de cada versão. O programa não sobrescreve evidência existente.

## Fontes reais e limites

A página traz paráfrases selecionadas de dois procedimentos públicos distintos: [ENAP, documento 2026/196](https://pncp.gov.br/pncp-api/v1/orgaos/00627612000109/compras/2026/196/arquivos/1) e [roteiro histórico SEFAZ/MS de 2023](https://www.sefaz.ms.gov.br/wp-content/uploads/2023/05/Convocacao-e-Roteiro-da-POC.pdf). Eles não são obrigações de um mesmo edital. O benchmark não atesta atendimento integral a qualquer requisito público; CSV, por exemplo, não substitui os formatos exigidos no roteiro SEFAZ.

Não há modelo de IA sendo chamado pelo programa, extração automática integral de edital, software de cliente, dados pessoais de cliente, parecer jurídico, certificação, compra ou contratação. A curadoria dos requisitos foi feita por agentes e pode conter erros de interpretação; consulte as fontes.

## Contribuir

Reproduções e relatos de erro são bem-vindos nas issues. Elas são públicas: não envie dados pessoais, credenciais, documentos privados ou material de clientes. Nenhum depoimento, avaliação humana independente ou resultado comercial é alegado. A demonstração não usa analytics; o GitHub pode registrar acessos à hospedagem.

## Licença

Código e apresentação originais: MIT. Os documentos externos vinculados não são licenciados por este projeto e permanecem sob as condições de suas fontes.

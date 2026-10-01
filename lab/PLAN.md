# Ensaio executável controlado — plano anterior à execução

01/10/2026. Ambiente e dados inteiramente sintéticos, próprios do estudo. Nenhum software de fornecedor ou cliente será testado. Este ensaio testa rastreabilidade e repetição da execução, não precisão de uma IA em software desconhecido.

Três critérios locais fixados antes da execução:

1. Consulta filtrada e CSV devem conter os mesmos IDs, sem registros fora do filtro.
2. Uma tentativa de alteração pelo papel de consulta deve ser rejeitada e preservar o registro.
3. Uma alteração autorizada deve criar evento de auditoria com entidade, ação e ator corretos.

A versão broken contém uma falha deliberada em cada critério; fixed corrige as três. Resultado esperado: três falhas e três sucessos, respectivamente. Incluir um requisito não executável no relatório como não verificado, sem aumentar a cobertura. Publicar todas as falhas e nunca transformar aprovação desses três critérios em conformidade integral com edital, legislação, segurança ou SLA.

O executor inicia e encerra sua própria aplicação em 127.0.0.1 com porta efêmera. Não aceita URL externa. Cabeçalhos de papel são simulação, não implementação de autenticação para produção. Requisições, respostas sintéticas, hashes, versão do app e horário ficam no pacote privado de evidência. Fixar o plano não constitui pré-registro científico externo.

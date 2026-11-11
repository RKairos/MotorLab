# MotorLab — instruções de desenvolvimento

## Ambiente
- Windows, VS Code, Python 3.13 e PyQt6.
- Entrada do aplicativo: app.py.
- Pacote Python: motorLab. Preservar essa capitalização.
- Ambiente virtual: .venv.

## Forma de trabalho
- O usuário quer entender e aplicar as alterações manualmente.
- Não entregar ZIPs nem editar arquivos automaticamente, salvo pedido explícito.
- Trabalhar em incrementos pequenos, com um objetivo por etapa.
- Antes do código, explicar o problema e a solução proposta.
- Identificar cada arquivo como NOVO ou ALTERAR.
- Para alterações, indicar a classe/função e o trecho a localizar.
- Mostrar o código exato a adicionar ou substituir.
- Evitar referências apenas a números de linha, pois eles mudam.
- Explicar como os novos trechos se conectam ao código existente.
- Terminar com comandos de execução e critérios de verificação.
- Distinguir testes executados pelo assistente dos testes pendentes no Windows.
- Não avançar para outra funcionalidade antes do retorno sobre a etapa atual.

## Organização
- Usar o código atual fornecido pelo usuário como referência.
- Se um arquivo necessário estiver desatualizado ou ausente, solicitá-lo.
- Preservar alterações existentes e evitar refatorações não relacionadas.
- Não adicionar dependências sem explicar sua necessidade.
- Separar interface, dados e validação.
- Ao alterar o JSON, explicar compatibilidade e migração.
- Manter README.md e docs/STATUS.md coerentes com a implementação.
- Não incluir .venv, __pycache__ ou arquivos pessoais nos pacotes de código.
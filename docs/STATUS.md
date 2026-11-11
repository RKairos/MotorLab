# Estado do MotorLab

## Ambiente
- Windows / VS Code.
- Python 3.13 e PyQt6.
- Pacote principal: motorLab.
- Formato atual de projeto JSON: versão 2.

## Implementado no código entregue
- Janela com abas Grão, openMotor e Resultados.
- Nome, descrição e referências a arquivos.
- Novo, Abrir, Salvar e Salvar como.
- Aviso de alterações confirmadas não salvas.
- Editor 2D de círculos e polígonos.
- Seleção, movimentação, dimensões e edição de vértices.
- Grade, ajuste à grade, zoom e enquadramento.
- Persistência das formas no JSON.
- Abertura de projetos MotorLab versão 1.

## Validação
- Sete testes automatizados passaram no ambiente Linux do assistente.
- Inspeção visual realizada nesse ambiente.
- Validação desta versão no Windows do usuário: pendente.

## Limitações atuais
- Formas independentes, sem união ou subtração.
- Sem desfazer/refazer e sem rotação.
- Campos precisam ser confirmados em Aplicar propriedades.
- Polígonos precisam ser concluídos antes de salvar.
- openMotor não integrado.
- Sem progressão de queima ou simulação física.

## Próxima etapa
- Validar o editor atual no Windows.
- Registrar problemas observados antes de adicionar funcionalidades.

## Decisões
- Desenvolvimento incremental, explicado arquivo por arquivo.
- Usuário aplica as alterações no VS Code.
- Sem entrega de ZIPs, salvo solicitação.
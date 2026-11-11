# MotorLab — editor geométrico 2D

Aplicativo Python/PyQt6 com três abas. A aba Grão agora contém um editor genérico
2D de círculos e polígonos. Não há progressão de queima, modelos físicos,
exportação para openMotor, operações booleanas ou simulador integrado.
A aba openMotor permanece reservada; Resultados mostra referências a arquivos.

## Atualizar no Windows / VS Code

1. Feche o aplicativo. Guarde uma cópia da sua pasta de código atual.
2. Extraia Software.zip. Copie o conteúdo da pasta Software extraída para sua
   pasta Software existente, substituindo os arquivos correspondentes.
3. Mantenha a sua pasta .venv. Ela não é incluída no pacote.
4. Abra Software no VS Code. app.py e a pasta motorLab devem estar lado a lado.
   O nome motorLab foi preservado exatamente como no código enviado.
5. Ctrl+Shift+P > Python: Select Interpreter > escolha .venv/Scripts/python.exe.
6. No terminal PowerShell, dentro de Software:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Nenhuma dependência adicional foi introduzida. Se ainda não houver ambiente:
`py -3.13 -m venv .venv`. Para F5, use as extensões Microsoft Python e Python
Debugger. A configuração .vscode existente foi mantida.

## Começar a desenhar

- **+ Círculo:** cria um círculo de diâmetro 20 mm na origem. Selecione-o e altere
  X, Y e diâmetro à direita; clique em **Aplicar propriedades** para confirmar.
- **+ Polígono:** ativa o desenho por cliques nos vértices. Pressione Enter ou
  clique em Concluir polígono. O fechamento da última aresta é automático;
  não repita o primeiro ponto no final. Aceita polígonos convexos e côncavos.
- **Backspace:** remove o último ponto durante o desenho. **Esc** ou Cancelar
  desenho abandona os pontos ainda não concluídos.
- **Selecionar:** clique em uma forma ou em seu nome na lista à direita.
- **Mover forma:** arraste com o botão esquerdo ou edite X/Y e clique Aplicar.
- **Largura/altura:** redimensionam o polígono selecionado em torno da sua origem.
  Não há trava de proporção: as duas dimensões são independentes.
- **Editar vértices:** um par X;Y por linha, com ponto decimal, relativo à origem
  da forma. Exemplo: `10.5;-2`. Aplicar confirma; Cancelar mantém a forma anterior.
- **Excluir:** botão Excluir forma selecionada ou Delete com o foco no desenho.
- **Zoom:** roda do mouse. **Mover vista:** botão central pressionado e arraste.
- **Enquadrar:** mostra todas as formas; no desenho vazio, retorna à origem.
- **Grade:** pode ser ocultada. Ajustar à grade arredonda os pontos desenhados e
  as posições ao arrastar, usando o Passo. Os campos numéricos aceitam valores
  precisos independentemente do ajuste. Ao afastar o zoom, algumas linhas da
  grade são ocultadas para legibilidade; a legenda indica a grade visível.

Todos os valores são em mm, com X positivo à direita e Y positivo para cima.
Círculos usam seu centro como origem. Polígonos usam inicialmente o centro da
caixa delimitadora; os vértices são armazenados em relação a essa origem.
As formas são independentes. Sobrepor círculos/polígonos não cria furos, uniões
ou subtrações. Esta versão não tem desfazer/refazer nem rotação.

**Antes de salvar:** conclua o polígono e confirme os campos com Aplicar
propriedades. Pontos em andamento e campos ainda não aplicados são rascunhos
locais da interface e não fazem parte do projeto salvo.

## Projetos e arquivos

- O painel Projeto mantém nome, descrição e arquivos associados.
- Ctrl+S salva, Ctrl+O abre, Ctrl+N cria um projeto vazio.
- O asterisco indica alterações confirmadas ainda não salvas. Novo, Abrir e
  Fechar oferecem Salvar, Descartar e Cancelar quando há essas alterações.
- Arquivos associados guardam apenas caminhos absolutos. Não são copiados,
  interpretados nem apagados ao remover a referência. Atualize as referências
  se mover os arquivos ou trocar de computador.
- Projetos MotorLab versão 1 são abertos automaticamente com geometria vazia.
  Ao salvar, passam à versão 2, que inclui geometry/units/shapes. A versão antiga
  do programa não abre arquivos versão 2; use Salvar como para manter um original.
- O código valida os dados antes de carregar/salvar, rejeita números não finitos,
  polígonos degenerados ou com cruzamentos entre arestas não adjacentes e grava
  via arquivo temporário e substituição atômica.
- Limites do editor: 500 formas, 200 vértices por polígono, coordenadas locais e
  origens entre -1.000.000 e +1.000.000 mm, diâmetro de 0,001 a 1.000.000 mm.
  Os campos da interface exibem três casas decimais.

## Código

| Arquivo | Função |
|---|---|
| app.py | Inicialização |
| motorLab/window.py | Janela, menus e projeto compartilhado |
| motorLab/project.py | JSON, validação e migração v1 → v2 |
| motorLab/geometry.py | Validação das formas planas |
| motorLab/tabs/grain.py | Ferramentas, lista e propriedades |
| motorLab/tabs/canvas.py | Desenho, grade, zoom e interação com mouse |
| motorLab/tabs/openmotor.py | Aba reservada |
| motorLab/tabs/results.py | Lista de referências |
| tests/test_editor.py | Verificações de interface e persistência |

## Verificações

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Sete testes automatizados cobrem criação por mouse/teclado, edição de dimensões,
movimentação, exclusão, persistência, migração v1, cancelamento, JSON inválido e
preservação do arquivo quando os dados são inválidos. Também foi feita inspeção
visual da janela. Verificação realizada com Python 3.12/PyQt6 em Linux, em modo
sem tela; confirmar aparência e diálogos nativos no Windows/Python 3.13.

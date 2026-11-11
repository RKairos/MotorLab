from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget

class ResultsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.heading = QLabel()
        layout.addWidget(self.heading)
        layout.addWidget(QLabel("Arquivos associados (referências; conteúdo ainda não importado):"))
        self.files = QListWidget()
        layout.addWidget(self.files)
        layout.addWidget(QLabel("Gráficos e leitura de resultados serão implementados depois."))

    def refresh(self, project):
        self.heading.setText("Projeto: " + project["name"])
        self.files.clear()
        self.files.addItems(project["files"])

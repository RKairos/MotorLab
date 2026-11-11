from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class OpenMotorTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.heading = QLabel()
        layout.addWidget(self.heading)
        layout.addWidget(QLabel("Espaço reservado. O openMotor não está integrado nesta versão."))
        layout.addStretch()

    def refresh(self, project):
        self.heading.setText("Projeto: " + project["name"])

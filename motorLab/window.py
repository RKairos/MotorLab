from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPlainTextEdit, QListWidget, QPushButton, QHBoxLayout, QDockWidget,
    QTabWidget, QFileDialog, QMessageBox, QLabel)
from .project import new_project, load_project, save_project
from .tabs.grain import GrainTab
from .tabs.openmotor import OpenMotorTab
from .tabs.results import ResultsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1440, 860)
        self.project = new_project()
        self.path = None
        self.dirty = False
        self.loading = False
        tabs = QTabWidget()
        self.pages = [GrainTab(), OpenMotorTab(), ResultsTab()]
        for title, page in zip(("Grão", "openMotor", "Resultados"), self.pages):
            tabs.addTab(page, title)
        self.pages[0].geometryChanged.connect(self.geometry_changed)
        self.setCentralWidget(tabs)
        self.build_project_panel()
        menu = self.menuBar().addMenu("&Arquivo")
        for title, shortcut, callback in (
            ("Novo", QKeySequence.StandardKey.New, self.new),
            ("Abrir…", QKeySequence.StandardKey.Open, self.open),
            ("Salvar", QKeySequence.StandardKey.Save, self.save),
            ("Salvar como…", QKeySequence.StandardKey.SaveAs, self.save_as),
            ("Sair", QKeySequence.StandardKey.Quit, self.close)):
            action = QAction(title, self)
            action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(lambda checked=False, fn=callback: fn())
            menu.addAction(action)
        view = self.menuBar().addMenu("Exibir")
        view.addAction(self.dock.toggleViewAction())
        self.populate()

    def build_project_panel(self):
        self.dock = QDockWidget("Projeto", self)
        content = QWidget()
        layout = QVBoxLayout(content)
        form = QFormLayout()
        self.name = QLineEdit()
        self.description = QPlainTextEdit()
        self.description.setPlaceholderText("Descrição e anotações do projeto")
        form.addRow("Nome", self.name)
        form.addRow("Descrição", self.description)
        layout.addLayout(form)
        layout.addWidget(QLabel("Arquivos associados"))
        self.files = QListWidget()
        layout.addWidget(self.files)
        buttons = QHBoxLayout()
        for title, fn in (("Adicionar…", self.add_files), ("Remover referência", self.remove_file)):
            button = QPushButton(title)
            button.clicked.connect(fn)
            buttons.addWidget(button)
        layout.addLayout(buttons)
        note = QLabel("Os arquivos originais não são copiados nem apagados. As referências usam caminhos absolutos.")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.dock.setWidget(content)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)
        self.name.textChanged.connect(self.edit_metadata)
        self.description.textChanged.connect(self.edit_metadata)

    def populate(self):
        self.loading = True
        self.name.setText(self.project["name"])
        self.description.setPlainText(self.project["description"])
        self.files.clear()
        self.files.addItems(self.project["files"])
        self.loading = False
        self.refresh()

    def refresh(self):
        for page in self.pages:
            page.refresh(self.project)
        marker = " *" if self.dirty else ""
        self.setWindowTitle(f"{self.project['name'] or 'Sem nome'}{marker} — MotorLab")
        location = str(self.path) if self.path else "Projeto ainda não salvo"
        self.statusBar().showMessage(location + (" | Alterações não salvas" if self.dirty else ""))

    def geometry_changed(self):
        self.dirty = True
        self.refresh()

    def edit_metadata(self):
        if self.loading:
            return
        self.project["name"] = self.name.text()
        self.project["description"] = self.description.toPlainText()
        self.dirty = True
        self.refresh()

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Associar arquivos")
        added = [p for p in paths if p not in self.project["files"]]
        if added:
            self.project["files"].extend(added)
            self.dirty = True
            self.populate()

    def remove_file(self):
        index = self.files.currentRow()
        if index >= 0:
            del self.project["files"][index]
            self.dirty = True
            self.populate()

    def may_discard(self):
        if not self.dirty:
            return True
        B = QMessageBox.StandardButton
        answer = QMessageBox(self)
        answer.setWindowTitle("Alterações não salvas")
        answer.setText("Deseja salvar as alterações antes de continuar?")
        answer.setIcon(QMessageBox.Icon.Question)
        answer.setStandardButtons(B.Save | B.Discard | B.Cancel)
        answer.button(B.Save).setText("Salvar")
        answer.button(B.Discard).setText("Descartar")
        answer.button(B.Cancel).setText("Cancelar")
        answer.setDefaultButton(B.Cancel)
        result = answer.exec()
        if result == B.Save:
            return self.save()
        return result == B.Discard

    def new(self):
        if self.may_discard():
            self.project = new_project()
            self.path = None
            self.dirty = False
            self.populate()

    def open(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir projeto", "", "Projeto MotorLab (*.json)")
        if not filename:
            return
        try:
            candidate = load_project(filename)
        except (OSError, ValueError, UnicodeError) as error:
            QMessageBox.warning(self, "Não foi possível abrir", str(error))
            return
        if self.may_discard():
            self.project = candidate
            self.path = Path(filename)
            self.dirty = False
            self.populate()

    def save(self):
        return self.write(self.path) if self.path else self.save_as()

    def save_as(self):
        initial = str(self.path) if self.path else "projeto.motorlab.json"
        filename, _ = QFileDialog.getSaveFileName(self, "Salvar projeto", initial, "Projeto MotorLab (*.json)")
        if not filename:
            return False
        if not filename.lower().endswith(".json"):
            filename += ".json"
            if Path(filename).exists():
                B = QMessageBox.StandardButton
                if QMessageBox.question(self, "Substituir arquivo?", filename, B.Yes | B.No, B.No) != B.Yes:
                    return False
        return self.write(Path(filename))

    def write(self, path):
        try:
            save_project(path, self.project)
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Não foi possível salvar", str(error))
            return False
        self.path = path
        self.dirty = False
        self.refresh()
        return True

    def closeEvent(self, event):
        if self.may_discard():
            event.accept()
        else:
            event.ignore()

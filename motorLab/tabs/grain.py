"""Editor de formas 2D com modelo compartilhado pelo projeto."""
from copy import deepcopy
from uuid import uuid4
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSplitter, QFormLayout, QLineEdit, QDoubleSpinBox, QListWidget, QListWidgetItem,
    QCheckBox, QMessageBox, QDialog, QDialogButtonBox, QPlainTextEdit)
from .canvas import Canvas, ShapeItem
from ..geometry import validate_geometry, validate_points


class GrainTab(QWidget):
    geometryChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.project = None
        self.updating = False
        self.items = {}
        layout = QVBoxLayout(self)
        self.heading = QLabel("Editor geométrico 2D")
        layout.addWidget(self.heading)
        toolbar = QHBoxLayout()
        for title, callback in (("+ Círculo", self.add_circle), ("+ Polígono", self.start_polygon),
                                ("Concluir polígono", self.finish_polygon), ("Cancelar desenho", self.cancel_polygon),
                                ("Enquadrar", self.fit_shapes)):
            button = QPushButton(title)
            button.clicked.connect(callback)
            toolbar.addWidget(button)
        layout.addLayout(toolbar)
        options = QHBoxLayout()
        self.grid = QCheckBox("Grade"); self.grid.setChecked(True)
        self.snap = QCheckBox("Ajustar à grade"); self.snap.setChecked(True)
        self.step = QDoubleSpinBox(); self.step.setRange(.001,10000); self.step.setDecimals(3)
        self.step.setValue(10); self.step.setSuffix(" mm")
        options.addWidget(self.grid); options.addWidget(self.snap)
        options.addWidget(QLabel("Passo:")); options.addWidget(self.step); options.addStretch()
        layout.addLayout(options)
        split = QSplitter()
        self.canvas = Canvas()
        split.addWidget(self.canvas)
        side = QWidget(); panel = QVBoxLayout(side)
        panel.addWidget(QLabel("Formas"))
        self.shape_list = QListWidget(); self.shape_list.setMaximumHeight(190)
        panel.addWidget(self.shape_list)
        self.properties = QWidget(); form = QFormLayout(self.properties)
        self.shape_name = QLineEdit(); form.addRow("Nome", self.shape_name)
        self.x = self.spin(-1000000); self.y = self.spin(-1000000)
        self.diameter = self.spin(.001); self.width = self.spin(.001); self.height = self.spin(.001)
        for title, field in (("X (origem)",self.x),("Y (origem)",self.y),("Diâmetro",self.diameter),
                             ("Largura",self.width),("Altura",self.height)):
            form.addRow(title,field)
        self.apply_button = QPushButton("Aplicar propriedades")
        self.apply_button.clicked.connect(self.apply_properties); form.addRow(self.apply_button)
        self.vertices_button = QPushButton("Editar vértices…")
        self.vertices_button.clicked.connect(self.edit_vertices); form.addRow(self.vertices_button)
        self.delete_button = QPushButton("Excluir forma selecionada")
        self.delete_button.clicked.connect(self.delete_selected); form.addRow(self.delete_button)
        panel.addWidget(self.properties)
        note = QLabel("X/Y posicionam a origem da forma. Nos círculos, é o centro.\n\nLargura e altura redimensionam o polígono em torno da sua origem. Formas sobrepostas permanecem independentes.")
        note.setWordWrap(True); panel.addWidget(note); panel.addStretch()
        split.addWidget(side); split.setStretchFactor(0,1); split.setSizes([650,260])
        layout.addWidget(split,1)
        self.hint = QLabel(); self.hint.setWordWrap(True); layout.addWidget(self.hint)
        self.canvas.hintChanged.connect(self.hint.setText)
        self.canvas.cancel_polygon()
        self.canvas.polygonFinished.connect(self.add_polygon)
        self.canvas.moved.connect(self.commit_positions)
        self.canvas.deleteRequested.connect(self.delete_selected)
        self.canvas.scene().selectionChanged.connect(self.scene_selected)
        self.shape_list.currentItemChanged.connect(self.list_selected)
        self.grid.toggled.connect(self.options_changed)
        self.snap.toggled.connect(self.options_changed)
        self.step.valueChanged.connect(self.options_changed)
        self.properties.setEnabled(False)

    @staticmethod
    def spin(minimum):
        field = QDoubleSpinBox(); field.setDecimals(3); field.setRange(minimum,1000000)
        field.setSuffix(" mm"); field.setKeyboardTracking(False)
        return field

    def options_changed(self, *_):
        self.canvas.show_grid = self.grid.isChecked()
        self.canvas.snap = self.snap.isChecked()
        self.canvas.grid_step = self.step.value()
        self.canvas.viewport().update()

    def refresh(self, project):
        self.heading.setText("Editor geométrico 2D  •  " + project["name"])
        if self.project is not project:
            self.project = project
            self.canvas.cancel_polygon()
            self.rebuild()
            self.canvas.fit_shapes()

    def shapes(self):
        return self.project["geometry"]["shapes"] if self.project else []

    def selected(self):
        selected = self.canvas.scene().selectedItems()
        if not selected:
            return None
        identifier = selected[0].record_id
        return next((s for s in self.shapes() if s["id"] == identifier), None)

    def rebuild(self, select_id=None):
        self.updating = True
        self.canvas.cancel_polygon()
        self.canvas.scene().clear()
        self.items.clear(); self.shape_list.clear()
        for s in self.shapes():
            item = ShapeItem(s); self.canvas.scene().addItem(item); self.items[s["id"]] = item
            row = QListWidgetItem(s["name"] or "Sem nome")
            row.setData(Qt.ItemDataRole.UserRole,s["id"]); self.shape_list.addItem(row)
            if s["id"] == select_id:
                item.setSelected(True); self.shape_list.setCurrentItem(row)
        self.updating = False
        self.update_properties()

    def scene_selected(self):
        if self.updating:
            return
        self.updating = True
        record = self.selected()
        self.shape_list.setCurrentRow(-1)
        if record:
            for i in range(self.shape_list.count()):
                if self.shape_list.item(i).data(Qt.ItemDataRole.UserRole) == record["id"]:
                    self.shape_list.setCurrentRow(i); break
        self.updating = False
        self.update_properties()

    def list_selected(self, current, previous):
        if self.updating:
            return
        self.updating = True
        self.canvas.scene().clearSelection()
        if current:
            self.items[current.data(Qt.ItemDataRole.UserRole)].setSelected(True)
        self.updating = False
        self.update_properties()

    def update_properties(self):
        record = self.selected()
        self.properties.setEnabled(record is not None)
        if not record:
            self.shape_name.clear(); return
        self.shape_name.setText(record["name"])
        self.x.setValue(record["x"]); self.y.setValue(record["y"])
        circle = record["type"] == "circle"
        self.diameter.setEnabled(circle); self.width.setEnabled(not circle); self.height.setEnabled(not circle)
        self.vertices_button.setEnabled(not circle)
        if circle:
            d = record["radius"]*2
            self.diameter.setValue(d); self.width.setValue(d); self.height.setValue(d)
        else:
            xs, ys = zip(*record["points"])
            self.width.setValue(max(xs)-min(xs)); self.height.setValue(max(ys)-min(ys))
            self.diameter.setValue(.001)

    def store_shapes(self, shapes, selected=None):
        geometry = {"units":"mm", "shapes":shapes}
        try:
            geometry = validate_geometry(geometry)
        except ValueError as error:
            QMessageBox.warning(self,"Geometria inválida",str(error)); return False
        self.project["geometry"] = geometry
        self.rebuild(selected)
        self.geometryChanged.emit()
        return True

    def add_circle(self):
        if self.project is None:
            return
        self.canvas.cancel_polygon()
        record = {"id":uuid4().hex,"name":f"Círculo {len(self.shapes())+1}","type":"circle",
                  "x":0.0,"y":0.0,"radius":10.0}
        if self.store_shapes(self.shapes()+[record],record["id"]):
            self.canvas.fit_shapes()

    def start_polygon(self):
        self.canvas.start_polygon()

    def finish_polygon(self):
        if self.canvas.drawing:
            self.canvas.finish_polygon()

    def cancel_polygon(self):
        self.canvas.cancel_polygon()

    def fit_shapes(self):
        self.canvas.fit_shapes()

    def add_polygon(self, points):
        try:
            validate_points(points)
        except ValueError as error:
            QMessageBox.warning(self,"Polígono inválido",str(error)); return
        # A origem local é o centro da caixa delimitadora inicial.
        xs, ys = zip(*points)
        cx, cy = (min(xs)+max(xs))/2,(min(ys)+max(ys))/2
        record = {"id":uuid4().hex,"name":f"Polígono {len(self.shapes())+1}","type":"polygon",
                  "x":cx,"y":cy,"points":[[x-cx,y-cy] for x,y in points]}
        self.store_shapes(self.shapes()+[record],record["id"])

    def apply_properties(self):
        original = self.selected()
        if original is None:
            return
        candidate = deepcopy(original)
        candidate.update(name=self.shape_name.text(),x=self.x.value(),y=self.y.value())
        if candidate["type"] == "circle":
            candidate["radius"] = self.diameter.value()/2
        else:
            xs,ys = zip(*candidate["points"])
            sx = self.width.value()/(max(xs)-min(xs)); sy = self.height.value()/(max(ys)-min(ys))
            candidate["points"] = [[x*sx,y*sy] for x,y in candidate["points"]]
        if candidate != original:
            self.store_shapes([candidate if s["id"]==original["id"] else s for s in self.shapes()],candidate["id"])

    def commit_positions(self):
        changed = False
        for record in self.shapes():
            item = self.items[record["id"]]
            x,y = item.pos().x(), -item.pos().y()
            if abs(x-record["x"]) < 1e-9 and abs(y-record["y"]) < 1e-9:
                continue
            if self.canvas.snap:
                step = self.canvas.grid_step
                x,y = round(x/step)*step,round(y/step)*step
            x,y = max(-1000000,min(1000000,x)),max(-1000000,min(1000000,y))
            item.setPos(x,-y)
            if (x,y) != (record["x"],record["y"]):
                record["x"],record["y"] = x,y; changed = True
        if changed:
            self.update_properties()
            self.geometryChanged.emit()

    def delete_selected(self):
        record = self.selected()
        if record:
            self.store_shapes([s for s in self.shapes() if s["id"] != record["id"]])

    def edit_vertices(self):
        record = self.selected()
        if not record or record["type"] != "polygon":
            return
        dialog = QDialog(self); dialog.setWindowTitle("Vértices locais — mm")
        dialog.resize(420,420)
        layout = QVBoxLayout(dialog)
        label = QLabel("Um vértice por linha: X;Y. Use ponto decimal.\nCoordenadas relativas à origem X/Y da forma.\nNão repita o primeiro vértice no final.")
        label.setWordWrap(True); layout.addWidget(label)
        editor = QPlainTextEdit("\n".join(f"{x:.12g};{y:.12g}" for x,y in record["points"]))
        layout.addWidget(editor)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Aplicar")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        def accept():
            try:
                points = [[float(v.strip()) for v in line.split(';')] for line in editor.toPlainText().splitlines() if line.strip()]
                validate_points(points)
            except (ValueError,OverflowError) as error:
                QMessageBox.warning(dialog,"Vértices inválidos",str(error)); return
            candidate = deepcopy(record); candidate["points"] = points
            if self.store_shapes([candidate if s["id"]==record["id"] else s for s in self.shapes()],record["id"]):
                dialog.accept()
        buttons.accepted.connect(accept); buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons); dialog.exec()

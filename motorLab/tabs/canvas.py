"""Tela de desenho: coordenadas do modelo em mm, Y positivo para cima."""
import math
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QBrush
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem


class ShapeItem(QGraphicsPathItem):
    def __init__(self, record):
        path = QPainterPath()
        if record["type"] == "circle":
            r = record["radius"]
            path.addEllipse(QPointF(0, 0), r, r)
        else:
            pts = record["points"]
            path.moveTo(pts[0][0], -pts[0][1])
            for x, y in pts[1:]:
                path.lineTo(x, -y)
            path.closeSubpath()
        super().__init__(path)
        self.record_id = record["id"]
        self.setPos(record["x"], -record["y"])
        self.setFlags(self.GraphicsItemFlag.ItemIsSelectable | self.GraphicsItemFlag.ItemIsMovable)
        pen = QPen(QColor("#42b8cc"), 2)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setBrush(QBrush(QColor(66, 184, 204, 35)))


class Canvas(QGraphicsView):
    polygonFinished = pyqtSignal(list)
    moved = pyqtSignal()
    deleteRequested = pyqtSignal()
    hintChanged = pyqtSignal(str)

    def __init__(self):
        super().__init__(QGraphicsScene())
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setSceneRect(-2000000, -2000000, 4000000, 4000000)
        self.setBackgroundBrush(QColor("#17212b"))
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(self.ViewportAnchor.AnchorViewCenter)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.scale(4, 4)
        self.centerOn(0, 0)
        self.drawing = False
        self.points = []
        self.cursor_point = None
        self.pan_start = None
        self.grid_step = 10
        self.show_grid = True
        self.snap = True
        self.preview = None

    def point(self, position):
        p = self.mapToScene(position)
        x, y = p.x(), -p.y()
        if self.snap:
            x = round(x/self.grid_step)*self.grid_step
            y = round(y/self.grid_step)*self.grid_step
        return [max(-1000000,min(1000000,x)), max(-1000000,min(1000000,y))]

    def start_polygon(self):
        self.cancel_polygon()
        self.scene().clearSelection()
        self.drawing = True
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setFocus()
        self.hintChanged.emit("Polígono: clique nos vértices • Enter conclui • Backspace desfaz ponto • Esc cancela")

    def cancel_polygon(self):
        if self.preview is not None:
            self.scene().removeItem(self.preview)
            self.preview = None
        self.points = []
        self.cursor_point = None
        self.drawing = False
        self.unsetCursor()
        self.viewport().update()
        self.hintChanged.emit("Roda: zoom • botão central: mover vista • arraste uma forma para movê-la • unidades: mm")

    def finish_polygon(self):
        if len(self.points) < 3:
            self.hintChanged.emit("Adicione pelo menos três vértices antes de concluir.")
            return
        points = [p[:] for p in self.points]
        self.polygonFinished.emit(points)

    def update_preview(self):
        if self.preview is not None:
            self.scene().removeItem(self.preview)
        path = QPainterPath()
        if self.points:
            path.moveTo(self.points[0][0], -self.points[0][1])
            for x, y in self.points[1:]:
                path.lineTo(x, -y)
            if self.cursor_point:
                path.lineTo(self.cursor_point[0], -self.cursor_point[1])
        pen = QPen(QColor("#ffcc66"), 2, Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        self.preview = self.scene().addPath(path, pen)
        self.preview.setZValue(1000)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.pan_start = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if self.drawing and event.button() == Qt.MouseButton.LeftButton:
            p = self.point(event.position().toPoint())
            if not self.points or p != self.points[-1]:
                if len(self.points) < 200:
                    self.points.append(p)
                    self.update_preview()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pan_start is not None:
            current = event.position().toPoint()
            delta = current-self.pan_start
            self.pan_start = current
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()-delta.y())
            event.accept()
            return
        if self.drawing:
            self.cursor_point = self.point(event.position().toPoint())
            self.update_preview()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.pan_start = None
            self.setCursor(Qt.CursorShape.CrossCursor if self.drawing else Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)
        if not self.drawing and event.button() == Qt.MouseButton.LeftButton:
            self.moved.emit()

    def keyPressEvent(self, event):
        if self.drawing:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.finish_polygon(); return
            if event.key() == Qt.Key.Key_Escape:
                self.cancel_polygon(); return
            if event.key() == Qt.Key.Key_Backspace:
                if self.points:
                    self.points.pop()
                    self.update_preview()
                return
        elif event.key() == Qt.Key.Key_Delete:
            self.deleteRequested.emit(); return
        super().keyPressEvent(event)

    def wheelEvent(self, event):
        if not event.angleDelta().y():
            return
        factor = 1.2 if event.angleDelta().y() > 0 else 1/1.2
        scale = self.transform().m11()
        target = max(.00005, min(500, scale*factor))
        self.scale(target/scale, target/scale)
        event.accept()

    def fit_shapes(self):
        items = [i for i in self.scene().items() if isinstance(i, ShapeItem)]
        if not items:
            self.resetTransform(); self.scale(4,4); self.centerOn(0,0)
            return
        bounds = items[0].sceneBoundingRect()
        for item in items[1:]:
            bounds = bounds.united(item.sceneBoundingRect())
        margin = max(bounds.width(), bounds.height(), 10)*.15
        self.fitInView(bounds.adjusted(-margin,-margin,margin,margin), Qt.AspectRatioMode.KeepAspectRatio)
        scale = self.transform().m11()
        target = max(.00005, min(500, scale))
        self.scale(target/scale, target/scale)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        step = self.grid_step
        while step*self.transform().m11() < 16:
            step *= 10
        if self.show_grid:
            pen = QPen(QColor("#293845"), 0)
            painter.setPen(pen)
            x = math.floor(rect.left()/step)*step
            while x <= rect.right():
                painter.drawLine(QPointF(x,rect.top()),QPointF(x,rect.bottom())); x += step
            y = math.floor(rect.top()/step)*step
            while y <= rect.bottom():
                painter.drawLine(QPointF(rect.left(),y),QPointF(rect.right(),y)); y += step
        painter.setPen(QPen(QColor("#647787"), 0))
        painter.drawLine(QPointF(rect.left(),0),QPointF(rect.right(),0))
        painter.drawLine(QPointF(0,rect.top()),QPointF(0,rect.bottom()))
        # Legenda em pixels, independente do zoom do desenho.
        painter.save(); painter.resetTransform()
        painter.setPen(QColor("#b7c9d8"))
        painter.drawText(12,22,f"X →   Y ↑   |   grade visível: {step:g} mm" if self.show_grid else "X →   Y ↑   |   mm")
        painter.restore()

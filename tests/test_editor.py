"""Execute: python -m unittest discover -s tests -v"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from motorLab.project import new_project, load_project, save_project
from motorLab.geometry import validate_geometry, validate_points
from motorLab.window import MainWindow

APP = QApplication.instance() or QApplication([])


class ProjectTests(unittest.TestCase):
    def test_round_trip_and_v1_migration(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'project.json'
            old = {k:v for k,v in new_project().items() if k != 'geometry'}
            old['version'] = 1
            p.write_text(json.dumps(old),encoding='utf-8')
            current = load_project(p)
            self.assertEqual(current['version'],2)
            self.assertEqual(current['geometry']['shapes'],[])
            current['geometry']['shapes'].append({'id':'1','name':'Teste','type':'circle','x':2,'y':3,'radius':4})
            save_project(p,current)
            self.assertEqual(load_project(p),current)

    def test_invalid_geometry_preserves_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'project.json'
            save_project(p,new_project()); before = p.read_bytes()
            data = new_project()
            data['geometry']['shapes'] = [{'id':'a','name':'x','type':'circle','x':0,'y':0,'radius':float('nan')}]
            with self.assertRaises(ValueError): save_project(p,data)
            self.assertEqual(before,p.read_bytes())

    def test_bad_polygons(self):
        for pts in ([[0,0],[1,1],[0,1],[1,0]], [[0,0],[1,0],[2,0]], [[0,0],[0,0],[1,1]]):
            with self.assertRaises(ValueError): validate_points(pts)
        validate_points([[0,0],[20,0],[20,20],[10,10],[0,20]])


class EditorTests(unittest.TestCase):
    def setUp(self):
        self.w = MainWindow(); self.w.show(); APP.processEvents()
        self.g = self.w.pages[0]

    def tearDown(self):
        self.w.dirty = False; self.w.close(); APP.processEvents()

    def test_circle_properties_move_and_delete(self):
        g = self.g
        g.add_circle()
        self.assertTrue(self.w.dirty)
        g.x.setValue(25); g.y.setValue(30); g.diameter.setValue(42)
        g.apply_properties()
        record = g.selected()
        self.assertEqual((record['x'],record['y'],record['radius']),(25,30,21))
        self.w.dirty = False
        g.items[record['id']].setPos(43,-54)
        g.commit_positions()
        self.assertEqual((record['x'],record['y']),(40,50))
        self.assertTrue(self.w.dirty)
        g.delete_selected()
        self.assertEqual(g.shapes(),[])

    def test_polygon_mouse_keyboard_dimensions(self):
        g = self.g; canvas = g.canvas
        g.start_polygon()
        for x,y in [(-30,-20),(30,-20),(30,20),(-30,20)]:
            QTest.mouseClick(canvas.viewport(),Qt.MouseButton.LeftButton,pos=canvas.mapFromScene(QPointF(x,-y)))
        QTest.keyClick(canvas,Qt.Key.Key_Return)
        self.assertEqual(len(g.shapes()),1)
        self.assertFalse(canvas.drawing)
        g.width.setValue(120); g.height.setValue(80); g.apply_properties()
        xs,ys = zip(*g.shapes()[0]['points'])
        self.assertAlmostEqual(max(xs)-min(xs),120)
        self.assertAlmostEqual(max(ys)-min(ys),80)
        g.start_polygon()
        QTest.mouseClick(canvas.viewport(),Qt.MouseButton.LeftButton,pos=canvas.mapFromScene(QPointF(0,0)))
        QTest.keyClick(canvas,Qt.Key.Key_Escape)
        self.assertFalse(canvas.drawing)
        self.assertEqual(len(g.shapes()),1)

    def test_save_open_and_cancel(self):
        w,g = self.w,self.g
        g.add_circle(); g.add_polygon([[0,0],[30,0],[0,30]])
        expected = deepcopy(w.project)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'roundtrip.json'
            with patch.object(QFileDialog,'getSaveFileName',return_value=(str(path),'')):
                self.assertTrue(w.save())
            self.assertFalse(w.dirty)
            w.new(); self.assertEqual(len(g.shapes()),0)
            with patch.object(QFileDialog,'getOpenFileName',return_value=(str(path),'')):
                w.open()
            self.assertEqual(w.project,expected)
            self.assertEqual(len(g.items),2)
            g.add_circle()
            with patch.object(QMessageBox,'exec',return_value=QMessageBox.StandardButton.Cancel):
                w.new(); self.assertEqual(len(g.shapes()),3)
                self.assertFalse(w.close())
            path.write_text('{broken')
            with patch.object(QFileDialog,'getOpenFileName',return_value=(str(path),'')), patch.object(QMessageBox,'warning'):
                w.open()
            self.assertEqual(len(g.shapes()),3)

    def test_metadata_does_not_reset_selection(self):
        self.g.add_circle(); identifier = self.g.selected()['id']
        self.w.name.setText('Renomeado')
        self.assertEqual(self.g.selected()['id'],identifier)
        self.assertIn('Renomeado',self.g.heading.text())

if __name__ == '__main__':
    unittest.main()

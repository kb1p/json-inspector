# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 19:58:07 2020

@author: kb1p
"""

import sys
import PyQt5.QtCore as Core
import PyQt5.QtWidgets as Gui
import data_models
import json

class MainWindow(Gui.QMainWindow):
    __slots__ = "tvStructure", "tblProps", "mdlStructure", "mdlProps", "currentFile", "config", \
                "splitter"

    def __init__(self, p = None):
        Gui.QMainWindow.__init__(self, parent = p)

        # Work area
        self.tvStructure = Gui.QTreeView(self)
        self.tvStructure.setHeaderHidden(True)
        self.tblProps = Gui.QTableView(self)

        self.splitter = Gui.QSplitter(self)
        self.splitter.addWidget(self.tvStructure)
        self.splitter.addWidget(self.tblProps)
        self.setCentralWidget(self.splitter)

        # Menu
        mnuBar = Gui.QMenuBar(self)
        mnuFile = Gui.QMenu("File", self)
        actOpen = Gui.QAction("Open", self)
        #actSave = Gui.QAction("Save", self)
        actSaveAs = Gui.QAction("Save as...", self)
        actExit = Gui.QAction("Exit", self)
        mnuFile.addAction(actOpen)
        mnuFile.addAction(actSaveAs)
        mnuFile.addSeparator()
        mnuFile.addAction(actExit)
        mnuBar.addMenu(mnuFile)
        self.setMenuBar(mnuBar)

        actOpen.triggered.connect(self.openScene)
        actSaveAs.triggered.connect(self.saveSceneAs)
        actExit.triggered.connect(self.close)

        self.mdlStructure = data_models.JSONTreeModel(self)
        self.tvStructure.setModel(self.mdlStructure)
        self.mdlProps = data_models.JSONPropertiesModel(self)
        self.tblProps.setModel(self.mdlProps)

        self.tvStructure.pressed.connect(self.showElement)
        self.tvStructure.activated.connect(self.showElement)

        self.setCurrentFile(None)
        self.statusBar().showMessage("No selection")
        self.resize(500, 450)

        self.config = Core.QSettings("kb1p", "json-inspector")
        k = self.config.value("main/geometry")
        if k != None:
            self.restoreGeometry(k)
        k = self.config.value("main/state")
        if k != None:
            self.restoreState(k)
        k = self.config.value("splitter/state")
        if k != None:
            self.splitter.restoreState(k)

    def showElement(self, index):
        self.mdlProps.displayElement(index)
        idList = []
        e = self.mdlProps.selection
        while e != None:
            idList.append(e.id)
            e = e.parent
        idList.reverse()
        self.statusBar().showMessage(" / ".join(idList))

    def setCurrentFile(self, fn):
        self.currentFile = fn
        t = self.currentFile if self.currentFile != None else "<no data>"
        self.window().setWindowTitle("JSON inspector: %s" % t)

    def openScene(self):
        fn, _ = Gui.QFileDialog.getOpenFileName(self, "Select input file", filter = "JSON files (*.json *.gltf)")
        if len(fn) > 0:
            with open(fn, "r") as fin:
                d = json.load(fin)
                self.mdlStructure.loadData(d)
                self.mdlProps.displayElement(None)
                self.setCurrentFile(fn)

    def saveSceneAs(self):
        if self.currentFile == None:
            Gui.QMessageBox.warning(self, "Warning", "No data was loaded - nothing to save")
            return
        fn, _ = Gui.QFileDialog.getSaveFileName(self, "Select output file", filter = "JSON files (*.json *.gltf)")
        if len(fn) > 0:
            with open(fn, "w") as fout:
                d = self.mdlStructure.getData()
                json.dump(d, fout, indent = 4, separators = (",", ": "), sort_keys = True)
                self.setCurrentFile(fn)

    def closeEvent(self, evt):
        self.config.setValue("main/geometry", self.saveGeometry())
        self.config.setValue("main/state", self.saveState())
        self.config.setValue("splitter/state", self.splitter.saveState())
        Gui.QMainWindow.closeEvent(self, evt)

def main(args):
    app = Gui.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main(sys.argv))


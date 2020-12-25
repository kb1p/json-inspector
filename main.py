# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 19:58:07 2020

@author: kb1p
"""

import sys
import PyQt5.QtCore as Core
import PyQt5.QtWidgets as Gui
import PyQt5.QtGui as GuiMisc
import data_models
import dialogs
import json

class MainWindow(Gui.QMainWindow):
    __slots__ = "tvStructure", "tblProps", "mdlStructure", "mdlProps", "currentFile", "config", \
                "splitter", "editorDlg"

    def __init__(self, p = None):
        Gui.QMainWindow.__init__(self, parent = p)

        # Work area
        self.tvStructure = Gui.QTreeView(self)
        self.tvStructure.setHeaderHidden(True)
        self.tvStructure.setSelectionMode(Gui.QAbstractItemView.SingleSelection)
        self.tblProps = Gui.QTableView(self)

        self.splitter = Gui.QSplitter(self)
        self.splitter.addWidget(self.tvStructure)
        self.splitter.addWidget(self.tblProps)
        self.setCentralWidget(self.splitter)

        # Menu
        mnuBar = Gui.QMenuBar(self)
        mnuFile = mnuBar.addMenu("File")
        mnuFile.addAction("Open", self.openScene, GuiMisc.QKeySequence("Ctrl+O"))
        mnuFile.addAction("Save as...", self.saveSceneAs, GuiMisc.QKeySequence("Ctrl+S"))
        mnuFile.addSeparator()
        mnuFile.addAction("Exit", self.close)
        mnuElem = mnuBar.addMenu("Element")
        # mnuElem.addAction("Add sub-element", self.addElement, GuiMisc.QKeySequence("Ctrl+A"))
        mnuElem.addAction("Edit JSON code", self.editElement, GuiMisc.QKeySequence("Ctrl+E"))
        mnuElem.addAction("Remove", self.removeElement, GuiMisc.QKeySequence("Ctrl+R"))
        self.setMenuBar(mnuBar)

        self.mdlStructure = data_models.JSONTreeModel(self)
        self.tvStructure.setModel(self.mdlStructure)
        self.mdlProps = data_models.JSONPropertiesModel(self)
        self.tblProps.setModel(self.mdlProps)

        self.tvStructure.selectionModel().currentChanged.connect(self.showElement)

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

        self.editorDlg = dialogs.EditorDialog(self, self.config)

    def showElement(self, index, prevIndex):
        self.mdlProps.displayElement(index)
        assert self.mdlProps.selection != None
        self.statusBar().showMessage(self.mdlProps.selection.fullPath())

    def editElement(self):
        idx = self.tvStructure.selectionModel().currentIndex()
        try:
            if not idx.isValid():
                raise RuntimeError("Element is not selected")

            elm = idx.internalPointer()
            jsIn = data_models.serializeTree(elm)
            strIn = json.dumps(jsIn, indent = 4, separators = (",", ": "), sort_keys = True)
            strOut = self.editorDlg.requestText(elm.fullPath(), strIn)
            if strOut != strIn:
                jsOut = json.loads(strOut)
                self.mdlStructure.layoutAboutToBeChanged.emit()
                data_models.rebuildTree(jsOut, elm)
                self.mdlStructure.layoutChanged.emit()
                self.mdlProps.displayElement(idx)
        except json.JSONDecodeError as err:
            line = err.doc.splitlines()[err.lineno - 1]
            Gui.QMessageBox.critical(self, \
                                     "JSON syntax error", \
                                     "Illegal JSON syntax: %s.\nMalformed line:\n%s" % \
                                     (err.msg, line))
        except RuntimeError as err:
            Gui.QMessageBox.critical(self, "Error", str(err))

    def removeElement(self):
        idx = self.tvStructure.selectionModel().currentIndex()
        try:
            if not idx.isValid():
                raise RuntimeError("Illegal element selected")
            if not idx.parent().isValid():
                raise RuntimeError("Cannot remove root element")
            name = str(idx.data())
            if Gui.QMessageBox.question(self, \
                                        "Confirmation required", \
                                        "Are you sure want to remove element %s?" % name) == Gui.QMessageBox.Yes:
                parIdx = idx.parent()
                self.mdlStructure.removeRow(idx.row(), parIdx)
                self.tvStructure.selectionModel().setCurrentIndex(parIdx, Core.QItemSelectionModel.Current)
        except RuntimeError as err:
            Gui.QMessageBox.critical(self, "Error", str(err))

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


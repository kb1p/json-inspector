# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 11:49:02 2020

@author: kb1p
"""

import PyQt5.QtCore as Core
import PyQt5.QtWidgets as Gui
import PyQt5.QtGui as GuiMisc
import data_models

def queryType(par):
    dlg = Gui.QDialog(par)
    dlg.setWindowTitle("Select type")
    lyt = Gui.QVBoxLayout()
    lyt.addWidget(Gui.QLabel("Choose a node type to create", dlg))
    rbObj = Gui.QRadioButton("Object", dlg)
    rbArr = Gui.QRadioButton("Array", dlg)
    rbVal = Gui.QRadioButton("Value", dlg)
    rbVal.setChecked(True)
    lyt.addWidget(rbObj)
    lyt.addWidget(rbArr)
    lyt.addWidget(rbVal)
    bbox = Gui.QDialogButtonBox(Gui.QDialogButtonBox.Ok | Gui.QDialogButtonBox.Cancel, dlg)
    bbox.accepted.connect(dlg.accept)
    bbox.rejected.connect(dlg.reject)
    lyt.addWidget(bbox)
    dlg.setLayout(lyt)
    resTy = None
    if dlg.exec() == Gui.QDialog.Accepted:
        m = (rbObj, data_models.TreeElement.ObjectType), \
            (rbArr, data_models.TreeElement.ArrayType), \
            (rbVal, data_models.TreeElement.ValueType)
        for s, t in m:
            if s.isChecked():
                resTy = t
                break
    return resTy

class EditorDialog(Gui.QDialog):
    __slots__ = "config", "editor", "elementName"

    def __init__(self, par, cfg):
        Gui.QDialog.__init__(self, par)
        self.config = cfg

        self.setWindowTitle("JSON editor")
        lyt = Gui.QVBoxLayout()
        lyt.addWidget(Gui.QLabel("Enter JSON code for the element:", self))
        self.elementName = Gui.QLabel("---")
        self.elementName.setWordWrap(True)
        self.editor = Gui.QTextEdit(self)
        self.editor.setAcceptRichText(False)
        self.editor.setLineWrapMode(Gui.QTextEdit.NoWrap)
        fnt = GuiMisc.QFontDatabase.systemFont(GuiMisc.QFontDatabase.FixedFont)
        self.editor.setFont(fnt)
        lyt.addWidget(self.elementName)
        lyt.addWidget(self.editor)
        bbox = Gui.QDialogButtonBox(Gui.QDialogButtonBox.Ok | Gui.QDialogButtonBox.Cancel, self)
        bbox.accepted.connect(self.accept)
        bbox.rejected.connect(self.reject)
        lyt.addWidget(bbox)
        self.setLayout(lyt)

    def requestText(self, elmNm, initText = None, readOnly = False):
        self.elementName.setText(elmNm)
        if initText != None:
            self.editor.setPlainText(initText)
        self.editor.setReadOnly(readOnly)
        resText = initText
        k = self.config.value("editor/geometry")
        if k != None:
            self.restoreGeometry(k)
        if self.exec() == Gui.QDialog.Accepted:
            resText = self.editor.toPlainText()
        self.config.setValue("editor/geometry", self.saveGeometry())
        return resText

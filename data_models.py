# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 11:39:50 2020

@author: kb1p
"""

# TODO: table -> tree selection

import PyQt5.QtCore as Core
import itertools
import re
import sys

VER3 = sys.version_info.major >= 3

class TreeElement(object):
    ValueType = 0
    ArrayType = 1
    ObjectType = 2
    __slots__ = "type", "id", "parent", "value", "children"

    def __init__(self, id, parent):
        self.id = id
        self.type = None
        self.children = []
        self.parent = parent
        self.value = None

    def __str__(self):
        if self.type == TreeElement.ValueType:
            return str(self.value)
        elif self.type == TreeElement.ArrayType:
            return "[ " + (", ".join(map(str, self.children)) if len(self.children) < 4 else "...") + " ]"
        else:
            assert self.type == TreeElement.ObjectType
            return "{ ... }"

def buildTree(jsobj, id, par = None):
    n = TreeElement(id, par)
    if isinstance(jsobj, dict):
        n.type = TreeElement.ObjectType
        n.children = [buildTree(v, k, n) for k, v in jsobj.items()]
    elif isinstance(jsobj, list):
        n.type = TreeElement.ArrayType
        n.children = [buildTree(v, "%s[%d]" % (id, k), n) for k, v in zip(itertools.count(), jsobj)]
    else:
        n.type = TreeElement.ValueType
        n.value = jsobj
    return n

def serializeTree(node):
    if node.type == TreeElement.ArrayType:
        return [serializeTree(subNode) for subNode in node.children]
    elif node.type == TreeElement.ObjectType:
        return dict((sn.id, serializeTree(sn)) for sn in node.children)
    else:
        return node.value

class JSONTreeModel(Core.QAbstractItemModel):
    __slots__ = "dataRoot"

    def __init__(self, par):
        Core.QAbstractItemModel.__init__(self, par)
        self.dataRoot = None

    def index(self, row, col, pmi):
        re = None
        if not pmi.isValid():
            re = self.dataRoot
        else:
            elm = pmi.internalPointer()
            assert elm.type != TreeElement.ValueType
            assert row < len(elm.children)
            re = elm.children[row]

        i = self.createIndex(row, col, re)
        return i

    def parent(self, mi):
        idx = Core.QModelIndex()
        if mi.isValid():
            e = mi.internalPointer()
            if e.parent != None:
                idx = self.createIndex(mi.row(), 0, e.parent)
        return idx

    def rowCount(self, pmi):
        if self.dataRoot == None:
            return 0
        if pmi.isValid():
            e = pmi.internalPointer()
            return len(e.children)
        else:
            return 1

    def columnCount(self, pmi):
        if self.dataRoot == None:
            return 0
        return 1

    def data(self, mi, role):
        if not mi.isValid() or role != Core.Qt.DisplayRole:
            return Core.QVariant()

        e = mi.internalPointer()
        v = None
        if e.type == TreeElement.ValueType or e.type == TreeElement.ObjectType:
            v = str(e.id)
        else:
            v = "%s (%d)" % (e.id, len(e.children))

        return Core.QVariant(v)

    def loadData(self, jsonData):
        self.dataRoot = buildTree(jsonData, "Model")
        self.modelReset.emit()

    def getData(self):
        return serializeTree(self.dataRoot)

# How to treat user input
STRING_AFFINITY = ((re.compile(r"True|true"), lambda s: True),
                   (re.compile(r"False|false"), lambda s: False),
                   (re.compile(r"None|null"), lambda s: None),
                   (re.compile(r"^-?\d+[.eE]\d+$"), float),
                   (re.compile(r"^-?\d+$"), int))

class JSONPropertiesModel(Core.QAbstractTableModel):
    __slots__ = "selection"

    def __init__(self, par):
        Core.QAbstractTableModel.__init__(self, par)
        self.selection = None

    def headerData(self, section, ornt, role):
        if ornt != Core.Qt.Horizontal or role != Core.Qt.DisplayRole or self.selection == None:
            return Core.QVariant()
        v = "Value"
        if section == 0:
            if self.selection.type == TreeElement.ArrayType:
                v = "Element #"
            elif self.selection.type == TreeElement.ObjectType:
                v = "Property"
        return Core.QVariant(v)

    def rowCount(self, pmi):
        if self.selection != None and not pmi.isValid():
            return 1 if self.selection.type == TreeElement.ValueType else len(self.selection.children)
        return 0

    def columnCount(self, pmi):
        if self.selection != None:
            return 1 if self.selection.type == TreeElement.ValueType else 2
        return 0

    def flags(self, mi):
        f = Core.QAbstractTableModel.flags(self, mi)
        if (mi.column() == 0 and self.selection.type == TreeElement.ValueType) or \
           (mi.column() == 1 and self.selection.children[mi.row()].type == TreeElement.ValueType):
            f |= Core.Qt.ItemIsEditable
        return f

    def data(self, mi, role):
        if role != Core.Qt.DisplayRole and role != Core.Qt.EditRole:
            return Core.QVariant()
        v = "???"
        if mi.column() == 0:
            if self.selection.type == TreeElement.ObjectType:
                v = self.selection.children[mi.row()].id
            elif self.selection.type == TreeElement.ArrayType:
                v = str(mi.row())
            else:
                v = str(self.selection.value)
        else:
            v = str(self.selection.children[mi.row()])
        return Core.QVariant(v)

    def setData(self, mi, val, role):
        changed = False
        if role == Core.Qt.EditRole:
            # additional parsing for strings
            if isinstance(val, str if VER3 else unicode):
                for r, t in STRING_AFFINITY:
                    if r.match(val) != None:
                        val = t(val)
                        break
            if mi.column() == 0 and self.selection.type == TreeElement.ValueType:
                self.selection.value = val
                changed = True
            elif mi.column() == 1 and self.selection.children[mi.row()].type == TreeElement.ValueType:
                self.selection.children[mi.row()].value = val
                changed = True
        if changed:
            self.dataChanged.emit(mi, mi)
        return changed

    def displayElement(self, idx):
        self.selection = idx.internalPointer() if idx != None else None
        self.modelReset.emit()

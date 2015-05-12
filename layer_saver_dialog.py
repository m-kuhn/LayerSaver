# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerSaverDialog
                                 A QGIS plugin
 This plugins saves and loads layers, their style and other layers they depend on
                             -------------------
        begin                : 2015-05-11
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Matthias Kuhn, OPENGIS.ch
        email                : info@opengis.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog, QCompleter, QDirModel, QFileDialog
from PyQt4 import uic
from qgis.core import QgsLayerTreeModel, QgsProject, QgsLayerTree

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer_saver_dialog_base.ui'))

class MyLayerTreeModel(QgsLayerTreeModel):
  def __init__(self, rootNode, parent):
    super(MyLayerTreeModel, self).__init__(rootNode, parent )

    self.selectionMap = dict()

  def data(self, index, role):
    if role == Qt.CheckStateRole:
      node = self.index2node( index )
      if QgsLayerTree.isLayer( node ):
        try:
          return self.selectionMap[node.layer().id()]
        except KeyError:
          return False
      else:
        return None
    else:
      return super(MyLayerTreeModel, self).data(index,role)

  def flags(self, index):
    if not index.isValid():
      return

    flags = super(MyLayerTreeModel, self).flags(index)
    node = self.index2node(index)
    if QgsLayerTree.isLayer(node):
      return flags | Qt.ItemIsUserCheckable
    else:
      return flags & ~Qt.ItemIsUserCheckable

  def setData(self, index, value, role):
    if role == Qt.CheckStateRole:
      node = self.index2node( index )
      self.selectionMap[node.layer().id()] = value
      return True
    else:
      return super(MyLayerTreeModel, self).setData(index, value, role)

class LayerSaverDialog(QDialog, FORM_CLASS):
  def __init__(self, parent=None):
    """Constructor."""
    super(LayerSaverDialog, self).__init__(parent)
    self.setupUi(self)
    self.model = MyLayerTreeModel( QgsProject.instance().layerTreeRoot(), self )
    self.view.setModel( self.model )
    self.completer = QCompleter(self)
    self.completer.setModel(QDirModel(self.completer))
    self.filename.setCompleter(self.completer)
    self.searchdir.clicked.connect(self.opensearchform)

  def opensearchform(self):
    dn = QFileDialog.getExistingDirectory(self, self.tr('Choose target directory for layers'), self.filename.text() )
    if dn:
      self.filename.setText(dn)

  def set_target_directory(self, dn):
    self.filename.setText(dn)

  def target_directory(self):
    return self.filename.text()

  def layers(self):
    return [layer[0] for layer in self.model.selectionMap.items() if layer[1]]

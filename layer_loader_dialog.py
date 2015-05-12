# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerLoaderDialog
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
from PyQt4.QtGui import QDialog, QCompleter, QFileSystemModel, QFileDialog
from PyQt4 import uic
from qgis.core import QgsLayerTreeModel, QgsProject, QgsLayerTree

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer_loader_dialog_base.ui'))


class LayerLoaderDialog(QDialog, FORM_CLASS):
  def __init__(self, parent=None):
    """Constructor."""
    super(LayerLoaderDialog, self).__init__(parent)
    self.setupUi(self)
    self.completer = QCompleter(self)
    self.fsmodel = QFileSystemModel(self.completer)
    self.fsmodel.setNameFilters(['*.qlf'])
    self.completer.setModel(self.fsmodel)
    self.filename.setCompleter(self.completer)
    self.searchdir.clicked.connect(self.opensearchform)

  def opensearchform(self):
    dn = QFileDialog.getOpenFileName(self, self.tr('Choose target directory for layers'), self.filename.text(), '*.qlf' )
    if dn:
      self.filename.setText(dn)

  def set_target_directory(self, dn):
    self.filename.setText(dn)

  def layer(self):
    return self.filename.text()

# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerSaver
                 A QGIS plugin
 This plugins saves and loads layers, their style and other layers they depend on
                -------------------
    begin        : 2015-05-11
    git sha        : $Format:%H$
    copyright      : (C) 2015 by Matthias Kuhn, OPENGIS.ch
    email        : info@opengis.ch
 ***************************************************************************/

/***************************************************************************
 *                                     *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or   *
 *   (at your option) any later version.                   *
 *                                     *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
import resources_rc
from layer_saver_dialog import LayerSaverDialog
from layer_loader_dialog import LayerLoaderDialog
from lib_layer_saver.bridge import *
from qgis.core import *
import os.path


class LayerSaver:
  """QGIS Plugin Implementation."""

  def __init__(self, iface):
    """Constructor.

    :param iface: An interface instance that will be passed to this class
      which provides the hook by which you can manipulate the QGIS
      application at run time.
    :type iface: QgsInterface
    """
    # Save reference to the QGIS interface
    self.iface = iface
    # initialize plugin directory
    self.plugin_dir = os.path.dirname(__file__)
    # initialize locale
    locale = QSettings().value('locale/userLocale')[0:2]
    locale_path = os.path.join(
      self.plugin_dir,
      'i18n',
      'LayerSaver_{}.qm'.format(locale))

    if os.path.exists(locale_path):
      self.translator = QTranslator()
      self.translator.load(locale_path)

      QCoreApplication.installTranslator(self.translator)

    # Create the dialog (after translation) and keep reference
    self.saverDlg = LayerSaverDialog()
    self.loaderDlg = LayerLoaderDialog()

    # Declare instance attributes
    self.actions = []
    self.menu = self.tr(u'&Layer Saver')
    # TODO: We are going to let the user set this up in a future iteration
    self.toolbar = self.iface.addToolBar(u'LayerSaver')
    self.toolbar.setObjectName(u'LayerSaver')

  # noinspection PyMethodMayBeStatic
  def tr(self, message):
    """Get the translation for a string using Qt translation API.

    We implement this ourselves since we do not inherit QObject.

    :param message: String for translation.
    :type message: str, QString

    :returns: Translated version of message.
    :rtype: QString
    """
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
    return QCoreApplication.translate('LayerSaver', message)


  def add_action(
    self,
    icon_path,
    text,
    callback,
    enabled_flag=True,
    add_to_menu=True,
    add_to_toolbar=True,
    status_tip=None,
    whats_this=None,
    parent=None):
    """Add a toolbar icon to the toolbar.

    :param icon_path: Path to the icon for this action. Can be a resource
      path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
    :type icon_path: str

    :param text: Text that should be shown in menu items for this action.
    :type text: str

    :param callback: Function to be called when the action is triggered.
    :type callback: function

    :param enabled_flag: A flag indicating if the action should be enabled
      by default. Defaults to True.
    :type enabled_flag: bool

    :param add_to_menu: Flag indicating whether the action should also
      be added to the menu. Defaults to True.
    :type add_to_menu: bool

    :param add_to_toolbar: Flag indicating whether the action should also
      be added to the toolbar. Defaults to True.
    :type add_to_toolbar: bool

    :param status_tip: Optional text to show in a popup when mouse pointer
      hovers over the action.
    :type status_tip: str

    :param parent: Parent widget for the new action. Defaults None.
    :type parent: QWidget

    :param whats_this: Optional text to show in the status bar when the
      mouse pointer hovers over the action.

    :returns: The action that was created. Note that the action is also
      added to self.actions list.
    :rtype: QAction
    """

    icon = QIcon(icon_path)
    action = QAction(icon, text, parent)
    action.triggered.connect(callback)
    action.setEnabled(enabled_flag)

    if status_tip is not None:
      action.setStatusTip(status_tip)

    if whats_this is not None:
      action.setWhatsThis(whats_this)

    if add_to_toolbar:
      self.toolbar.addAction(action)

    if add_to_menu:
      self.iface.addPluginToMenu(
        self.menu,
        action)

    self.actions.append(action)

    return action

  def initGui(self):
    """Create the menu entries and toolbar icons inside the QGIS GUI."""

    self.add_action(
      ':/plugins/LayerSaver/export.svg',
      text=self.tr(u'Save layer'),
      callback=self.saveLayer,
      parent=self.iface.mainWindow())
    self.add_action(
      ':/plugins/LayerSaver/import.svg',
      text=self.tr(u'Load layer'),
      callback=self.loadLayer,
      parent=self.iface.mainWindow())


  def unload(self):
    """Removes the plugin menu item and icon from QGIS GUI."""
    for action in self.actions:
      self.iface.removePluginMenu(
        self.tr(u'&Layer Saver'),
        action)
      self.iface.removeToolBarIcon(action)
    # remove the toolbar
    del self.toolbar


  def saveLayer(self):
    # show the dialog
    self.saverDlg.set_target_directory(QSettings().value( 'plugins/layersaver/path', QgsProject.instance().homePath() ) )
    self.saverDlg.show()
    result = self.saverDlg.exec_()
    # See if OK was pressed
    if result:
      QSettings().setValue( 'plugins/layersaver/path', self.saverDlg.target_directory() )
      for layerid in self.saverDlg.layers():
        layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
        exporter = LayerExporter(self.saverDlg.target_directory())
        exporter.save_layer_definition(layer)
        self.iface.messageBar().pushInfo( self.tr( 'LayerSaver' ), self.tr( 'Exported {0} layers' ).format( len( exporter.traversed_layers ) ) )

  def loadLayer(self):
    # show the dialog
    self.loaderDlg.set_target_directory(QSettings().value( 'plugins/layersaver/path', QgsProject.instance().homePath() ) )
    self.loaderDlg.show()
    result = self.loaderDlg.exec_()
    # See if OK was pressed
    if result:
      QSettings().setValue( 'plugins/layersaver/path', self.saverDlg.target_directory() )
      (path, filename) = os.path.split(self.loaderDlg.layer())
      (layername, extension) = os.path.splitext(filename)
      importer = LayerImporter(path)
      importer.load_layer_definition(layername)

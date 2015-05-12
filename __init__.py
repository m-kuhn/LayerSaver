# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerSaver
                                 A QGIS plugin
 This plugins saves and loads layers, their style and other layers they depend on
                             -------------------
        begin                : 2015-05-11
        copyright            : (C) 2015 by Matthias Kuhn, OPENGIS.ch
        email                : info@opengis.ch
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load LayerSaver class from file LayerSaver.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .layer_saver import LayerSaver
    return LayerSaver(iface)

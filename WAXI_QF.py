# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WAXI_QF
                                 A QGIS plugin
 Supoprt QField usage by WAXI Team
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-05-31
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Mark Jessell UWA
        email                : mark.jessell@uwa.edu.au
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import Qgis, QgsProject, QgsVectorLayer
import pandas as pd

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .WAXI_QF_dialog import WAXI_QFDialog
import os.path


class WAXI_QF:
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
            'WAXI_QF_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&WAXI_QF')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('WAXI_QF', message)


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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/WAXI_QF/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'WAXI QF'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def clipToCanvas(self):
        from qgis.core import QgsRectangle, Qgis
        from qgis.core.additions.edit import edit
        import processing
        from qgis.core import (
        QgsGeometry,
        QgsWkbTypes,
        QgsProject,
        QgsVectorLayer,
        QgsVectorFileWriter,
        QgsApplication,
        QgsFeature
        )
        import pandas as pd
        import os
        import shutil

        dirs=["0. STOPS-SAMPLING-PHOTOGRAPHS-COMMENTS","1. STRUCTURES","2. LITHOLOGY","3. GEOPHYSICAL MEASUREMENTS","99. CSV FILES"]
        e = self.iface.mapCanvas().extent()  
        extent = QgsRectangle(e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum())  # Replace with the desired extents
        shp_list=QgsApplication.qgisSettingsDirPath()+"/python/plugins/waxi_qf/shp.csv"
        csv_list=QgsApplication.qgisSettingsDirPath()+"/python/plugins/waxi_qf/csv.csv"

        shps=pd.read_csv(shp_list,names=['name','dir_code'])
        shps=shps.set_index("name")
        csvs=pd.read_csv(csv_list,names=['name'])

        geom = QgsGeometry().fromRect(extent)

        ftr = QgsFeature()
        ftr.setGeometry(geom)

        #Define your Coordinate Reference System here
        project = QgsProject.instance()
        crs = project.crs()

        layer = QgsVectorLayer('Polygon?{}'.format(crs), 'Test_polygon','memory')

        with edit(layer):
            layer.addFeature(ftr)


        # Specify the output file path for the shapefile 
        output_path = "C:/Users/00073294/Dropbox/WAXI4/gis/TESTCLIP"  # Replace with the desired output shapefile path
        output_path = self.dlg.lineEdit_3.text()
        
        
        overlay_path = output_path+"/0. FIELD DATA/0. CURRENT MISSION/0. STOPS-SAMPLING-PHOTOGRAPHS-COMMENTS/cliprect.shp"  # Path to clip rectangle in memory
        if(not os.path.exists(output_path)):
            os.mkdir(output_path)
        if(not os.path.exists(output_path+"/0. FIELD DATA")):
            os.mkdir(output_path+"/0. FIELD DATA")
        if(not os.path.exists(output_path+"/0. FIELD DATA/0. CURRENT MISSION")):
            os.mkdir(output_path+"/0. FIELD DATA/0. CURRENT MISSION")
        if(not os.path.exists(output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[0])):
            os.mkdir(output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[0])
        if(not os.path.exists(output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[1])):
            os.mkdir(output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[1])
        if(not os.path.exists(output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[2])):
            os.mkdir(output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[2])
        if(not os.path.exists(output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[3])):
            os.mkdir(output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[3])
            
            
        # Prepare the output shapefile parameters
        output_fields = layer.fields()
        output_geometry_type = layer.geometryType()
        output_crs = layer.crs()
        #print("XXX",output_fields,output_geometry_type,output_crs)
        # Create the vector file writer instance
        writer = QgsVectorFileWriter(overlay_path, "UTF-8", output_fields, QgsWkbTypes.Polygon, output_crs, "ESRI Shapefile")

        if writer.hasError() != QgsVectorFileWriter.NoError:
            print("Error occurred while creating shapefile:", writer.errorMessage())
        else:
            # Write features to the shapefile
            for feature in layer.getFeatures():
                writer.addFeature(feature)

            # Finish writing and close the shapefile
            del writer

            print("Shapefile saved successfully.")
        for layer in project.mapLayers().values():
                        # Check if the layer name matches the target name
                        if layer.name() in shps.index.tolist():   
                            # Get the file path of the layer
                            print("Clipping ",layer.name())
                            input_path = layer.dataProvider().dataSourceUri()
                            output_path_2="/0. FIELD DATA/0. CURRENT MISSION/"+dirs[int(shps.loc[layer.name()].dir_code)]+"/"
                            print("saving to",output_path+output_path_2+layer.name()+".shp")
                            ### REDO output_path as output_dir + input_filename.shp
                            processing.run("native:clip", {   
                                'INPUT': input_path,   
                                'OUTPUT': output_path+output_path_2+layer.name()+".shp",   
                                'OVERLAY': overlay_path   
                            })   

        if(not os.path.exists(output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[4])):
            src_path=os.path.split(input_path)
            src_path=src_path[0]+"/../"+dirs[4]
            dst_path=output_path+"/0. FIELD DATA/0. CURRENT MISSION/"+dirs[4]+"/"
            print("src",src_path)
            print("dest",dst_path)
            shutil.copytree(src_path, dst_path)

        #clipped_layer = QgsVectorLayer(output_path, "Clipped Layer", "ogr")   
        #QgsProject.instance().addMapLayer(clipped_layer)   
        self.iface.messageBar().pushMessage("Files clipped to current extent, saved in directory" + output_path, level=Qgis.Success, duration=5)

    def addUserName(self):
        username = self.dlg.lineEdit.text()
        description = self.dlg.lineEdit_2.text()
        layer_name='User list'
        project = QgsProject.instance()

        layer = project.mapLayersByName(layer_name)
        group = QgsProject.instance().layerTreeRoot()

        if len(layer) > 0:
            # Remove the layer from the project
            for layer in project.mapLayers().values():
                # Check if the layer name matches the target name
                if layer.name() == layer_name:
                    # Get the file path of the layer
                    file_path = layer.dataProvider().dataSourceUri()

                    QgsProject.instance().removeMapLayer(layer)
                    User_List= pd.read_csv(file_path,encoding="latin_1",sep=";")
                    User_List.loc[str(len(User_List))] = [username,description]
                    User_List.to_csv(file_path,index=False,sep=";",encoding="latin_1")
                    updated_layer = QgsVectorLayer(file_path, layer_name, "ogr")
                    if updated_layer.isValid():

                        # Add the updated layer to the project
                        QgsProject.instance().addMapLayer(updated_layer,False)
                        group = QgsProject.instance().layerTreeRoot().findGroup("CSV FILES")
                        
                        if group:

                            # Add the layer to the new group
                            group.addLayer(updated_layer)
                            self.iface.messageBar().pushMessage("User "+username+" added to User list", level=Qgis.Success, duration=5)

                    else:
                        self.iface.messageBar().pushMessage("Layer Failed to load updated layer: "+layer_name, level=Qgis.Warning, duration=15)
                    break  # Stop iterating once the layer is found
        else:
            self.iface.messageBar().pushMessage("Layer not found: "+layer_name, level=Qgis.Warning, duration=15)

    def select_dst_directory(self):
        filename = QFileDialog.getExistingDirectory(None, "Select Folder")

        self.dlg.lineEdit_3.setText(filename)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&WAXI_QF'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = WAXI_QFDialog()
            self.dlg.pushButton.clicked.connect(self.select_dst_directory)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            if(self.dlg.lineEdit.text()):
                self.addUserName()
            if(self.dlg.checkBox.isChecked()):
                self.clipToCanvas()
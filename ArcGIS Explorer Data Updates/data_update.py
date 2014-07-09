import arcpy, shutil

#Setting workspace
arcpy.env.overwriteOutput = True

# Open MXD Template and retrieve layer groups for ArcGIS Explorer Map
mxd = arcpy.mapping.MapDocument(r"ExplorerPackageSetups.mxd")
lyrs = []
lyrs.append(arcpy.mapping.ListLayers(mxd, "Base"))
lyrs.append(arcpy.mapping.ListLayers(mxd, "Planning Development"))
lyrs.append(arcpy.mapping.ListLayers(mxd, "Misc"))
lyrs.append(arcpy.mapping.ListLayers(mxd, "Utilities"))

# Create Layer Package with list of layer groups
arcpy.PackageLayer_management(lyrs, r"CityOfParisData.lpk", "CONVERT", "CONVERT_ARCSDE", "DEFAULT", "ALL", "ALL", "CURRENT")

# Copy and overwrite date file on S: drive used by ArcGIS Explorer
shutil.copyfile("CityOfParisData.lpk", "S:\citydata\GIS\Data\CityOfParisData.lpk")
import arcpy, shutil, time

processTime = time.time()

#Setting workspace
arcpy.env.overwriteOutput = True

# Open MXD Template and retrieve layer groups for ArcGIS Explorer Map
print "Opening MXD Template..."
mxd = arcpy.mapping.MapDocument(r"ExplorerPackageSetups.mxd")

print "Extracting Layers..."
lyrs = arcpy.mapping.ListLayers(mxd)


# Create Layer Package with list of layer groups
print "Packaging Layers..."
arcpy.PackageLayer_management(lyrs, r"CityOfParisData.lpk", "CONVERT", "CONVERT_ARCSDE", "DEFAULT", "ALL", "ALL", "CURRENT")


# Copy and overwrite date file on S: drive used by ArcGIS Explorer
print "Copying Layer Package To 'citydata' folder"
shutil.copyfile("CityOfParisData.lpk", "S:\citydata\GIS\Data\CityOfParisData.lpk")

print "Done in " + str(time.time() - processTime) + " seconds"
#!/usr/bin/env python

from collections import OrderedDict
import fiona, time, math, glob, shutil
from shapely.ops import cascaded_union
from shapely.geometry import Polygon, shape, mapping, LineString
from rtree import index

processTime = time.time()

historical_districts_location = r'S:\GIS\DWGS\GIS_Data\Planning_and_Zoning\Overlays\Historic Districts.shp'
reinvestment_zone_location = r'S:\GIS\DWGS\GIS_Data\Planning_and_Zoning\Overlays\Reinvestment Zone.shp'
child_safety_location = r'S:\GIS\DWGS\GIS_Data\Police_Department\Child_Safety_Zones\Child_Safety_Zones.shp'
fema_location = r'S:\GIS\DWGS\GIS_Data\FEMA\S_FLD_HAZ_AR.shp'
parcel_location = r'S:\GIS\DWGS\GIS_Data\_Processing\automation-scripts\Parcel_Import\LCAD_Parcels\parcels.shp'
parcel_export_location = r'S:\GIS\DWGS\GIS_Data\_Processing\automation-scripts\Parcel_Import\Output\Parcels.shp'
ce_area_location = r'S:\GIS\DWGS\GIS_Data\Code_Enforcement\CE_Area.shp'

zoning_location = r'S:\GIS\DWGS\GIS_Data\Planning_and_Zoning\Zoning_Contiguous.shp'
landuse_location = r'S:\GIS\DWGS\GIS_Data\Planning_and_Zoning\Landuse_Present.shp'

# Opening polygon data that contain attributes to be assigned to Parcel polygons (zoning, landuse, reinvestment zones, etc)
historic_districts_shp = fiona.open(historical_districts_location, 'r')
reinvestment_zone_shp = fiona.open(reinvestment_zone_location, 'r')
child_safety_shp = fiona.open(child_safety_location, 'r')
ce_area_shp = fiona.open(ce_area_location, 'r')
#fema_shp = fiona.open(fema_location, 'r')

# Merging histroic districts and child safety zones into single MultiPolygon. 
# For use to compare single parcel polygons to a single feature
shapes = []
for f in historic_districts_shp:
    shapes.append(shape(f['geometry']))

historic_shape = cascaded_union(shapes)

shapes = []
for f in child_safety_shp:
    shapes.append(shape(f['geometry']))

child_shape = cascaded_union(shapes)

# Pull the East and West areas of Code Enforcement for later comparison

ce_east = shape(next(ce_area_shp)['geometry'])
ce_west = shape(next(ce_area_shp)['geometry'])

# Merge FEMA zones into individual floodways, 100 year zones, 500 year zones for later parcel assignment

#floodway = []
#year100 = []
#year500 = []

#for f in fema_shp:
#    if f['properties']['FLOODWAY'] == 'FLOODWAY':
#        floodway.append(shape(f['geometry']))
#    if f['properties']['FLD_ZONE'] == 'A' or  f['properties']['FLD_ZONE'] == 'AE':
#        year100.append(shape(f['geometry']))
#    if f['properties']['FLD_ZONE'] == '0.2 PCT ANNUAL CHANCE FLOOD HAZARD':
#        year500.append(shape(f['geometry']))

#fema_floodway_shape = cascaded_union(floodway)
#fema_100year_shape = cascaded_union(year100)
#fema_500year_shape = cascaded_union(year500)

# Convert Reinvestment Zone into Shapely shape for compare with parcel polygons
reinvestment_shape = shape(next(reinvestment_zone_shp)['geometry'])

# Zoning rtree index created for parcel comparison
zoningidx = index.Index()
idxcounter = 0
with fiona.collection(zoning_location, 'r') as input:
    for f in input:
        zoningidx.add(idxcounter, shape(f['geometry']).bounds, obj=f)
        idxcounter += 1

# Landuse rtree index created for parcel comparison
landuseidx = index.Index()
idxcounter = 0
with fiona.collection(landuse_location, 'r') as input:
    for f in input:
        landuseidx.add(idxcounter, shape(f['geometry']).bounds, obj=f)
        idxcounter += 1

# Schema for cleaned, exported parcel file
schema = {'geometry': 'Polygon',
          'properties': OrderedDict([('PROP_ID', 'int'),
                                     ('file_as_na', 'str'),
                                     ('addr_line1', 'str'),
                                     ('addr_line2', 'str'),
                                     ('addr_line3', 'str'),
                                     ('addr_city', 'str'),
                                     ('addr_state', 'str'),
                                     ('addr_zip', 'str'),
                                     ('school', 'str'),
                                     ('city', 'str'),
                                     ('county', 'str'),
                                     ('legal_desc', 'str'),
                                     ('land_val', 'str'),
                                     ('imprv_val', 'str'),
                                     ('market_val', 'str'),
                                     ('geo_id', 'str'),
                                     ('situs_num', 'str'),
                                     ('situs_stre', 'str'),
                                     ('situs_st_1', 'str'),
                                     ('situs_st_2', 'str'),
                                     ('situs_city', 'str'),
                                     ('situs_stat', 'str'),
                                     ('situs_zip', 'str'),
                                     ('hist_dist', 'str'),
                                     ('reinvest', 'str'),
                                     ('childsafe', 'str'),
                                     ('zoning', 'str'),
                                     ('landuse', 'str'),
                                     ('ce_area', 'str')
                                   ])}


print time.time() - processTime, 'Intial Setup Done'

# Open parcel file
with fiona.collection(parcel_location, 'r') as input:
    # Create new shapeile to export clean parcel data
    with fiona.collection(parcel_export_location, 'w', 'ESRI Shapefile', schema, input.crs) as output:
        # Loop through each Parcel, clean data, assign new attributes, and skip over invalid polygons
        parcelcounter = 0
        for f in input:
            
            if shape(f['geometry']).area > 0:

                ## Get envelope of parcel polygon to calculate angle
                #envelope = shape(f['geometry']).envelope

                ## Determine if Parcel is within Historic District
                if historic_shape.contains(shape(f['geometry'])): 
                    HistoricDistrict = 'Yes'
                else:
                    HistoricDistrict = 'No' 

                ## Determine if Parcel is within Reinvestment Zone
                if reinvestment_shape.contains(shape(f['geometry'])):
                    ReinvestmentZone = 'Yes'
                else:
                    ReinvestmentZone = 'No' 

                ## Determine if Parcel is within Child Safety Zone
                if child_shape.contains(shape(f['geometry'])):
                    ChildSafetyZone = 'Yes'
                else:
                    ChildSafetyZone = 'No' 

                if ce_east.contains(shape(f['geometry'])):
                    CE_Area = 'East'
                else:
                    CE_Area = 'West'

                ## Compare parcel to zoning index, intersect and check matches, add to attribute listing

                zoning_attribute = ''
                zoning_hits = list(zoningidx.intersection(shape(f['geometry']).bounds, objects=True))
    
                for i in zoning_hits:
                    if shape(f['geometry']).intersection(shape(i.object['geometry'])).area / shape(f['geometry']).area > .02:
                        zoning_attribute = zoning_attribute + i.object['properties']['ZoneCode'] + ','

                zoning_attribute = zoning_attribute.rstrip(', ')

                ## Compare parcel to landuse index, intersect and check matches, add to attribute listing

                landuse_attribute = ''
                landuse_hits = list(landuseidx.intersection(shape(f['geometry']).bounds, objects=True))

                for i in landuse_hits:
                    if shape(f['geometry']).intersection(shape(i.object['geometry'])).area / shape(f['geometry']).area > .02:
                        landuse_attribute = landuse_attribute + i.object['properties']['LUCode'] + ','

                landuse_attribute = landuse_attribute.rstrip(', ')

                ## Compare parcel to fema zones, intersect and check matches, add to attribute listing
                fema_attribute = ''
                #if fema_floodway_shape.contains(shape(f['geometry'])):
                #    fema_attribute = fema_attribute + 'Floodway, '
                #if fema_100year_shape.contains(shape(f['geometry'])):
                #    fema_attribute = fema_attribute + '100 Year, '
                #if fema_500year_shape.contains(shape(f['geometry'])):
                #    fema_attribute = fema_attribute + '500 Year, '

                #fema_attribute = fema_attribute.rstrip(', ')

                ##Check validity of parcel Geometry
                geom = ''
                if shape(f['geometry']).is_valid:
                    geom = f['geometry']
                else:
                    geom = mapping(shape(f['geometry']).buffer(0))
                ## Add clean parcel feature to output shapefile (export)
                output.write({
                        'properties' : {
                        'PROP_ID': int(f['properties']['PROP_ID']),
                        'file_as_na': f['properties']['file_as_na'],
                        'addr_line1': f['properties']['addr_line1'],
                        'addr_line2': f['properties']['addr_line2'],
                        'addr_line3': f['properties']['addr_line3'],
                        'addr_city': f['properties']['addr_city'],
                        'addr_state': f['properties']['addr_state'],
                        'addr_zip': f['properties']['zip'],
                        'school': f['properties']['school'],
                        'city': f['properties']['city'],
                        'county': f['properties']['county'],
                        'legal_desc': f['properties']['legal_desc'],
                        'land_val': f['properties']['land_val'],
                        'imprv_val': f['properties']['imprv_val'],
                        'market_val': f['properties']['market'],
                        'geo_id': f['properties']['geo_id'],
                        'situs_num': f['properties']['situs_num'],
                        'situs_stre': f['properties']['situs_stre'],
                        'situs_st_1': f['properties']['situs_st_1'],
                        'situs_st_2': f['properties']['situs_st_2'],
                        'situs_city': f['properties']['situs_city'],
                        'situs_stat': f['properties']['situs_stat'],
                        'situs_zip': f['properties']['situs_zip'],
                        'hist_dist': HistoricDistrict,
                        'reinvest': ReinvestmentZone,
                        'childsafe': ChildSafetyZone,
                        'zoning': zoning_attribute,
                        'landuse': landuse_attribute,
                        'ce_area': CE_Area
                        },
                    'geometry': geom
                    })
                parcelcounter += 1
                #print int(f['properties']['PROP_ID'])

                if parcelcounter % 1000 == 0:
                    print parcelcounter, time.time() - processTime

dest_dir = r'..\..\..\Lamar_County_CAD'
for file in glob.glob(r'output\parcels.*'):
    shutil.copy(file, dest_dir)
                    
processTime = time.time() - processTime

print processTime

historic_districts_shp.closed
reinvestment_zone_shp.closed
child_safety_shp.closed
ce_area_shp.closed


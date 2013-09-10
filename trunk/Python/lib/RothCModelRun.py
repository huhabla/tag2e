#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Authors: Soeren Gebbert, soeren.gebbert@vti.bund.de
#          Rene Dechow, rene.dechow@vti.bund.de
#
# Copyright:
#
# Johann Heinrich von Thuenen-Institut
# Institut fuer Agrarrelevante Klimaforschung
#
# Phone: +49 (0)531 596 2601
#
# Fax:+49 (0)531 596 2699
#
# Mail: ak@vti.bund.de
#
# Bundesallee 50
# 38116 Braunschweig
# Germany
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
import grass.script as grass
import grass.temporal as tgis
from vtk import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *

def RothCModelRun(mapmatrix, pools, clayContent, outputName=None, baseName=None,
        RothCParameter=None, NullValue=-99999, overwrite=False):
    """!Run the RothC model using space time raster datasets

       @param: mapmatrix - A two dimensional matrix taht contains the sampled
               space time raster datasets. This matrix is usually created using
               tgis.sample_stds_by_stds_topology()
       @param: pools - The poly dataset with DPM, RPM, HUM, BIO and IOM pools
       @param: clayContent - The name of the raster map with clay content in [%]
       @param: outputName - The name of the output space time raster dataset
       @param: basename - The name of the
    """
    # Check the temporal type
    first = mapmatrix[0][0]["granule"]

    if outputName != None and baseName != None:
        # We need a database interface
        dbif = tgis.SQLDatabaseInterfaceConnection()
        dbif.connect()

        mapset = grass.gisenv()["MAPSET"]
        # Create the output space time raster dataset
        out = tgis.open_new_space_time_dataset(outputName, "strds",
                                               first.get_temporal_type(),
                                               "RothC", "RothC", "mean",
                                               dbif, overwrite)

        sqlStatements = ""
        outMapList = []

    # We define the line length as 30cm
    lineLengths = vtkDoubleArray()
    lineLengths.InsertNextValue(0.30)

    # Clay content is not a time series
    names = vtkStringArray()
    names.InsertNextValue(clayContent)
    clayReader = vtkGRASSMultiRasterPolyDataLineReader()
    clayReader.SetRasterNames(names)
    clayReader.SetDataName("Clay")
    clayReader.SetLineLengths(lineLengths)

    # Initiate the models and connect them
    # Compute potential evapo-transpiration
    ETpot = vtkTAG2ETurcETPotModel()
    ETpot.SetNullValue(NullValue)

    # Soil moisture computation
    SoilMoisture = vtkTAG2ERothCWaterBudgetModel()
    SoilMoisture.SetNullValue(NullValue)

    # Residual distribution
    residuals = vtkTAG2ERothCResidualFilter()
    residuals.SetNullValue(NullValue)

    # RothC model computation
    if not RothCParameter or RothCParameter == None:
        print("Create default RothCModelParameter")
        RothCParameter = vtkTAG2ERothCModelParameter()

    RothC = vtkTAG2ERothCModel()
    RothC.SetModelParameter(RothCParameter)
    RothC.AddCPoolsToOutputOn()
    RothC.EquilibriumRunOff()
    RothC.SetNullValue(NullValue)

    # Some dataset join filter
    dc1 = vtkTAG2EDataSetJoinFilter()
    dc2 = vtkTAG2EDataSetJoinFilter()
    join = vtkTAG2EDataSetJoinFilter()

    # This is the iterator over the time series
    for j in range(len(mapmatrix[0])):

        # Initialize the joiner
        join.RemoveAllInputs()
        join.AddInputConnection(clayReader.GetOutputPort())

        for i in range(len(mapmatrix)):

            entry = mapmatrix[i][j]

            samples = entry["samples"]
            granule = entry["granule"]

            # Gaps can appear for resiuals
            if samples[0].get_id() == None:
                continue

            if len(samples) > 1:
                messages.Warning("More than one map found in sample. "
                                 "Using the first one only.")
                for sample in samples:
                    print sample.get_id()

            names = vtkStringArray()
            names.InsertNextValue(samples[0].get_id())

            reader = vtkGRASSMultiRasterPolyDataLineReader()
            reader.SetRasterNames(names)
            reader.SetLineLengths(lineLengths)

            # Precipitation
            if i == 0:
                reader.SetDataName("Precipitation")
                join.AddInputConnection(reader.GetOutputPort())
            # Global radiation
            elif i == 1:
                reader.SetDataName("GlobalRadiation")
                join.AddInputConnection(reader.GetOutputPort())
            # Soil cover
            elif i == 2:
                reader.SetDataName("SoilCover")
                join.AddInputConnection(reader.GetOutputPort())
            # Soil cover
            elif i == 3:
                reader.SetDataName("FertilizerCarbon")
                join.AddInputConnection(reader.GetOutputPort())
            # Residuals
            elif i == 4:
                reader.SetDataName("Residuals")
                residuals.SetInputConnection(reader.GetOutputPort())
                join.AddInputConnection(residuals.GetOutputPort())
             # Fertilizer Id
            elif i == 5:
                reader.SetDataName("FertilizerID")
                join.AddInputConnection(reader.GetOutputPort())
            elif i == 6:
                reader.SetDataName("PlantID")
                join.AddInputConnection(reader.GetOutputPort())

        granule = mapmatrix[0][j]["granule"]
        start, end = granule.get_temporal_extent_as_tuple()
        id = granule.get_id()
        # Mean temperature must be used for sampling
        names = vtkStringArray()
        names.InsertNextValue(id)
        reader = vtkGRASSMultiRasterPolyDataLineReader()
        reader.SetRasterNames(names)
        reader.SetDataName("MeanTemperature")
        reader.SetLineLengths(lineLengths)
        join.AddInputConnection(reader.GetOutputPort())

        dc1.RemoveAllInputs()
        dc2.RemoveAllInputs()

        ETpot.SetInputConnection(join.GetOutputPort())
        """!ATTENTION WE NEED TO COMPUTE THE CORRECT NUMBER OF DAYS HERE"""
        days = tgis.time_delta_to_relative_time(end - start)
        ETpot.SetTimeInterval(days)

        # Soil moisture input
        dc1.AddInputConnection(ETpot.GetOutputPort())
        dc1.AddInputConnection(join.GetOutputPort())

        SoilMoisture.SetInputConnection(dc1.GetOutputPort())

        # ETpot input
        dc2.AddInputConnection(join.GetOutputPort())
        dc2.AddInputConnection(SoilMoisture.GetOutputPort())
        # The pools must be added in the first iteration
        if j == 0:
            dc2.AddInput(pools)

        RothC.SetInputConnection(dc2.GetOutputPort())
        RothC.Update()

        if outputName != None and baseName != None:
            # Write the output as raster map
            mapname = "%s_%05i"%(outputName, j)

            writer = vtkGRASSMultiRasterPolyDataLineWriter()
            writer.SetRasterMapName(mapname)
            writer.SetArrayName("SoilCarbon")
            writer.SetLayer(1)
            writer.SetInputConnection(RothC.GetOutputPort())
            # This update does all the work :)
            writer.Update()

            # Register the new map in the temporal database and the space time raster dataset
            mapid = granule.build_id(mapname, mapset)
            map = granule.get_new_instance(mapid)

            # Delete if the map was already in the temporal database
            if map.is_in_db(dbif):
                map.select(dbif)
                # We store the SQL delete statements
                sqlStatements += map.delete(dbif, False)

            map = granule.get_new_instance(mapid)
            # Read metadata from the computed map
            map.load()
            # We use the time from the current granule
            map.set_temporal_extent(granule.get_temporal_extent())
            # We store the SQL insert statements
            sqlStatements += map.insert(dbif, False)
            # We need to store the map objects to register them in
            # the space time raster dataset
            outMapList.append(map)

    if outputName != None and baseName != None:
        # Execute all SQL state,ents in a single transaction
        dbif.execute_transaction(sqlStatements)

        # Register maps in space time raster dataset
        for map in outMapList:
            out.register_map(map, dbif)

        # Update the space time dataset
        out.update_from_registered_maps(dbif)

        dbif.close()

    return RothC.GetOutput()

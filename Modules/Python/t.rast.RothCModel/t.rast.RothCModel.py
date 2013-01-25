#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: t.rast.RothCModel
#
# Purpose: Compute the RothC model
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

import sys
import grass.script as grass
import grass.temporal as tgis
import os
#include the VTK and vtkGRASSBridge Python libraries
from vtk import *
import libvtkTAG2EFilteringPython
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *
from RothCEqulibriumRun import *

################################################################################
################################################################################
################################################################################

def main():
    # Initiate GRASS
    init = vtkGRASSInit()
    init.Init("t.rast.RothCModel")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Compute the RothC model")
    module.AddKeyword("temporal")
    module.AddKeyword("RothC")
    
    temperature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    temperature.SetKey("temperature")
    temperature.SetDescription("Space time raster dataset with "
                               "monthly temperature mean [degree C]"
                               ". This dataset will be used to temporally sample all other.")
    
    precipitation = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    precipitation.SetKey("precipitation")
    precipitation.SetDescription("Space time raster dataset with "
                                 "monthly accumulated precipitation [mm]")
    
    radiation = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    radiation.SetKey("radiation")
    radiation.SetDescription("Space time raster dataset with "
                             "global radiation [J/(cm^2 * day)]")
    
    fertilizer = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    fertilizer.SetKey("fertilizer")
    fertilizer.SetDescription("Raster map with fertilizer of the RothC model [tC/ha]")
    
    residuals = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    residuals.SetKey("residuals")
    residuals.SetDescription("Raster map with residuals of the RothC model [tC/ha]")
    
    # Space time raster datasets
    soilCover = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    soilCover.SetKey("soilcover")
    soilCover.SetDescription("Space time raster dataset with long term monthly  (exactly 12 months)")
                       
    # Raster map input
    clayContent = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    clayContent.SetKey("claycontent")
    clayContent.SetDescription("Raster map with clay content in percent [%]")
    
    poolDPM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolDPM.SetKey("dpmpool")
    poolDPM.SetDescription("The model DPM pool at the start of the computation")
        
    poolRPM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolRPM.SetKey("rpmpool")
    poolRPM.SetDescription("The model RPM pool at the start of the computation")
        
    poolHUM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolHUM.SetKey("humpool")
    poolHUM.SetDescription("The model HUM pool at the start of the computation")
        
    poolBIO = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolBIO.SetKey("biopool")
    poolBIO.SetDescription("The model BIO pool at the start of the computation")
        
    poolIOM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolIOM.SetKey("iompool")
    poolIOM.SetDescription("The model IOM pool at the start of the computation")

    baseName = vtkGRASSOption()
    baseName.SetKey("base")
    baseName.SetTypeToString()
    baseName.MultipleOff()
    baseName.RequiredOn()
    baseName.SetDescription("The base name of the new created raster maps")
    
    # Space time raster datasets
    soc = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSOutputType())
    soc.SetKey("soc")
    soc.SetDescription("Result space time raster dataset with SOC content")
    
    # INIT
    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1
    # We need to modify the environment settings so that the
    # overwrite flag will be recognized
    os.environ["GRASS_OVERWRITE"] = str(init.Overwrite())
    os.environ["GRASS_VERBOSE"] = str(init.Verbosity())

    messages = vtkGRASSMessagingInterface()
    messages.VerboseMessage("Sampling of input datasets")

    tgis.init()
    
    inputNames = "%s,%s,%s,%s,%s"%(precipitation.GetAnswer(), radiation.GetAnswer(),
                            soilCover.GetAnswer(), fertilizer.GetAnswer(), 
                            residuals.GetAnswer())
    
    mapmatrix = tgis.sample_stds_by_stds_topology("strds", "strds", inputNames,
                                           temperature.GetAnswer(), False,
                                 "|", "equal", False, True)

    pools = read_pools(poolDPM=poolDPM.GetAnswer(), poolRPM=poolRPM.GetAnswer(),
                       poolHUM=poolHUM.GetAnswer(), poolBIO=poolBIO.GetAnswer(),
                       poolIOM=poolIOM.GetAnswer())
     
    RothCRun(mapmatrix, pools, clayContent, soc.GetAnswer(), baseName.GetAnswer(), 
        None, -99999, bool(init.Overwrite()))

################################################################################

def read_pools(poolDPM, poolRPM, poolHUM, poolBIO, poolIOM):
    """
    Read the RothC pools and return a single poly dataset
    that includes all pools.
    """    
    joiner = vtkTAG2EDataSetJoinFilter()

    # We define the line length as 30cm
    lineLengths = vtkDoubleArray()
    lineLengths.InsertNextValue(0.30)
    # Read the pools
    names = vtkStringArray()
    names.InsertNextValue(poolDPM)
    poolDPMreader = vtkGRASSMultiRasterPolyDataLineReader()
    poolDPMreader.SetRasterNames(names)
    poolDPMreader.SetDataName("DPM")
    poolDPMreader.SetLineLengths(lineLengths)
    
    joiner.AddInputConnection(poolDPMreader.GetOutputPort())
    
    names = vtkStringArray()
    names.InsertNextValue(poolRPM)
    poolRPMreader = vtkGRASSMultiRasterPolyDataLineReader()
    poolRPMreader.SetRasterNames(names)
    poolRPMreader.SetDataName("RPM")
    poolRPMreader.SetLineLengths(lineLengths)
    
    joiner.AddInputConnection(poolRPMreader.GetOutputPort())
    
    names = vtkStringArray()
    names.InsertNextValue(poolHUM)
    poolHUMreader = vtkGRASSMultiRasterPolyDataLineReader()
    poolHUMreader.SetRasterNames(names)
    poolHUMreader.SetDataName("HUM")
    poolHUMreader.SetLineLengths(lineLengths)
    
    joiner.AddInputConnection(poolHUMreader.GetOutputPort())
    
    names = vtkStringArray()
    names.InsertNextValue(poolBIO)
    poolBIOreader = vtkGRASSMultiRasterPolyDataLineReader()
    poolBIOreader.SetRasterNames(names)
    poolBIOreader.SetDataName("BIO")
    poolBIOreader.SetLineLengths(lineLengths)
    
    joiner.AddInputConnection(poolDPMreader.GetOutputPort())
    
    names = vtkStringArray()
    names.InsertNextValue(poolIOM)
    poolIOMreader = vtkGRASSMultiRasterPolyDataLineReader()
    poolIOMreader.SetRasterNames(names)
    poolIOMreader.SetDataName("IOM")
    poolIOMreader.SetLineLengths(lineLengths)
    
    joiner.AddInputConnection(poolIOMreader.GetOutputPort())
    joiner.Update()
    
    return joiner.GetOutput()
    
################################################################################

def RothCRun(mapmatrix, pools, clayContent, outputName=None, baseName=None, 
        RothCParameter=None, NullValue=-99999, overwrite=False):
    """!
    """
    # Check the temporal type
    first = mapmatrix[0][0]["granule"]
    
    if outputName != None and baseName != None:
        # We need a database interface
        dbif = tgis.SQLDatabaseInterfaceConnection()
        dbif.connect()
    
        mapset = grass.gisenv()["MAPSET"]
        # Create the output space time raster dataset
        out = tgis.create_space_time_dataset(outputName, "strds", first.get_temporal_type(), 
                                       "RothC", "RothC", "mean",
                                       dbif, overwrite)
    
        sqlStatements = ""
        outMapList = []

    # We define the line length as 30cm
    lineLengths = vtkDoubleArray()
    lineLengths.InsertNextValue(0.30)
    
    # Clay content is not a time series
    names = vtkStringArray()
    names.InsertNextValue(clayContent.GetAnswer())
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
            if i == 1:
                reader.SetDataName("GlobalRadiation")
                join.AddInputConnection(reader.GetOutputPort())
            # Soil cover
            if i == 2:
                reader.SetDataName("SoilCover")
                join.AddInputConnection(reader.GetOutputPort())
            # Soil cover
            if i == 3:
                reader.SetDataName("FertilizerCarbon")
                join.AddInputConnection(reader.GetOutputPort())
            # Residuals
            if i == 4:
                reader.SetDataName("Residuals")
                residuals.SetInputConnection(reader.GetOutputPort())
                join.AddInputConnection(residuals.GetOutputPort())
        
        granule = mapmatrix[0][j]["granule"]
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
        ETpot.SetTimeInterval(30)
        
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
            if granule.is_time_absolute():
                start, end, zone = granule.get_absolute_time()
                map.set_absolute_time(start, end, zone)
            else:
                start, end, unit = granule.get_relative_time()
                map.set_relative_time(start, end, unit)
                
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

################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()

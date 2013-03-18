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
from RothCModelRun import *

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
     
    RothCModelRun(mapmatrix, pools, clayContent.GetAnswer(), soc.GetAnswer(), 
                  baseName.GetAnswer(), None, -99999, bool(init.Overwrite()))

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
################################################################################
################################################################################

if __name__ == "__main__":
    main()

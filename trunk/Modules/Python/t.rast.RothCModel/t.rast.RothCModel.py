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
import grass.temporal as tgis
import os
#include the VTK and vtkGRASSBridge Python libraries
from vtk import *
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
    module.SetDescription("Soil organic carbon computation using the RothC model")
    module.AddKeyword("temporal")
    module.AddKeyword("RothC")

    xmlParam = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileInputType())
    xmlParam.SetKey("param")
    xmlParam.RequiredOff()
    xmlParam.SetDescription("The parameter XML file that describes the RothC configuarion ")

    temperature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    temperature.SetKey("temperature")
    temperature.SetDescription("Input space time raster dataset with "
                               "monthly temperature mean [degree C]"
                               ". This dataset will be used to temporally sample all other.")

    precipitation = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    precipitation.SetKey("precipitation")
    precipitation.SetDescription("Input space time raster dataset with "
                                 "monthly accumulated precipitation [mm]")

    radiation = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    radiation.SetKey("radiation")
    radiation.SetDescription("Input space time raster dataset with "
                             "global radiation [J/(cm^2 * day)]")

    fertilizer = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    fertilizer.SetKey("fertilizer")
    fertilizer.SetDescription("Input space time raster dataset with organic "
                              "fertilizer of the RothC model [tC/ha]")

    roots = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    roots.SetKey("roots")
    roots.SetDescription("Input space time raster dataset with root residuals of the RothC model [tC/ha]")
    
    shoots = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    shoots.SetKey("shoots")
    shoots.SetDescription("Input space time raster dataset with shoot residuals of the RothC model [tC/ha]")
    
    # Space time raster datasets
    soilCover = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    soilCover.SetKey("soilcover")
    soilCover.SetDescription("Input space time raster dataset with soil cover time series [0;1]")

    fertId = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    fertId.SetKey("fertid")
    fertId.RequiredOff()
    fertId.SetDescription("Input space time raster dataset with fertilizer ids of the RothC model parameter")

    shootId = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    shootId.SetKey("shootid")
    shootId.RequiredOff()
    shootId.SetDescription("Input space time raster dataset with shoot ids of the RothC model parameter")

    rootId = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSInputType())
    rootId.SetKey("rootid")
    rootId.RequiredOff()
    rootId.SetDescription("Input space time raster dataset with root ids of the RothC model parameter")

    # Raster map input
    clayContent = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    clayContent.SetKey("claycontent")
    clayContent.SetDescription("Input raster map with clay content in percent [%]")

    poolDPM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolDPM.SetKey("dpmpool")
    poolDPM.SetDescription("Input raster map specifying the DPM pool [tC/ha] at the start "
                           "of the computation (usually from generated by equilibrium run)")

    poolRPM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolRPM.SetKey("rpmpool")
    poolRPM.SetDescription("Input raster map specifying the RPM pool [tC/ha] at the start "
                           "of the computation (usually from generated by equilibrium run)")

    poolHUM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolHUM.SetKey("humpool")
    poolHUM.SetDescription("Input raster map specifying the HUM pool [tC/ha] at the start "
                           "of the computation (usually from generated by equilibrium run)")

    poolBIO = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolBIO.SetKey("biopool")
    poolBIO.SetDescription("Input raster map specifying the BIO pool [tC/ha] at the start "
                           "of the computation (usually from generated by equilibrium run)")

    poolIOM = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType())
    poolIOM.SetKey("iompool")
    poolIOM.SetDescription("Input raster map specifying the IOM pool [tC/ha] at the start "
                           "of the computation (usually from generated by equilibrium run)")

    baseName = vtkGRASSOption()
    baseName.SetKey("base")
    baseName.SetTypeToString()
    baseName.MultipleOff()
    baseName.RequiredOn()
    baseName.SetDescription("The base name of the new created raster maps")

    # Soil organic carbon Space time raster datasets
    soc = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetSTRDSOutputType())
    soc.SetKey("soc")
    soc.SetDescription("Output space time raster dataset with SOC content [tC/ha]")

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

    inputNames = "%s,%s,%s,%s,%s,%s"%(precipitation.GetAnswer(), radiation.GetAnswer(),
                            soilCover.GetAnswer(), fertilizer.GetAnswer(),
                            roots.GetAnswer(), shoots.GetAnswer())

    if fertId.GetAnswer():
        inputNames += ",%s"%(fertId.GetAnswer())

    if shootId.GetAnswer() and not fertId.GetAnswer():
        print("ERROR: Shoot id and fertilizer id must be set")
        return -1

    if shootId.GetAnswer():
        inputNames += ",%s"%(shootId.GetAnswer())

    if rootId.GetAnswer() and not shootId.GetAnswer():
        print("ERROR: Root id and shoot id must be set")
        return -1

    if rootId.GetAnswer():
        inputNames += ",%s"%(rootId.GetAnswer())

    mapmatrix = tgis.sample_stds_by_stds_topology("strds", "strds", inputNames,
                                           temperature.GetAnswer(), False,
                                 "|", "equal,during,contains", False, True)

    pools = read_pools(poolDPM=poolDPM.GetAnswer(), poolRPM=poolRPM.GetAnswer(),
                       poolHUM=poolHUM.GetAnswer(), poolBIO=poolBIO.GetAnswer(),
                       poolIOM=poolIOM.GetAnswer())

    xml = None
    if xmlParam.GetAnswer():
        xml = vtkTAG2ERothCModelParameter()
        xml.SetFileName(xmlParam.GetAnswer())
        xml.Read()
        xml.GenerateInternalSchemeFromXML()

    RothCModelRun(mapmatrix, pools, clayContent.GetAnswer(), soc.GetAnswer(),
                  baseName.GetAnswer(), xml, -99999, bool(init.Overwrite()))

    return 0

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

    joiner.AddInputConnection(poolBIOreader.GetOutputPort())

    names = vtkStringArray()
    names.InsertNextValue(poolIOM)
    poolIOMreader = vtkGRASSMultiRasterPolyDataLineReader()
    poolIOMreader.SetRasterNames(names)
    poolIOMreader.SetDataName("IOM")
    poolIOMreader.SetLineLengths(lineLengths)

    joiner.AddInputConnection(poolIOMreader.GetOutputPort())
    joiner.Update()

    print joiner.GetOutput()
    return joiner.GetOutput()

################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()

#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: i.n2o.freibauer
#
# Purpose: Estimation of n2o emission in agriculture using the freibauer approach
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

#include the VTK and vtkGRASSBridge Python libraries
from vtk import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *

def main():
    # Initiate GRASS
    init = vtkGRASSInit()
    init.Init("i.n2o.freibauer")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Estimation of n2o emission in agriculture using the freibauer approach")
    module.AddKeyword("raster")


    nrate = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType(), "nrate")
    nrate.SetDescription("The Nitrogen fertilization rate raster map")

    sand = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType(), "sand")
    sand.SetDescription("The sand fraction raster map in percent")

    soilC = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType(), "csoil")
    soilC.SetDescription("The oranic carbon soil fraction raster map in percent")

    soilN =vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType(), "nsoil")
    soilN.SetDescription("The soil nitrogen fraction raster map in percent")

    croptype = vtkGRASSOption()
    croptype.SetKey("croptype")
    croptype.MultipleOff()
    croptype.RequiredOff()
    croptype.SetDefaultAnswer("grass")
    croptype.SetDefaultOptions("grass,other")
    croptype.SetDescription("The crop type")
    croptype.SetTypeToString()
    
    climate = vtkGRASSOption()
    climate.SetKey("climate")
    climate.MultipleOff()
    climate.RequiredOff()
    climate.SetDefaultAnswer("temperate")
    climate.SetDefaultOptions("subboreal,temperate")
    climate.SetDescription("The climate type")
    climate.SetTypeToString()

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    output.SetDescription("The N2O emission estimation")

    threads = vtkGRASSOption()
    threads.SetKey("numthreads")
    threads.SetDescription("Number of threads to process the data")
    threads.RequiredOff()
    threads.MultipleOff()
    threads.SetTypeToInteger()
    threads.SetDefaultAnswer("2")

    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1

    messages = vtkGRASSMessagingInterface()

    messages.Message("Reading raster maps into memory")
    # Reader
    rnrate = vtkGRASSRasterImageReader()
    rnrate.SetRasterName(nrate.GetAnswer())
    rnrate.UseCurrentRegion()
    rnrate.SetNullValue(-999999)
    rnrate.ReadMapAsDouble()
    rnrate.UseNullValueOn()

    rsand = vtkGRASSRasterImageReader()
    rsand.SetRasterName(sand.GetAnswer())
    rsand.UseCurrentRegion()
    rsand.SetNullValue(-999999)
    rsand.ReadMapAsDouble()
    rsand.UseNullValueOn()

    rsoilC = vtkGRASSRasterImageReader()
    rsoilC.SetRasterName(soilC.GetAnswer())
    rsoilC.UseCurrentRegion()
    rsoilC.SetNullValue(-999999)
    rsoilC.ReadMapAsDouble()
    rsoilC.UseNullValueOn()

    rsoilN = vtkGRASSRasterImageReader()
    rsoilN.SetRasterName(soilN.GetAnswer())
    rsoilN.UseCurrentRegion()
    rsoilN.SetNullValue(-999999)
    rsoilN.ReadMapAsDouble()
    rsoilN.UseNullValueOn()

    messages.Message("Start N2O emission computation")
    
    model = vtkTAG2EImageDataN2OFilterFreibauer()
    model.SetNitrogenRate(rnrate.GetOutput())
    model.SetSandFraction(rsand.GetOutput())
    model.SetSoilOrganicCarbon(rsoilC.GetOutput())
    model.SetSoilNitrogen(rsoilN.GetOutput())
    model.SetNumberOfThreads(int(threads.GetAnswer()))
    if croptype.GetAnswer() == "grass":
        model.SetCropTypeToGrass()
    else:
        model.SetCropTypeToOther()
    if climate.GetAnswer() == "temperate":
        model.SetClimateTypeToTemperate()
    else:
        model.SetClimateTypeToSubBoreal()
    model.SetNullValue(rnrate.GetNullValue())
    model.Update()

    messages.Message("Writing result raster map")
    # Write the result as raster map
    writer = vtkGRASSRasterImageWriter()
    writer.SetInputConnection(model.GetOutputPort())
    writer.SetNullValue(rnrate.GetNullValue())
    writer.UseNullValueOn()
    writer.UseCurrentRegion()
    writer.SetRasterName(output.GetAnswer())
    writer.Update()


if __name__ == "__main__":
    main()

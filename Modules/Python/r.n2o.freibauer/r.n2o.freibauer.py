#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: r.n2o.freibauer
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
from libvtkFilteringPython import *
from libvtkImagingPython import *
from libvtkCommonPython import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *

def main():
    # Initiate GRASS
    init = vtkGRASSInit()
    init.Init("r.n2o.freibauer")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Estimation of n2o emission in agriculture using the freibauer approach")
    module.AddKeyword("raster")

    nrate = vtkGRASSOption()
    nrate.CreateOption_R_INPUT()
    nrate.SetKey("nrate")
    nrate.SetDescription("The Nitrogen fertilization rate rater map")

    sand = vtkGRASSOption()
    sand.CreateOption_R_INPUT()
    sand.SetKey("sand")
    sand.SetDescription("The sand fraction rater map in percent")

    soilC = vtkGRASSOption()
    soilC.CreateOption_R_INPUT()
    soilC.SetKey("csoil")
    soilC.SetDescription("The oranic carbon soil fraction raster map in percent")

    soilN = vtkGRASSOption()
    soilN.CreateOption_R_INPUT()
    soilN.SetKey("nsoil")
    soilN.SetDescription("The soil nitrogen fraction rater map in percent")

    croptype = vtkGRASSOption()
    croptype.CreateOption_R_INPUT()
    croptype.SetKey("croptype")
    croptype.SetDescription("The crop type")

    climate = vtkGRASSOption()
    climate.CreateOption_R_INPUT()
    climate.SetKey("climate")
    climate.SetDescription("The climate type")

    output = vtkGRASSOption()
    output.CreateOption_R_OUTPUT()
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

    init.Parser(paramter)

    messages = vtkGRASSMessagingInterface()

    messages.Message("Reading raster maps into memory")
    # Reader
    rnrate = vtkGRASSRasterImageReader()
    rnrate.SetRasterName(nrate.GetAnswer())
    rnrate.UseCurrentRegion()
    rnrate.SetNullValue(-999999)
    rnrate.UseNullValueOn()

    rsand = vtkGRASSRasterImageReader()
    rsand.SetRasterName(sand.GetAnswer())
    rsand.UseCurrentRegion()
    rsand.SetNullValue(-999999)
    rsand.UseNullValueOn()

    rsoilC = vtkGRASSRasterImageReader()
    rsoilC.SetRasterName(soilC.GetAnswer())
    rsoilC.UseCurrentRegion()
    rsoilC.SetNullValue(-999999)
    rsoilC.UseNullValueOn()

    rsoilN = vtkGRASSRasterImageReader()
    rsoilN.SetRasterName(soilN.GetAnswer())
    rsoilN.UseCurrentRegion()
    rsoilN.SetNullValue(-999999)
    rsoilN.UseNullValueOn()

    rcroptype = vtkGRASSRasterImageReader()
    rcroptype.SetRasterName(croptype.GetAnswer())
    rcroptype.UseCurrentRegion()
    rcroptype.SetNullValue(-999999)
    rcroptype.UseNullValueOn()

    rclimate = vtkGRASSRasterImageReader()
    rclimate.SetRasterName(climate.GetAnswer())
    rclimate.UseCurrentRegion()
    rclimate.SetNullValue(-999999)
    rclimate.UseNullValueOn()

    messages.Message("Start n2o emission computation")
    # The VTK filter
    model = vtkTAG2EFreibauerN2OEstimation()
    model.SetNitrogenRate(rnrate.GetOutput())
    model.SetSandFraction(rsand.GetOutput())
    model.SetSoilOrganicCorbonate(rsoilC.GetOutput())
    model.SetSoilNitrogen(rsoilN.GetOutput())
    model.SetCropType(rcroptype.GetOutput())
    model.SetClimateType(rclimate.GetOutput())
    model.SetNumberOfThreads(int(threads.GetAnswer()))
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

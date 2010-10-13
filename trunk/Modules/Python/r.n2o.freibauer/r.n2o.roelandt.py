#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: r.n2o.roelandt
#
# Purpose: Estimation of n2o emission in agriculture using the roelandt approach
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
    init.Init("r.n2o.roelandt")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Estimation of n2o emission in agriculture using the roelandt approach")
    module.AddKeyword("raster")

    nrate = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType(), "nrate")
    nrate.SetDescription("The Nitrogen fertilization rate raster map")

    T_win = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType(), "twinter")
    T_win.SetDescription("The mean temperature of jan, feb and mar")

    T_spring = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType(), "tspring")
    T_spring.SetDescription("The mean temperature of apr, may and jun")

    P_sum =vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType(), "prec")
    P_sum.SetDescription("The summer precipitation")

    croptype = vtkGRASSOption()
    croptype.SetKey("croptype")
    croptype.MultipleOff()
    croptype.RequiredOff()
    croptype.SetDefaultAnswer("grass")
    croptype.SetDefaultOptions("grass,other")
    croptype.SetDescription("The crop type")
    croptype.SetTypeToString()

    categories = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterInputType(), "categories")
    categories.SetDescription("The categories")

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetRasterOutputType())
    output.SetDescription("The N2O emission estimation")

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
    rnrate.UseNullValueOn()
    rnrate.ReadMapAsDouble()
    rnrate.Update()
    rnrate.GetOutput().GetPointData().GetScalars().SetName(nrate.GetAnswer())

    dataset = vtkImageData()
    dataset.DeepCopy(rnrate.GetOutput())

    rT_win = vtkGRASSRasterImageReader()
    rT_win.SetRasterName(T_win.GetAnswer())
    rT_win.UseCurrentRegion()
    rT_win.SetNullValue(-999999)
    rT_win.UseNullValueOn()
    rT_win.ReadMapAsDouble()
    rT_win.Update()
    rT_win.GetOutput().GetPointData().GetScalars().SetName(T_win.GetAnswer())
    
    dataset.GetPointData().AddArray(rT_win.GetOutput().GetPointData().GetScalars())

    rT_spring = vtkGRASSRasterImageReader()
    rT_spring.SetRasterName(T_spring.GetAnswer())
    rT_spring.UseCurrentRegion()
    rT_spring.SetNullValue(-999999)
    rT_spring.UseNullValueOn()
    rT_spring.ReadMapAsDouble()
    rT_spring.Update()
    rT_spring.GetOutput().GetPointData().GetScalars().SetName(T_spring.GetAnswer())

    dataset.GetPointData().AddArray(rT_spring.GetOutput().GetPointData().GetScalars())

    rP_sum = vtkGRASSRasterImageReader()
    rP_sum.SetRasterName(P_sum.GetAnswer())
    rP_sum.UseCurrentRegion()
    rP_sum.SetNullValue(-999999)
    rP_sum.UseNullValueOn()
    rP_sum.ReadMapAsDouble()
    rP_sum.Update()
    rP_sum.GetOutput().GetPointData().GetScalars().SetName(P_sum.GetAnswer())

    dataset.GetPointData().AddArray(rP_sum.GetOutput().GetPointData().GetScalars())

    rcategories = vtkGRASSRasterImageReader()
    rcategories.SetRasterName(categories.GetAnswer())
    rcategories.UseCurrentRegion()
    rcategories.SetNullValue(-999999)
    rcategories.UseNullValueOn()
    rcategories.ReadMapAsDouble()
    rcategories.Update()
    rcategories.GetOutput().GetPointData().GetScalars().SetName(categories.GetAnswer())

    dataset.GetPointData().AddArray(rcategories.GetOutput().GetPointData().GetScalars())

    messages.Message("Start N2O emission computation")

    model = vtkTAG2EDataSetN2OFilterRoelandt()
    model.SetInput(dataset)
    model.SetNitrogenRateArrayName(nrate.GetAnswer())
    model.SetTempWinterArrayName(T_win.GetAnswer())
    model.SetTempSpringArrayName(T_spring.GetAnswer())
    model.SetPrecipitationSumArrayName(P_sum.GetAnswer())
    if croptype.GetAnswer() == "grass":
        model.SetCropTypeToGrass()
    else:
        model.SetCropTypeToOther()
    model.SetCategoryArrayName(categories.GetAnswer())
    model.SetNullValue(rnrate.GetNullValue())
    model.UsePointDataOn()
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

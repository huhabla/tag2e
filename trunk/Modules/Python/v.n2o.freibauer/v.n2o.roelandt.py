#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: r.n2o.freibauer
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
from libvtkIOPython import *
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

    input = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorInputType())

    feature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorFeatureType())
    feature.SetDefaultOptions("point,centroid,area")
    feature.SetDefaultAnswer("area")
    feature.MultipleOff()
    
    nrate = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "nrate")
    nrate.SetDescription("The Nitrogen fertilization rate column name (N kg/ha)")

    T_win = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "twinter")
    T_win.SetDescription("The mean temperature of jan, feb and mar column name (C)")

    T_spring = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "tspring")
    T_spring.SetDescription("The mean temperature of apr, may and jun column name (C)")

    P_sum =vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "prec")
    P_sum.SetDescription("The summer precipitation  column name (mm)")

    croptype = vtkGRASSOption()
    croptype.SetKey("croptype")
    croptype.MultipleOff()
    croptype.RequiredOff()
    croptype.SetDefaultAnswer("grass")
    croptype.SetDefaultOptions("grass,other")
    croptype.SetDescription("The crop type")
    croptype.SetTypeToString()

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorOutputType())
    output.SetDescription("The N2O emission estimation")

    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1

    messages = vtkGRASSMessagingInterface()

    columns = vtkStringArray()
    columns.InsertNextValue(nrate.GetAnswer())
    columns.InsertNextValue(T_win.GetAnswer())
    columns.InsertNextValue(T_spring.GetAnswer())
    columns.InsertNextValue(P_sum.GetAnswer())
    columns.InsertNextValue("cat")

    messages.Message("Reading vector map into memory")
    # Reader
    dataset = vtkGRASSVectorTopoPolyDataReader()
    dataset.SetVectorName(input.GetAnswer())
    dataset.SetColumnNames(columns)
    if feature.GetAnswer() == "point":
        dataset.SetFeatureTypeToPoint()
    if feature.GetAnswer() == "centroid" or feature.GetAnswer() == "area":
        dataset.SetFeatureTypeToCentroid()
    dataset.Update()

    messages.Message("Start N2O emission computation")

    model = vtkTAG2EDataSetN2OFilterRoelandt()
    model.SetInput(dataset.GetOutput())
    model.SetNitrogenRateArrayName(nrate.GetAnswer())
    model.SetTempWinterArrayName(T_win.GetAnswer())
    model.SetTempSpringArrayName(T_spring.GetAnswer())
    model.SetPrecipitationSumArrayName(P_sum.GetAnswer())
    if croptype.GetAnswer() == "grass":
        model.SetCropTypeToGrass()
    else:
        model.SetCropTypeToOther()
    model.SetCategoryArrayName("cat")
    model.UsePointDataOff()
    model.Update()
    
    writer = vtkXMLPolyDataWriter()
    writer.SetInput(model.GetOutput())
    writer.SetFileName("/tmp/1.vtp")
    writer.Write()
    
    messages.Message("Writing result vector map")
    
    # Areas must be treated in a specific way to garant correct topology
    if feature.GetAnswer() == "area":
        columns = vtkStringArray()
        columns.InsertNextValue("cat")
        # Read the centroids
        boundaries = vtkGRASSVectorTopoPolyDataReader()
        boundaries.SetVectorName(input.GetAnswer())
        boundaries.SetColumnNames(columns)
        boundaries.SetFeatureTypeToBoundary()
        
        writer = vtkGRASSVectorPolyDataAreaWriter()
        writer.SetInputConnection(0, boundaries.GetOutputPort())
        writer.SetInputConnection(1, model.GetOutputPort())
        writer.SetVectorName(output.GetAnswer())
        writer.BuildTopoOn()
        writer.Update()     
    else:
        # Write the result as vector map
        writer = vtkGRASSVectorPolyDataWriter()
        writer.SetInputConnection(model.GetOutputPort())
        writer.SetVectorName(output.GetAnswer())
        writer.BuildTopoOn()
        writer.Update()

if __name__ == "__main__":
    main()

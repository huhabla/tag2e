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
from vtk import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *

def main():
    # Initiate GRASS
    init = vtkGRASSInit()
    init.Init("v.n2o.freibauer")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Estimation of n2o emission in agriculture using the freibauer approach")
    module.AddKeyword("raster")

    input = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorInputType())

    feature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorFeatureType())
    feature.SetDefaultOptions("point,centroid,area")
    feature.SetDefaultAnswer("area")
    feature.MultipleOff()
    
    nrate = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "nrate")
    nrate.SetDescription("The Nitrogen fertilization rate column name (%)")

    sand = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "sand")
    sand.SetDescription("The sand fraction rater column name (%)")

    soilC = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "csoil")
    soilC.SetDescription("The organic carbon soil fraction  column name (%)")

    soilN =vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "nsoil")
    soilN.SetDescription("The soil nitrogen fraction  column name (%)")

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

    output = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorOutputType())
    output.SetDescription("The N2O emission estimation output map")

    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1

    messages = vtkGRASSMessagingInterface()

    columns = vtkStringArray()
    columns.InsertNextValue(nrate.GetAnswer())
    columns.InsertNextValue(sand.GetAnswer())
    columns.InsertNextValue(soilC.GetAnswer())
    columns.InsertNextValue(soilN.GetAnswer())
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

    messages.Message("Start N2O emission computation")

    model = vtkTAG2EDataSetN2OFilterFreibauer()
    model.SetInputConnection(dataset.GetOutputPort())
    model.SetNitrogenRateArrayName(nrate.GetAnswer())
    model.SetSandFractionArrayName(sand.GetAnswer())
    model.SetSoilOrganicCarbonArrayName(soilC.GetAnswer())
    model.SetSoilNitrogenArrayName(soilN.GetAnswer())
    model.SetCategoryArrayName("cat")
    if croptype.GetAnswer() == "grass":
        model.SetCropTypeToGrass()
    else:
        model.SetCropTypeToOther()
    if climate.GetAnswer() == "temperate":
        model.SetClimateTypeToTemperate()
    else:
        model.SetClimateTypeToSubBoreal()
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

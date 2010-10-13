#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: r.n2o.freibauer
#
# Purpose: Estimation of n2o emission in agriculture using the stehfest approach
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
    init.Init("r.n2o.stehfest")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Estimation of n2o emission in agriculture using the stehfest approach")
    module.AddKeyword("raster")

    input = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorInputType())

    feature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorFeatureType())
    feature.SetDefaultOptions("point,centroid,area")
    feature.SetDefaultAnswer("area")
    feature.MultipleOff()
    
    nrate = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "nrate")
    nrate.SetDescription("The Nitrogen fertilization rate column name (N Kg/ha)")

    silt = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "silt")
    silt.SetDescription("The silt fraction  column name (%)")

    clay = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "clay")
    clay.SetDescription("The clay fraction  column name (%)")

    soilC = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "csoil")
    soilC.SetDescription("The oranic carbon soil fraction column name (%)")

    soilN =vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "nsoil")
    soilN.SetDescription("The soil nitrogen fraction column name (%)")

    pH =vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "ph")
    pH.SetDescription("The pH of the upper value")

    croptype = vtkGRASSOption()
    croptype.SetKey("croptype")
    croptype.MultipleOff()
    croptype.RequiredOff()
    croptype.SetDefaultAnswer("grass")
    croptype.SetDefaultOptions("grass,cereals,fallow,legume,roots,vegt,other")
    croptype.SetDescription("The crop type")
    croptype.SetTypeToString()
    
    climate = vtkGRASSOption()
    climate.SetKey("climate")
    climate.MultipleOff()
    climate.RequiredOff()
    climate.SetDefaultAnswer("boreal")
    climate.SetDefaultOptions("boreal,continental,oceanic,subtropic,tropic")
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
    columns.InsertNextValue(silt.GetAnswer())
    columns.InsertNextValue(clay.GetAnswer())
    columns.InsertNextValue(pH.GetAnswer())
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
    dataset.Update()

    messages.Message("Start N2O emission computation")

    model = vtkTAG2EDataSetN2OFilterStehfest()
    model.SetInput(dataset.GetOutput())
    model.SetNitrogenRateArrayName(nrate.GetAnswer())
    model.SetSiltFractionArrayName(silt.GetAnswer())
    model.SetClayFractionArrayName(clay.GetAnswer())
    model.SetSoilNitrogenArrayName(soilN.GetAnswer())
    model.SetSoilOrganicCarbonArrayName(soilC.GetAnswer())
    model.SetpHArrayName(pH.GetAnswer())
    model.SetCategoryArrayName("cat")
    model.UsePointDataOff()
    
    if croptype.GetAnswer() == "grass":
        model.SetCropTypeToGrass()
    elif croptype.GetAnswer() == "cereals":
        model.SetCropTypeToCereals()
    elif croptype.GetAnswer() == "fallow":
        model.SetCropTypeToFallow()
    elif croptype.GetAnswer() == "legume":
        model.SetCropTypeToLegume()
    elif croptype.GetAnswer() == "vegt":
        model.SetCropTypeToVegetables()
    else:
        model.SetCropTypeToOther()
        
    if climate.GetAnswer() == "continental":
        model.SetClimateTypeToContinental()
    elif climate.GetAnswer() == "oceanic":
        model.SetClimateTypeToOceanic()
    elif climate.GetAnswer() == "subtropic":
        model.SetClimateTypeToSubTropic()
    elif climate.GetAnswer() == "tropic":
        model.SetClimateTypeToTropic()
    else:
        model.SetClimateTypeToBoreal()
        
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

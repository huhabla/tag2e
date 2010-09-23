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

    input = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorInputType())

    nrate = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "nrate")
    nrate.SetDescription("The Nitrogen fertilization rate column name (%)")

    sand = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "sand")
    sand.SetDescription("The sand fraction rater column name (%)")

    soilC = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "csoil")
    soilC.SetDescription("The oranic carbon soil fraction  column name (%)")

    soilN =vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "nsoil")
    soilN.SetDescription("The soil nitrogen fraction  column name (%)")

    croptype = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "croptype")
    croptype.SetDescription("The crop type column name")

    climate = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "climate")
    climate.SetDescription("The climate type column name")

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
    columns.InsertNextValue(croptype.GetAnswer())
    columns.InsertNextValue(climate.GetAnswer())
    columns.InsertNextValue("cat")

    messages.Message("Reading vector map into memory")
    # Reader
    dataset = vtkGRASSVectorTopoPolyDataReader()
    dataset.SetVectorName(input.GetAnswer())
    dataset.SetColumnNames(columns)
    #dataset.SetFeatureTypeToCentroid()
    dataset.SetFeatureTypeToArea()
    dataset.Update()

    messages.Message("Start N2O emission computation")
    # The VTK filter
    model = vtkTAG2EDataSetN2OFilterFreibauer()
    model.SetInput(dataset.GetOutput())
    model.SetNitrogenRateArrayName(nrate.GetAnswer())
    model.SetSandFractionArrayName(sand.GetAnswer())
    model.SetSoilOrganicCorbonArrayName(soilC.GetAnswer())
    model.SetSoilNitrogenArrayName(soilN.GetAnswer())
    model.SetCropTypeArrayName(croptype.GetAnswer())
    model.SetClimateTypeArrayName(climate.GetAnswer())
    model.SetCategoryArrayName("cat")
    model.UsePointDataOff()
    model.Update()

    messages.Message("Writing result vector map")
    # Write the result as vector map
    writer = vtkGRASSVectorPolyDataWriter()
    writer.SetInputConnection(model.GetOutputPort())
    writer.SetVectorName(output.GetAnswer())
    writer.BuildTopoOn()
    writer.Update()


if __name__ == "__main__":
    main()

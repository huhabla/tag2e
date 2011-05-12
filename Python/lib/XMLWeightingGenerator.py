#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
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

#include the VTK and vtkGRASSBridge Python libraries
from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *


def BuildXML(factorName, numWeights, min, max, init=0):

    root  = vtk.vtkXMLDataElement()

    factor = vtkXMLDataElement()
    factor.SetName("Factor")
    factor.SetAttribute("name", factorName)

    weights = vtkXMLDataElement()
    weights.SetName("Weights")

    for i in range(numWeights):
        weight = vtkXMLDataElement()
        weight.SetName("Weight")
        weight.SetIntAttribute("id", i)
        weight.SetIntAttribute("const", 0)
        weight.SetIntAttribute("active", 0)
        weight.SetDoubleAttribute("min", min)
        weight.SetDoubleAttribute("max", max)
        weight.SetCharacterData(str(init), 6)
        weights.AddNestedElement(weight)

    root.SetName("Weighting")
    root.AddNestedElement(factor)
    root.AddNestedElement(weights)
    root.SetAttribute("name", "test")
    root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/Weighting")
    root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/Weighting http://tag2e.googlecode.com/files/Weighting.xsd")

    return root
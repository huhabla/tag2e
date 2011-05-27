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

from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeTemporalPython import *
from libvtkGRASSBridgeCommonPython import *

################################################################################
################################################################################
################################################################################

def ComputeDoubleArrayRange(array, noData):

    min, max = array.GetRange()

    if max == noData:
        max = min

    for i in range(array.GetNumberOfTuples()):
        val = array.GetValue(i)
        if val < min:
            min = val
        elif val != noData and val > max:
            max = val

    return min, max

################################################################################
################################################################################
################################################################################

def BuildXML5(factorNames, measureName, dataset, noData, useCellData=False):
    """Build a weighted fuzzy inference model with 5 fuzzy sets each factor.
    The initial fuzzy set values are computed based on min and max values."""

# Triangular test shape layout
#    _                _
#     \  /\  /\  /\  /
#      \/  \/  \/  \/
#      /\  /\  /\  /\
#     /  \/  \/  \/  \
#    0   25  50  75   100
#

    resp = vtkXMLDataElement()

    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")

    numberOfFuzzySets = 5
    numberOfRules = 1
    
    for i in range(len(factorNames)):
        numberOfRules *= numberOfFuzzySets

        if useCellData == False:
            min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(factorNames[i]), noData)
        else:
            min, max = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(factorNames[i]), noData)
        mean = (max - min)/4.0

        # Generate the initial shapes automatically

        shapeL = [9999, min, mean]
        shapeI1 = [mean, min + mean, mean]
        shapeI2 = [mean, min + mean + mean, mean]
        shapeI3 = [mean, min + mean + mean + mean, mean]
        shapeR = [mean, max, 9999]

        fs1 = vtkXMLDataElement()
        fs2 = vtkXMLDataElement()
        fs3 = vtkXMLDataElement()
        fs4 = vtkXMLDataElement()
        fs5 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr2 = vtkXMLDataElement()
        tr3 = vtkXMLDataElement()
        tr4 = vtkXMLDataElement()
        tr5 = vtkXMLDataElement()
        fss = vtkXMLDataElement()

        tr1.SetName("Triangular")
        tr1.SetDoubleAttribute("left",   shapeL[0])
        tr1.SetDoubleAttribute("center", shapeL[1])
        tr1.SetDoubleAttribute("right",  shapeL[2])

        tr2.SetName("Triangular")
        tr2.SetDoubleAttribute("left",    shapeI1[0])
        tr2.SetDoubleAttribute("center",  shapeI1[1])
        tr2.SetDoubleAttribute("right",   shapeI1[2])

        tr3.SetName("Triangular")
        tr3.SetDoubleAttribute("left",    shapeI2[0])
        tr3.SetDoubleAttribute("center",  shapeI2[1])
        tr3.SetDoubleAttribute("right",   shapeI2[2])

        tr4.SetName("Triangular")
        tr4.SetDoubleAttribute("left",    shapeI3[0])
        tr4.SetDoubleAttribute("center",  shapeI3[1])
        tr4.SetDoubleAttribute("right",   shapeI3[2])

        tr5.SetName("Triangular")
        tr5.SetDoubleAttribute("left",    shapeR[0])
        tr5.SetDoubleAttribute("center",  shapeR[1])
        tr5.SetDoubleAttribute("right",   shapeR[2])

        fs1.SetName("FuzzySet")
        fs1.SetAttribute("type", "Triangular")
        fs1.SetIntAttribute("priority", 0)
        fs1.SetIntAttribute("const", 0)
        fs1.SetAttribute("position", "left")
        fs1.AddNestedElement(tr1)

        fs2.SetName("FuzzySet")
        fs2.SetAttribute("type", "Triangular")
        fs2.SetIntAttribute("priority", 0)
        fs2.SetIntAttribute("const", 0)
        fs2.SetAttribute("position", "intermediate")
        fs2.AddNestedElement(tr2)

        fs3.SetName("FuzzySet")
        fs3.SetAttribute("type", "Triangular")
        fs3.SetIntAttribute("priority", 0)
        fs3.SetIntAttribute("const", 0)
        fs3.SetAttribute("position", "intermediate")
        fs3.AddNestedElement(tr3)

        fs4.SetName("FuzzySet")
        fs4.SetAttribute("type", "Triangular")
        fs4.SetIntAttribute("priority", 0)
        fs4.SetIntAttribute("const", 0)
        fs4.SetAttribute("position", "intermediate")
        fs4.AddNestedElement(tr4)

        fs5.SetName("FuzzySet")
        fs5.SetAttribute("type", "Triangular")
        fs5.SetIntAttribute("priority", 0)
        fs5.SetIntAttribute("const", 0)
        fs5.SetAttribute("position", "right")
        fs5.AddNestedElement(tr5)

        fss.SetName("Factor")
        fss.SetIntAttribute("portId", 0)
        fss.SetAttribute("name", factorNames[i])
        fss.SetDoubleAttribute("min", min)
        fss.SetDoubleAttribute("max",  max)
        fss.AddNestedElement(fs1)
        fss.AddNestedElement(fs2)
        fss.AddNestedElement(fs3)
        fss.AddNestedElement(fs4)
        fss.AddNestedElement(fs5)

        fuzzyRoot.AddNestedElement(fss)

    if useCellData == False:
        min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(measureName), noData)
    else:
        min, max = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(measureName), noData)

    print "Using ", numberOfRules, " number of rules "

    resp.SetName("Responses")
    resp.SetDoubleAttribute("min", min)
    resp.SetDoubleAttribute("max", max)

    for i in range(numberOfRules):
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(0), 6)

        resp.AddNestedElement(rval)

    fuzzyRoot.AddNestedElement(resp)
    fuzzyRoot.SetAttribute("name", "Test")
    fuzzyRoot.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
    fuzzyRoot.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    fuzzyRoot.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
    
    return fuzzyRoot

################################################################################
################################################################################
################################################################################

def BuildXML4(factorNames, measureName, dataset, noData, useCellData=False):
    """Build a weighted fuzzy inference model with 4 fuzzy sets each factor.
    The initial fuzzy set values are computed based on min and max values."""

# Triangular test shape layout
#    _            _
#     \  /\  /\  /
#      \/  \/  \/
#      /\  /\  /\
#     /  \/  \/  \
#    0   33  66   100
#

    resp = vtkXMLDataElement()

    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")
    
    numberOfFuzzySets = 4
    numberOfRules = 1
    
    for i in range(len(factorNames)):
        numberOfRules *= numberOfFuzzySets

        if useCellData == False:
            min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(factorNames[i]), noData)
        else:
            min, max = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(factorNames[i]), noData)
        mean = (max - min)/3.0

        # Generate the initial shapes automatically

        shapeL = [9999, min, mean]
        shapeI1 = [mean, min + mean, mean]
        shapeI2 = [mean, min + mean + mean, mean]
        shapeR = [mean, max, 9999]

        fs1 = vtkXMLDataElement()
        fs2 = vtkXMLDataElement()
        fs3 = vtkXMLDataElement()
        fs4 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr2 = vtkXMLDataElement()
        tr3 = vtkXMLDataElement()
        tr4 = vtkXMLDataElement()
        fss = vtkXMLDataElement()

        tr1.SetName("Triangular")
        tr1.SetDoubleAttribute("left",   shapeL[0])
        tr1.SetDoubleAttribute("center", shapeL[1])
        tr1.SetDoubleAttribute("right",  shapeL[2])

        tr2.SetName("Triangular")
        tr2.SetDoubleAttribute("left",    shapeI1[0])
        tr2.SetDoubleAttribute("center",  shapeI1[1])
        tr2.SetDoubleAttribute("right",   shapeI1[2])

        tr3.SetName("Triangular")
        tr3.SetDoubleAttribute("left",    shapeI2[0])
        tr3.SetDoubleAttribute("center",  shapeI2[1])
        tr3.SetDoubleAttribute("right",   shapeI2[2])

        tr4.SetName("Triangular")
        tr4.SetDoubleAttribute("left",    shapeR[0])
        tr4.SetDoubleAttribute("center",  shapeR[1])
        tr4.SetDoubleAttribute("right",   shapeR[2])

        fs1.SetName("FuzzySet")
        fs1.SetAttribute("type", "Triangular")
        fs1.SetIntAttribute("priority", 0)
        fs1.SetIntAttribute("const", 0)
        fs1.SetAttribute("position", "left")
        fs1.AddNestedElement(tr1)

        fs2.SetName("FuzzySet")
        fs2.SetAttribute("type", "Triangular")
        fs2.SetIntAttribute("priority", 0)
        fs2.SetIntAttribute("const", 0)
        fs2.SetAttribute("position", "intermediate")
        fs2.AddNestedElement(tr2)

        fs3.SetName("FuzzySet")
        fs3.SetAttribute("type", "Triangular")
        fs3.SetIntAttribute("priority", 0)
        fs3.SetIntAttribute("const", 0)
        fs3.SetAttribute("position", "intermediate")
        fs3.AddNestedElement(tr3)

        fs4.SetName("FuzzySet")
        fs4.SetAttribute("type", "Triangular")
        fs4.SetIntAttribute("priority", 0)
        fs4.SetIntAttribute("const", 0)
        fs4.SetAttribute("position", "right")
        fs4.AddNestedElement(tr4)

        fss.SetName("Factor")
        fss.SetIntAttribute("portId", 0)
        fss.SetAttribute("name", factorNames[i])
        fss.SetDoubleAttribute("min", min)
        fss.SetDoubleAttribute("max",  max)
        fss.AddNestedElement(fs1)
        fss.AddNestedElement(fs2)
        fss.AddNestedElement(fs3)
        fss.AddNestedElement(fs4)

        fuzzyRoot.AddNestedElement(fss)

    if useCellData == False:
        min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(measureName), noData)
    else:
        min, max = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(measureName), noData)

    print "Using ", numberOfRules, " number of rules "

    resp.SetName("Responses")
    resp.SetDoubleAttribute("min", min)
    resp.SetDoubleAttribute("max", max)

    for i in range(numberOfRules):
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(0), 6)

        resp.AddNestedElement(rval)

    fuzzyRoot.AddNestedElement(resp)
    fuzzyRoot.SetAttribute("name", "Test")
    fuzzyRoot.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
    fuzzyRoot.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    fuzzyRoot.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")

    return fuzzyRoot

################################################################################
################################################################################
################################################################################

def BuildXML3(factorNames, measureName, dataset, noData, useCellData=False):
    """Build a weighted fuzzy inference model with 3 fuzzy sets each factor.
    The initial fuzzy set values are computed based on min and max values."""

# Triangular test shape layout
#   _        _
#    \  /\  /
#     \/  \/
#     /\  /\
#    /  \/  \
#   0   50  100
#

    resp = vtkXMLDataElement()
    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")

    numberOfFuzzySets = 3
    numberOfRules = 1
    
    for i in range(len(factorNames)):
        numberOfRules *= numberOfFuzzySets

        if useCellData == False:
            min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(factorNames[i]), noData)
        else:
            min, max = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(factorNames[i]), noData)
        mean = (max - min)/2.0

        # Generate the initial shapes automatically

        shapeL = [9999, min, mean]
        shapeI = [mean, min + mean, mean]
        shapeR = [mean, max, 9999]

        fs1 = vtkXMLDataElement()
        fs2 = vtkXMLDataElement()
        fs3 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr2 = vtkXMLDataElement()
        tr3 = vtkXMLDataElement()
        fss = vtkXMLDataElement()

        tr1.SetName("Triangular")
        tr1.SetDoubleAttribute("left",   shapeL[0])
        tr1.SetDoubleAttribute("center", shapeL[1])
        tr1.SetDoubleAttribute("right",  shapeL[2])

        tr2.SetName("Triangular")
        tr2.SetDoubleAttribute("left",    shapeI[0])
        tr2.SetDoubleAttribute("center",  shapeI[1])
        tr2.SetDoubleAttribute("right",   shapeI[2])

        tr3.SetName("Triangular")
        tr3.SetDoubleAttribute("left",    shapeR[0])
        tr3.SetDoubleAttribute("center",  shapeR[1])
        tr3.SetDoubleAttribute("right",   shapeR[2])

        fs1.SetName("FuzzySet")
        fs1.SetAttribute("type", "Triangular")
        fs1.SetIntAttribute("priority", 0)
        fs1.SetIntAttribute("const", 0)
        fs1.SetAttribute("position", "left")
        fs1.AddNestedElement(tr1)

        fs2.SetName("FuzzySet")
        fs2.SetAttribute("type", "Triangular")
        fs2.SetIntAttribute("priority", 0)
        fs2.SetIntAttribute("const", 0)
        fs2.SetAttribute("position", "intermediate")
        fs2.AddNestedElement(tr2)

        fs3.SetName("FuzzySet")
        fs3.SetAttribute("type", "Triangular")
        fs3.SetIntAttribute("priority", 0)
        fs3.SetIntAttribute("const", 0)
        fs3.SetAttribute("position", "right")
        fs3.AddNestedElement(tr3)

        fss.SetName("Factor")
        fss.SetIntAttribute("portId", 0)
        fss.SetAttribute("name", factorNames[i])
        fss.SetDoubleAttribute("min", min)
        fss.SetDoubleAttribute("max",  max)
        fss.AddNestedElement(fs1)
        fss.AddNestedElement(fs2)
        fss.AddNestedElement(fs3)

        fuzzyRoot.AddNestedElement(fss)

    if useCellData == False:
        min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(measureName), noData)
    else:
        min, max = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(measureName), noData)

        
    resp.SetName("Responses")
    resp.SetDoubleAttribute("min", min)
    resp.SetDoubleAttribute("max", max)

    print "Using ", numberOfRules, " number of rules "

    for i in range(numberOfRules):
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(0), 6)

        resp.AddNestedElement(rval)

    fuzzyRoot.AddNestedElement(resp)
    fuzzyRoot.SetAttribute("name", "Test")
    fuzzyRoot.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
    fuzzyRoot.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    fuzzyRoot.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")

    return fuzzyRoot

################################################################################
################################################################################
################################################################################

def BuildXML2(factorNames, measureName, dataset, noData, useCellData=False):

# Triangular test shape layout
#   _    _
#    \  /
#     \/
#     /\ 
#    /  \
#   0    100
#

    resp = vtkXMLDataElement()
    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")
    
    numberOfFuzzySets = 2
    numberOfRules = 1
    
    for i in range(len(factorNames)):
        numberOfRules *= numberOfFuzzySets

        if useCellData == False:
            min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(factorNames[i]), noData)
        else:
            min, max = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(factorNames[i]), noData)

        # Generate the initial shapes automatically

        shapeL = [min, 9999, max - min]
        shapeR = [max, max - min, 9999]

        fs1 = vtkXMLDataElement()
        fs3 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr3 = vtkXMLDataElement()
        fss = vtkXMLDataElement()

        tr1.SetName("Triangular")
        tr1.SetDoubleAttribute("center", shapeL[0])
        tr1.SetDoubleAttribute("left",   shapeL[1])
        tr1.SetDoubleAttribute("right",  shapeL[2])

        tr3.SetName("Triangular")
        tr3.SetDoubleAttribute("center",  shapeR[0])
        tr3.SetDoubleAttribute("left",    shapeR[1])
        tr3.SetDoubleAttribute("right",   shapeR[2])

        fs1.SetName("FuzzySet")
        fs1.SetAttribute("type", "Triangular")
        fs1.SetIntAttribute("priority", 0)
        fs1.SetIntAttribute("const", 0)
        fs1.SetAttribute("position", "left")
        fs1.AddNestedElement(tr1)

        fs3.SetName("FuzzySet")
        fs3.SetAttribute("type", "Triangular")
        fs3.SetIntAttribute("priority", 0)
        fs3.SetIntAttribute("const", 0)
        fs3.SetAttribute("position", "right")
        fs3.AddNestedElement(tr3)

        fss.SetName("Factor")
        fss.SetIntAttribute("portId", 0)
        fss.SetAttribute("name", factorNames[i])
        fss.SetDoubleAttribute("min", min)
        fss.SetDoubleAttribute("max",  max)
        fss.AddNestedElement(fs1)
        fss.AddNestedElement(fs3)

        fuzzyRoot.AddNestedElement(fss)

    if useCellData == False:
        min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(measureName), noData)
    else:
        min, max = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(measureName), noData)

    resp.SetName("Responses")
    resp.SetDoubleAttribute("min", min)
    resp.SetDoubleAttribute("max", max)

    print "Using ", numberOfRules, " number of rules "

    for i in range(numberOfRules):
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(0), 6)

        resp.AddNestedElement(rval)

    fuzzyRoot.AddNestedElement(resp)
    fuzzyRoot.SetAttribute("name", "Test")
    fuzzyRoot.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
    fuzzyRoot.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    fuzzyRoot.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")

    return fuzzyRoot

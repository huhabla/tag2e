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
from libvtkGRASSBridgeCommonPython import *

################################################################################
################################################################################
################################################################################

def ComputeDoubleArrayRange(array, noData):

    min, max = array.GetRange()
    
    sum = 0.0

    """We assume that no data is always the maximum value"""
    if max == noData:
        max = min

    for i in range(array.GetNumberOfTuples()):
        val = array.GetValue(i)
	if val != noData:
            sum += val
        if val < min:
            min = val
        elif val != noData and val > max:
            max = val

    return min, max, sum/array.GetNumberOfTuples()

################################################################################
################################################################################
################################################################################

def BuildXML(factorNames, fuzzySetNum, measureName, dataset, noData, useCellData=False):
    """Build a weighted fuzzy inference model with fuzzy sets of different size for each factor.
    The initial fuzzy set values are computed based on min and max values."""

    resp = vtkXMLDataElement()

    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")

    numberOfRules = 1
    
    for i in range(len(factorNames)):
        numberOfRules *= fuzzySetNum[i]

        if useCellData == False:
            min, max, rmean = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(factorNames[i]), noData)
        else:
            min, max, rmean = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(factorNames[i]), noData)

        # Generate the initial shapes automatically
        if fuzzySetNum[i] == 2:
            fuzzyRoot.AddNestedElement(GenerateFactor2(factorNames[i], min, max, 0.0))
        if fuzzySetNum[i] == 3:
            mean = (max - min)/2.0
            fuzzyRoot.AddNestedElement(GenerateFactor3(factorNames[i], min, max, mean))
        if fuzzySetNum[i] == 4:
            mean = (max - min)/3.0
            fuzzyRoot.AddNestedElement(GenerateFactor4(factorNames[i], min, max, mean))
        if fuzzySetNum[i] == 5:
            mean = (max - min)/4.0
            fuzzyRoot.AddNestedElement(GenerateFactor5(factorNames[i], min, max, mean))

    if useCellData == False:
        min, max, rmean = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(measureName), noData)
    else:
        min, max, rmean = ComputeDoubleArrayRange(dataset.GetCellData().GetArray(measureName), noData)

    print "Using ", numberOfRules, " number of rules "
    print "Responses: min: %g max: %g rmean: %g"%(min, max, rmean)

    resp.SetName("Responses")
    resp.SetAttribute("min", "%.15f" % min)
    resp.SetAttribute("max", "%.15f" % max)

    for i in range(numberOfRules):
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(rmean), 15)

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

def GenerateFactor5(factorName, min, max, mean):
    """

    Triangular test shape layout
   _                _
    \  /\  /\  /\  /
     \/  \/  \/  \/
     /\  /\  /\  /\
    /  \/  \/  \/  \
    0   25  50  75   100


    """
    print "Generate 5 fuzzy sets"

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
    tr1.SetAttribute("left",   "%.15f" % shapeL[0])
    tr1.SetAttribute("center", "%.15f" % shapeL[1])
    tr1.SetAttribute("right",  "%.15f" % shapeL[2])

    tr2.SetName("Triangular")
    tr2.SetAttribute("left",    "%.15f" % shapeI1[0])
    tr2.SetAttribute("center",  "%.15f" % shapeI1[1])
    tr2.SetAttribute("right",   "%.15f" % shapeI1[2])

    tr3.SetName("Triangular")
    tr3.SetAttribute("left",    "%.15f" % shapeI2[0])
    tr3.SetAttribute("center",  "%.15f" % shapeI2[1])
    tr3.SetAttribute("right",   "%.15f" % shapeI2[2])

    tr4.SetName("Triangular")
    tr4.SetAttribute("left",    "%.15f" % shapeI3[0])
    tr4.SetAttribute("center",  "%.15f" % shapeI3[1])
    tr4.SetAttribute("right",   "%.15f" % shapeI3[2])

    tr5.SetName("Triangular")
    tr5.SetAttribute("left",    "%.15f" % shapeR[0])
    tr5.SetAttribute("center",  "%.15f" % shapeR[1])
    tr5.SetAttribute("right",   "%.15f" % shapeR[2])

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
    fss.SetAttribute("name", factorName)
    fss.SetAttribute("min", "%.15f" % min)
    fss.SetAttribute("max", "%.15f" % max)
    fss.AddNestedElement(fs1)
    fss.AddNestedElement(fs2)
    fss.AddNestedElement(fs3)
    fss.AddNestedElement(fs4)
    fss.AddNestedElement(fs5)

    return fss

################################################################################
################################################################################
################################################################################

def GenerateFactor4(factorName, min, max, mean):
    """

     Triangular test shape layout
        _            _
         \  /\  /\  /
          \/  \/  \/
          /\  /\  /\
         /  \/  \/  \
        0   33  66   100
    print "Generate 4 fuzzy sets"
    """
    print "Generate 4 fuzzy sets"

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
    tr1.SetAttribute("left",   "%.15f" % shapeL[0])
    tr1.SetAttribute("center", "%.15f" % shapeL[1])
    tr1.SetAttribute("right",  "%.15f" % shapeL[2])

    tr2.SetName("Triangular")
    tr2.SetAttribute("left",    "%.15f" % shapeI1[0])
    tr2.SetAttribute("center",  "%.15f" % shapeI1[1])
    tr2.SetAttribute("right",   "%.15f" % shapeI1[2])

    tr3.SetName("Triangular")
    tr3.SetAttribute("left",    "%.15f" % shapeI2[0])
    tr3.SetAttribute("center",  "%.15f" % shapeI2[1])
    tr3.SetAttribute("right",   "%.15f" % shapeI2[2])

    tr4.SetName("Triangular")
    tr4.SetAttribute("left",    "%.15f" % shapeR[0])
    tr4.SetAttribute("center",  "%.15f" % shapeR[1])
    tr4.SetAttribute("right",   "%.15f" % shapeR[2])

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
    fss.SetAttribute("name", factorName)
    fss.SetAttribute("min", "%.15f" % min)
    fss.SetAttribute("max", "%.15f" % max)
    fss.AddNestedElement(fs1)
    fss.AddNestedElement(fs2)
    fss.AddNestedElement(fs3)
    fss.AddNestedElement(fs4)

    return fss

################################################################################
################################################################################
################################################################################

def GenerateFactor3(factorName, min, max, mean):
    """
     Triangular test shape layout
       _        _
        \  /\  /
         \/  \/
         /\  /\
        /  \/  \
       0   50  100
    """
    print "Generate 3 fuzzy sets"

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
    tr1.SetAttribute("left",   "%.15f" % shapeL[0])
    tr1.SetAttribute("center", "%.15f" % shapeL[1])
    tr1.SetAttribute("right",  "%.15f" % shapeL[2])

    tr2.SetName("Triangular")
    tr2.SetAttribute("left",    "%.15f" % shapeI[0])
    tr2.SetAttribute("center",  "%.15f" % shapeI[1])
    tr2.SetAttribute("right",   "%.15f" % shapeI[2])

    tr3.SetName("Triangular")
    tr3.SetAttribute("left",    "%.15f" % shapeR[0])
    tr3.SetAttribute("center",  "%.15f" % shapeR[1])
    tr3.SetAttribute("right",   "%.15f" % shapeR[2])

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
    fss.SetAttribute("name", factorName)
    fss.SetAttribute("min", "%.15f" % min)
    fss.SetAttribute("max", "%.15f" % max)
    fss.AddNestedElement(fs1)
    fss.AddNestedElement(fs2)
    fss.AddNestedElement(fs3)

    return fss

################################################################################
################################################################################
################################################################################

def GenerateFactor2(factorName, min, max, mean):
    """
     Triangular test shape layout
       _    _
        \  /
         \/
         /\
        /  \
       0    100
       
    """
    print "Generate 2 fuzzy sets"

    shapeL = [min, 9999, max - min]
    shapeR = [max, max - min, 9999]

    fs1 = vtkXMLDataElement()
    fs3 = vtkXMLDataElement()
    tr1 = vtkXMLDataElement()
    tr3 = vtkXMLDataElement()
    fss = vtkXMLDataElement()

    tr1.SetName("Triangular")
    tr1.SetAttribute("center", "%.15f" % shapeL[0])
    tr1.SetAttribute("left",   "%.15f" % shapeL[1])
    tr1.SetAttribute("right",  "%.15f" % shapeL[2])

    tr3.SetName("Triangular")
    tr3.SetAttribute("center",  "%.15f" % shapeR[0])
    tr3.SetAttribute("left",    "%.15f" % shapeR[1])
    tr3.SetAttribute("right",   "%.15f" % shapeR[2])

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
    fss.SetAttribute("name", factorName)
    fss.SetAttribute("min", "%.15f" % min)
    fss.SetAttribute("max", "%.15f" % max)
    fss.AddNestedElement(fs1)
    fss.AddNestedElement(fs3)

    return fss

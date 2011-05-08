#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.
import random
import math

from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeFilteringPython import *
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

def BuildFuzzyXMLRepresentation5(factorNames, measureName, dataset, noData):
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

    root  = vtk.vtkXMLDataElement()
    resp = vtkXMLDataElement()
    weight = vtkXMLDataElement()

    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")

    for i in range(len(factorNames)):

        min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(factorNames[i]), noData)
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

    min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(measureName), noData)
        
    resp.SetName("Responses")
    resp.SetDoubleAttribute("min", min)
    resp.SetDoubleAttribute("max", max)

    for i in range(625):
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(0), 6)

        resp.AddNestedElement(rval)

    fuzzyRoot.AddNestedElement(resp)

    weight.SetName("Weight")
    weight.SetAttribute("name", "grass")
    weight.SetIntAttribute("active", 1)
    weight.SetIntAttribute("const", 1)
    weight.SetDoubleAttribute("min", 0)
    weight.SetDoubleAttribute("max", 10)
    weight.SetCharacterData("1", 1)

    root.SetName("WeightedFuzzyInferenceScheme")
    root.SetAttribute("name", "Test")
    root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
    root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
    root.AddNestedElement(fuzzyRoot)
    root.AddNestedElement(weight)
    
    return root

################################################################################
################################################################################
################################################################################

def BuildFuzzyXMLRepresentation4(factorNames, measureName, dataset, noData):
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

    root  = vtk.vtkXMLDataElement()
    resp = vtkXMLDataElement()
    weight = vtkXMLDataElement()

    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")

    for i in range(len(factorNames)):

        min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(factorNames[i]), noData)
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

    min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(measureName), noData)
        
    resp.SetName("Responses")
    resp.SetDoubleAttribute("min", min)
    resp.SetDoubleAttribute("max", max)

    for i in range(256):
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(0), 6)

        resp.AddNestedElement(rval)

    fuzzyRoot.AddNestedElement(resp)

    weight.SetName("Weight")
    weight.SetAttribute("name", "grass")
    weight.SetIntAttribute("active", 1)
    weight.SetIntAttribute("const", 1)
    weight.SetDoubleAttribute("min", 0)
    weight.SetDoubleAttribute("max", 10)
    weight.SetCharacterData("1", 1)

    root.SetName("WeightedFuzzyInferenceScheme")
    root.SetAttribute("name", "Test")
    root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
    root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
    root.AddNestedElement(fuzzyRoot)
    root.AddNestedElement(weight)
    
    return root

################################################################################
################################################################################
################################################################################

def BuildFuzzyXMLRepresentation3(factorNames, measureName, dataset, noData):
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

    root  = vtk.vtkXMLDataElement()
    resp = vtkXMLDataElement()
    weight = vtkXMLDataElement()

    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")

    for i in range(len(factorNames)):

        min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(factorNames[i]), noData)
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

    min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(measureName), noData)
        
    resp.SetName("Responses")
    resp.SetDoubleAttribute("min", min)
    resp.SetDoubleAttribute("max", max)

    for i in range(81):
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(0), 6)

        resp.AddNestedElement(rval)

    fuzzyRoot.AddNestedElement(resp)

    weight.SetName("Weight")
    weight.SetAttribute("name", "grass")
    weight.SetIntAttribute("active", 1)
    weight.SetIntAttribute("const", 1)
    weight.SetDoubleAttribute("min", 0)
    weight.SetDoubleAttribute("max", 10)
    weight.SetCharacterData("1", 1)

    root.SetName("WeightedFuzzyInferenceScheme")
    root.SetAttribute("name", "Test")
    root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
    root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
    root.AddNestedElement(fuzzyRoot)
    root.AddNestedElement(weight)
    
    return root

################################################################################
################################################################################
################################################################################

def BuildFuzzyXMLRepresentation2(factorNames, measureName, dataset, noData):

# Triangular test shape layout
#   _    _
#    \  /
#     \/
#     /\ 
#    /  \
#   0    100
#

    root  = vtk.vtkXMLDataElement()
    resp = vtkXMLDataElement()
    weight = vtkXMLDataElement()

    fuzzyRoot = vtkXMLDataElement()
    fuzzyRoot.SetName("FuzzyInferenceScheme")

    for i in range(len(factorNames)):

        min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(factorNames[i]), noData)

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

    min, max = ComputeDoubleArrayRange(dataset.GetPointData().GetArray(measureName), noData)
        
    resp.SetName("Responses")
    resp.SetDoubleAttribute("min", min)
    resp.SetDoubleAttribute("max", max)

    for i in range(16):
        rval = vtkXMLDataElement()
        rval.SetName("Response")
        rval.SetIntAttribute("const", 0)
        rval.SetIntAttribute("sd", 1)
        rval.SetCharacterData(str(0), 6)

        resp.AddNestedElement(rval)

    fuzzyRoot.AddNestedElement(resp)

    weight.SetName("Weight")
    weight.SetAttribute("name", "cropland")
    weight.SetIntAttribute("active", 1)
    weight.SetIntAttribute("const", 1)
    weight.SetDoubleAttribute("min", 0)
    weight.SetDoubleAttribute("max", 10)
    weight.SetCharacterData("1", 1)

    root.SetName("WeightedFuzzyInferenceScheme")
    root.SetAttribute("name", "Test")
    root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
    root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme http://tag2e.googlecode.com/files/WeightedFuzzyInferenceScheme.xsd")
    root.AddNestedElement(fuzzyRoot)
    root.AddNestedElement(weight)
    
    return root

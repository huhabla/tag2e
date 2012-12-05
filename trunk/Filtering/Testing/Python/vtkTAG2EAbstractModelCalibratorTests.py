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
import unittest
import random
import math

from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeCommonPython import *

################################################################################
################################################################################
################################################################################

class vtkTAG2EAbstractModelCalibratorTests(unittest.TestCase):
  
    def setUp(self):
        
        # Create the point data
        xext = 10
        yext = 1
        num = xext*yext

        self.ds = vtkPolyData()
        self.ds.Allocate(xext,yext)

        self.model = vtkDoubleArray()
        self.model.SetNumberOfTuples(num)
        self.model.SetName("model")
        
        self.measure = vtkDoubleArray()
        self.measure.SetNumberOfTuples(num)
        self.measure.SetName("measure")
        
        # Point ids for poly vertex cell
        points = vtkPoints()
        
        count = 0
        for i in range(xext):
            for j in range(yext):
                ids = vtkIdList()
                ids.InsertNextId(points.InsertNextPoint(i, j, 0))
                # Data range [1:100] -> linear function x
                self.model.SetValue(count, count + 1)
                self.measure.SetValue(count, count + 1)
                self.ds.InsertNextCell(vtk.VTK_VERTEX, ids)
                count += 1

        self.ds.GetPointData().SetScalars(self.model)
        self.ds.GetPointData().AddArray(self.measure)
        self.ds.GetCellData().SetScalars(self.model)
        self.ds.GetCellData().AddArray(self.measure)
        self.ds.SetPoints(points) 
        
        self._BuildXML()
        
    def _BuildXML(self):
        
        self.root  = vtk.vtkXMLDataElement()
        
        fss1 = vtkXMLDataElement()
        fs1 = vtkXMLDataElement()
        fs2 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr2 = vtkXMLDataElement()
        resp = vtkXMLDataElement()
        
# Triangular test shape layout
# ____    ____
#     \  /
#      \/ 
#      /\ 
#     /  \
#0  30 50 70  100
#
# - 1 -  - 3 - 
#
# 1: left = 101 center = 30 right = 40
# 2: left = 40  center = 70 right = 101
#       
        
        tr1.SetName("Triangular")
        tr1.SetDoubleAttribute("center", 30)
        tr1.SetDoubleAttribute("left",   101)
        tr1.SetDoubleAttribute("right",  40)
                
        tr2.SetName("Triangular")
        tr2.SetDoubleAttribute("center",  70)
        tr2.SetDoubleAttribute("left",    40)
        tr2.SetDoubleAttribute("right",   101)
        
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
        fs2.SetAttribute("position", "right")
        fs2.AddNestedElement(tr2)
        
        # A single factor
        fss1.SetName("Factor")
        fss1.SetIntAttribute("portId", 0)
        fss1.SetAttribute("name", "model")
        fss1.SetDoubleAttribute("min", 0.0)
        fss1.SetDoubleAttribute("max", 100.0)
        fss1.AddNestedElement(fs1)
        fss1.AddNestedElement(fs2)
                
        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 120)
        
        rval1 = vtkXMLDataElement()
        rval1.SetName("Response")
        rval1.SetIntAttribute("const", 0)
        rval1.SetIntAttribute("sd", 1)
        rval1.SetCharacterData(str(5), 6)
                
        rval2 = vtkXMLDataElement()
        rval2.SetName("Response")
        rval2.SetIntAttribute("const", 0)
        rval2.SetIntAttribute("sd", 1)
        rval2.SetCharacterData(str(5), 6)
        
        resp.AddNestedElement(rval1)
        resp.AddNestedElement(rval2)
                
        self.root.SetName("FuzzyInferenceScheme")
        self.root.AddNestedElement(fss1)
        self.root.AddNestedElement(resp)
        self.root.SetAttribute("name", "Test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/FuzzyInferenceScheme http://tag2e.googlecode.com/files/FuzzyInferenceScheme.xsd")
        
        
    def test1(self):
        
        self._BuildXML()

        # Set up the parameter and the model
        parameter = vtkTAG2EFuzzyInferenceModelParameter()
        parameter.SetXMLRepresentation(self.root)

        model = vtkTAG2EFuzzyInferenceModel()
        model.SetInput(self.ds)
        model.SetModelParameter(parameter)
        model.Update()

        caliModel = vtkTAG2EAbstractModelCalibrator()
        caliModel.SetInput(self.ds)
        caliModel.SetModel(model)
        caliModel.SetModelParameter(parameter)
        caliModel.Update()
        
        print vtkTAG2EAbstractModelCalibrator.ArithmeticMean(self.model)
        print vtkTAG2EAbstractModelCalibrator.ArithmeticMean(self.measure)
        
        print vtkTAG2EAbstractModelCalibrator.Variance(self.model, True, False)
        print vtkTAG2EAbstractModelCalibrator.Variance(self.measure, False, False)
        
        print vtkTAG2EAbstractModelCalibrator.StandardDeviation(self.model, True)
        print vtkTAG2EAbstractModelCalibrator.StandardDeviation(self.measure, False)
        
        print vtkTAG2EAbstractModelCalibrator.CompareDataSets(model.GetOutput(), 
                                                              "model", "measure", 
                                                              0, 1, False)
        print vtkTAG2EAbstractModelCalibrator.CompareDataSets(model.GetOutput(), 
                                                              "model", "measure", 
                                                              1, 1, True)

  
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EAbstractModelCalibratorTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 
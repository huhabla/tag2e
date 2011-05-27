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

from vtk import *

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeTemporalPython import *
from libvtkGRASSBridgeCommonPython import *

class vtkTAG2EWeightingModelParameterTests(unittest.TestCase):
  
    def setUp(self):

        self.root  = vtk.vtkXMLDataElement()
        
        factor = vtkXMLDataElement()
        factor.SetName("Factor")
        factor.SetAttribute("name", "cropcat")
        
        weights = vtkXMLDataElement()
        weights.SetName("Weights")

        for i in range(9):
            weight = vtkXMLDataElement()
            weight.SetName("Weight")
            weight.SetIntAttribute("id", i)
            weight.SetIntAttribute("const", 0)
            weight.SetIntAttribute("active", 0)
            weight.SetDoubleAttribute("min", 0)
            weight.SetDoubleAttribute("max", 10)
            weight.SetCharacterData(str(i), 6)
            weights.AddNestedElement(weight)
        
        self.root.SetName("Weighting")
        self.root.AddNestedElement(factor)
        self.root.AddNestedElement(weights)
        self.root.SetAttribute("name", "test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/Weighting")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/Weighting http://tag2e.googlecode.com/files/Weighting.xsd")
        
    def test2FuzzyXML(self):
        
        fisc = vtkTAG2EWeightingModelParameter()
        fisc.SetFileName("/tmp/Weighting1.xml")
        fisc.SetXMLRepresentation(self.root)
        fisc.Write()
        # Read/Write it again
        fisc.Read();
        fisc.SetFileName("/tmp/Weighting2.xml")
        fisc.Write()
             
    def test3FuzzyParameter(self):
        
        fisc = vtkTAG2EWeightingModelParameter()
        fisc.SetXMLRepresentation(self.root)
        
        for j in range(fisc.GetNumberOfCalibratableParameter()):
            print "Modify Parameter " + str(j)
            for i in range(10):
                fisc.ModifyParameter(j, 0.1*(j + 1)/2)
                print fisc.GetParameterValue(j)
  
                
        root = vtkXMLDataElement()
        fisc.GetXMLRepresentation(root)
        fisc.SetFileName("/tmp/Weighting3.xml")
        fisc.Write()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EWeightingModelParameterTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 

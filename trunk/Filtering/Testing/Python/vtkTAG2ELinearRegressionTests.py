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

class vtkTAG2EDFuzzyTest(unittest.TestCase):
    def testFuzzyXML(self):
        
        fisc = vtkTAG2EFuzzyInferenceModelParameter()
        
        root  = vtk.vtkXMLDataElement()
        
        intercept = vtkXMLDataElement()
        coefficient1 = vtkXMLDataElement()
        coefficient2 = vtkXMLDataElement()
        coefficient3 = vtkXMLDataElement()
        coefficient4 = vtkXMLDataElement()
        
        intercept.SetName("Intercept")
        intercept.SetCharacterData("0.6", 5)
        
        coefficient1.SetName("Coefficient")
        coefficient1.SetAttribute("name", "nrate")
        coefficient1.SetCharacterData("0.002", 5)
        
        coefficient2.SetName("Coefficient")
        coefficient2.SetAttribute("name", "sand")
        coefficient2.SetCharacterData("0.024", 5)
        
        coefficient3.SetName("Coefficient")
        coefficient3.SetAttribute("name", "csoil")
        coefficient3.SetCharacterData("1.27", 5)
        
        coefficient4.SetName("Coefficient")
        coefficient4.SetAttribute("name", "nsoil")
        coefficient4.SetCharacterData("28", 5)
        
        root.SetName("LinearRegressionScheme")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/LinearRegressionScheme")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/LinearRegressionScheme http://tag2e.googlecode.com/files/LinearRegressionScheme.xsd")
        root.SetAttribute("name", "Freibauer")
        root.SetIntAttribute("numberOfCoefficients", 3)
        root.SetIntAttribute("hasIntercept", 1)
        root.AddNestedElement(intercept)
        root.AddNestedElement(coefficient1)
        root.AddNestedElement(coefficient2)
        root.AddNestedElement(coefficient3)
        root.AddNestedElement(coefficient4)
        root.SetCharacterDataWidth(0)  
        
        fisc.SetFileName("LinearRegressionSchemeFreibauer1.xml")
        fisc.GetXMLRoot().DeepCopy(root)
        fisc.Write()
        # Read it again
        fisc.Read();
        fisc.SetFileName("LinearRegressionSchemeFreibauer2.xml")
        fisc.Write()
        
  
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDFuzzyTest)
    unittest.TextTestRunner(verbosity=2).run(suite1) 

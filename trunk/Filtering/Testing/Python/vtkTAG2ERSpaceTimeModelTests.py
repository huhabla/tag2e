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

class vtkTAG2ERSpaceTimeModelTests(unittest.TestCase):
    def test1(self):
        
        modelparam = vtkTAG2EAbstractModelParameter()
        
        root  = vtkXMLDataElement()
        inputs = vtkXMLDataElement()
        outputs = vtkXMLDataElement()
        script = vtkXMLDataElement()
        inputname1 = vtkXMLDataElement()
        inputname2 = vtkXMLDataElement()
        inputname3 = vtkXMLDataElement()
        outputname1 = vtkXMLDataElement()

        inputname1.SetName("ArrayName")
        inputname1.SetCharacterData("data1", 5)
        inputname2.SetName("ArrayName")
        inputname2.SetCharacterData("data2", 5)
        inputname3.SetName("ArrayName")
        inputname3.SetCharacterData("data3", 5)
        outputname1.SetName("ArrayName")
        outputname1.SetCharacterData("result", 6)

        inputs.SetName("InputArrays")
        inputs.AddNestedElement(inputname1)
        inputs.AddNestedElement(inputname2)
        inputs.AddNestedElement(inputname3)
        outputs.SetName("OutputArrays")
        outputs.AddNestedElement(outputname1)
        script.SetName("RScript")
        script.SetCharacterData("test = rnorm(10000)", 19)

        root.SetName("RSpaceTimeModelDescription")
        root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/RSpaceTimeModelDescription")
        root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/RSpaceTimeModelDescription http://tag2e.googlecode.com/files/RSpaceTimeModelDescription.xsd")
        root.SetAttribute("name", "test")
        root.AddNestedElement(inputs)
        root.AddNestedElement(outputs)
        root.AddNestedElement(script)
        root.SetCharacterDataWidth(0)  
        
        modelparam.SetFileName("/tmp/vtkTAG2ERSpaceTimeModelTests1.xml")
        modelparam.GetXMLRoot().DeepCopy(root)
        modelparam.Write()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ERSpaceTimeModelTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 

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

class vtkTAG2ERothCModelParameterTests(unittest.TestCase):
    
    def setUp(self):

        self.root  = vtk.vtkXMLDataElement()
        
        a = vtkXMLDataElement()
        a.SetName("a")

        # We generate the a Parameter and make them calibratable
        for i in range(1,4):
            an = vtkXMLDataElement()
            an.SetName("a%i"%i)
            an.SetIntAttribute("const", 0)
            an.SetDoubleAttribute("min", 0)
            an.SetDoubleAttribute("max", 10)
            a.AddNestedElement(an)
        
        self.root.SetName("RothC")
        self.root.AddNestedElement(a)
        self.root.SetAttribute("name", "test")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/Weighting")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/Weighting http://tag2e.googlecode.com/files/Weighting.xsd")
        
    def test2RothCXML(self):
        
        rot = vtkTAG2ERothCModelParameter()
        rot.SetFileName("/tmp/RothC1.xml")
        rot.SetXMLRepresentation(self.root)
        rot.Write()
        # Read/Write it again and create an XML representation
        # with the default values
        rot.Read();
        rot.GenerateInternalSchemeFromXML()
        rot.GenerateXMLFromInternalScheme()
        rot.SetFileName("/tmp/RothC2.xml")
        rot.Write()
        rot.Read();
        rot.GenerateInternalSchemeFromXML()
             
    def test3RothCParameter(self):
        
        rot = vtkTAG2ERothCModelParameter()
        rot.SetFileName("/tmp/RothC1.xml")
        rot.Read()
        rot.GenerateInternalSchemeFromXML()
        
        for j in range(rot.GetNumberOfCalibratableParameter()):
            print "Modify Parameter " + str(j)
            for i in range(10):
                rot.ModifyParameter(j, 0.1*(j + 1)/2)
                print rot.GetParameterValue(j)
  
        root = vtkXMLDataElement()
        rot.SetFileName("/tmp/RothC3.xml")
        rot.GenerateXMLFromInternalScheme()
        rot.Write()
        
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2ERothCModelParameterTests)
    unittest.TextTestRunner(verbosity=2).run(suite1) 

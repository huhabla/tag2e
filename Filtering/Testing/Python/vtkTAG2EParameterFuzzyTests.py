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
from libvtkGRASSBridgeCommonPython import *

class vtkTAG2EDParameterFuzzyTest(unittest.TestCase):
  
    def setUp(self):

        self.root  = vtk.vtkXMLDataElement()
        
        fss1 = vtkXMLDataElement()
        fss2 = vtkXMLDataElement()
        fs11 = vtkXMLDataElement()
        fs12 = vtkXMLDataElement()
        fs13 = vtkXMLDataElement()
        tr11 = vtkXMLDataElement()
        tr12 = vtkXMLDataElement()
        tr13 = vtkXMLDataElement()
        fs21 = vtkXMLDataElement()
        fs22 = vtkXMLDataElement()
        fs23 = vtkXMLDataElement()
        tr21 = vtkXMLDataElement()
        tr22 = vtkXMLDataElement()
        tr23 = vtkXMLDataElement()
        resp = vtkXMLDataElement()
        
# Triangular test shape layout first Factor 0.0 - 10.0
# ____        ____
#     \  /\  /
#      \/  \/
#      /\  /\
#     /  \/  \
# 0   3   5   7  10
#
# - 1 - - 2 - - 3 - 
#
# 1: left = 11 center = 3 right = 2
# 2: left = 2  center = 5 right = 2
# 3: left = 2  center = 7 right = 11
#       
               
# Triangular test shape layout second Factor 0.0 - 150
# ____        ____
#     \  /\  /
#      \/  \/
#      /\  /\
#     /  \/  \
# 0  50  75  100  150
#
# - 1 - - 2 - - 3 - 
#
# 1: left = 151 center = 50 right = 25
# 2: left = 25  center = 75 right = 25
# 3: left = 25  center = 100 right = 151
#        
        tr11.SetName("Triangular")
        tr11.SetDoubleAttribute("center", 3)
        tr11.SetDoubleAttribute("left",   11)
        tr11.SetDoubleAttribute("right",  2)
        
        tr12.SetName("Triangular")
        tr12.SetDoubleAttribute("center", 5)
        tr12.SetDoubleAttribute("left",   2)
        tr12.SetDoubleAttribute("right",  2)
        
        tr13.SetName("Triangular")
        tr13.SetDoubleAttribute("center",  7)
        tr13.SetDoubleAttribute("left",    2)
        tr13.SetDoubleAttribute("right",   11)
        
        
        tr21.SetName("Triangular")
        tr21.SetDoubleAttribute("center", 50)
        tr21.SetDoubleAttribute("left",   151)
        tr21.SetDoubleAttribute("right",  25)
        
        tr22.SetName("Triangular")
        tr22.SetDoubleAttribute("center", 75)
        tr22.SetDoubleAttribute("left",   25)
        tr22.SetDoubleAttribute("right",  25)
        
        tr23.SetName("Triangular")
        tr23.SetDoubleAttribute("center",  100)
        tr23.SetDoubleAttribute("left",    25)
        tr23.SetDoubleAttribute("right",   151)
        
        fs11.SetName("FuzzySet")
        fs11.SetAttribute("type", "Triangular")
        fs11.SetIntAttribute("priority", 0)
        fs11.SetIntAttribute("const", 0)
        fs11.SetAttribute("position", "left")
        fs11.AddNestedElement(tr11)
        
        fs12.SetName("FuzzySet")
        fs12.SetAttribute("type", "Triangular")
        fs12.SetIntAttribute("priority", 0)
        fs12.SetIntAttribute("const", 0)
        fs12.SetAttribute("position", "intermediate")
        fs12.AddNestedElement(tr12)
        
        fs13.SetName("FuzzySet")
        fs13.SetAttribute("type", "Triangular")
        fs13.SetIntAttribute("priority", 0)
        fs13.SetIntAttribute("const", 0)
        fs13.SetAttribute("position", "right")
        fs13.AddNestedElement(tr13)
        
        fs21.SetName("FuzzySet")
        fs21.SetAttribute("type", "Triangular")
        fs21.SetIntAttribute("priority", 0)
        fs21.SetIntAttribute("const", 0)
        fs21.SetAttribute("position", "left")
        fs21.AddNestedElement(tr21)
        
        fs22.SetName("FuzzySet")
        fs22.SetAttribute("type", "Triangular")
        fs22.SetIntAttribute("priority", 0)
        fs22.SetIntAttribute("const", 0)
        fs22.SetAttribute("position", "intermediate")
        fs22.AddNestedElement(tr22)
        
        fs23.SetName("FuzzySet")
        fs23.SetAttribute("type", "Triangular")
        fs23.SetIntAttribute("priority", 0)
        fs23.SetIntAttribute("const", 0)
        fs23.SetAttribute("position", "right")
        fs23.AddNestedElement(tr23)
        
        # Two factors 
        fss1.SetName("Factor")
        fss1.SetIntAttribute("portId", 0)
        fss1.SetAttribute("name", "pH")
        fss1.SetDoubleAttribute("min", 0.0)
        fss1.SetDoubleAttribute("max", 10.0)
        fss1.AddNestedElement(fs11)
        fss1.AddNestedElement(fs12)
        fss1.AddNestedElement(fs13)
        
        fss2.SetName("Factor")
        fss2.SetIntAttribute("portId", 0)
        fss2.SetAttribute("name", "nmin")
        fss2.SetDoubleAttribute("min", 0.0)
        fss2.SetDoubleAttribute("max", 150)
        fss2.AddNestedElement(fs21)
        fss2.AddNestedElement(fs22)
        fss2.AddNestedElement(fs23)
        
        resp.SetName("Responses")
        resp.SetDoubleAttribute("min", 0)
        resp.SetDoubleAttribute("max", 160)
        
        for i in range(9):
            rval1 = vtkXMLDataElement()
            rval1.SetName("Response")
            rval1.SetIntAttribute("const", 0)
            rval1.SetIntAttribute("sd", 1)
            rval1.SetCharacterData(str(i * 20), 6)
            resp.AddNestedElement(rval1)
                
        self.root.SetName("FuzzyInferenceScheme")
        self.root.AddNestedElement(fss1)
        self.root.AddNestedElement(fss2)
        self.root.AddNestedElement(resp)
        self.root.SetAttribute("name", "N2OEmission_V20101111")
        self.root.SetAttribute("xmlns", "http://tag2e.googlecode.com/files/WightedFuzzyInferenceScheme")
        self.root.SetAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.root.SetAttribute("xsi:schemaLocation", "http://tag2e.googlecode.com/files/FuzzyInferenceScheme http://tag2e.googlecode.com/files/FuzzyInferenceScheme.xsd")
        
    def test2FuzzyXML(self):
        
        fisc = vtkTAG2EFuzzyInferenceModelParameter()
        fisc.SetFileName("/tmp/FuzzyInferenceScheme1.xml")
        fisc.SetXMLRepresentation(self.root)
        fisc.Write()
        # Read/Write it again
        fisc.Read();
        fisc.SetFileName("/tmp/FuzzyInferenceScheme2.xml")
        fisc.Write()

        second = vtkTAG2EFuzzyInferenceModelParameter()
	root2 = vtkXMLDataElement()
        fisc.GetXMLRepresentation(root2)
        second.SetXMLRepresentation(root2)
        second.SetFileName("/tmp/FuzzyInferenceScheme3.xml")
        second.Write()
             
    def test3FuzzyParameter(self):
        
        fisc = vtkTAG2EFuzzyInferenceModelParameter()
        fisc.SetXMLRepresentation(self.root)
        
        for j in range(fisc.GetNumberOfCalibratableParameter()):
            print "Modify Parameter " + str(j)
            for i in range(10):
                fisc.ModifyParameter(j, 0.1*(j + 1)/2)
                print fisc.GetParameterValue(j)
  
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDParameterFuzzyTest)
    unittest.TextTestRunner(verbosity=2).run(suite1) 

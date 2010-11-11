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

from libvtkFilteringPython import *
from libvtkIOPython import *
from libvtkImagingPython import *
from libvtkCommonPython import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *

class vtkTAG2EDFuzzyTest(unittest.TestCase):
    def testSmoke(self):
        
        model = vtkTAG2EFuzzyInferenceSchemeModel()
        fisc = vtkTAG2EFuzzyInferenceSchemeCalibration()
        coll = vtkTAG2ECalibrationParameterCollection()
        coll.AddItem(fisc)
        model.SetParameterCollection(coll)
        
        root = vtkXMLDataElement()
        fss1 = vtkXMLDataElement()
        fss2 = vtkXMLDataElement()
        fs1 = vtkXMLDataElement()
        fs2 = vtkXMLDataElement()
        fs3 = vtkXMLDataElement()
        tr1 = vtkXMLDataElement()
        tr2 = vtkXMLDataElement()
        tr3 = vtkXMLDataElement()
        resp = vtkXMLDataElement()
        rval1 = vtkXMLDataElement()
        rval2 = vtkXMLDataElement()
        rval3 = vtkXMLDataElement()
        responseWeights = vtkXMLDataElement()
        responseWeight1 = vtkXMLDataElement()
        responseWeight2 = vtkXMLDataElement()
        
        tr1.SetName("triangular")
        tr1.SetDoubleAttribute("center", 5.0)
        tr1.SetDoubleAttribute("slopeLeft", 0.0)
        tr1.SetDoubleAttribute("slopeRight", 10.0)
        
        tr2.SetName("triangular")
        tr2.SetDoubleAttribute("center", 0.0)
        tr2.SetDoubleAttribute("slopeLeft", -4.0)
        tr2.SetDoubleAttribute("slopeRight", 4.0)
        
        tr3.SetName("triangular")
        tr3.SetDoubleAttribute("center", 5.0)
        tr3.SetDoubleAttribute("slopeLeft", 10.0)
        tr3.SetDoubleAttribute("slopeRight", 0.0)
        
        fs1.SetName("FuzzySet")
        fs1.SetIntAttribute("id", 1)
        fs1.SetAttribute("type", "triangular")
        fs1.SetIntAttribute("priority", 0)
        fs1.SetIntAttribute("const", 0)
        fs1.SetAttribute("position", "left")
        fs1.AddNestedElement(tr1)
        
        fs2.SetName("FuzzySet")
        fs2.SetIntAttribute("id", 2)
        fs2.SetAttribute("type", "triangular")
        fs2.SetIntAttribute("priority", 0)
        fs2.SetIntAttribute("const", 0)
        fs2.SetAttribute("position", "intermediate")
        fs2.AddNestedElement(tr2)
        
        fs3.SetName("FuzzySet")
        fs3.SetIntAttribute("id", 3)
        fs3.SetAttribute("type", "triangular")
        fs3.SetIntAttribute("priority", 0)
        fs3.SetIntAttribute("const", 0)
        fs3.SetAttribute("position", "right")
        fs3.AddNestedElement(tr3)
        
        fss1.SetName("Factor")
        fss1.SetIntAttribute("id", 1)
        fss1.SetAttribute("name", "pH")
        fss1.SetIntAttribute("numberOfFuzzySets", 3)
        fss1.SetDoubleAttribute("min", 0.0)
        fss1.SetDoubleAttribute("max", 10.0)
        fss1.AddNestedElement(fs1)
        fss1.AddNestedElement(fs2)
        fss1.AddNestedElement(fs3)
        
        fss2.SetName("Factor")
        fss2.SetIntAttribute("id", 2)
        fss2.SetAttribute("name", "nmin")
        fss2.SetIntAttribute("numberOfFuzzySets", 3)
        fss2.SetDoubleAttribute("min", 1.0)
        fss2.SetDoubleAttribute("max", 9.0)
        fss2.AddNestedElement(fs1)
        fss2.AddNestedElement(fs2)
        fss2.AddNestedElement(fs3)
        
        rval1.SetName("Response")
        rval1.SetIntAttribute("id", 1)
        rval1.SetIntAttribute("const", 0)
        rval1.SetCharacterData("120.00", 6)
        
        rval2.SetName("Response")
        rval2.SetIntAttribute("id", 2)
        rval2.SetIntAttribute("const", 0)
        rval2.SetCharacterData("80.00", 5)
        
        rval3.SetName("Response")
        rval3.SetIntAttribute("id", 3)
        rval3.SetIntAttribute("const", 0)
        rval3.SetCharacterData("40.00", 5)
        
        resp.SetName("Responces")
        resp.SetIntAttribute("numberOfResponces", 3)
        resp.AddNestedElement(rval1)
        resp.AddNestedElement(rval2)
        resp.AddNestedElement(rval3)

        responseWeight1.SetName("Weight")
        responseWeight1.SetIntAttribute("id", 1)
        responseWeight1.SetAttribute("name", "grass")
        responseWeight1.SetIntAttribute("active", 1)
        responseWeight1.SetIntAttribute("const", 0)
        responseWeight1.SetCharacterData("0.150", 5)
        
        responseWeight2.SetName("Weight")
        responseWeight2.SetIntAttribute("id", 2)
        responseWeight2.SetAttribute("name", "vegt")
        responseWeight2.SetIntAttribute("active", 1)
        responseWeight2.SetIntAttribute("const", 0)
        responseWeight2.SetCharacterData("0.150", 5)
        
        responseWeights.SetName("Weights")
        responseWeights.SetIntAttribute("active", 1)
        responseWeights.SetIntAttribute("numberOfWeights", 2)
        responseWeights.AddNestedElement(responseWeight1)
        responseWeights.AddNestedElement(responseWeight2)
        
        root.SetName("FuzzyInferenceScheme")
        root.SetAttribute("name", "N2OEmission_V20101111")
        root.SetIntAttribute("numberOfFaktors", 2)
        root.AddNestedElement(fss1)
        root.AddNestedElement(fss2)
        root.AddNestedElement(resp)
        root.AddNestedElement(responseWeights)
        
        fisc.SetFileName("FuzzyInferenceScheme1.xml")
        fisc.GetXMLRoot().DeepCopy(root)
        fisc.Write()
        # Read it again
        fisc.Read();
        # Change the name
        fisc.GetXMLRoot().SetAttribute("name", "CH4Emission_V20101111") 
        fisc.SetFileName("FuzzyInferenceScheme2.xml")
        fisc.Write()
        
  
if __name__ == '__main__':
    suite1 = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EDFuzzyTest)
    unittest.TextTestRunner(verbosity=2).run(suite1) 

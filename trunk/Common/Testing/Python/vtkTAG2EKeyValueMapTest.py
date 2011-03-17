#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
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

firstCheck = False

class vtkTAG2EKeyValueMapTest(unittest.TestCase):

    def testSmoke(self):

        mymap = vtkKeyValueMap()
        mymap.Add("pH", 100)
        mymap.Add("Prec", 50)
        mymap.Add("N", 0.1)
        
        self.assertEqual(mymap.GetValue("pH"), 100, "Error in GetValue(key)")
        self.assertEqual(mymap.GetValue("Prec"), 50, "Error in GetValue(key)")
        self.assertEqual(mymap.GetValue("N"), 0.1, "Error in GetValue(key)")
        self.assertEqual(mymap.GetValue(0), 100, "Error in GetValue(idx)")
        self.assertEqual(mymap.GetValue(1), 50, "Error in GetValue(idx)")
        self.assertEqual(mymap.GetValue(2), 0.1, "Error in GetValue(idx)")
        self.assertEqual(mymap.GetKey(0), "pH","Error in GetKey(idx)")
        self.assertEqual(mymap.GetKey(1), "Prec", "Error in GetKey(idx)")
        self.assertEqual(mymap.GetKey(2), "N","Error in GetKey(idx)")
        self.assertEqual(mymap.HasKey("pH"), True,"Error in HasKey(key)")
        self.assertEqual(mymap.HasKey("Prec"), True,"Error in HasKey(key)")
        self.assertEqual(mymap.HasKey("N"), True,"Error in HasKey(key)")
        self.assertEqual(mymap.HasKey("False"), False,"Error in HasKey(key)")
        
        mymap.Remove("pH");
        self.assertEqual(mymap.HasKey("pH"), False,"Error in HasKey(key)")
        mymap.Remove("Prec");
        self.assertEqual(mymap.HasKey("Prec"), False,"Error in HasKey(key)")
        mymap.Remove("N");
        self.assertEqual(mymap.HasKey("N"), False,"Error in HasKey(key)")
        
        mymap.Clear()
        self.assertEqual(mymap.GetNumberOfKeys(), 0,"Error in Clear")
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EKeyValueMapTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

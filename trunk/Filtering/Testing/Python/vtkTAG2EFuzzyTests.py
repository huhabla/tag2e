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
        
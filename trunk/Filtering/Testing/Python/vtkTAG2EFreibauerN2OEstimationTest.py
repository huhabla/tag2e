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
from libvtkImagingPython import *
from libvtkCommonPython import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *

class vtkTAG2EFreibauerN2OEstimationTest(unittest.TestCase):
    def setUp(self):
        self.nrate = vtkImageData()
        self.nrate.SetExtent(0, 10000, 0, 10000, 0, 0)
        self.nrate.AllocateScalars ()
        self.sand = vtkImageData()
        self.sand.SetExtent(0, 10000, 0, 10000, 0, 0)
        self.sand.AllocateScalars ()
        self.soilC = vtkImageData()
        self.soilC.SetExtent(0, 10000, 0, 10000, 0, 0)
        self.soilC.AllocateScalars ()
        self.soilN = vtkImageData()
        self.soilN.SetExtent(0, 10000, 0, 10000, 0, 0)
        self.soilN.AllocateScalars ()
        self.croptype = vtkImageData()
        self.croptype.SetExtent(0, 10000, 0, 10000, 0, 0)
        self.croptype.AllocateScalars ()
        self.climate = vtkImageData()
        self.climate.SetExtent(0, 10000, 0, 10000, 0, 0)
        self.climate.AllocateScalars ()

        print "Number of points", self.climate.GetNumberOfPoints()
        print "Data dimension: ", self.climate.GetDataDimension()

    def testSmoke(self):

        model = vtkTAG2EFreibauerN2OEstimation()
        model.SetNitrogenRate(self.nrate)
        model.SetSandFraction(self.sand)
        model.SetSoilOrganicCorbonate(self.soilC)
        model.SetSoilNitrogen(self.soilN)
        model.SetCropType(self.croptype)
        model.SetClimateType(self.climate)
        model.SetNumberOfThreads(6)
        model.Update()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EFreibauerN2OEstimationTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

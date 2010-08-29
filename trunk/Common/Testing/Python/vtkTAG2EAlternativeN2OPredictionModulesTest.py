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
from libvtkCommonPython import *
from libvtkTAG2ECommonPython import *

firstCheck = False

class vtkTAG2EAlternativeN2OPredictionModulesTest(unittest.TestCase):

    def testSmoke(self):

        models = vtkTAG2EAlternativeN2OPredictionModules()

        N_rate = 20
        Corg = 30
        silt = 20
        clay = 10
        pH = 6.5
        T_spring = 20
        P_sum = 30
        T_win = 2
        sand = 50
        soilC = 40
        soilN = 10
        croptype = 6
        climate = 1

        print " "
        print "Model Bouwman  : ",
        print models.Bouwman(N_rate)
        print "Model Freibauer: ",
        print models.Freibauer(N_rate, sand, soilC, soilN, croptype, climate)
        print "Model Roelandt : ",
        print models.Roelandt(N_rate, T_spring, P_sum, T_win, croptype)
        print "Model Stehfest : ",
        print models.Stehfest(N_rate, Corg, silt, clay, pH, croptype, climate)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EAlternativeN2OPredictionModulesTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

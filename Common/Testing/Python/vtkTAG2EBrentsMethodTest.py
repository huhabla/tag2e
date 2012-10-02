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
import math
from vtk import *
from libvtkTAG2ECommonPython import *

firstCheck = False

class vtkTAG2EBrentsMethodTest(unittest.TestCase):

    def testSmoke(self):
        # Suche Nullstelle von x^2
        brent = vtkTAG2EBrentsMethod()
        
        a = -10
        b =  6
        c =  10
        
        tol = 0.001
        
        result = -7
        
        model = self.f(b)
        
        fx = math.sqrt((result - model)*(result - model))
        
        brent.Init(a, b, c, tol, fx)
        
        for iter in xrange(100):
            print "Iter ", iter
            if brent.IsFinished() == True:
                print "Finished"
                return  
            fit = brent.Fit();
            model = self.f(fit)
            fx = math.sqrt((result - model)*(result - model))
            brent.Evaluate(fx); 
            print "Residual", fx             
            print "x", brent.Getx()
            print "fx", brent.Getfx()
            if fx < 0.00000001:
                print "Finished"
                return
        
    def f(self, x):
        return x*x - 7
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EBrentsMethodTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

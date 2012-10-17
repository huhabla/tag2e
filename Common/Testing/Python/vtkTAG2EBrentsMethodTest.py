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

    def test1(self):
        # Search root of x^2 - 7
        brent = vtkTAG2EBrentsMethod()
        
        a = -10
        b =  6
        c =  10
        
        tol = 0.001
        
        result = -7
        
        model = self.f1(b)
        
        fx = math.sqrt((result - model)*(result - model))
        
        brent.Init(a, b, c, tol, fx)
        
        for iter in xrange(100):
            print "Iter ", iter
            if brent.IsFinished() == True:
                print "Finished"
                return  
            fit = brent.Fit()          
            print "fit", fit
            model = self.f1(fit)
            fx = math.sqrt((result - model)*(result - model))
            brent.Evaluate(fx);  
        
        
    def test2(self):
        # Search root of x^2
        brent = vtkTAG2EBrentsMethod()
        
        a = -10
        b =  6
        c =  10
        
        tol = 0.001
        
        result = -7
        
        fx = self.f2(b)
        
        brent.Init(a, b, c, tol, fx)
        
        for iter in xrange(100):
            print "Iter ", iter
            if brent.IsFinished() == True:
                print "Finished"
                return  
            fit = brent.Fit()          
            print "fit", fit
            fx = self.f2(fit)
            brent.Evaluate(fx);  
        
    def f1(self, x):
        return x*x - 7
    
    def f2(self, x):
        return x*x
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(vtkTAG2EBrentsMethodTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

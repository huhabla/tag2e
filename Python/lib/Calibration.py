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
import random
import math

from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeFilteringPython import *
from libvtkGRASSBridgeCommonPython import *
from MetaModel import *

def MetaModelSimulatedAnnealing(metaModel, maxiter, initialT, sd, breakCriteria, outputName, TMinimizer):
    """The simulated annelaing algorithm"""

    metaModel.Run()

    firstError = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(metaModel.GetModelOutput(), metaModel.GetTargetDataSet(), 0, 0)

    count = 0

    T = initialT

    for i in range(maxiter):
        
        
        if i == 0:
            oldError = firstError
            Error = firstError
            
        if (i + 1) % 100 == 1:
            print "######### Iteration " + str(i) + " error " + str(Error) + " #########"

        sdNew = sd/((initialT - T)/initialT + 1)

        metaModel.ModifyParameterRandomly(sdNew)
        metaModel.Run()


        # Measure the difference between old and new error
        Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(metaModel.GetModelOutput(), metaModel.GetTargetDataSet(), 0, 0)

        diff = Error - oldError

        # Accept the new parameter
        if diff <= 0:
            oldError = Error
        else:
            # Create a random number
            r = random.uniform(1.0, 0.0)
            pa = math.exp(-1.0*diff/T)
            if pa > 1:
                pa = 1

            # restore the last parameter if the random variable is larger then the error
            if r > pa:
                metaModel.RestoreLastModifiedParameter()
            else:
                oldError = Error
                print "Accepted poor result at iteration ", i, " with Error ", Error, "T ", T, "sd ", sdNew
                T = T/TMinimizer

        count += 1

        if Error < breakCriteria:
            break

    metaModel.WriteParameter(outputName)

    print "Finished after " + str(count) + " Iterations with error ", Error


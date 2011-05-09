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


def SimulatedAnnealing(model, parameter, maxiter, \
                       maxFactor, sd, errorBreak, modelArray, \
                       measureArray, name, minT):
    """The simulated annelaing algorithm"""

    model.Update()

    firstError = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), modelArray, measureArray, 0, 0)

    count = 0

    T = maxFactor

    for i in range(maxiter):
        
        
        if i == 0:
            oldError = firstError
            Error = firstError
            
        if (i + 1) % 100 == 1:
            print "######### Iteration " + str(i) + " error " + str(Error) + " #########"

        sdNew = sd/((maxFactor - T)/maxFactor + 1)

        parameter.ModifyParameterRandomly(sdNew)
        model.Modified()
        model.Update()


        # Measure the difference between old and new error
        Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), modelArray, measureArray, 0, 0)

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
                parameter.RestoreLastModifiedParameter()
            else:
                oldError = Error
                print "Accepted poor result at iteration ", i, " with Error ", Error, "T ", T, "sd ", sdNew
                T = T/minT

        count += 1

        # print an intermediate state
        # if i % 1000 == 1:
            # Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), modelArray, measureArray, 0, 1)
            # print "Error ", Error
            #print "Save XML state"
            #parameter.GenerateXMLFromInternalScheme()
            #parameter.SetFileName(name + str(i) + ".xml")
            #parameter.Write()

        if Error < errorBreak:
            break

    parameter.SetFileName(name)
    parameter.Write()
    model.Modified()
    model.Update()

    Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), modelArray, measureArray, 0, 0)
    print "Finished after " + str(count) + " Iterations with error ", Error


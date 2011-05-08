#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.
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
        if (i + 1) % 100 == 1:
            print "######### Iteration " + str(i) + " #########"

        sdNew = sd/((maxFactor - T)/maxFactor + 1)

        parameter.ModifyParameterRandomly(sdNew)
        model.Modified()
        model.Update()

        if i == 0:
            oldError = firstError

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

    parameter.GenerateXMLFromInternalScheme()
    parameter.SetFileName(name)
    parameter.Write()
    model.Modified()
    model.Update()

    Error = vtkTAG2EAbstractModelCalibrator.CompareTemporalDataSets(model.GetOutput(), modelArray, measureArray, 0, 0)
    print "Finished after " + str(count) + " Iterations with error ", Error


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
from libvtkGRASSBridgeCommonPython import *
from MetaModel import *

################################################################################
################################################################################
################################################################################

def MetaModelSimulatedAnnealingImproved(metaModel, maxiter = 1000, initialT = 1,\
                                        sd = 1, breakCriteria = 0.01, TMinimizer = 1.0, \
                                        SdMinimizer = 1.0):
    """The simulated annealing algorithm with best fit storage and T as well as sd minimization"""

    # Check input values
    if SdMinimizer <= 0:
        print "Wrong SdMinimizer will set to 1.0"
        SdMinimizer = 1.0

    if TMinimizer <= 0:
        print "Wrong TMinimizer will set to 1.0"
        TMinimizer = 1.0
        
    metaModel.Run()

    error = vtkTAG2EAbstractModelCalibrator.CompareDataSets(metaModel.GetModelOutput(), 
                                                            metaModel.GetTargetDataSet(), 
                                                            1, 0, False)
    lastAcceptedError = error
    bestFitError = error
    
    # Initialize the best fit parameter and model output
    bestFitModelParameter = vtkXMLDataElement()
    metaModel.GetXMLRepresentation(bestFitModelParameter)
    bestFitDataSet = metaModel.GetTargetDataSet().NewInstance()
    bestFitDataSet.ShallowCopy(metaModel.GetModelOutput())
    bestFitModelAssessment = 1.0
    
    count = 0

    T = initialT

    for i in range(maxiter):
            
        if maxiter > 100:
            if (i + 1) % int(maxiter/100) == 1:
                print "Iteration ", i, " error ", error, " T ", T, " sd ", sd
        else:
            print "Iteration ", i, " error ", error, " T ", T, " sd ", sd

        metaModel.ModifyParameterRandomly(sd)

        # Run the model
        metaModel.Run()
        # Get the model assessment factor
        modelAssessment = metaModel.GetModelAssessmentFactor()

        # Measure the difference between old and new error
        error = vtkTAG2EAbstractModelCalibrator.CompareDataSets(metaModel.GetModelOutput(), \
                metaModel.GetTargetDataSet(), 1, 0, False) * modelAssessment

        diff = error - lastAcceptedError

        # Accept the new parameter and store the result at best fit
        if diff <= 0:
            lastAcceptedError = error
            if error < bestFitError:
                bestFitError = error
                
                bestFitModelAssessment = modelAssessment;
                print "Store best fit result at iteration ", i, " with error ", bestFitError
                metaModel.GetXMLRepresentation(bestFitModelParameter)
                bestFitDataSet.ShallowCopy(metaModel.GetModelOutput())
                # Modify the standard deviation
                sd = sd/SdMinimizer
        else:
            # Restore old configuration or accept new poor configuration
            
            # Create a random number
            r = random.uniform(1.0, 0.0)
            pa = math.exp(-1.0*diff/T)
            if pa > 1:
                pa = 1

            # restore the last parameter if the random variable is larger then the error
            if r > pa:
                metaModel.RestoreLastModifiedParameter()
            else:
                # Accept poor result to hop out a local minima
                lastAcceptedError = error
                # print "Accepted poor result at iteration ", i, " with Error ", error, "T ", T, "sd ", sdNew
                T = T/TMinimizer

        count += 1

        if bestFitError < breakCriteria:
            print "Best fit reached"
            break

    	if (i + 1)% 100 and bestFitError > 1E20:
            print "Error stays to large (>1E20), break computation."
	    break

    print "Finished after ", count, " Iterations with best fit ", bestFitError, " and Model assessment ", bestFitModelAssessment
    
    return bestFitModelParameter, bestFitDataSet, bestFitError, bestFitModelAssessment


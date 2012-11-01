#!/usr/bin/env python
#
# Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
#
# Program: Sequential Forward Selection Algorithm
#
# Purpose: Calibrate a (weighted) fuzzy inference model parameter based on vector data
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

import grass.script as grass
import subprocess
import os
import sys
import random
import math
import time

from vtk import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *

DEBUG = False

################################################################################
        
def selectBestModel(minBIC, errorList, BICList, AICList, MAFList, RsquaredList):
    """Select the best model run from a list of model 
         runs and return error, BIC, AIC, MAF 
    """
    # Compute the BIC weights and apply the MAF
    BICWeigthSum = 0.0
    BICWeightList = []
    for BIC in BICList:
        BICDelta = math.fabs(BIC - minBIC)
        BICWeight = math.exp(-1*BICDelta/2.0)
        BICWeightList.append(BICWeight) 
        BICWeigthSum = BICWeigthSum +  BICWeight
        
    resultArray = []
    for i in range(len(BICList)):
        error = errorList[i]
        BIC = BICList[i]
        AIC = AICList[i]
        BICWeight = BICWeightList[i]
        MAF = MAFList[i]
        Rsquared = RsquaredList[i]
        BICMAFWeight = BICWeight / MAF / BICWeigthSum
        resultArray.append([BICMAFWeight, BIC, AIC, MAF, error, Rsquared])
        
    resultArray = sorted(resultArray, key = lambda resultArray: resultArray[0])

    
    print "The following models are computed"
    for model in resultArray:     
        # The last entry has the best model result
        BICMAFWeight = model[0]
        BIC = model[1]
        AIC = model[2]
        MAF = model[3]
        error = model[4]
        Rsquared = model[5]
        print "Model "
        print "  BIC MAF Weight:", BICMAFWeight
        print "  BIC           :", BIC
        print "  AIC           :", AIC
        print "  MAF           :", MAF
        print "  Error         :", error
        print "  Rsquared      :", Rsquared
    
    print "Use best fit:"
    print "BIC MAF Weight:", BICMAFWeight
    print "BIC           :", BIC
    print "AIC           :", AIC
    print "MAF           :", MAF
    print "Error         :", error
    print "Rsquared      :", Rsquared
    return error, BIC, AIC, MAF, Rsquared

################################################################################

def StartCalibration(id, dir, inputvector, target, factornames, fuzzysets, iterations, runs, 
        treduce, sdreduce, breakcrit, bootstrapOn=False, samplingfactor=None):

    minBIC = 999999
    flags=""
    if bootstrapOn:
        flags += "b"
        
    BICList = []
    errorList = []
    AICList = []
    MAFList = []
    RsquaredList = []
    procList = []

    # Parallel model runs
    for i in range(runs):
        run_id = "%s_run_%i"%(id, i)
        
        print "Running calibration", i, inputvector, target, factornames, fuzzysets

        procList.append(grass.start_command("v.fuzzy.calibrator", flags=flags, overwrite=True, \
                          input=inputvector, factors=factornames,\
                          target=target, fuzzysets=fuzzysets, iterations=iterations, \
                          samplingfactor=samplingfactor, \
                          parameter=os.path.join(dir, (run_id + ".xml")), \
                          log=os.path.join(dir, (run_id + ".log")), treduce=treduce, \
                          sdreduce=sdreduce, breakcrit=breakcrit))

    # Wait for all created processes
    for i in range(runs):
        procList[i].wait()
        
    # Analyze the logfiles
    for i in range(runs):
        run_id = "%s_run_%i"%(id, i)
        
        # We need to read the logfile in the correct order
        # Logfile of the calibrator
        # 1. Error
        # 3. BIC
        # 4. AIC
        # 5. MAF (Model Assessment Factor)
        # 6. Rsquared
        logfile = open(os.path.join(dir, run_id + ".log"), "r")
        errorList.append(float(logfile.readline().split(":")[1]))
        runBIC = float(logfile.readline().split(":")[1])
        BICList.append(runBIC)
        AICList.append(float(logfile.readline().split(":")[1]))
        MAFList.append(float(logfile.readline().split(":")[1]))
        RsquaredList.append(float(logfile.readline().split(":")[1]))
        logfile.close()
        
        if runBIC < minBIC:
            minBIC = runBIC
            
    print "Finished", runs, "runs"
    return selectBestModel(minBIC, errorList, BICList, AICList, MAFList, RsquaredList)

################################################################################

def StartWeightedCalibration(id, dir, inputvector, target, factornames, fuzzysets, iterations, runs, 
        WeightNum, WeightFactor, treduce, sdreduce, breakcrit, bootstrapOn=False, samplingfactor=None):

    minBIC = 999999
    flags="w"
    if bootstrapOn:
        flags += "b"
        
    BICList = []
    errorList = []
    AICList = []
    MAFList = []
    RsquaredList = []
    procList = []

    for i in range(runs):
        run_id = "%s_run_%i"%(id, i)
        print "Running weighted calibration", i, inputvector, target, factornames, fuzzysets

        procList.append(grass.start_command("v.fuzzy.calibrator", flags=flags, overwrite=True, input=inputvector, factors=factornames,\
              target=target, fuzzysets=fuzzysets, iterations=iterations, \
              parameter=os.path.join(dir, (run_id + ".xml")), \
              log=os.path.join(dir, (run_id + ".log")), treduce=treduce, sdreduce=sdreduce,\
              weightnum=WeightNum, weightfactor=WeightFactor))
        
    # Wait for all created processes
    for i in range(runs):
        procList[i].wait()
        
    # Analyze the logfiles
    for i in range(runs):
        run_id = "%s_run_%i"%(id, i)
        # We need to read the logfile in the correct order
        # Logfile of the calibrator
        # 1. Error
        # 3. BIC
        # 4. AIC
        # 5. MAF (Model Assessment Factor)
        logfile = open(os.path.join(dir, run_id + ".log"), "r")
        errorList.append(float(logfile.readline().split(":")[1]))
        runBIC = float(logfile.readline().split(":")[1])
        BICList.append(runBIC)
        AICList.append(float(logfile.readline().split(":")[1]))
        MAFList.append(float(logfile.readline().split(":")[1]))
        RsquaredList.append(float(logfile.readline().split(":")[1]))
        logfile.close()
        
        if runBIC < minBIC:
            minBIC = runBIC
        
    print "Finished", runs, " runs"    
    return selectBestModel(minBIC, errorList, BICList, AICList, MAFList, RsquaredList)

################################################################################

def main():
    
    # Initiate GRASS
    init = vtkGRASSInit()
    init.Init("v.fuzzy.select")
    init.ExitOnErrorOn()

    module = vtkGRASSModule()
    module.SetDescription("Select best fitting factors of a fuzzy inference model parameter based on vector data")
    module.AddKeyword("vector")

    input = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorInputType())

    feature = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetVectorFeatureType())
    feature.SetDefaultOptions("point,centroid,area")
    feature.SetDefaultAnswer("point")
    feature.MultipleOff()
    
    factors = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "factors")
    factors.SetDescription("Names of the table columns of the fuzzy factors")

    target = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "target")
    target.SetDescription("Name of the table column of the target variable")

    weightingFactor = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetDataBaseColumnType(), "weightfactor")
    weightingFactor.SetDescription("Name of the table column of the weighting variable")
    weightingFactor.RequiredOff()

    iterations = vtkGRASSOption()
    iterations.SetKey("iterations")
    iterations.MultipleOff()
    iterations.RequiredOff()
    iterations.SetDefaultAnswer("5000")
    iterations.SetDescription("The maximum number of iterations")
    iterations.SetTypeToInteger()

    fuzzysets = vtkGRASSOption()
    fuzzysets.SetKey("fuzzysets")
    fuzzysets.MultipleOn()
    fuzzysets.RequiredOn()
    fuzzysets.SetDescription("The number of fuzzy sets to be used for calibration eg.: 2,3")
    fuzzysets.SetTypeToInteger()

    resultlist = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "result")
    resultlist.SetDescription("The name of the logfile to store a sorted list of all factor combinations with AIC and ERROR")

    samplingFactor = vtkGRASSOption()
    samplingFactor.SetKey("samplingfactor")
    samplingFactor.MultipleOff()
    samplingFactor.RequiredOff()
    samplingFactor.SetDescription("The name of the column with ids for bootstrap aggregation selection")
    samplingFactor.SetTypeToString()

    weightNum = vtkGRASSOption()
    weightNum.SetKey("weightnum")
    weightNum.MultipleOff()
    weightNum.RequiredOff()
    weightNum.SetDefaultAnswer("6")
    weightNum.SetDescription("The number of weights used for calibration")
    weightNum.SetTypeToInteger()

    null = vtkGRASSOption()
    null.SetKey("null")
    null.MultipleOff()
    null.RequiredOff()
    null.SetDefaultAnswer("9999")
    null.SetDescription("The value used fo no data")
    null.SetTypeToDouble()
   
    breakcrit = vtkGRASSOption()
    breakcrit.SetKey("breakcrit")
    breakcrit.MultipleOff()      
    breakcrit.RequiredOff()      
    breakcrit.SetDefaultAnswer("0.01")
    breakcrit.SetDescription("The break criteria")
    breakcrit.SetTypeToDouble()                   

    sdepth = vtkGRASSOption()
    sdepth.SetKey("sdepth")
    sdepth.MultipleOff()
    sdepth.RequiredOff()
    sdepth.SetDefaultAnswer("2")
    sdepth.SetDescription("The maximum number of depths (number of selected factors)")
    sdepth.SetTypeToInteger()

    runs = vtkGRASSOption()
    runs.SetKey("runs")
    runs.MultipleOff()
    runs.RequiredOff()
    runs.SetDefaultAnswer("1")
    runs.SetDescription("The number of runs for each selection anaylsis")
    runs.SetTypeToInteger()
                                                    
    treduce = vtkGRASSOption()                      
    treduce.SetKey("treduce")                       
    treduce.MultipleOff()                           
    treduce.RequiredOff()                           
    treduce.SetDefaultAnswer("1.01")                
    treduce.SetDescription("This factor is used to reduce the annealing temperature each step")
    treduce.SetTypeToDouble()                                                                  
                                                                                               
    sdreduce = vtkGRASSOption()                                                                
    sdreduce.SetKey("sdreduce")                                                                
    sdreduce.MultipleOff()                                                                     
    sdreduce.RequiredOff()                                                                     
    sdreduce.SetDefaultAnswer("1.01")                                                          
    sdreduce.SetDescription("This factor is used to reduce the standard deviation each step")  
    sdreduce.SetTypeToDouble()                                                                 
 
    bagging = vtkGRASSFlag()
    bagging.SetDescription("Use boostrap aggregation (bagging) for input data selection")
    bagging.SetKey('b')

    weighting = vtkGRASSFlag()
    weighting.SetDescription("Use weighting for input data calibration. A weightingfactor and the number of weights must be provided.")
    weighting.SetKey('w')

    paramter = vtkStringArray()
    for arg in sys.argv:
        paramter.InsertNextValue(str(arg))

    if init.Parser(paramter) == False:
        return -1

    messages = vtkGRASSMessagingInterface()

    # Check for weighting support
    if weighting.GetAnswer() == True:
        if not weightingFactor.GetAnswer():
            messages.FatalError("The name of the weighting column name must be provided")

    # Create the names for the vector import and the (weighted) fuzzy inference scheme generation
    columns = vtkStringArray()
    factors.GetAnswers(columns)

    setnums = vtkStringArray()
    fuzzysets.GetAnswers(setnums)

    Factors = []
    for i in range(columns.GetNumberOfValues()):
        Factors.append(columns.GetValue(i))

    FuzzySets = []
    for i in range(setnums.GetNumberOfValues()):
        FuzzySets.append(int(setnums.GetValue(i)))

    columns.InsertNextValue(target.GetAnswer())
    
    Vector = input.GetAnswer()
    Target = target.GetAnswer()
    WeightNum = int(weightNum.GetAnswer())
    WeightFactor = weightingFactor.GetAnswer()
    Iterations = int(iterations.GetAnswer())
    runs = int(runs.GetAnswer())
    searchDepth = int(sdepth.GetAnswer())
    
    tmpdir = grass.tempdir()

    Count = 0
    CalibrationResultFactors = []
    CalibrationResultFuzzySets = []
    StartFactors = Factors
    
    if searchDepth == 0:
        searchDepth = len(Factors)

    CalibrationResult = {}
    
    SelectedCalibration = ""

    while Count < searchDepth:

        factorNames = []
        fuzzySetNums = []

        CalibrationResultCount = len(CalibrationResultFactors)

        # Insert the previous selected factors and fuzzy set numbers
        for i in range(CalibrationResultCount):
            factorNames.append(CalibrationResultFactors[i])
            fuzzySetNums.append(CalibrationResultFuzzySets[i])

        # Allocate the next entry
        factorNames.append("")
        fuzzySetNums.append("")

        # For each factor left
        for factor in StartFactors:
            factorNames[CalibrationResultCount] = factor
            for fuzzySet in FuzzySets:
                fuzzySetNums[CalibrationResultCount] = fuzzySet

                # Create the unique id of the calibration
                id = ""
                for i in range(len(factorNames)):
                    id += str(factorNames[i]) + str(fuzzySetNums[i])

                # Make a copy of the lists, otherwise the references get modified
                a = 1*factorNames
                b = 1*fuzzySetNums
                
                if weighting.GetAnswer():
                    error, BIC, AIC, MAF, Rsquared = StartWeightedCalibration(id, tmpdir, Vector, 
						     Target, factorNames, 
						     fuzzySetNums, Iterations, 
						     runs, WeightNum, WeightFactor, 
						     treduce.GetAnswer(), 
                                                     sdreduce.GetAnswer(), 
                                                     breakcrit.GetAnswer(), 
                                                     bagging.GetAnswer(), 
                                                     samplingFactor.GetAnswer())

                    CalibrationResult[id] = {"NAME":a, "FIS":b, "ERROR":error, 
                                             "BIC":BIC, "AIC":AIC, "MAF":MAF, 
                                             "Rsquared":Rsquared, "WEIGHTING":True}
                else:
                    error, BIC, AIC, MAF, Rsquared = StartCalibration(id, tmpdir, Vector, Target, 
                                                        factorNames, fuzzySetNums, 
                                                        Iterations, runs, 
                                                        treduce.GetAnswer(), 
                                                        sdreduce.GetAnswer(), 
                                                        breakcrit.GetAnswer(), 
                                                        bagging.GetAnswer(), 
                                                        samplingFactor.GetAnswer())
                
                    CalibrationResult[id] = {"NAME":a, "FIS":b, "ERROR":error, 
                                         "BIC":BIC, "AIC":AIC, "MAF":MAF, 
                                         "Rsquared":Rsquared, "WEIGHTING":False}
        
        # Selection of the best fit model
        
        minBIC = 99999999
        # Compute the delta BIC and BIC weight and append it to the Calibration result
        for key in CalibrationResult.keys():
            BIC = CalibrationResult[key]["BIC"]
            if BIC < minBIC:
                minBIC = BIC
                
        BICWeigthSum = 0
        for key in CalibrationResult.keys():
            BIC = CalibrationResult[key]["BIC"]
            BICDelta = math.fabs(BIC - minBIC)
            CalibrationResult[key]["DELTA_BIC"] = BICDelta
            CalibrationResult[key]["BIC_WEIGHT"] = math.exp(-1*BICDelta/2.0) 
            BICWeigthSum = BICWeigthSum +  CalibrationResult[key]["BIC_WEIGHT"]
            
        for key in CalibrationResult.keys():
            BICWeight = CalibrationResult[key]["BIC_WEIGHT"]
            MAF = CalibrationResult[key]["MAF"]
            BICWeight = BICWeight / BICWeigthSum
            CalibrationResult[key]["BIC_WEIGHT"] = BICWeight
            CalibrationResult[key]["BIC_MAF_WEIGHT"] = BICWeight / MAF
            
        # Select the best result from the CalibrationResult
        bestFitKey = None
        bestBICMAFWeight = 999999
        for key in CalibrationResult.keys():
            BICMAFWeight = CalibrationResult[key]["BIC_MAF_WEIGHT"]
            if BICMAFWeight < bestBICMAFWeight:
                bestFitKey = key
                
        # Copy the best fit factor names and fuzzy sets
        CalibrationResultFactors = CalibrationResult[bestFitKey]["NAME"]
        CalibrationResultFuzzySets = CalibrationResult[bestFitKey]["FIS"]
        
        # Build new StartFactor list
        StartFactors = []
        
        print "Factors ", Factors
        print "CalibrationResultFactors ", CalibrationResultFactors

        for factor in Factors:
            if factor not in CalibrationResultFactors:
                StartFactors.append(factor)
        
        print "StartFactors ", StartFactors

        # Search depth
        Count += 1

        print "Selected best fit model: "
        for name in CalibrationResult[bestFitKey].keys():
            print name, ":", CalibrationResult[bestFitKey][name]

    ###########################################################################
    # Write all results into the best fit file
    count = 0
    result = []
    for key in CalibrationResult.keys():
        result.append([str(key),CalibrationResult[key]["BIC_MAF_WEIGHT"]])
        count = count + 1
            
    # We sort the result based on the delta BIC
    result = sorted(result, key = lambda result: result[1])
    
    messageout = "RANK|NAME|BIC_MAF_WEIGHT|BIC_WEIGHT|DELTA_BIC|ERROR|BIC|AIC|MAF|Rsquared|WEIGHTING\n"
    
    file = open(resultlist.GetAnswer(), 'w')
    file.write(messageout)
    
    for key in range(count-1,0-1,-1):
        messageout = str(count  - key) + "|" + \
                     str(result[key][0]) + "|" + \
                     str(CalibrationResult[result[key][0]]["BIC_MAF_WEIGHT"]) + "|" + \
                     str(CalibrationResult[result[key][0]]["BIC_WEIGHT"]) + "|" + \
                     str(CalibrationResult[result[key][0]]["DELTA_BIC"]) + "|" + \
                     str(CalibrationResult[result[key][0]]["ERROR"]) + "|" + \
                     str(CalibrationResult[result[key][0]]["BIC"]) + "|" + \
                     str(CalibrationResult[result[key][0]]["AIC"]) + "|" + \
                     str(CalibrationResult[result[key][0]]["MAF"]) + "|" + \
                     str(CalibrationResult[result[key][0]]["Rsquared"]) + "|" + \
                     str(CalibrationResult[result[key][0]]["WEIGHTING"]) + "\n"
        file.write(messageout)

    file.close()

################################################################################

if __name__ == "__main__":
    main()

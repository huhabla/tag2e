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
# This is the content of the plotSelectionResult.R script located
# iwhtin htis directory
RScript = """
# We store the stdout output in a file
sink(file="Summary.txt")

# Rad data
sfs = read.table("input.txt", header=TRUE, sep="|")

################################################################################
# Compute linear regression model
sfslm = lm(sfs$target_variable ~ 0 + sfs$result_variable)
sfslmsum = summary(sfslm)
sfslmsum
paste("AKAIKE: " , AIC(sfslm))

# Plot to the first page
pdf("Result.pdf")
par(mfrow = c(3, 2))

axlim = c(min(sfs$target_variable), max(sfs$target_variable))
plot(sfs$target_variable ~ sfs$result_variable, xlim=axlim, ylim=axlim, asp="1", 
     main="current result", sub = paste("R squared: ", round(100 * sfslmsum$r.squared)/100, "   AKAIKE: " , round(AIC(sfslm))), 
     xlab="Model data", ylab="Reference data")
abline(sfslm, col="red")
abline(0,1, col="grey60", lty="dashed")

plot(sfslm)
dev.set(dev.next())

###END
"""

import grass.script as grass
import subprocess
import os
import sys
import random

from vtk import *
from libvtkTAG2ECommonPython import *
from libvtkTAG2EFilteringPython import *
from libvtkGRASSBridgeIOPython import *
from libvtkGRASSBridgeCommonPython import *
from libvtkGRASSBridgeTemporalPython import *

DEBUG = False

################################################################################

def StartCalibration(id, dir, inputvector, target, factornames, fuzzysets, iterations, runs, treduce, sdreduce, breakcrit):

    if DEBUG == True:
        error = random.randint(0,20)
        akaike = random.randint(0,2000)
        print id, " finished", runs, id, "weighted calibration runs with best fit error ", error, " akaike ", akaike
        return error, akaike

    error = 999
    akaike = 999999

    for i in range(runs):
        print "Running calibration", i, inputvector, target, factornames, fuzzysets

        grass.run_command("v.fuzzy.calibrator", overwrite=True, input=inputvector, factors=factornames,\
              target=target, fuzzysets=fuzzysets, iterations=iterations, \
              parameter=os.path.join(dir, (id + ".xml")), output=id, \
              log=os.path.join(dir, (id + ".log")), treduce=treduce, sdreduce=sdreduce, breakcrit=breakcrit)

        logfile = open(os.path.join(dir, id + ".log"), "r")
        runerror = float(logfile.readline())
        runakaike = float(logfile.readline())
        logfile.close()
        
        if runerror < error:
            error = runerror
        if runakaike < akaike:
            akaike = runakaike
        
    print "Finished", runs, " calibration runs with best fit", error, akaike
    return error, akaike

################################################################################

def StartWeightedCalibration(id, dir, inputvector, target, factornames, fuzzysets, iterations, runs, WeightNum, WeightFactor, treduce, sdreduce, breakcrit):

    if DEBUG == True:
        error = random.randint(0,20)
        akaike = random.randint(0,2000)
        print id, " finished", runs, "weighted calibration runs with best fit", error, akaike
        return error, akaike

    error = 999
    akaike = 999999

    for i in range(runs):
        print "Running weighted calibration", i, inputvector, target, factornames, fuzzysets

        grass.run_command("v.fuzzy.calibrator", flags="w", overwrite=True, input=inputvector, factors=factornames,\
              target=target, fuzzysets=fuzzysets, iterations=iterations, \
              parameter=os.path.join(dir, (id + ".xml")), output=id, \
              log=os.path.join(dir, (id + ".log")), treduce=treduce, sdreduce=sdreduce,\
              weightnum=WeightNum, weightfactor=WeightFactor)

        logfile = open(os.path.join(dir, id + ".log"), "r")
        runerror = float(logfile.readline())
        runakaike = float(logfile.readline())
        logfile.close()
        
        if runerror < error:
            error = runerror
        if runakaike < akaike:
            akaike = runakaike
        
    print "Finished", runs, "weighted calibration runs with best fit", error, akaike
    return error, akaike

################################################################################

def main():
    
    # Initiate GRASS
    init = vtkGRASSInit()
    init.Init("v.fuzzy.calibrator")
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

    rpdf = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "rpdf")
    rpdf.SetDescription("The output file name of the R script generated pdf file")

    rsum = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "rsum")
    rsum.SetDescription("The output file name of the R script generated summary file")

    resultlist = vtkGRASSOptionFactory().CreateInstance(vtkGRASSOptionFactory.GetFileOutputType(), "result")
    resultlist.SetDescription("The name of the logfile to store a sorted list of all factor combinations with AKAIKE and ERROR")

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

                error, akaike = StartCalibration(id, tmpdir, Vector, Target, factorNames, fuzzySetNums, \
                                                 Iterations, runs, treduce.GetAnswer(), sdreduce.GetAnswer(), breakcrit.GetAnswer())

                # Make a copy of the lists, otherwise the references get modified
                a = 1*factorNames
                b = 1*fuzzySetNums
                
                CalibrationResult[id] = [a, b, error, akaike, False]
                
                if weighting.GetAnswer():
                    id += "Weighting"
                    error, akaike = StartWeightedCalibration(id, tmpdir, Vector, Target, factorNames, fuzzySetNums, \
                                                             Iterations, runs, WeightNum, WeightFactor, treduce.GetAnswer(), \
                                                             sdreduce.GetAnswer(), breakcrit.GetAnswer())

                    # Make a copy of the lists, otherwise the references get modified
                    a = 1*factorNames
                    b = 1*fuzzySetNums

                    CalibrationResult[id] = [a, b, error, akaike, True]

        # Select the best result from the CalibrationResult
        firstError = 9999
        firstAKAIKE = 999999
        bestFitName = ""
        weightingOn = False
        for key in CalibrationResult.keys():
            fact, fuset, error, akaike, weight = CalibrationResult[key]
            if akaike < firstAKAIKE:
                firstAKAIKE = akaike
                CalibrationResultFactors = fact
                CalibrationResultFuzzySets = fuset
                bestFitName = key
                weightingOn = weight
                firstError = error

        # Check if the step results in a new selection, if not break
        if SelectedCalibration == bestFitName:
            break

        if weightingOn:
            print "Selected weighted model: ", bestFitName, firstAKAIKE, firstError, CalibrationResultFactors, CalibrationResultFuzzySets
        else:
            print "Selected model: ", bestFitName, firstAKAIKE, firstError, CalibrationResultFactors, CalibrationResultFuzzySets

        # Build new StartFactor list
        StartFactors = []

        for factor in Factors:
            if factor not in CalibrationResultFactors:
                StartFactors.append(factor)

        Count += 1

    # Write the best fit vector name and error into a log file
    print "Best fit" , bestFitName, "with akaike", firstAKAIKE, "and error", firstError
    print "File with result list: ", resultlist.GetAnswer()
    file = open(resultlist.GetAnswer(), 'w')
    file.write("Best fit: " + str(bestFitName) + "\n")
    file.write("Error: " + str(firstError))
    file.write("\n")
    file.write("AKAIKE: " + str(firstAKAIKE))
    file.write("\n")
    # Write all results into the best fit file
    count = 1
    result = []
    for key in CalibrationResult.keys():
        result.append([str(key),CalibrationResult[key][3]])	
        count = count + 1
            
    result =sorted(result, key = lambda result: result[1])
    
    for key in range(0,count-1,1):
        messageout = str(key) + " " + result[key][0] + "\t\tAKAIKE " +\
                     str(CalibrationResult[result[key][0]][3]) + "\tERROR  " +\
                     str(CalibrationResult[result[key][0]][2]) + "\tWeighting:  " + \
                     str(CalibrationResult[result[key][0]][4]) + "\n"
        file.write(messageout)

    file.close()
    
    # Write the result of the calibration into a text file
    filename = os.path.join(tmpdir, bestFitName + "_result.txt")
    grass.run_command("v.db.select", overwrite=True, map=bestFitName, file=filename)
    
    global RScript
    
    # Replace some palceholder in the R-script
    newRScript = RScript.replace("current", bestFitName)
    newRScript = newRScript.replace("Summary.txt", rsum.GetAnswer())
    newRScript = newRScript.replace("Result.pdf", rpdf.GetAnswer())
    newRScript = newRScript.replace("input.txt", filename)
    newRScript = newRScript.replace("target_variable", target.GetAnswer())
    newRScript = newRScript.replace("result_variable", "result")
    
    # Run R to analyze the result auomtatically and store the result in files
    inputlist = ["R", "--vanilla"]
    proc = subprocess.Popen(args=inputlist, stdin=subprocess.PIPE)
    proc.stdin.write(newRScript)
    proc.communicate()

################################################################################

if __name__ == "__main__":
    main()

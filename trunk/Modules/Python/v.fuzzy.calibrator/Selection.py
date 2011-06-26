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



Vector="n2o_emission"
Factors=["sand","Twin","Paut", "fertN"]
FuzzySets = [2]
Target="n2o"


################################################################################
################################################################################
################################################################################

def StartCalibration(id, inputvector, target, factornames, fuzzysets, iterations):

    print "Running calibration ", inputvector, target, factornames, fuzzysets

    grass.run_command("v.fuzzy.calibrator", input=inputvector, factors=factornames,\
          target=target, fuzzysets=fuzzysets, iterations=iterations, \
          parameter=(id + ".xml"), output=id, log=(id + ".log"))

    logfile = open(id + ".log")
    error = float(logfile.readline())
    logfile.close()
    return error


Count = 0
hierarchyFactors = []
hierarchyFuzzySets = []
StartFactors = Factors

hierarchy = {}

while Count < len(Factors):

    factorNames = []
    fuzzySetNums = []

    hierarchyCount = len(hierarchyFactors)

    # Insert the previous selected factors and fuzzy set numbers
    for i in range(hierarchyCount):
        factorNames.append(hierarchyFactors[i])
        fuzzySetNums.append(hierarchyFuzzySets[i])

    # Allocate the next entry
    factorNames.append("")
    fuzzySetNums.append("")

    # For each factor left
    for factor in StartFactors:
        factorNames[hierarchyCount] = factor
        for fuzzySet in FuzzySets:
            fuzzySetNums[hierarchyCount] = fuzzySet

            id = ""
            for i in range(len(factorNames)):
                id += str(factorNames[i]) + str(fuzzySetNums[i])
                
            error = StartCalibration(id, Vector, Target, factorNames, fuzzySetNums, 10000)

            # Make a copy of the lists, otherwise the references get modified
            a = 1*factorNames
            b = 1*fuzzySetNums
            
            hierarchy[id] = [a, b, error]

    # Select the best result from the hierarchy
    firstError = 9999
    bestFitName = ""
    for key in hierarchy.keys():
        fact, fuset, error = hierarchy[key]
        if error < firstError:
            firstError = error
            hierarchyFactors = fact
            hierarchyFuzzySets = fuset
            bestFitName = key

    print "Selected ", bestFitName, firstError, hierarchyFactors, hierarchyFuzzySets
    
    # Build new StartFactor list
    StartFactors = []

    for factor in Factors:
        if factor not in hierarchyFactors:
            StartFactors.append(factor)
            
    Count += 1

print "Best fit ", bestFitName, " with error ", firstError
file = open("BestFit.txt", 'w')
file.write("Best fit: " + str(bestFitName) + ".xml\n")
file.write("Error: " + str(firstError))
file.close()
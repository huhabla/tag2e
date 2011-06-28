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

################################################################################
################################################################################
################################################################################

def StartCalibration(id, inputvector, target, factornames, fuzzysets, iterations, runs):

    error = 999

    for i in range(runs):
        print "Running calibration", i, inputvector, target, factornames, fuzzysets

        grass.run_command("v.fuzzy.calibrator", overwrite=True, input=inputvector, factors=factornames,\
              target=target, fuzzysets=fuzzysets, iterations=iterations, \
              parameter=(id + ".xml"), output=id, log=(id + ".log"), \
              treduce=1.1, sdreduce=1.1)

        logfile = open(id + ".log")
        runerror = float(logfile.readline())
        logfile.close()
        
        if runerror < error:
            error = runerror
        
    print "Finished", runs, " calibration runs with best fit", error
    return error


################################################################################
################################################################################
################################################################################

def SequentialForwardSelection(Vector, Factors, FuzzySets, Target, Iterations, runs, searchDepth = 0):

    Count = 1
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

                error = StartCalibration(id, Vector, Target, factorNames, fuzzySetNums, Iterations, runs)

                # Make a copy of the lists, otherwise the references get modified
                a = 1*factorNames
                b = 1*fuzzySetNums

                CalibrationResult[id] = [a, b, error]

        # Select the best result from the CalibrationResult
        firstError = 9999
        bestFitName = ""
        for key in CalibrationResult.keys():
            fact, fuset, error = CalibrationResult[key]
            if error < firstError:
                firstError = error
                CalibrationResultFactors = fact
                CalibrationResultFuzzySets = fuset
                bestFitName = key

        # Check if the step results in a new selection, if not break
        if SelectedCalibration == bestFitName:
            break

        print "Selected ", bestFitName, firstError, CalibrationResultFactors, CalibrationResultFuzzySets

        # Build new StartFactor list
        StartFactors = []

        for factor in Factors:
            if factor not in CalibrationResultFactors:
                StartFactors.append(factor)

        Count += 1

    # Write the best fit into a file
    print "Best fit ", bestFitName, " with error ", firstError
    file = open(bestFitName + "_BestFit.txt", 'w')
    file.write("Best fit: " + str(bestFitName) + ".xml\n")
    file.write("Error: " + str(firstError))
    file.close()


def main():
    Vector="n2o_emission_param"
    Factors=["clay", "silt","sand","ph", "soc", "Twin", "Paut_before","Twin_before", "Paut", "fertN"]
    #Factors=["clay", "silt","sand", "fertN"]
    FuzzySets = [2]
    Target="n2o"
    Iterations = 5000
    runs = 1
    searchDepth = 3

    SequentialForwardSelection(Vector, Factors, FuzzySets, Target, Iterations, runs, searchDepth)
    

################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()
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

# This is the content of the plotSelectionResult.R script located
# iwhtin htis directory
RScript = """
# We store the stdout output in a file
sink(file="current_R_summary.txt")

# Rad data
sfs = read.table("current_result.txt", header=TRUE, sep="|")

################################################################################
# Compute linear regression model
sfslm = lm(sfs$n2o ~ 0 + sfs$result)
sfslmsum = summary(sfslm)
sfslmsum
paste("AKAIKE: " , AIC(sfslm))

# Plot to the first page
pdf("current_R_noscale_nointerc_result.pdf")
par(mfrow = c(3, 2))

axlim = c(min(sfs$n2o), max(sfs$n2o))
plot(sfs$n2o ~ sfs$result, xlim=axlim, ylim=axlim, asp="1", 
     main="current result", sub = paste("R squared: ", round(100 * sfslmsum$r.squared)/100, "   AKAIKE: " , round(AIC(sfslm))), 
     xlab="Model result", ylab="n2o Emission")
abline(sfslm, col="red")
abline(0,1, col="grey60", lty="dashed")

plot(sfslm)
dev.set(dev.next())

################################################################################
# Compute linear regression model with sqrt scaled data
sfslmsqrt = lm(sqrt(sfs$n2o) ~ 0 + sqrt(sfs$result))
sfslmsumsqrt = summary(sfslmsqrt)
sfslmsumsqrt
paste("AKAIKE: " , AIC(sfslmsqrt))


# Plot to the second page
pdf("current_R_sqrtscale_nointerc_result.pdf")
par(mfrow = c(3, 2))

axlimsqrt = c(min(sqrt(sfs$n2o)), max(sqrt(sfs$n2o)))
plot(sqrt(sfs$n2o) ~ sqrt(sfs$result), xlim=axlimsqrt, ylim=axlimsqrt, asp="1", 
     main="current result sqrt scaled", sub = paste("R squared: ", round(100 * sfslmsumsqrt$r.squared)/100, "   AKAIKE: " , round(AIC(sfslmsqrt))), 
     xlab="Model result", ylab="n2o Emission")
abline(sfslmsqrt, col="red")
abline(0,1, col="grey60", lty="dashed")

plot(sfslmsqrt)
dev.set(dev.next())

################################################################################
# Compute linear regression model
sfslm = lm(sfs$n2o ~ sfs$result)
sfslmsum = summary(sfslm)
sfslmsum
paste("AKAIKE: " , AIC(sfslm))

# Plot to the first page
pdf("current_R_noscale_result.pdf")
par(mfrow = c(3, 2))

axlim = c(min(sfs$n2o), max(sfs$n2o))
plot(sfs$n2o ~ sfs$result, xlim=axlim, ylim=axlim, asp="1", 
     main="current result", sub = paste("R squared: ", round(100 * sfslmsum$r.squared)/100, "   AKAIKE: " , round(AIC(sfslm))), 
     xlab="Model result", ylab="n2o Emission")
abline(sfslm, col="red")
abline(0,1, col="grey60", lty="dashed")

plot(sfslm)
dev.set(dev.next())

################################################################################
# Compute linear regression model with sqrt scaled data
sfslmsqrt = lm(sqrt(sfs$n2o) ~ sqrt(sfs$result))
sfslmsumsqrt = summary(sfslmsqrt)
sfslmsumsqrt
paste("AKAIKE: " , AIC(sfslmsqrt))

# Plot to the second page
pdf("current_R_sqrtscale_result.pdf")
par(mfrow = c(3, 2))

axlimsqrt = c(min(sqrt(sfs$n2o)), max(sqrt(sfs$n2o)))
plot(sqrt(sfs$n2o) ~ sqrt(sfs$result), xlim=axlimsqrt, ylim=axlimsqrt, asp="1", 
     main="current result sqrt scaled", sub = paste("R squared: ", round(100 * sfslmsumsqrt$r.squared)/100, "   AKAIKE: " , round(AIC(sfslmsqrt))), 
     xlab="Model result", ylab="n2o Emission")
abline(sfslmsqrt, col="red")
abline(0,1, col="grey60", lty="dashed")

plot(sfslmsqrt)
dev.set(dev.next())


###END
"""

################################################################################
################################################################################
################################################################################

def StartCalibration(id, inputvector, target, factornames, fuzzysets, iterations, runs):

    error = 999
    akaike = 999999

    for i in range(runs):
        print "Running calibration", i, inputvector, target, factornames, fuzzysets

        grass.run_command("v.fuzzy.calibrator", overwrite=True, input=inputvector, factors=factornames,\
              target=target, fuzzysets=fuzzysets, iterations=iterations, \
              parameter=(id + ".xml"), output=id, log=(id + ".log"), \
              treduce=1.1, sdreduce=1.1)

        logfile = open(id + ".log")
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
################################################################################
################################################################################

def SequentialForwardSelection(Vector, Factors, FuzzySets, Target, Iterations, runs, searchDepth = 0):

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

                error, akaike = StartCalibration(id, Vector, Target, factorNames, fuzzySetNums, Iterations, runs)

                # Make a copy of the lists, otherwise the references get modified
                a = 1*factorNames
                b = 1*fuzzySetNums
                
                CalibrationResult[id] = [a, b, error, akaike]

        # Select the best result from the CalibrationResult
        firstError = 9999
        firstAKAIKE = 999999
        bestFitName = ""
        for key in CalibrationResult.keys():
            fact, fuset, error, akaike = CalibrationResult[key]
            if akaike < firstAKAIKE:
                firstAKAIKE = akaike
                CalibrationResultFactors = fact
                CalibrationResultFuzzySets = fuset
                bestFitName = key
            if error < firstError:
                firstError = error

        # Check if the step results in a new selection, if not break
        if SelectedCalibration == bestFitName:
            break

        print "Selected ", bestFitName, firstAKAIKE, CalibrationResultFactors, CalibrationResultFuzzySets

        # Build new StartFactor list
        StartFactors = []

        for factor in Factors:
            if factor not in CalibrationResultFactors:
                StartFactors.append(factor)

        Count += 1

    # Write the best fit vector name and error into a log file
    print "Best fit ", bestFitName, " with error ", firstError, " with akaike", firstAKAIKE
    file = open(bestFitName + "_BestFit.txt", 'w')
    file.write("Best fit: " + str(bestFitName) + ".xml\n")
    file.write("Error: " + str(firstError))
    file.write("\n")
    file.write("AKAIKE: " + str(firstAKAIKE))
    file.close()
    
    # Write the result of the calibration into a text file
    grass.run_command("v.db.select", overwrite=True, map=bestFitName, file=(bestFitName + "_result.txt"))
    
    global RScript
    
    # Replace current in the R script with the best fit result vector name
    newRScript = RScript.replace("current", bestFitName)
    
    # Run R to analyze the result auomtatically and store the result in files
    inputlist = ["R", "--vanilla"]
    proc = subprocess.Popen(args=inputlist, stdin=subprocess.PIPE)
    proc.stdin.write(newRScript)
    proc.communicate()

def main():
    Vector="n2o_emission_param"
    Factors=["clay", "silt","sand","ph", "soc", "Twin", "Paut_before","Twin_before", "Paut", "fertN"]
    # Factors=["Paut", "Twin_before","sand", "fertN", "soc"]
    # Factors=["sand"]
    FuzzySets = [2,3]
    Target="n2o"
    Iterations = 5000
    runs = 1
    searchDepth = 4

    SequentialForwardSelection(Vector, Factors, FuzzySets, Target, Iterations, runs, searchDepth)
    

################################################################################
################################################################################
################################################################################

if __name__ == "__main__":
    main()
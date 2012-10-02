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
from libvtkGRASSBridgeTemporalPython import *
from libvtkGRASSBridgeCommonPython import *
from MetaModel import *

DaysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

################################################################################
################################################################################
################################################################################

def _RothCEquilibrium(ETpotInputs, WaterBudgetInputs, RothCInputs, 
                        ResidualsInput, Years, NumberOfRuns,
                        RothCParameter=None, NullValue=-99999):
    """!Compute the RothC soil carbon equilibrium
    
       @param ETpotInputs: A list of 12 inputs, each the long term parameter
                          for ETpot computation.
                          - Long term monthly temperature mean [degree C]
                          - Long term monthly global radiation [J/(cm^2 * day)]
       
       @param WaterBudgetInputs: A list of 12 inputs, each the long term 
                          parameter for Water Budget computation.
                          - Long term monthly accumulated precipitation [mm]
                          - Long term monthly soil cover (0 or 1) [-]
                          - Clay content in percent [%]
       
       param RothCInputs: A list of 12 vtkPolyData inputs, each the long term
                          parameter of the RothC model
                          - Clay content in percent [%]
                          - Long term monthly soil cover (0 or 1) [-]
                          - Long term monthly temperature mean [degree C]
                          - Long term monthly fertilizer carbon (should be 0)
                          - Initial C-org
                          
       param ResidualsInput: The initial residuals as vtkPolyData input
                          for the RothC model [tC/ha]
                          
       @param Years: The maximum number of Iterations (years) for a single run
       @param NumberOfRuns: The maximum number of runs to find the equilibrium
       @param RothCParameter: The parameter object for the RothC Model
       @param NullValue: The Null value that represents unknown values
       
       @return A vtkPolyDataSet with RothC pools and initial Carbon
    """
    
    # Check the inputs
    if len(ETpotInputs) != 12:
        raise IOError("Not enough dataset in ETpotInput")
    for dataset in ETpotInputs:
        if dataset.GetNumberOfPoints() != ETpotInputs[0].GetNumberOfPoints():
            raise IOError("Datasets in ETpotInput have different number of points")
        if dataset.GetNumberOfCells() != ETpotInputs[0].GetNumberOfCells():
            raise IOError("Datasets in ETpotInput have different number of cells")
    
    # Check the inputs
    if len(WaterBudgetInputs) != 12:
        raise IOError("Not enough dataset in WaterBudgetInput")
    for dataset in WaterBudgetInputs:
        if dataset.GetNumberOfPoints() != WaterBudgetInputs[0].GetNumberOfPoints():
            raise IOError("Datasets in WaterBudgetInput have different number of points")
        if dataset.GetNumberOfCells() != WaterBudgetInputs[0].GetNumberOfCells():
            raise IOError("Datasets in WaterBudgetInput have different number of cells")
    
    # Check the inputs
    if len(RothCInputs) != 12:
        raise IOError("Not enough dataset in RothCInput")
    for dataset in RothCInputs:
        if dataset.GetNumberOfPoints() != RothCInputs[0].GetNumberOfPoints():
            raise IOError("Datasets in RothCInput have different number of points")
        if dataset.GetNumberOfCells() != RothCInputs[0].GetNumberOfCells():
            raise IOError("Datasets in RothCInput have different number of cells")
    
    # Initiate the models and connect them
    
    # Compute potential evapo-transpiration
    ETpot = vtkTAG2ETurcETPotModel()
    ETpot.SetNullValue(NullValue)
    
    # Soil moisture computation
    SoilMoisture = vtkTAG2ERothCWaterBudgetModel()
    SoilMoisture.SetNullValue(NullValue)
         
    # Residual distribution
    residuals = vtkTAG2ERothCResidualFilter()
    residuals.SetNullValue(NullValue)
    
    # RothC model computation
    if not RothCParameter:
        RothCParameter = vtkTAG2ERothCModelParameter()

    RothC = vtkTAG2ERothCModel()
    RothC.SetModelParameter(RothCParameter)
    RothC.AddCPoolsToOutputOn()
    RothC.SetNullValue(NullValue)

    # Split the residuals   
    residuals.SetInput(ResidualsInput)
    
    for year in xrange(0, Years, 1):
        print "Year", year
        for month in xrange(0, 12, 1):                
            ETpot.SetInput(ETpotInputs[month])
            ETpot.SetTimeInterval(DaysPerMonth[month])
            
            # Soil moisture input
            dc1 = vtkTAG2EDataSetJoinFilter()
            dc1.AddInputConnection(ETpot.GetOutputPort())
            dc1.AddInput(WaterBudgetInputs[month])
            
            SoilMoisture.SetInputConnection(dc1.GetOutputPort())
            
            dc2 = vtkTAG2EDataSetJoinFilter()
            dc2.AddInput(RothCInputs[month])
            dc2.AddInputConnection(SoilMoisture.GetOutputPort())
            
            # Add the residuals at August
            if month == 7:
                dc2.AddInputConnection(residuals.GetOutputPort())

            RothC.SetInputConnection(dc2.GetOutputPort())
            RothC.Update()
    
    # Return the output of RothC
    output = vtkPolyData()
    output.ShallowCopy(RothC.GetOutput())
    
    return output
        
################################################################################
################################################################################
################################################################################

def RothCEquilibriumRun(ETpotInputs, WaterBudgetInputs, RothCInputs, 
                        ResidualsInput, SoilCarbonInput, Years, NumberOfRuns,
                        RothCParameter=None, NullValue=-99999):
    """!Compute the RothC soil carbon equilibrium using Brents method
    
       @param ETpotInputs: A list of 12 inputs, each the long term parameter
                          for ETpot computation.
                          - Long term monthly temperature mean [degree C]
                          - Long term monthly global radiation [J/(cm^2 * day)]
       
       @param WaterBudgetInputs: A list of 12 inputs, each the long term 
                          parameter for Water Budget computation.
                          - Long term monthly accumulated precipitation [mm]
                          - Long term monthly soil cover (0 or 1) [-]
                          - Clay content in percent [%]
       
       param RothCInputs: A list of 12 vtkPolyData inputs, each the long term
                          parameter of the RothC model
                          - Clay content in percent [%]
                          - Long term monthly soil cover (0 or 1) [-]
                          - Long term monthly temperature mean [degree C]
                          - Long term monthly fertilizer carbon (should be 0)
                          - Initial C-org
                          
       param ResidualsInput: The initial residuals as vtkPolyData input
                          for the RothC model [tC/ha]
                          
       param SoilCarbonInput: The resulting carbon as vtkPolyData input
                          for the distance computation of model and target values [tC/ha]
                          
       @param Years: The maximum number of Iterations (years) for a single run
       @param NumberOfRuns: The maximum number of runs to find the equilibrium
       @param RothCParameter: The parameter object for the RothC Model
       @param NullValue: The Null value that represents unknown values
       
       @return A vtkPolyDataSet with RothC pools and initial Carbon
    """   
    
    # Initial model run
    model = _RothCEquilibrium(ETpotInputs, WaterBudgetInputs, RothCInputs, 
                        ResidualsInput, Years, NumberOfRuns, RothCParameter, NullValue)
            
    # The brent and check lists
    blist = model.GetNumberOfCells()*[vtkTAG2EBrentsMethod()]
    clist = model.GetNumberOfCells()*[False]
    
    # Initiate brents computation
    for id in xrange(model.GetNumberOfCells()):
        bx = ResidualsInput.GetCellData().GetScalars().GetTuple1(id)
        fx = model.GetCellData().GetScalars().GetTuple1(id)
        blist[id].Init(0, bx, 0.5, 0.0000000001, fx)
                
    # Iterate
    for run in range(NumberOfRuns):
                
        meanBx = 0.0
        for id in xrange(model.GetNumberOfCells()):
            if blist[id].IsFinished():
                print "Brent finished at id", id
                clist[id] = True
                continue
            
            # Compute the best fit and use it as input for the equilibrium run
            bx = blist[id].Fit()
            ResidualsInput.GetCellData().GetScalars().SetTuple1(id, bx)
            meanBx += bx
            
        print "Mean bx", meanBx / model.GetNumberOfCells()
            
        # Run the model
        model = _RothCEquilibrium(ETpotInputs, WaterBudgetInputs, RothCInputs, 
                        ResidualsInput, Years, NumberOfRuns, RothCParameter, NullValue)
                
        meanRes = 0.0
        for id in xrange(model.GetNumberOfCells()):
            if clist[id] == True:
                continue
            
            fx = model.GetCellData().GetScalars().GetTuple1(id)
            target = SoilCarbonInput.GetCellData().GetScalars().GetTuple1(id)
            
            res = math.sqrt((target -fx) * (target - fx))
            meanRes += res
            
            # Check break criteria
            if res < 0.01:
                print "Break criteria reached at id", id
                clist[id] = True
                continue
            
            #Evaluate the model result
            blist[id].Evaluate(res)
        
        print "Mean res", meanRes / model.GetNumberOfCells()
            
        # Break if all values are computed
        if min(clist) == True:
            print "Finished after ", run, " iterations"
            break
            
    return model

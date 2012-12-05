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

DaysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

################################################################################
################################################################################
################################################################################

def _RothCEquilibrium(Inputs, ResidualsInput, Years, RothCParameter=None, 
                        NullValue=-99999):
    """!Compute the RothC soil carbon equilibrium
    
       @param ETpotInputs: A list of 12 inputs, each with the long term parameter
                          - Long term monthly temperature mean [degree C]
                          - Long term monthly global radiation [J/(cm^2 * day)]
                          - Long term monthly accumulated precipitation [mm]
                          - Long term monthly soil cover (0 or 1) [-]
                          - Clay content in percent [%]
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
    if len(Inputs) != 12:
        raise IOError("Not enough datasets in Inputs")
    for dataset in Inputs:
        if dataset.GetNumberOfPoints() != Inputs[0].GetNumberOfPoints():
            raise IOError("Datasets in Inputs have different number of points")
        if dataset.GetNumberOfCells() != Inputs[0].GetNumberOfCells():
            raise IOError("Datasets in Inputs have different number of cells")
    
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
    if not RothCParameter or RothCParameter == None:
        RothCParameter = vtkTAG2ERothCModelParameter()

    RothC = vtkTAG2ERothCModel()
    RothC.SetModelParameter(RothCParameter)
    RothC.AddCPoolsToOutputOn()
    RothC.EquilibriumRunOn()
    RothC.SetNullValue(NullValue)
    
    dc1 = vtkTAG2EDataSetJoinFilter()
    dc2 = vtkTAG2EDataSetJoinFilter()
    
    # We need to distribute the residuals equally over the year
    res = vtkPolyData()
    res.DeepCopy(ResidualsInput)
    a = res.GetCellData().GetArray("Residuals")
    for id in xrange(ResidualsInput.GetNumberOfCells()):
        a.SetTuple1(id, a.GetTuple1(id)/12.0)
    
    # Split the residuals   
    residuals.SetInput(res)
    
    for year in xrange(0, Years, 1):
        #print "\n\n**** Year", year
        for month in xrange(0, 12, 1): 
            
            dc1.RemoveAllInputs()
            dc2.RemoveAllInputs()
                           
            ETpot.SetInput(Inputs[month])
            ETpot.SetTimeInterval(DaysPerMonth[month])
            
            # Soil moisture input
            dc1.AddInputConnection(ETpot.GetOutputPort())
            dc1.AddInput(Inputs[month])
            
            SoilMoisture.SetInputConnection(dc1.GetOutputPort())
            
            # ETpot input
            dc2.AddInput(Inputs[month])
            dc2.AddInputConnection(SoilMoisture.GetOutputPort())
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

def RothCEquilibriumRun(Inputs, ResidualsInput, SoilCarbonInput, Years, NumberOfRuns,
                        RothCParameter=None, NullValue=-99999, ax=0, cx=15, 
                        brent_error=0.00001):
    """!Compute the RothC soil carbon equilibrium using Brents method
    
       @param Inputs: A list of 12 inputs, each with long term parameter
                          - Long term monthly temperature mean [degree C]
                          - Long term monthly global radiation [J/(cm^2 * day)]
                          - Long term monthly accumulated precipitation [mm]
                          - Long term monthly soil cover (0 or 1) [-]
                          - Long term monthly fertilizer carbon (should be 0)
                          - Clay content in percent [%]
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
    model = _RothCEquilibrium(Inputs, ResidualsInput, Years, RothCParameter, 
                              NullValue)
            
    # The brent and check lists
    blist = model.GetNumberOfCells()*[None]
    clist = model.GetNumberOfCells()*[False]
    
    squaredResiduals = vtkDoubleArray()
    
    # Compute squared residuals
    vtkTAG2EAbstractModelCalibrator.ComputeDataSetsResiduals(model, SoilCarbonInput, 
                                                             True, squaredResiduals, True)
    
    # Initiate brents computation
    for id in xrange(model.GetNumberOfCells()):
        bx = ResidualsInput.GetCellData().GetScalars().GetTuple1(id)
        res = squaredResiduals.GetTuple1(id)
        cal = vtkTAG2EBrentsMethod()
        blist[id] = cal
        blist[id].Init(ax, bx, cx, brent_error, res)
    
    # Iterate
    for run in range(NumberOfRuns):
        
        print "***** Run ", run
                
        for id in xrange(model.GetNumberOfCells()):
            
            # Jump over finished cells
            if clist[id]:
                continue
            
            if blist[id].IsFinished():
                #print "Brent break criteria reached at id", id, " fx ", blist[id].Getfx(), " x", blist[id].Getx()
                # Put the computed model input value into the residuals dataset
                ResidualsInput.GetCellData().GetScalars().SetTuple1(id, blist[id].Getx())
                clist[id] = True
                continue
            
            # Compute the best fit and use it as input for the equilibrium run
            bx = blist[id].Fit()
            ResidualsInput.GetCellData().GetScalars().SetTuple1(id, bx)
            
        # Run the model
        model = _RothCEquilibrium(Inputs, ResidualsInput, Years, RothCParameter, 
                                  NullValue)
        
        # Compute squared residuals
        vtkTAG2EAbstractModelCalibrator.ComputeDataSetsResiduals(model, SoilCarbonInput, 
                                                                 True, squaredResiduals, True)
        
        for id in xrange(model.GetNumberOfCells()):
            # Jump over finished cells
            if clist[id]:
                continue
            
            res = squaredResiduals.GetTuple1(id)
            #print "Id", id, "squared res ", res
            
            #Evaluate the model result
            blist[id].Evaluate(res)
            
            # Check break criteria
            if res < 0.01:
                #print "Residual break criteria reached at id", id, " fx ", blist[id].Getfx(), " x", blist[id].Getx()
                clist[id] = True
                ResidualsInput.GetCellData().GetScalars().SetTuple1(id, blist[id].Getx())
                continue
            
        # Break if all values are computed
        if min(clist) == True:
            print "Finished after ", run, " iterations"
            break
    
    print "Final run with latest residuals"
    model = _RothCEquilibrium(Inputs, ResidualsInput, Years, RothCParameter, 
                              NullValue)
                
    return model

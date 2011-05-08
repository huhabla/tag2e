/*
 *  Toolkit for Agriculture Greenhouse Gas Emission Estimation TAG2E
 *
 * Authors: Soeren Gebbert, soeren.gebbert@vti.bund.de
 *          Rene Dechow, rene.dechow@vti.bund.de
 *
 * Copyright:
 *
 * Johann Heinrich von Thünen-Institut
 * Institut für Agrarrelevante Klimaforschung
 *
 * Phone: +49 (0)531 596 2601
 *
 * Fax:+49 (0)531 596 2699
 *
 * Mail: ak@vti.bund.de
 *
 * Bundesallee 50
 * 38116 Braunschweig
 * Germany
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 */

#include <vtkObjectFactory.h>
#include <vtkDataSet.h>
#include <vtkDataArray.h>
#include <vtkPointData.h>
#include <vtkDoubleArray.h>
#include <vtkCellData.h>
#include <vtkTemporalDataSet.h>
#include <vtkFieldData.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include "vtkTAG2ESimulatedAnnealingModelCalibrator.h"
#include <stdlib.h>
#include <time.h>
#include <math.h>


vtkCxxRevisionMacro(vtkTAG2ESimulatedAnnealingModelCalibrator, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ESimulatedAnnealingModelCalibrator);

//----------------------------------------------------------------------------

vtkTAG2ESimulatedAnnealingModelCalibrator::vtkTAG2ESimulatedAnnealingModelCalibrator()
{
  this->BreakCriteria = 0.01;
  this->StandardDeviation = 1;
  this->TMinimizer = 1.001;
  this->MaxNumberOfIterations = 5000;
  this->InitialT = 1;
  time_t t = time(NULL);
  this->Seed = (unsigned int) t;
  this->BestFitModelParameter = NULL;
}

//----------------------------------------------------------------------------

vtkTAG2ESimulatedAnnealingModelCalibrator::~vtkTAG2ESimulatedAnnealingModelCalibrator()
{
  if (this->BestFitModelParameter)
    this->BestFitModelParameter->Delete();
}

//----------------------------------------------------------------------------

int vtkTAG2ESimulatedAnnealingModelCalibrator::RequestData(
  vtkInformation *vtkNotUsed(request),
  vtkInformationVector **vtkNotUsed(inputVector),
  vtkInformationVector *outputVector)
{
  vtkInformation *outInfo = outputVector->GetInformationObject(0);

  vtkTemporalDataSet *output = vtkTemporalDataSet::SafeDownCast(
    outInfo->Get(vtkDataObject::DATA_OBJECT()));

  // Initiate the random number generator
  srand(this->Seed);

  int i;
  double error;
  double lastAcceptedError;
  double bestFitError;

  if (this->Model == NULL) {
    vtkErrorMacro( << "The model is not set");
    return 0;
  }

  if (this->ModelParameter == NULL) {
    vtkErrorMacro( << "The model parameter is not set");
    return 0;
  }

  // Check for existing best fit model parameter
  if (this->BestFitModelParameter)
    this->BestFitModelParameter->Delete();

  // We store the parameter of the best fit separately in an instance of the same type
  this->BestFitModelParameter = this->ModelParameter->NewInstance();
  this->BestFitModelParameter->GetXMLRoot()->DeepCopy(this->ModelParameter->GetXMLRoot());
  
  // The initial run of the model with the initial initialization
  this->Model->SetModelParameter(this->ModelParameter);
  this->Model->Update();

  // Make a shallow copy of the model output
  output->ShallowCopy(this->Model->GetOutput());

  // Compute the initial error
  error = vtkTAG2EAbstractModelCalibrator::CompareTemporalDataSets(this->Model->GetOutput(),
    this->Model->GetResultArrayName(), this->TargetArrayName, this->Model->GetUseCellData(), 0);

  // Initialize best fit and old error
  bestFitError = lastAcceptedError = error;

  // This is the main loop
  for (i = 0; i < this->MaxNumberOfIterations; i++) {
    // Some verbose output
    if ((i + 1) % (int)(this->MaxNumberOfIterations / 100.0) == 1) {
      std::cout << "Iteration " << i << " error " << error << " T " << this->InitialT << std::endl;
    }

    // Modify the model parameter randomly
    bool success = this->ModelParameter->ModifyParameterRandomly(this->StandardDeviation);
    if (success == false) {
      vtkErrorMacro( << "Unable to modify model parameter");
      return 0;
    }
    // Run the model, the modified parameter is referenced internally 
    // so we need to tell the model that its modified
    this->Model->SetModelParameter(this->ModelParameter);
    this->Model->Update();

    // Compute the error between the model result and the target values
    error = vtkTAG2EAbstractModelCalibrator::CompareTemporalDataSets(this->Model->GetOutput(),
      this->Model->GetResultArrayName(), this->TargetArrayName, this->Model->GetUseCellData(), 0);
    
    // The difference between last and current computation
    double diff = error - lastAcceptedError;
    
    // In case the new error is lower the old error
    if (diff <= 0.0) {
      lastAcceptedError = error;
      // Store the best fit
      if (error < bestFitError) {
        bestFitError = error;
        std::cout << "Store best result at error " << bestFitError << std::endl;
        output->ShallowCopy(this->Model->GetOutput());
        this->BestFitModelParameter->GetXMLRoot()->DeepCopy(this->ModelParameter->GetXMLRoot());
      }
    } else {
      // Compute the criteria to accept poor configurations
      double r = (double) rand() / (double) RAND_MAX;
      double pa = exp(-1.0 * diff / this->InitialT);

      if (pa > 1)
        pa = 1;

      // Restore the last modified parameter
      if (r > pa) {
        success = this->ModelParameter->RestoreLastModifiedParameter();
        if (success == false) {
          vtkErrorMacro( << "Unable to restore modified parameter");
          return 0;
        }
      } else {
        lastAcceptedError = error;
        this->InitialT /= this->TMinimizer;
      }
    }

    // Break if the best fit is reached
    if (bestFitError < this->BreakCriteria)
      break;
  }

  std::cout << "Finished after " << i << " iteration with best fit error " << bestFitError << std::endl;

  return 1;

}
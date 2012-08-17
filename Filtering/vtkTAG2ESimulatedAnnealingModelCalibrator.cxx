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
#include <vtkFieldData.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include "vtkTAG2ESimulatedAnnealingModelCalibrator.h"
#include "vtkTAG2EFuzzyInferenceModelParameter.h"
#include <stdlib.h>
#include <time.h>
#include <math.h>

vtkCxxRevisionMacro(vtkTAG2ESimulatedAnnealingModelCalibrator,
    "$Revision: 1.0 $");
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
  this->BestFitError = 999999;
  this->BestFitModelAssessmentFactor = 1;
}

//----------------------------------------------------------------------------

vtkTAG2ESimulatedAnnealingModelCalibrator::~vtkTAG2ESimulatedAnnealingModelCalibrator()
{
  if (this->BestFitModelParameter)
    this->BestFitModelParameter->Delete();
}

//----------------------------------------------------------------------------

int vtkTAG2ESimulatedAnnealingModelCalibrator::RequestData(
    vtkInformation *vtkNotUsed(request), vtkInformationVector **inputVector,
    vtkInformationVector *outputVector)
{
  int i;
  double error;
  double modelAssessment;
  double lastAcceptedError;
  double bestFitError;
  double bestFitModelAssessment;
  vtkXMLDataElement *root = vtkXMLDataElement::New();

  vtkDataSet* input = vtkDataSet::GetData(inputVector[0]);
  vtkDataSet* output = vtkDataSet::GetData(outputVector);

  if (this->Model == NULL)
    {
    vtkErrorMacro( << "The model is not set");
    return 0;
    }

  if (this->ModelParameter == NULL)
    {
    vtkErrorMacro( << "The model parameter is not set");
    return 0;
    }

  // Initiate the random number generator
  srand(this->Seed);

  // Check for existing best fit model parameter
  if (this->BestFitModelParameter)
    this->BestFitModelParameter->Delete();

  // We store the parameter of the best fit separately in an instance of the same type
  this->BestFitModelParameter = this->ModelParameter->NewInstance();
  this->ModelParameter->GetXMLRepresentation(root);
  this->BestFitModelParameter->SetXMLRepresentation(root);

  // The initial run of the model with initialization
  this->Model->SetModelParameter(this->ModelParameter);
  this->Model->Update();
  bestFitModelAssessment = modelAssessment =
      this->Model->GetModelAssessmentFactor();

  // Make a shallow copy of the model output
  output->ShallowCopy(this->Model->GetOutput());

  // Compute the initial error
  error = vtkTAG2EAbstractModelCalibrator::CompareDataSets(
      this->Model->GetOutput(), input, this->Model->GetUseCellData(), 0)
      * modelAssessment;

  // Initialize the error variables
  bestFitError = lastAcceptedError = error;

  // This is the main loop
  for (i = 0; i < this->MaxNumberOfIterations; i++)
    {

    // Some verbose output
    if (this->MaxNumberOfIterations > 100)
      {
      if ((i + 1) % (int) (this->MaxNumberOfIterations / 100.0) == 1)
        {
        std::cout << "Iteration " << i << " error " << error << " Best fit "
            << bestFitError << " T " << this->InitialT << std::endl;
        }
      } else
      {
      std::cout << "Iteration " << i << " error " << error << " Best fit "
          << bestFitError << " T " << this->InitialT << std::endl;
      }

    // Modify the model parameter randomly
    bool success = this->ModelParameter->ModifyParameterRandomly(
        this->StandardDeviation);
    if (success == false)
      {
      vtkErrorMacro( << "Unable to modify model parameter");
      return 0;
      }
    // Run the model, the modified parameter is referenced internally 
    // so we need to tell the model that its modified
    this->Model->Modified();
    this->Model->Update();
    modelAssessment = this->Model->GetModelAssessmentFactor();

    // Compute the error between the model result and the target values
    error = vtkTAG2EAbstractModelCalibrator::CompareDataSets(
        this->Model->GetOutput(), input, this->Model->GetUseCellData(), 0)
        * modelAssessment;

    // The difference between last and current computation
    double diff = error - lastAcceptedError;

    // In case the new error is lower as the last configuration
    if (diff <= 0.0)
      {
      lastAcceptedError = error;
      // Store the best fit
      if (error < bestFitError)
        {
        bestFitError = error;
        bestFitModelAssessment = modelAssessment;
        std::cout << "Store best result at iteration " << i << " with error "
            << bestFitError << std::endl;
        output->ShallowCopy(this->Model->GetOutput());
        this->ModelParameter->GetXMLRepresentation(root);
        this->BestFitModelParameter->SetXMLRepresentation(root);
        }
      } else
      {
      // Compute the criteria to accept poor configurations
      double r = (double) rand() / (double) RAND_MAX;
      double pa = exp(-1.0 * diff / this->InitialT);

      if (pa > 1)
        pa = 1;

      // Restore the last modified parameter
      if (r > pa)
        {
        success = this->ModelParameter->RestoreLastModifiedParameter();
        if (success == false)
          {
          vtkErrorMacro( << "Unable to restore modified parameter");
          return 0;
          }
        } else
        {
        lastAcceptedError = error;
        this->InitialT /= this->TMinimizer;
        }
      }

    // Break if the best fit is reached
    if (bestFitError < this->BreakCriteria)
      break;
    }

  this->BestFitError = bestFitError;
  this->BestFitModelAssessmentFactor = bestFitModelAssessment;

  std::cout << "Finished after " << i << " iteration with best fit error "
      << bestFitError << " model assessment factor " << bestFitModelAssessment
      << std::endl;

  root->Delete();

  return 1;

}

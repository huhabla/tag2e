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
#include <vtkCommand.h>
#include <vtkCompositeDataPipeline.h>
#include <vtkDataSet.h>
#include <vtkPointData.h>
#include <vtkIntArray.h>
#include <vtkDoubleArray.h>
#include <vtkStringArray.h>
#include <vtkTemporalDataSet.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkDataSetAttributes.h>

#include <vtkDataSetAlgorithm.h>
#include <vtkObjectFactory.h>
#include "vtkTAG2EWeightedFuzzyInferenceModel.h"
#include "vtkTAG2EFuzzyInferenceModelParameter.h"

vtkCxxRevisionMacro(vtkTAG2EWeightedFuzzyInferenceModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EWeightedFuzzyInferenceModel);

//----------------------------------------------------------------------------

vtkTAG2EWeightedFuzzyInferenceModel::vtkTAG2EWeightedFuzzyInferenceModel()
{
  this->FuzzyModelParameter = NULL;
}

//----------------------------------------------------------------------------

vtkTAG2EWeightedFuzzyInferenceModel::~vtkTAG2EWeightedFuzzyInferenceModel()
{
  ;
}

//----------------------------------------------------------------------------

int vtkTAG2EWeightedFuzzyInferenceModel::FillInputPortInformation(
  int vtkNotUsed(port),
  vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkTemporalDataSet");
  return 1;
}


//----------------------------------------------------------------------------

int vtkTAG2EWeightedFuzzyInferenceModel::RequestUpdateExtent(
  vtkInformation *vtkNotUsed(request),
  vtkInformationVector **inputVector,
  vtkInformationVector *outputVector)
{
  int numInputs = this->GetNumberOfInputPorts();
  vtkInformation *outInfo = outputVector->GetInformationObject(0);

  //cerr << "Setting UPDATE_TIME_STEPS for " << numInputs << " inputs" << endl;

  // Remove any existing output UPDATE_TIME_STEPS, beacuse we will set them from 
  // the first input
  if (outInfo->Has(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS()))
    outInfo->Remove(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS());

  if (!outInfo->Has(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS())) {
    int i;
    double *timeSteps = inputVector[0]->GetInformationObject(0)->Get(vtkStreamingDemandDrivenPipeline::TIME_STEPS());
    int numTimeSteps = inputVector[0]->GetInformationObject(0)->Length(vtkStreamingDemandDrivenPipeline::TIME_STEPS());

    // We request for each input the same number of update timesteps as for the first input
    for (i = 1; i < numInputs; i++) {
      //cerr << "Setting from first input numTimeSteps: "<< numTimeSteps << " for input " << i << endl;
      inputVector[i]->GetInformationObject(0)->Set(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS(), timeSteps, numTimeSteps);
    }

    outInfo->Set(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS(), timeSteps, numTimeSteps);
  }

  return 1;
}



//----------------------------------------------------------------------------

int vtkTAG2EWeightedFuzzyInferenceModel::RequestData(
  vtkInformation * vtkNotUsed(request),
  vtkInformationVector **inputVector,
  vtkInformationVector *outputVector)
{
  unsigned int timeStep;

  // get the info objects
  vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
  vtkInformation *outInfo = outputVector->GetInformationObject(0);

  // Check for model parameter
  if (this->ModelParameter == NULL) {
    vtkErrorMacro("Model parameter not set or invalid.");
    return -1;
  }

  // get the first input and ouptut
  vtkTemporalDataSet *firstInput = vtkTemporalDataSet::SafeDownCast(
    inInfo->Get(vtkDataObject::DATA_OBJECT()));

  vtkTemporalDataSet *output = vtkTemporalDataSet::SafeDownCast(
    outInfo->Get(vtkDataObject::DATA_OBJECT()));

  output->SetNumberOfTimeSteps(firstInput->GetNumberOfTimeSteps());

  vtkDataSetAttributes *Data = vtkDataSetAttributes::New();

  this->ComputeFIS(Data);

  return 1;

  // Iterate over each timestep of the first input
  // Timesteps must be equal in the inputs.
  for (timeStep = 0; timeStep < firstInput->GetNumberOfTimeSteps(); timeStep++) {
    int i = 0;
    int port;

    // The first input is used to create the ouput
    // It is assumed that each input has the same number of points and the same topology
    // The number of point data arrays can/should differ
    vtkDataSet *firstInputDataSet = vtkDataSet::SafeDownCast(firstInput->GetTimeStep(timeStep));
    vtkDataSet *outputDataSet = firstInputDataSet->NewInstance();
    outputDataSet->DeepCopy(firstInputDataSet);

    // For input port and defeined array name
    for (i = 0; i < this->GetNumberOfInputPorts(); i++) {


      //cerr << "Processing input port " << port << " at time step " << timeStep << endl;

      // Get the correct input port for the input
      vtkInformation *activeInputInfo = inputVector[port]->GetInformationObject(0);

      // Check if the input port was filled with data
      if (activeInputInfo == NULL) {
        vtkErrorMacro( << "No temporal dataset available at input port " << port);
        return -1;
      }

      vtkTemporalDataSet *activeInput = vtkTemporalDataSet::SafeDownCast(activeInputInfo->Get(vtkDataObject::DATA_OBJECT()));
      vtkDataSet *activeInputDataSet = vtkDataSet::SafeDownCast(activeInput->GetTimeStep(timeStep));

      // Check if a dataset is present at actual time step
      if (activeInputDataSet == NULL) {
        vtkErrorMacro( << "No dataset available at input port " << port << " time step " << timeStep);
        return -1;
      }

      // Check if the number of points and cells in the active input are identical with the first input
      if (firstInputDataSet->GetNumberOfPoints() != activeInputDataSet->GetNumberOfPoints() ||
        firstInputDataSet->GetNumberOfCells() != activeInputDataSet->GetNumberOfCells()) {
        vtkErrorMacro( << "The number of points or cells differ between the inputs.");
        return -1;
      }

      //TODO: Support point and cell data 
      // Get the point data
      vtkPointData *inputData = activeInputDataSet->GetPointData();


    }

    //TODO: Support point and cell data 
    output->SetTimeStep(timeStep, outputDataSet);
    outputDataSet->Delete();
  }

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2EWeightedFuzzyInferenceModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}

//----------------------------------------------------------------------------

bool vtkTAG2EWeightedFuzzyInferenceModel::ComputeFIS(vtkDataSetAttributes *Data)
{
  int numberOfRules = 0;
  int numberOfFactors = 0;
  int **RuleCodeArray;

  if (this->ModelParameter->IsA("vtkTAG2EFuzzyInferenceModelParameter")) {
    this->FuzzyModelParameter = static_cast<vtkTAG2EFuzzyInferenceModelParameter *> (this->ModelParameter);
  } else {
    vtkErrorMacro( << "The ModelParameter is not of type vtkTAG2EFuzzyInferenceModelParameter");
    return false;
  }

  this->FuzzyModelParameter->GenerateInternalSchemeFromXML();

  WeightedFuzzyInferenceScheme &WFIS = this->FuzzyModelParameter->GetInternalScheme();

  numberOfRules = WFIS.FIS.Factors[0].Sets.size();
  numberOfFactors = WFIS.FIS.Factors.size();

  int j, i = 0;

  for (i = 0; i < numberOfFactors; i++) {
    FuzzyFactor &Factor = WFIS.FIS.Factors[i];

    if (i > 0)
      numberOfRules *= Factor.Sets.size();

    vtkDoubleArray *array = vtkDoubleArray::New();
    array->SetName(Factor.name.c_str());

    for (j = 0; j < 100; j++) {
      array->InsertNextTuple1(Factor.max);
    }

    Data->AddArray(array);
    array->Delete();
  }

  cout << "Number of Rules " << numberOfRules << endl;

  // Allocate memory for the rules code
  RuleCodeArray = (int**) calloc(numberOfRules, sizeof (int*));
  for (i = 0; i < numberOfRules; i++) {
    RuleCodeArray[i] = (int*) calloc(numberOfFactors + 1, sizeof (int));
  }
 
  this->ComputeRuleCodeArrayEntries(RuleCodeArray, numberOfRules, WFIS);
  
  return true;
}


bool vtkTAG2EWeightedFuzzyInferenceModel::ComputeRuleCodeArrayEntries(int **RuleCodeArray, int numberOfRules, WeightedFuzzyInferenceScheme &WFIS)
{
  int col, x, length, length1, dum, inp, num, num1;
  int numberOfFactors = WFIS.FIS.Factors.size();
  
  for (col = numberOfFactors - 1; col >= 0; col--) {
    length = 1;
    dum = col + 1;
    while (dum <= numberOfFactors - 1) {
      FuzzyFactor &Factor = WFIS.FIS.Factors[dum];
      length = length * Factor.Sets.size();
      dum = dum + 1;
    }
    length1 = 1;
    dum = col;
    while (dum <= numberOfFactors - 1) {
      FuzzyFactor &Factor = WFIS.FIS.Factors[dum];
      length1 = length1 * Factor.Sets.size();
      dum = dum + 1;
    }
    inp = 0;
    num = 0;
    num1 = 0;
    for (x = 0; x < numberOfRules; x++) {
      RuleCodeArray [x][col] = inp;
      printf("%i %i %i\n",col,x,inp);
      num = num + 1;
      num1 = num1 + 1;
      if (num == length) {
        num = 0;
        inp = inp + 1;
      }
      if (num1 == length1) {
        num = 0;
        inp = 0;
        num1 = 0;
      }
    }
  }


  return true;
}
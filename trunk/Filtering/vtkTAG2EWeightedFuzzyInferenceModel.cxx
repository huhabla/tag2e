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

#include "tag2eWFIS.h"

vtkCxxRevisionMacro(vtkTAG2EWeightedFuzzyInferenceModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EWeightedFuzzyInferenceModel);

//----------------------------------------------------------------------------

vtkTAG2EWeightedFuzzyInferenceModel::vtkTAG2EWeightedFuzzyInferenceModel()
{
  this->FuzzyModelParameter = NULL;
  this->InputPorts = vtkIntArray::New();
  this->ArrayNames = vtkStringArray::New();
}

//----------------------------------------------------------------------------

vtkTAG2EWeightedFuzzyInferenceModel::~vtkTAG2EWeightedFuzzyInferenceModel()
{
  this->InputPorts->Delete();
  this->ArrayNames->Delete();
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

void vtkTAG2EWeightedFuzzyInferenceModel::SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter)
{
  int i = 0;

  this->Superclass::SetModelParameter(modelParameter);

  this->ArrayNames->Initialize();
  this->InputPorts->Initialize();

  // Check if the ModelParameter is of correct type
  if (this->ModelParameter->IsA("vtkTAG2EFuzzyInferenceModelParameter")) {
    this->FuzzyModelParameter = static_cast<vtkTAG2EFuzzyInferenceModelParameter *> (this->ModelParameter);
  } else {
    vtkErrorMacro( << "The ModelParameter is not of type vtkTAG2EFuzzyInferenceModelParameter");
    this->SetModelParameter(NULL);
    return;
  }

  // Generate the internal representation
  this->FuzzyModelParameter->GenerateInternalSchemeFromXML();

  WeightedFuzzyInferenceScheme &WFIS = this->FuzzyModelParameter->GetInternalScheme();

  // Count the input ports and array names
  for (i = 0; i < this->FuzzyModelParameter->GetNumberOfFactors(); i++) {
    this->InputPorts->InsertValue(i, WFIS.FIS.Factors[i].portId);
    this->ArrayNames->InsertValue(i, WFIS.FIS.Factors[i].name);
  }

  double *range = this->InputPorts->GetRange();
  // Ports from 0 ... n must be used  
  this->SetNumberOfInputPorts((int) (range[1] + 1));
}

//----------------------------------------------------------------------------

int vtkTAG2EWeightedFuzzyInferenceModel::RequestData(
  vtkInformation * vtkNotUsed(request),
  vtkInformationVector **inputVector,
  vtkInformationVector *outputVector)
{
  unsigned int timeStep;
  int numberOfRules = 0;
  int numberOfFactors = 0;

  // get the info objects
  vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
  vtkInformation *outInfo = outputVector->GetInformationObject(0);

  // Check for model parameter
  if (this->ModelParameter == NULL) {
    vtkErrorMacro("Model parameter not set or invalid.");
    return -1;
  }

  WeightedFuzzyInferenceScheme &WFIS = this->FuzzyModelParameter->GetInternalScheme();

  // Compute the number of rules and number of factors
  numberOfRules = this->FuzzyModelParameter->GetNumberOfRules();
  numberOfFactors = this->FuzzyModelParameter->GetNumberOfFactors();

  // Create the rule code matrix
  std::vector< std::vector<int> > RuleCodeMatrix(numberOfRules, std::vector<int>(numberOfFactors));

  // Compute the rule code matrix entries 
  tag2eWFIS::ComputeRuleCodeMatrixEntries(RuleCodeMatrix, numberOfRules, WFIS);

  // get the first input and ouptut
  vtkTemporalDataSet *firstInput = vtkTemporalDataSet::SafeDownCast(
    inInfo->Get(vtkDataObject::DATA_OBJECT()));

  vtkTemporalDataSet *output = vtkTemporalDataSet::SafeDownCast(
    outInfo->Get(vtkDataObject::DATA_OBJECT()));

  output->SetNumberOfTimeSteps(firstInput->GetNumberOfTimeSteps());

  // Iterate over each timestep of the first input
  // Timesteps must be equal in the inputs.
  for (timeStep = 0; timeStep < firstInput->GetNumberOfTimeSteps(); timeStep++) {
    int i, j;
    int port;

    // The first input is used to create the ouput
    // It is assumed that each input has the same number of points and the same topology
    // The number of point data arrays can/should differ
    vtkDataSet *firstInputDataSet = vtkDataSet::SafeDownCast(firstInput->GetTimeStep(timeStep));
    vtkDataSet *outputDataSet = firstInputDataSet->NewInstance();
    // outputDataSet->CopyStructure(firstInputDataSet);
    outputDataSet->DeepCopy(firstInputDataSet);

    // Result for the current time step
    vtkDoubleArray *result = vtkDoubleArray::New();
    result->SetNumberOfComponents(0);
    result->SetName(this->ResultArrayName);
    result->SetNumberOfTuples(firstInputDataSet->GetNumberOfPoints());
    result->FillComponent(0,0.0);

    // This is used to store the needed arrays pointer to collect the 
    // data for fuzzy computation
    std::vector<vtkDataArray *> Data;

    // Get the arrays for each input port and factor
    for (i = 0; i < this->InputPorts->GetNumberOfTuples(); i++) {

      port = this->InputPorts->GetValue(i);
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
      vtkDataSetAttributes *inputData = activeInputDataSet->GetPointData();
      // Get the array and 

      // Check if the array exists in the current input
      if (!inputData->HasArray(this->ArrayNames->GetValue(i))) {
        vtkErrorMacro( << "Array " << this->ArrayNames->GetValue(i) << " is missing in input. Wrong reference in the model parameter");
        return -1;
      }

      // Put the array pointer into the vector template
      Data.push_back(inputData->GetArray(this->ArrayNames->GetValue(i)));
    }
    
    //TODO: Support point and cell data
    // Run the Fuzzy model for each point/pixel
    for (i = 0; i < firstInputDataSet->GetNumberOfPoints(); i++) {

      // Input array for fuzzy logic computation
      double *fuzzyInput = new double[numberOfFactors];

      for (j = 0; j < numberOfFactors; j++) {
        Data[j]->GetTuple(i, &fuzzyInput[j]);
      }

      double val = tag2eWFIS::ComputeFISResult(fuzzyInput, numberOfRules, RuleCodeMatrix, WFIS);
      result->SetValue(i, val);
      delete [] fuzzyInput;
    }

    //TODO: Support point and cell data 
    outputDataSet->GetPointData()->AddArray(result);
    outputDataSet->GetPointData()->SetActiveScalars(result->GetName());
    output->SetTimeStep(timeStep, outputDataSet);
    outputDataSet->Delete();
    result->Delete();
  }

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2EWeightedFuzzyInferenceModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}


//----------------------------------------------------------------------------

#define TOLERANCE 0.000000001

bool vtkTAG2EWeightedFuzzyInferenceModel::TestFISComputation()
{
  // Create a simple weighted fuzzy inference scheme
  WeightedFuzzyInferenceScheme WFIS;

  WFIS.name = "Test";

  FuzzyFactor F1; // nrate
  FuzzyFactor F2; // temprature

  FuzzySet F1S1;
  FuzzySet F1S2;

  FuzzySet F2S1;
  FuzzySet F2S2;

  FuzzyResponse R1;
  FuzzyResponse R2;
  FuzzyResponse R3;
  FuzzyResponse R4;

  // Create a factor with two triangle shape fuzzy sets

  // The triangle shape has the following form
  //   ___  ___
  //  |   \/   |
  //  |   /\   |
  //  0 .4 .6  1

  F1S1.type = FUZZY_SET_TYPE_TRIANGULAR;
  F1S2.type = FUZZY_SET_TYPE_TRIANGULAR;

  F1S1.constant = false;
  F1S2.constant = false;

  F1S1.position = FUZZY_SET_POISITION_LEFT;
  F1S2.position = FUZZY_SET_POISITION_RIGHT;

  F1S1.priority = 0;
  F1S2.priority = 0;

  F1S1.Triangular.left = 2222;
  F1S1.Triangular.center = 0.4;
  F1S1.Triangular.right = 0.2;

  F1S2.Triangular.left = 0.2;
  F1S2.Triangular.center = 0.6;
  F1S2.Triangular.right = 2222;

  // The second factor has the same shape
  F2S1 = F1S1;
  F2S2 = F1S2;

  F1.min = 0;
  F1.max = 150;
  F1.name = "nrate";
  F1.portId = 0;
  F1.Sets.push_back(F1S1);
  F1.Sets.push_back(F1S2);

  F2.min = -15;
  F2.max = 35;
  F2.name = "temp";
  F2.portId = 0;
  F2.Sets.push_back(F2S1);
  F2.Sets.push_back(F2S2);

  R1.value = 1;
  R2.value = 2;
  R3.value = 3;
  R4.value = 4;

  WFIS.FIS.Responses.Responses.push_back(R1);
  WFIS.FIS.Responses.Responses.push_back(R2);
  WFIS.FIS.Responses.Responses.push_back(R3);
  WFIS.FIS.Responses.Responses.push_back(R4);

  WFIS.FIS.Responses.min = 1;
  WFIS.FIS.Responses.max = 4;

  WFIS.FIS.Factors.push_back(F1);
  WFIS.FIS.Factors.push_back(F2);

  WFIS.Weight.active = true;
  WFIS.Weight.constant = false;
  WFIS.Weight.max = 100;
  WFIS.Weight.min = 0.001;
  WFIS.Weight.name = "vegetables";
  WFIS.Weight.value = 1.0;

  int i, j;
  int numberOfRules = 4;
  int numberOfFactors = 2;

  cout << "ComputeRuleCodeMatrixEntries Test" << endl;

  // Create the rule code matrix
  std::vector< std::vector<int> > RuleCodeMatrix(numberOfRules, std::vector<int>(numberOfFactors));

  tag2eWFIS::ComputeRuleCodeMatrixEntries(RuleCodeMatrix, numberOfRules, WFIS);

  for (i = 0; i < numberOfRules; i++) {
    for (j = 0; j < numberOfFactors; j++) {
      cout << RuleCodeMatrix[i][j] << " ";
    }
    cout << endl;
  }

  if (RuleCodeMatrix[0][0] != 0 ||
    RuleCodeMatrix[0][1] != 0 ||
    RuleCodeMatrix[1][0] != 0 ||
    RuleCodeMatrix[1][1] != 1 ||
    RuleCodeMatrix[2][0] != 1 ||
    RuleCodeMatrix[2][1] != 0 ||
    RuleCodeMatrix[3][0] != 1 ||
    RuleCodeMatrix[3][1] != 1) {
    (std::cerr << "ComputeRuleCodeMatrixEntries failed");
    return false;
  }

  cout << "ComputeDOF Test 1 Mean" << endl;
  // First test the mean
  double Input[2] = {75.0, 10.0};
  double result;

  result = tag2eWFIS::ComputeDOF(Input, 0, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 1 1");
    return false;
  }
  result = tag2eWFIS::ComputeDOF(Input, 1, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 1 2");
    return false;
  }
  result = tag2eWFIS::ComputeDOF(Input, 2, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 1 3");
    return false;
  }
  result = tag2eWFIS::ComputeDOF(Input, 3, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 1 4");
    return false;
  }

  cout << "ComputeFISResult Test 1" << endl;
  result = tag2eWFIS::ComputeFISResult(Input, numberOfRules, RuleCodeMatrix, WFIS);
  cout << "Result = " << result << endl;
  if (fabs(result - 2.5) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeFISResult Test 1");
  }

  cout << "ComputeDOF Test 2 Left border" << endl;

  Input[0] = 0.0;
  Input[1] = -15.0;

  result = tag2eWFIS::ComputeDOF(Input, 0, RuleCodeMatrix, WFIS);
  if (fabs(result - 1.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 2 1");
  }
  result = tag2eWFIS::ComputeDOF(Input, 1, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 2 2");
  }
  result = tag2eWFIS::ComputeDOF(Input, 2, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 2 3");
  }
  result = tag2eWFIS::ComputeDOF(Input, 3, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 2 4");
  }

  cout << "ComputeFISResult Test 2" << endl;
  result = tag2eWFIS::ComputeFISResult(Input, numberOfRules, RuleCodeMatrix, WFIS);
  cout << "Result = " << result << endl;
  if (fabs(result - 1.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeFISResult Test 2");
  }

  cout << "ComputeDOF Test 3 right border" << endl;

  Input[0] = 150;
  Input[1] = 35;

  result = tag2eWFIS::ComputeDOF(Input, 0, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 3 1");
  }
  result = tag2eWFIS::ComputeDOF(Input, 1, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 3 2");
  }
  result = tag2eWFIS::ComputeDOF(Input, 2, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 3 3");
  }
  result = tag2eWFIS::ComputeDOF(Input, 3, RuleCodeMatrix, WFIS);
  if (fabs(result - 1.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeDOF Test 3 4");
  }

  cout << "ComputeFISResult Test 3" << endl;
  result = tag2eWFIS::ComputeFISResult(Input, numberOfRules, RuleCodeMatrix, WFIS);
  cout << "Result = " << result << endl;
  if (fabs(result - 4.0) > TOLERANCE) {
    (std::cerr << "Wrong result in ComputeFISResult Test 3");
  }

  return true;
}

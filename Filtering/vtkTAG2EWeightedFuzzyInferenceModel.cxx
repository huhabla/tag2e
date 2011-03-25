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

#define TOLERANCE 0.000000001

/* This is a static array with smapling points and associated values
 * of the standard normal distribution. It is
 * used for faster computation.
 */
static double NormDistSamplingPoints[27][2] = {
  {-4, 0.000335463},
  {-3, 0.011108997},
  {-2.5, 0.043936934},
  {-2, 0.135335283},
  {-1.8, 0.197898699},
  {-1.6, 0.2780373},
  {-1.4, 0.375311099},
  {-1.2, 0.486752256},
  {-1, 0.60653066},
  {-0.8, 0.726149037},
  {-0.6, 0.835270211},
  {-0.4, 0.923116346},
  {-0.2, 0.980198673},
  {0, 1},
  {0.2, 0.980198673},
  {0.4, 0.923116346},
  {0.6, 0.835270211},
  {0.8, 0.726149037},
  {1, 0.60653066},
  {1.2, 0.486752256},
  {1.4, 0.375311099},
  {1.6, 0.2780373},
  {1.8, 0.197898699},
  {2, 0.135335283},
  {2.5, 0.043936934},
  {3, 0.011108997},
  {4, 0.000335463}
};

// Simple maximum computation
static double max(double x, double y);

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
  double *fuzzyInput;
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
  this->ComputeRuleCodeMatrixEntries(RuleCodeMatrix, numberOfRules, WFIS);

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

    // Input array for fuzzy logic computation
    fuzzyInput = new double(numberOfFactors);

    // The first input is used to create the ouput
    // It is assumed that each input has the same number of points and the same topology
    // The number of point data arrays can/should differ
    vtkDataSet *firstInputDataSet = vtkDataSet::SafeDownCast(firstInput->GetTimeStep(timeStep));
    vtkDataSet *outputDataSet = firstInputDataSet->NewInstance();
    outputDataSet->CopyStructure(firstInputDataSet);

    // Result for the current time step
    vtkDataArray *result = vtkDoubleArray::New();
    result->SetNumberOfComponents(0);
    result->SetName(this->ResultArrayName);
    result->SetNumberOfTuples(firstInputDataSet->GetNumberOfPoints());

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
      vtkPointData *inputData = activeInputDataSet->GetPointData();
      // Get the array and 

      // Check if the array exists in the current input
      if (!inputData->HasArray(this->ArrayNames->GetValue(i))) {
        vtkErrorMacro( << "Array " << this->ArrayNames->GetValue(i) << " is missing in input. Wrong reference in the model parameter");
        return -1;
      }

      // Put the array pointer into the vector template
      Data.push_back(inputData->GetArray(this->ArrayNames->GetValue(i)));
    }
    
    double val;
    // Run the Fuzzy model for each point/pixel
    for (i = 0; i < firstInputDataSet->GetNumberOfPoints(); i++) {
      for (j = 0; j < numberOfFactors; j++) {
        fuzzyInput[j] = Data[j]->GetTuple1(i);
      }
      val = this->ComputeFISResult(fuzzyInput, numberOfRules, RuleCodeMatrix, WFIS);
      result->SetTuple1(i, val);
    }

    //TODO: Support point and cell data 
    outputDataSet->GetPointData()->AddArray(result);
    outputDataSet->GetPointData()->SetActiveScalars(result->GetName());
    output->SetTimeStep(timeStep, outputDataSet);
    outputDataSet->Delete();
    result->Delete();
    delete [] fuzzyInput;
  }


  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2EWeightedFuzzyInferenceModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}

//----------------------------------------------------------------------------

bool vtkTAG2EWeightedFuzzyInferenceModel::ComputeRuleCodeMatrixEntries(std::vector< std::vector<int> > &RuleCodeMatrix, int numberOfRules, WeightedFuzzyInferenceScheme &WFIS)
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
      RuleCodeMatrix [x][col] = inp;
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

//----------------------------------------------------------------------------

double vtkTAG2EWeightedFuzzyInferenceModel::ComputeFISResult(double *Input,
  int numberOfRules, std::vector< std::vector<int> > &RuleCodeMatrix, WeightedFuzzyInferenceScheme &WFIS)
{
  int rule;
  double result;
  double dof, sum_dofs;

  sum_dofs = 0.0;
  result = 0.0;

  // Compute the deegree of fullfillment for each rule
  for (rule = 0; rule < numberOfRules; rule++) {

    dof = this->ComputeDOF(Input, rule, RuleCodeMatrix, WFIS);

    sum_dofs = sum_dofs + dof;
    result = result + WFIS.FIS.Responses.Responses[rule].value * dof;
  }

  // Check for wrong results and apply the deegreees of fullfillment
  if (sum_dofs == 0) {
    vtkErrorMacro( << "Sum of deegrees of fullfillments is 0. Expect wrong model results.");
    result = 0.0;
  } else {
    result = result / sum_dofs;
  }

  // Weight the result
  if (WFIS.Weight.active) {
    result *= WFIS.Weight.value;
  }

  return result;
}

//----------------------------------------------------------------------------

double vtkTAG2EWeightedFuzzyInferenceModel::ComputeDOF(double *Input,
  int rule, std::vector< std::vector<int> > &RuleCodeMatrix, WeightedFuzzyInferenceScheme &WFIS)
{

  int numberOfFactors = WFIS.FIS.Factors.size();
  int d = 0, pos, shape;
  double *dom = new double[numberOfFactors]; // Deegree of membership of a fuzzy set
  double *normedInput = new double(numberOfFactors); // Normalized input values
  double dof; // The resulting deegree of fullfillment for the rule


  //cout << "Normed values" << endl;
  // Norm the Input values and write the result in normedInput
  for (d = 0; d < numberOfFactors; d++) {
    normedInput[d] = (Input[d] - WFIS.FIS.Factors[d].min) / (WFIS.FIS.Factors[d].max - WFIS.FIS.Factors[d].min);
    //cout << normedInput[d] << endl;
  }

  d = 0;
  dof = 1; // We need o initialize the resulting DOF with 1
  do {
    pos = (RuleCodeMatrix[rule][d]);
    shape = WFIS.FIS.Factors[d].Sets[pos].type;

    // The value of normedInput at position d is normed [0:1]. In case larger values than 10 we assume 
    // the membership is 100%. Values larger than 10 my occure in case values are missing and 
    // replaced by a large default number.
    if ((normedInput[d] > 10) || (normedInput[d] < 0)) {
      dom[d] = 1;
    } else {
      FuzzySet &Set = WFIS.FIS.Factors[d].Sets[pos];
      switch (shape) {
      case FUZZY_SET_TYPE_BELL_SHAPE: //stanorm
        if (normedInput[d] - Set.BellShape.center <= 0) //left_side of the mean of the fuzzy number
        {
          if ((normedInput[d] - Set.BellShape.center) / Set.BellShape.sdLeft<-4) {
            dom[d] = 0.000001;
          } else {
            dom[d] = InterpolatePointInNormDist((normedInput[d] - Set.BellShape.center) / Set.BellShape.sdLeft);
          }
        } else { //right side of the mean of the fuzzy number
          if ((normedInput[d] - Set.BellShape.center) / Set.BellShape.sdRight > 4) {
            dom[d] = 0.000001;
          } else {
            dom[d] = InterpolatePointInNormDist((normedInput[d] - Set.BellShape.center) / Set.BellShape.sdRight);
          }
        }
        break;
      case FUZZY_SET_TYPE_TRIANGULAR: // triangular fuzzy numbers
        double m;

        if (normedInput[d] - Set.Triangular.center <= 0) //left side of the fuzzy number
        {
          //cout << "Is left" << endl;
          if ((Set.Triangular.left) > 1111) {
            dom[d] = 1;
          } else {
            m = 1 / Set.Triangular.left;
            dom[d] = max(0.0, m * (normedInput[d] - Set.Triangular.center) + 1);
          }
        } else//right side of fuzzy number
        {
          //cout << "Is right" << endl;
          if (Set.Triangular.right > 1111) {
            dom[d] = 1;
          } else {
            m = -1 / Set.Triangular.right;
            dom[d] = max(0.0, m * (normedInput[d] - Set.Triangular.center) + 1);
          }
        }

        break;
      case FUZZY_SET_TYPE_CRISP: // all or nothing the split is just in the middle between two alphas
        if (normedInput[d] >= Set.Crisp.left && normedInput[d] <= Set.Crisp.right) {
          dom[d] = 1;
        } else {
          dom[d] = 0;
        }
        break;
      }
    }
    dof *= dom[d]; // Accumulate the deegree of fullfillment
    //printf(" %f\n", dom[d]);
    d++;
  } while (d < (numberOfFactors));

  //  cout << "Deegree of fullfillment " << dof << endl;
  return dof;
}

//----------------------------------------------------------------------------

double vtkTAG2EWeightedFuzzyInferenceModel::InterpolatePointInNormDist(double value)
{
  int w1 = 0, w2 = 26, w3 = 0;
  double dummy;
  do {
    dummy = (w1 + w2) / 2;
    w3 = floor(dummy);
    if (value > NormDistSamplingPoints[w3 ][0]) {
      w1 = w3;
    } else {
      w2 = w3;
    }
  } while (w1 + 1 < w2);

  return NormDistSamplingPoints[w1][1] +
    (NormDistSamplingPoints[w2][1] -
    NormDistSamplingPoints[w1][1]) /
    (NormDistSamplingPoints[w2][0] -
    NormDistSamplingPoints[w1][0]) *
    (value - NormDistSamplingPoints[w1][0]);

}

//----------------------------------------------------------------------------

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
  //  |   ̣\/   |
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

  this->ComputeRuleCodeMatrixEntries(RuleCodeMatrix, numberOfRules, WFIS);

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
    vtkErrorMacro( << "ComputeRuleCodeMatrixEntries failed");
    return false;
  }

  cout << "ComputeDOF Test 1 Mean" << endl;
  // First test the mean
  double Input[2] = {75.0, 10.0};
  double result;

  result = ComputeDOF(Input, 0, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 1 1");
    return false;
  }
  result = ComputeDOF(Input, 1, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 1 2");
    return false;
  }
  result = ComputeDOF(Input, 2, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 1 3");
    return false;
  }
  result = ComputeDOF(Input, 3, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.25) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 1 4");
    return false;
  }

  cout << "ComputeFISResult Test 1" << endl;
  result = ComputeFISResult(Input, numberOfRules, RuleCodeMatrix, WFIS);
  cout << "Result = " << result << endl;
  if (fabs(result - 2.5) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeFISResult Test 1");
  }

  cout << "ComputeDOF Test 2 Left border" << endl;

  Input[0] = 0.0;
  Input[1] = -15.0;

  result = ComputeDOF(Input, 0, RuleCodeMatrix, WFIS);
  if (fabs(result - 1.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 2 1");
  }
  result = ComputeDOF(Input, 1, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 2 2");
  }
  result = ComputeDOF(Input, 2, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 2 3");
  }
  result = ComputeDOF(Input, 3, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 2 4");
  }

  cout << "ComputeFISResult Test 2" << endl;
  result = ComputeFISResult(Input, numberOfRules, RuleCodeMatrix, WFIS);
  cout << "Result = " << result << endl;
  if (fabs(result - 1.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeFISResult Test 2");
  }

  cout << "ComputeDOF Test 3 right border" << endl;

  Input[0] = 150;
  Input[1] = 35;

  result = ComputeDOF(Input, 0, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 3 1");
  }
  result = ComputeDOF(Input, 1, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 3 2");
  }
  result = ComputeDOF(Input, 2, RuleCodeMatrix, WFIS);
  if (fabs(result - 0.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 3 3");
  }
  result = ComputeDOF(Input, 3, RuleCodeMatrix, WFIS);
  if (fabs(result - 1.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeDOF Test 3 4");
  }

  cout << "ComputeFISResult Test 3" << endl;
  result = ComputeFISResult(Input, numberOfRules, RuleCodeMatrix, WFIS);
  cout << "Result = " << result << endl;
  if (fabs(result - 4.0) > TOLERANCE) {
    vtkErrorMacro( << "Wrong result in ComputeFISResult Test 3");
  }

  return true;
}

//----------------------------------------------------------------------------

double max(double x, double y)
{
  double w;
  if (x < y) {
    w = y;
  } else {
    w = x;
  }
  return w;
}
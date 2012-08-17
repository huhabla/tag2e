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
#include <vtkStringArray.h>
#include <vtkIntArray.h>
#include <vtkDoubleArray.h>
#include <vtkDataArrayCollection.h>
#include <vtkRInterface.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkPointSet.h>
#include <vtkPolyData.h>
#include <vtkPointData.h>
#include <vtkPoints.h>
#include <vtkDataSet.h>
#include <vtkStreamingDemandDrivenPipeline.h>
#include <vtkIdList.h>
#include "vtkTAG2EModelMonteCarloVariationAnalyser.h"
#include "vtkTAG2ELinearRegressionModel.h"
#include <math.h>

vtkCxxRevisionMacro(vtkTAG2EModelMonteCarloVariationAnalyser,
    "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EModelMonteCarloVariationAnalyser);

vtkTAG2EModelMonteCarloVariationAnalyser::vtkTAG2EModelMonteCarloVariationAnalyser()
{
  this->RInterface = vtkRInterface::New();

  this->NormalizedCumulativeSum = vtkDoubleArray::New();
  this->BreakCriterion = 0.01; // Change of the cummultive sum
}

//----------------------------------------------------------------------------

vtkTAG2EModelMonteCarloVariationAnalyser::~vtkTAG2EModelMonteCarloVariationAnalyser()
{
  ;
}

//----------------------------------------------------------------------------
int vtkTAG2EModelMonteCarloVariationAnalyser::FillOutputPortInformation(
    int port, vtkInformation* info)
{
  if (!this->Superclass::FillOutputPortInformation(port, info))
    {
    return 0;
    }
  info->Set(vtkDataObject::DATA_TYPE_NAME(), "vtkDataSet");
  return 1;
}

//----------------------------------------------------------------------------

int vtkTAG2EModelMonteCarloVariationAnalyser::RequestData(
    vtkInformation * vtkNotUsed(request),
    vtkInformationVector **vtkNotUsed(inputVector),
    vtkInformationVector *outputVector)
{
  // Build the Array which describes the input variable distribution
  this->BuildDataDistributionDescriptionArrays();

  // Check for data distribution parameter
  if (this->DataDistributionDescription == NULL)
    {
    vtkErrorMacro("DataDistributionDescription not set or invalid.");
    return -1;
    }

  // The result distribution array 
  vtkDoubleArray *dist = vtkDoubleArray::New();
  dist->SetNumberOfComponents(1);
  dist->SetName(this->Model->GetResultArrayName());

  this->NormalizedCumulativeSum->SetNumberOfValues(this->NumberOfRandomValues);

  int iter;
  double lastsum = 0.0;

  for (iter = 0; iter < this->MaxNumberOfIterations; iter++)
    {
    // We need at least two runs for Monte Carlo simulation
    vtkDataSet *first = this->GenerateModelInput();

    this->Model->SetInput(first);
    this->Model->Update();

    lastsum = this->ComputeNormalizedCumulativeSum(
        this->NormalizedCumulativeSum, dist, this->Model->GetOutput(), lastsum,
        iter * this->NumberOfRandomValues);

    if (this->CheckBreakCriterion(this->NormalizedCumulativeSum))
      {
      cout << "Break criteria reached at iteration " << iter << endl;
      break;
      }

    first->Delete();

    if (iter == this->MaxNumberOfIterations - 1)
      cout << "Break criteria not reached" << endl;

    }

  vtkDataSet* output = vtkDataSet::GetData(outputVector);
  output->ShallowCopy(this->Model->GetOutput());
  // Add the final distribution as field data array to the output
  output->GetFieldData()->AddArray(dist);

  dist->Delete();

  return 1;
}

//----------------------------------------------------------------------------

double vtkTAG2EModelMonteCarloVariationAnalyser::ComputeNormalizedCumulativeSum(
    vtkDoubleArray *sum, vtkDoubleArray *dist, vtkDataSet *modelOutput,
    double startsum, int startcount)
{
  double lastsum;
  int i, j;

  vtkDataArray *result = modelOutput->GetPointData()->GetArray(
      this->Model->GetResultArrayName());

  for (j = 0; j < this->NumberOfRandomValues; j++)
    {
    sum->SetValue(j, result->GetTuple1(j));
    dist->InsertNextTuple1(result->GetTuple1(j));
    }

  // Compute the cumulative sum
  for (i = 0; i < sum->GetNumberOfTuples(); i++)
    {
    if (i == 0)
      sum->SetValue(i, sum->GetValue(i) + startsum);
    else
      sum->SetValue(i, sum->GetValue(i) + sum->GetValue(i - 1));
    }
  // Get the last cumulative sum
  lastsum = sum->GetValue(this->NumberOfRandomValues - 1);

  // Normalize the cumulative sum
  for (i = 0; i < sum->GetNumberOfTuples(); i++)
    {
    sum->SetValue(i, sum->GetValue(i) / (1 + startcount + i));
    }

  return lastsum;
}

//----------------------------------------------------------------------------

bool vtkTAG2EModelMonteCarloVariationAnalyser::CheckBreakCriterion(
    vtkDoubleArray *sum)
{
  int i;
  double tmp = 0.0;
  double min = 0.0;
  double max = 0.0;

  if (sum->GetNumberOfTuples() == 0)
    return false;

  min = max = sum->GetValue(0);

  for (i = 1; i < sum->GetNumberOfTuples(); i++)
    {
    if (min > sum->GetValue(i))
      min = sum->GetValue(i);
    if (max < sum->GetValue(i))
      max = sum->GetValue(i);
    }

  tmp = fabs(max - min);

  cout << "Cummulative range error difference " << tmp << endl;

  if (tmp < this->BreakCriterion)
    return true;

  return false;
}

//----------------------------------------------------------------------------

vtkDataSet *vtkTAG2EModelMonteCarloVariationAnalyser::GenerateModelInput()
{
  int timeStep;
  int i, j;

  // Generate the random value arrays
  vtkDataArrayCollection *arrayCollection =
      this->GenerateRandomValuesArrayCollection(this->NumberOfRandomValues);
  // Generate the points which are used in each time step
  vtkPoints *points = vtkPoints::New();
  vtkIdList *ids = vtkIdList::New();
  vtkPolyData *pd = vtkPolyData::New();
  pd->Allocate(this->NumberOfRandomValues, this->NumberOfRandomValues);

  // Generate uniform distributed point coordinates
  vtkDataArray *xcoor = this->GenerateRandomValueArray(
      this->NumberOfRandomValues, "rnorm", 0.0, 1.0);
  vtkDataArray *ycoor = this->GenerateRandomValueArray(
      this->NumberOfRandomValues, "rnorm", 0.0, 1.0);
  vtkDataArray *zcoor = this->GenerateRandomValueArray(
      this->NumberOfRandomValues, "rnorm", 0.0, 1.0);

  for (j = 0; j < this->NumberOfRandomValues; j++)
    {
    ids->InsertNextId(j);
    points->InsertNextPoint(xcoor->GetTuple1(j), ycoor->GetTuple1(j),
        zcoor->GetTuple1(j));
    }

  // Add the generated values as point data
  for (i = 0; i < arrayCollection->GetNumberOfItems(); i++)
    {
    vtkDataArray *array = arrayCollection->GetItem(i);
    // We support only point data
    pd->GetPointData()->AddArray(array);
    }

  // Add the points and generate a poly vertex cell
  pd->SetPoints(points);
  pd->InsertNextCell(VTK_POLY_VERTEX, ids);

  arrayCollection->Delete();
  points->Delete();
  ids->Delete();

  return pd;
}

//----------------------------------------------------------------------------

vtkDataArray *vtkTAG2EModelMonteCarloVariationAnalyser::GenerateRandomValueArray(
    int numRandomValues, const char *df, double param1, double param2)
{
  vtkDataArray *array = NULL;
  char buff[1024];

  snprintf(buff, 1024, "x = %s(%i, %g, %g)", df, numRandomValues, param1,
      param2);

  vtkDebugMacro( << "Running R-script" << buff);

  // Generate the random values
  this->RInterface->EvalRscript((const char*) buff, true);
  // Read the random values from R
  array = this->RInterface->AssignRVariableToVTKDataArray("x");

  return array;
}

//----------------------------------------------------------------------------

vtkDataArrayCollection *vtkTAG2EModelMonteCarloVariationAnalyser::GenerateRandomValuesArrayCollection(
    int numRandomValues)
{
  int i;
  vtkDataArrayCollection *arrayCollection = vtkDataArrayCollection::New();

  // Generate the random variables for monte carlo simulation
  for (i = 0; i < this->VariableName->GetNumberOfValues(); i++)
    {
    vtkDataArray *array = NULL;

    // Generate the R script
    if (this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_NORM)
      {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "rnorm", param[0],
          param[1]);
      }
    if (this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_LNORM)
      {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "rlnorm",
          param[0], param[1]);
      }
    if (this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_UNIF)
      {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "runif", param[0],
          param[1]);
      }
    if (this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_BINOM)
      {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "rbinom",
          param[0], param[1]);
      }
    if (this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_CHISQ)
      {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "rchisq",
          param[0], param[1]);
      }

    // Attach the array to the collection
    if (array)
      {
      // Set the name of the array
      array->SetName(this->VariableName->GetValue(i));
      arrayCollection->AddItem(array);
      array->Delete();
      }
    }

  return arrayCollection;
}

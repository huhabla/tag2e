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
#include <vtkTemporalDataSet.h>
#include <vtkTemporalDataSetSource.h>
#include <vtkStreamingDemandDrivenPipeline.h>
#include <vtk-5.9/vtkIdList.h>
#include "vtkTAG2EModelMonteCarloVariationAnalyser.h"
#include "vtkTAG2ELinearRegressionModel.h"

vtkCxxRevisionMacro(vtkTAG2EModelMonteCarloVariationAnalyser, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EModelMonteCarloVariationAnalyser);

vtkTAG2EModelMonteCarloVariationAnalyser::vtkTAG2EModelMonteCarloVariationAnalyser()
{
  this->SetNumberOfInputPorts(0);
  this->SetNumberOfOutputPorts(1);
}

//----------------------------------------------------------------------------

vtkTAG2EModelMonteCarloVariationAnalyser::~vtkTAG2EModelMonteCarloVariationAnalyser()
{
  ;
}

//----------------------------------------------------------------------------

int vtkTAG2EModelMonteCarloVariationAnalyser::RequestData(
  vtkInformation * vtkNotUsed(request),
  vtkInformationVector **vtkNotUsed(inputVector),
  vtkInformationVector *outputVector)
{
  // get the output info object
  vtkInformation *outInfo = outputVector->GetInformationObject(0);
  
  // Build the Array which describes the input variable distribution
  this->BuildDataDistributionDescriptionArrays();

  // Check for data distribution parameter
  if (this->DataDistributionDescription == NULL) {
    vtkErrorMacro("DataDistributionDescription not set or invalid.");
    return -1;
  }
  
  int iter;
  
  for(iter = 0; iter < this->MaxNumberOfIterations; iter++)
  {
    // We need at least two runs for monte carlo simulation
    vtkTemporalDataSetSource *first = this->GenerateModelInput(this->NumberOfTimeSteps);
  
    this->Model->SetInputConnection(first->GetOutputPort());
    this->Model->Update();
    
    first->Delete();
  }
  
  vtkTemporalDataSet *output = vtkTemporalDataSet::SafeDownCast(
    outInfo->Get(vtkDataObject::DATA_OBJECT()));
  
  output->ShallowCopy(this->Model->GetOutput());
  
  return 1;
}

//----------------------------------------------------------------------------

vtkTemporalDataSetSource *vtkTAG2EModelMonteCarloVariationAnalyser::GenerateModelInput(int numTimeSteps)
{
  int timeStep;
  int i, j;
  
  // Generate the random value arrays
  vtkDataArrayCollection *arrayCollection = this->GenerateRandomValuesArrayCollection(this->NumberOfRandomValues * numTimeSteps);
  
  // We need a temporal data source to create the model input
  vtkTemporalDataSetSource *tds = vtkTemporalDataSetSource::New();
  vtkDoubleArray *timeSteps = vtkDoubleArray::New();
  timeSteps->SetNumberOfComponents(1);
  timeSteps->SetNumberOfValues(numTimeSteps);
  
  // Generate the time step value array
  for (timeStep = 0; timeStep < numTimeSteps; timeStep++) 
  {
    timeSteps->SetValue(timeStep, (double)timeStep);
  }
  
  // Set the range and the time steps for the temporal data sets sosurce
  tds->SetTimeRange(timeSteps->GetRange()[0], timeSteps->GetRange()[1], timeSteps);

  // Generate the points which are used in each time step
  vtkPoints *points = vtkPoints::New();
  vtkIdList *ids = vtkIdList::New();

  // Generate uniform distributed point coordinates
  vtkDataArray *xcoor = this->GenerateRandomValueArray(this->NumberOfRandomValues, "runif", -1000.0, 1000.0);
  vtkDataArray *ycoor = this->GenerateRandomValueArray(this->NumberOfRandomValues, "runif", -1000.0, 1000.0);
  vtkDataArray *zcoor = this->GenerateRandomValueArray(this->NumberOfRandomValues, "runif", -1000.0, 1000.0);

  for(j = 0; j < this->NumberOfRandomValues; j++)
  {
    ids->InsertNextId(j);
    points->InsertNextPoint(xcoor->GetTuple1(j), ycoor->GetTuple1(j), zcoor->GetTuple1(j));
  }
  
  // Iterate over each time step
  for (timeStep = 0; timeStep < numTimeSteps; timeStep++) 
  {
    // Create the poly data
    vtkPolyData *pd =  vtkPolyData::New();
    pd->Allocate(this->NumberOfRandomValues,this->NumberOfRandomValues);
    
    // Add the generated values for the single time step as point data
    for(i = 0; i < arrayCollection->GetNumberOfItems(); i++)
    {
      vtkDataArray *array = arrayCollection->GetItem(i);
      vtkDoubleArray *pdarray = vtkDoubleArray::New();
      
      pdarray->SetNumberOfComponents(1);
      pdarray->SetNumberOfTuples(this->NumberOfRandomValues);
      pdarray->SetName(array->GetName());
      
      // Extract the points of a single time step
      for(j = 0; j < this->NumberOfRandomValues; j++)
      {
        pdarray->SetValue(j, array->GetTuple1(j + timeStep * this->NumberOfRandomValues));
      }
      
      // We support only point data
      pd->GetPointData()->AddArray(pdarray);
      pdarray->Delete();
      
    }
    // Add the points and generate a poly vertex cell
    pd->SetPoints(points);
    pd->InsertNextCell(VTK_POLY_VERTEX, ids);
      
    // Add the time step
    tds->SetInput(timeStep, pd);
    pd->Delete();
  }
  
  arrayCollection->Delete();
  points->Delete();
  ids->Delete();
  
  tds->Update();
    
  return tds;
}

//----------------------------------------------------------------------------

vtkDataArray *vtkTAG2EModelMonteCarloVariationAnalyser::GenerateRandomValueArray(int numRandomValues, const char *df, double param1, double param2)
{
  vtkDataArray *array  = NULL;
  char buff[1024];
  vtkRInterface *riface = vtkRInterface::New(); // This is a singleton, so we can call it as often as we want :)
  
  snprintf(buff, 1024, "x = %s(%i, %g, %g)", df, numRandomValues, param1, param2);
  cerr << buff << endl;
  
  // Generate the random values
  riface->EvalRscript((const char*)buff, true);
  // Read the random values from R
  array = riface->AssignRVariableToVTKDataArray("x");
  
  //for(int i = 0; i < array->GetNumberOfTuples(); i++)
  //  cout << array->GetTuple1(i) << endl;
    
  return array;
}

//----------------------------------------------------------------------------

vtkDataArrayCollection *vtkTAG2EModelMonteCarloVariationAnalyser::GenerateRandomValuesArrayCollection(int numRandomValues)
{
  int i;
  vtkDataArrayCollection *arrayCollection = vtkDataArrayCollection::New();
  
  
  // Generate the random variables for monte carlo simulation
  for(i = 0; i < this->VariableName->GetNumberOfValues(); i++)
  {    
    vtkDataArray *array  = NULL;
    
    // Generate the R script
    if(this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_NORM) {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "rnorm", param[0], param[1]);
    }
    if(this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_LNORM) {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "rlnorm", param[0], param[1]);
    }
    if(this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_UNIF) {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "runif", param[0], param[1]);
    }
    if(this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_BINOM) {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "rbinom", param[0], param[1]);
    }
    if(this->VariableDistributionType->GetValue(i) == TAG2E_R_DF_CHISQ) {
      double *param = this->DistributionParameter->GetTuple2(i);
      array = this->GenerateRandomValueArray(numRandomValues, "rchisq", param[0], param[1]);
    }
    
    // Attach the array to the collection
    if(array) {
      // Set the name of the array
      array->SetName(this->VariableName->GetValue(i));
      arrayCollection->AddItem(array);
      array->Delete();
    }
  }
  
  return arrayCollection;
}
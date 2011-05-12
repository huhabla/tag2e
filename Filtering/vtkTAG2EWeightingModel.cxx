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
#include <vtkCellData.h>
#include <vtkIntArray.h>
#include <vtkDoubleArray.h>
#include <vtkStringArray.h>
#include <vtkTemporalDataSet.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkDataSetAttributes.h>

#include <vtkDataSetAlgorithm.h>
#include <vtkObjectFactory.h>
#include "vtkTAG2EWeightingModel.h"
#include "vtkTAG2EWeightingModelParameter.h"
#include "vtkTAG2EAbstractModelParameter.h"


vtkCxxRevisionMacro(vtkTAG2EWeightingModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EWeightingModel);

//----------------------------------------------------------------------------

vtkTAG2EWeightingModel::vtkTAG2EWeightingModel()
{
  this->WeightingModelParameter = NULL;
  this->SetNumberOfInputPorts(1);
}

//----------------------------------------------------------------------------

vtkTAG2EWeightingModel::~vtkTAG2EWeightingModel()
{
    ;
}

//----------------------------------------------------------------------------

int vtkTAG2EWeightingModel::FillInputPortInformation(
  int vtkNotUsed(port),
  vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkTemporalDataSet");
  return 1;
}


//----------------------------------------------------------------------------

int vtkTAG2EWeightingModel::RequestUpdateExtent(
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

void vtkTAG2EWeightingModel::SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter)
{
  this->Superclass::SetModelParameter(modelParameter);

  // Check if the ModelParameter is of correct type
  if (this->ModelParameter->IsA("vtkTAG2EWeightingModelParameter")) {
    this->WeightingModelParameter = static_cast<vtkTAG2EWeightingModelParameter *> (this->ModelParameter);
  } else {
    vtkErrorMacro( << "The ModelParameter is not of type vtkTAG2EWeightingModelParameter");
    this->SetModelParameter(NULL);
    return;
  }

  // Generate the internal representation
  this->WeightingModelParameter->GenerateInternalSchemeFromXML();

  this->Modified();
}

//----------------------------------------------------------------------------

int vtkTAG2EWeightingModel::RequestData(
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

  Weighting &W = this->WeightingModelParameter->GetInternalScheme();

  // get the first input and ouptut
  vtkTemporalDataSet *input = vtkTemporalDataSet::SafeDownCast(
    inInfo->Get(vtkDataObject::DATA_OBJECT()));

  vtkTemporalDataSet *output = vtkTemporalDataSet::SafeDownCast(
    outInfo->Get(vtkDataObject::DATA_OBJECT()));

  output->SetNumberOfTimeSteps(input->GetNumberOfTimeSteps());

  // Iterate over each timestep of the first input
  // Timesteps must be equal in the inputs.
  for (timeStep = 0; timeStep < input->GetNumberOfTimeSteps(); timeStep++) {
    int i;

    // The first input is used to create the ouput
    // It is assumed that each input has the same number of points and the same topology
    // The number of point data arrays can/should differ
    vtkDataSet *inputDataSet = vtkDataSet::SafeDownCast(input->GetTimeStep(timeStep));
    vtkDataSet *outputDataSet = inputDataSet->NewInstance();
    outputDataSet->CopyStructure(inputDataSet);
    //outputDataSet->DeepCopy(inputDataSet);

    // Result for the current time step
    vtkDoubleArray *result = vtkDoubleArray::New();
    result->SetNumberOfComponents(0);
    result->SetName(this->ResultArrayName);
    
    if(this->UseCellData)
      result->SetNumberOfTuples(inputDataSet->GetNumberOfCells());
    else
      result->SetNumberOfTuples(inputDataSet->GetNumberOfPoints());
    result->FillComponent(0,0.0);

    vtkDataArray *scalars, *factors;
    vtkDataSetAttributes *attrData;
    int num = 0;
    
    if(this->UseCellData) {
        attrData = inputDataSet->GetCellData();
        num = inputDataSet->GetNumberOfCells();
    } else {
        attrData = inputDataSet->GetPointData();
        num = inputDataSet->GetNumberOfPoints();
    }

    scalars = attrData->GetScalars();
    if(attrData->HasArray(W.Factor.name.c_str())) {
        factors = attrData->GetArray(W.Factor.name.c_str());
    } else {
        if(this->UseCellData) {
            vtkErrorMacro(<<"Factor array " << W.Factor.name.c_str() << " does not exist in cell data of dataset at time step " << timeStep);
        } else {
            vtkErrorMacro(<<"Factor array " << W.Factor.name.c_str() << " does not exist in point data of dataset at time step " << timeStep);
        }
        return -1;
    }

    double val;
    unsigned int id;
    for(i = 0; i < num; i++)
    {
        val = scalars->GetTuple1(i);
        id = (int)factors->GetTuple1(i);
        if(id < 0 || id > W.Weights.size()) {
            vtkErrorMacro(<<"Factor id is out of range " << id);
            continue;
        }
        val = W.Weights[id].value * val;
        // std::cout << "Factor " << i << " with id " << id << " value " << val << std::endl;
        result->SetValue(i, val);
    }

    if(this->UseCellData) {
        outputDataSet->GetCellData()->AddArray(result);
        outputDataSet->GetCellData()->SetActiveScalars(result->GetName());
    } else {
        outputDataSet->GetPointData()->AddArray(result);
        outputDataSet->GetPointData()->SetActiveScalars(result->GetName());
    }
    output->SetTimeStep(timeStep, outputDataSet);
    outputDataSet->Delete();
    result->Delete();
  }

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2EWeightingModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}

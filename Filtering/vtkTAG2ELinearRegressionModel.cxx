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

#include <vtkDataSetAlgorithm.h>
#include <vtkObjectFactory.h>
#include "vtkTAG2ELinearRegressionModel.h"

vtkCxxRevisionMacro(vtkTAG2ELinearRegressionModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ELinearRegressionModel);

//----------------------------------------------------------------------------

vtkTAG2ELinearRegressionModel::vtkTAG2ELinearRegressionModel()
{
  this->InputPorts = vtkIntArray::New();
  this->Coefficents = vtkDoubleArray::New();
  this->Power = vtkDoubleArray::New();
  this->ArrayNames = vtkStringArray::New();
  this->Intercept = 0.0;
}

//----------------------------------------------------------------------------

vtkTAG2ELinearRegressionModel::~vtkTAG2ELinearRegressionModel()
{
  this->InputPorts->Delete();
  this->Coefficents->Delete();
  this->Power->Delete();
  this->ArrayNames->Delete();
}

//----------------------------------------------------------------------------
int vtkTAG2ELinearRegressionModel::FillInputPortInformation(
  int port,
  vtkInformation* info)
{
  // port 0 must be temporal data, but port 1 can be any dataset
  if (port==0) {
    info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkTemporalDataSet");
  }
  return 1;
}

//----------------------------------------------------------------------------

int vtkTAG2ELinearRegressionModel::RequestData(
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
    vtkErrorMacro("Model parameter not set.");
    return -1;
  }

  if (true != this->BuildCoefficientPowerMaps())
    return -1;

  // get the input and ouptut
  vtkTemporalDataSet *input = vtkTemporalDataSet::SafeDownCast(
    inInfo->Get(vtkDataObject::DATA_OBJECT()));

  vtkTemporalDataSet *output = vtkTemporalDataSet::SafeDownCast(
    outInfo->Get(vtkDataObject::DATA_OBJECT()));
  
  output->SetNumberOfTimeSteps(input->GetNumberOfTimeSteps());
  
  // Iterate over each timestep 
  for (timeStep = 0; timeStep < input->GetNumberOfTimeSteps(); timeStep++) {
    int id;
    double power = 0.0;
    double coef = 0.0;
    double r = 0.0;
    int i = 0;

    // Extract the datasets
    vtkDataSet *in = vtkDataSet::SafeDownCast(input->GetTimeStep(timeStep));
    vtkDataSet *out = in->NewInstance();
    out->CopyStructure(in);

    vtkPointData *inputData = in->GetPointData();

    vtkDataArray *result = vtkDoubleArray::New();
    result->SetNumberOfComponents(0);
    result->SetName("result");
    result->SetNumberOfTuples(in->GetNumberOfPoints());
    result->FillComponent(0, this->Intercept);

    // For each array 
    for (i = 0; i < this->Coefficents->GetNumberOfTuples(); i++) {

      const char *arrayName = this->ArrayNames->GetValue(i);
      coef = this->Coefficents->GetValue(i);
      power = this->Power->GetValue(i);

      // Check if the array exists
      if (!inputData->HasArray(arrayName)) {
        vtkErrorMacro("Array " << arrayName << " is missing in input. Wrong reference in the model parameter");
        return -1;
      }

      vtkDataArray *array = inputData->GetArray(arrayName);

      // For each point in the point data array compute the linear regression
      for (id = 0; id < in->GetNumberOfPoints(); id++) {
        r = result->GetTuple1(id) + coef * pow(array->GetTuple1(id), power);
        result->SetTuple1(id, r);
      }
    }

    out->GetPointData()->SetScalars(result);
    output->SetTimeStep(timeStep, out);
    out->Delete();
    result->Delete();
  }
  
  return 1;
}

//----------------------------------------------------------------------------

bool vtkTAG2ELinearRegressionModel::BuildCoefficientPowerMaps()
{
  int i;

  this->Coefficents->Initialize();
  this->Power->Initialize();
  this->ArrayNames->Initialize();

  vtkXMLDataElement *root = this->ModelParameter->GetXMLRoot();

  // Check for correct 
  if (strncmp(root->GetName(), "LinearRegressionScheme", 22) != 0) {
    vtkErrorMacro("The model parameter does not contain a valid linear regression scheme");
    return false;
  }

  // Fetch the intercept value. This value is optional
  vtkXMLDataElement *intercept = root->FindNestedElementWithName("Intercept");

  if (intercept != NULL)
    this->Intercept = atof(intercept->GetCharacterData());

  // Add the power and coefficients to the maps
  for (i = 0; i < root->GetNumberOfNestedElements(); i++) {
    vtkXMLDataElement *element = root->GetNestedElement(i);

    // Check for Coefficient elements
    if (strncmp(element->GetName(), "Coefficient", 11) == 0) {
      const char* arrayName = NULL;
      double coefficient = 0;
      double power = 0;
      int inputPort = 0;

      if (element->GetAttribute("name") != NULL)
        arrayName = element->GetAttribute("name");
      
      if (element->GetAttribute("power") != NULL)
        power = atof(element->GetAttribute("power"));
      
      if (element->GetAttribute("portId") != NULL)
        inputPort = atoi(element->GetAttribute("portId"));
      
      if (element->GetCharacterData() != NULL)
        coefficient = atof(element->GetCharacterData());

      this->InputPorts->InsertNextValue(inputPort);
      this->Coefficents->InsertNextValue(coefficient);
      this->Power->InsertNextValue(power);
      this->ArrayNames->InsertNextValue(arrayName);
    }
  }

  return true;
}


//----------------------------------------------------------------------------

void vtkTAG2ELinearRegressionModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
  os << indent << "Intercept: " << this->Intercept << endl;
  os << indent << "Coefficient:" << endl;
  this->Coefficents->PrintSelf(os, indent.GetNextIndent());
  os << indent << "Power:" << endl;
  this->Power->PrintSelf(os, indent.GetNextIndent());
}
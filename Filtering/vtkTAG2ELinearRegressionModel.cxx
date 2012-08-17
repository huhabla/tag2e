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

int vtkTAG2ELinearRegressionModel::RequestData(
    vtkInformation * vtkNotUsed(request), vtkInformationVector **inputVector,
    vtkInformationVector *outputVector)
{
  unsigned int timeStep;
  int id;
  double power = 0.0;
  double coef = 0.0;
  double r = 0.0;
  int i = 0;
  int port;

  // Check for model parameter
  if (this->ModelParameter == NULL)
    {
    vtkErrorMacro("Model parameter not set or invalid.");
    return -1;
    }

  vtkDataSet* firstInput = vtkDataSet::GetData(inputVector[0]);
  vtkDataSet* output = vtkDataSet::GetData(outputVector);
  // The first input is used to create the ouput
  // It is assumed that each input has the same number of points and the same topology
  // The number of point data arrays can/should differ
  output->DeepCopy(firstInput);

  // Result for the current time step
  vtkDataArray *result = vtkDoubleArray::New();
  result->SetNumberOfComponents(0);
  result->SetName(this->ResultArrayName);
  result->SetNumberOfTuples(firstInput->GetNumberOfPoints());
  result->FillComponent(0, this->Intercept);

  // For input port and defined array name
  for (i = 0; i < this->InputPorts->GetNumberOfTuples(); i++)
    {
    // Gather all needed information for the current input port
    port = this->InputPorts->GetValue(i);
    const char *arrayName = this->ArrayNames->GetValue(i);
    coef = this->Coefficents->GetValue(i);
    power = this->Power->GetValue(i);

    vtkDataSet *activeInput = vtkDataSet::GetData(inputVector[port]);

    // Check if a dataset is present at actual time step
    if (activeInput == NULL)
      {
      vtkErrorMacro(<<"No dataset available at input port " << port);
      return -1;
      }

    // Check if the number of points and cells in the active input are identical with the first input
    if (firstInput->GetNumberOfPoints() != activeInput->GetNumberOfPoints()
        || firstInput->GetNumberOfCells() != activeInput->GetNumberOfCells())
      {
      vtkErrorMacro(
          << "The number of points or cells differ between the inputs.");
      return -1;
      }

    //TODO: Support point and cell data
    // Get the point data
    vtkPointData *inputData = activeInput->GetPointData();

    // Check if the array exists in the current input
    if (!inputData->HasArray(arrayName))
      {
      vtkErrorMacro(<< "Array " << arrayName << " is missing in input. "
      "Wrong reference in the model parameter");
      return -1;
      }

    vtkDataArray *array = inputData->GetArray(arrayName);

    // For each point in the point data array compute the linear regression
    for (id = 0; id < activeInput->GetNumberOfPoints(); id++)
      {
      r = result->GetTuple1(id) + coef * pow(array->GetTuple1(id), power);
      result->SetTuple1(id, r);
      }
    }

  //TODO: Support point and cell data
  output->GetPointData()->AddArray(result);
  output->GetPointData()->SetActiveScalars(result->GetName());
  result->Delete();

  return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2ELinearRegressionModel::SetModelParameter(
    vtkTAG2EAbstractModelParameter* modelParameter)
{
  this->Superclass::SetModelParameter(modelParameter);

  if (true != this->BuildLRValueArrays())
    this->Superclass::SetModelParameter(NULL);

  double *range = this->InputPorts->GetRange();
  // Ports from 0 ... n must be used  
  this->SetNumberOfInputPorts((int) (range[1] + 1));
}

//----------------------------------------------------------------------------

bool vtkTAG2ELinearRegressionModel::BuildLRValueArrays()
{
  int i;

  this->InputPorts->Initialize();
  this->Coefficents->Initialize();
  this->Power->Initialize();
  this->ArrayNames->Initialize();

  vtkXMLDataElement *root = vtkXMLDataElement::New();
  this->ModelParameter->GetXMLRepresentation(root);

  // Check for correct 
  if (strncasecmp(root->GetName(), "LinearRegressionScheme", 22) != 0)
    {
    vtkErrorMacro(
        "The model parameter does not contain a valid linear regression scheme");
    return false;
    }

  // Fetch the intercept value. This value is optional
  vtkXMLDataElement *intercept = root->FindNestedElementWithName("Intercept");

  if (intercept != NULL)
    this->Intercept = atof(intercept->GetCharacterData());

  // Add the power and coefficients to the maps
  for (i = 0; i < root->GetNumberOfNestedElements(); i++)
    {
    vtkXMLDataElement *element = root->GetNestedElement(i);

    // Check for Coefficient elements
    if (strncasecmp(element->GetName(), "Coefficient", 11) == 0)
      {
      const char* arrayName = NULL;
      double coefficient = 0;
      double power = 0;
      int inputPort = 0;

      if (element->GetAttribute("name") != NULL)
        {
        arrayName = element->GetAttribute("name");
        } else
        {
        vtkErrorMacro(
            <<"Attribute \"name\" is missing in Coefficient element: " << i);
        return false;
        }

      if (element->GetAttribute("power") != NULL)
        {
        power = atof(element->GetAttribute("power"));
        } else
        {
        vtkErrorMacro(
            <<"Attribute \"power\" is missing in Coefficient element: " << i);
        return false;
        }

      if (element->GetAttribute("portId") != NULL)
        {
        inputPort = atoi(element->GetAttribute("portId"));
        } else
        {
        vtkErrorMacro(
            <<"Attribute \"portId\" is missing in Coefficient element: " << i);
        return false;
        }

      if (element->GetCharacterData() != NULL)
        {
        coefficient = atof(element->GetCharacterData());
        } else
        {
        vtkErrorMacro(
            <<"Character data is missing in Coefficient element: " << i);
        return false;
        }

      this->InputPorts->InsertNextValue(inputPort);
      this->Coefficents->InsertNextValue(coefficient);
      this->Power->InsertNextValue(power);
      this->ArrayNames->InsertNextValue(arrayName);
      }
    }

  root->Delete();

  return true;
}

//----------------------------------------------------------------------------

void vtkTAG2ELinearRegressionModel::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
  os << indent << "Intercept: " << this->Intercept << endl;
  os << indent << "InputPorts:" << endl;
  this->InputPorts->PrintSelf(os, indent.GetNextIndent());
  os << indent << "Coefficient:" << endl;
  this->Coefficents->PrintSelf(os, indent.GetNextIndent());
  os << indent << "Power:" << endl;
  this->Power->PrintSelf(os, indent.GetNextIndent());
}

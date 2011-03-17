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
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkStreamingDemandDrivenPipeline.h>
#include "vtkTAG2EAbstractModelVariationAnalyser.h"
#include "vtkTAG2ELinearRegressionModel.h"

vtkCxxRevisionMacro(vtkTAG2EAbstractModelVariationAnalyser, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EAbstractModelVariationAnalyser);

//----------------------------------------------------------------------------

vtkTAG2EAbstractModelVariationAnalyser::vtkTAG2EAbstractModelVariationAnalyser()
{
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
  this->Model = NULL;
  this->DataDistributionDescription = NULL;

  this->TimeSteps = NULL;
  this->NumberOfTimeSteps = 1; // We generate only a single time step as default
  this->MaxNumberOfIterations = 1000; // This is the number of 

  this->VariableName = vtkStringArray::New();
  ;
  this->VariableDistributionType = vtkIntArray::New();
  this->DistributionParameter = vtkDoubleArray::New();
  this->DistributionParameter->SetNumberOfComponents(2);
}

//----------------------------------------------------------------------------

vtkTAG2EAbstractModelVariationAnalyser::~vtkTAG2EAbstractModelVariationAnalyser()
{
  if (this->Model)
    this->Model->Delete();
  if (this->DataDistributionDescription)
    this->DataDistributionDescription->Delete();

  this->VariableDistributionType->Delete();
  this->VariableName->Delete();
  this->DistributionParameter->Delete();
}

//----------------------------------------------------------------------------

int vtkTAG2EAbstractModelVariationAnalyser::RequestUpdateExtent(
  vtkInformation *vtkNotUsed(request),
  vtkInformationVector **vtkNotUsed(inputVector),
  vtkInformationVector *outputVector)
{
  if (this->TimeSteps) {
    vtkInformation *outInfo = outputVector->GetInformationObject(0);

    // Remove any existing output UPDATE_TIME_STEPS
    if (outInfo->Has(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS()))
      outInfo->Remove(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS());

    // Set the generated time steps, its the same as TIME_STEPS
    if (!outInfo->Has(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS())) {
      outInfo->Set(vtkStreamingDemandDrivenPipeline::UPDATE_TIME_STEPS(), this->TimeSteps, this->NumberOfTimeSteps);
    }
  }

  return 1;
}

//-----------------------------------------------------------------------

int vtkTAG2EAbstractModelVariationAnalyser::RequestInformation(
  vtkInformation *vtkNotUsed(request),
  vtkInformationVector **vtkNotUsed(inputVector),
  vtkInformationVector *outputVector)
{
  int i;

  this->TimeSteps = new double[this->NumberOfTimeSteps];

  if (this->TimeSteps) {
    // Generate the time steps
    for (i = 0; i < this->NumberOfTimeSteps; i++)
      this->TimeSteps[i] = (double) i;

    double range[2] = {0, 1};

    vtkInformation *outInfo = outputVector->GetInformationObject(0);

    // Set the time stept and range for the first input.
    outInfo->Set(vtkStreamingDemandDrivenPipeline::TIME_STEPS(), this->TimeSteps, this->NumberOfTimeSteps);
    outInfo->Set(vtkStreamingDemandDrivenPipeline::TIME_RANGE(), range, 2);
  }

  return 1;
}

//----------------------------------------------------------------------------

bool vtkTAG2EAbstractModelVariationAnalyser::BuildDataDistributionDescriptionArrays()
{
  int i;

  this->VariableName->Initialize();
  this->VariableDistributionType->Initialize();
  this->DistributionParameter->Initialize();

  vtkXMLDataElement *root = this->DataDistributionDescription->GetXMLRoot();

  // Check for correct 
  if (strncasecmp(root->GetName(), "DataDistributionDescription", 27) != 0) {
    vtkErrorMacro("The model parameter does not contain a valid data distribution description scheme");
    return false;
  }

  for (i = 0; i < root->GetNumberOfNestedElements(); i++) {
    vtkXMLDataElement *variable = root->GetNestedElement(i);

    if (strncasecmp(variable->GetName(), "Variable", 8) == 0) {
      const char* variableName = NULL;
      const char *typeName = NULL;
      double param1 = 0.0;
      double param2 = 0.0;
      int dfType = 0;

      if (variable->GetAttribute("name") != NULL) {
        variableName = variable->GetAttribute("name");
      } else {
        vtkErrorMacro( << "Attribute \"name\" is missing in Variable element: " << i);
        return false;
      }

      if (variable->GetAttribute("type") != NULL) {

        typeName = variable->GetAttribute("type");

        if (strncasecmp(typeName, "norm", 4) == 0) {
          dfType = TAG2E_R_DF_NORM;
          vtkXMLDataElement *df = variable->GetNestedElement(0);
          if (df) {
            if (strncasecmp(df->GetName(), "Norm", 4) != 0) {
              vtkErrorMacro( << "Element \"Norm\" is missing in Variable element: " << i);
              return false;
            }
            if (df->GetAttribute("mean") != NULL) {
              param1 = atof(df->GetAttribute("mean"));
            } else {
              vtkErrorMacro( << "Attribute \"mean\" is missing in Norm element: " << i);
              return false;
            }
            if (df->GetAttribute("sd") != NULL) {
              param2 = atof(df->GetAttribute("sd"));
            } else {
              vtkErrorMacro( << "Attribute \"sd\" is missing in Norm element: " << i);
              return false;
            }
          } else {
            vtkErrorMacro( << "Element \"Norm\" is missing in Variable element: " << i);
            return false;
          }
        }

        if (strncasecmp(typeName, "lnorm", 5) == 0) {
          dfType = TAG2E_R_DF_LNORM;
          vtkXMLDataElement *df = variable->GetNestedElement(0);

          if (df) {
            if (strncasecmp(df->GetName(), "Lnorm", 5) != 0) {
              vtkErrorMacro( << "Element \"Lnorm\" is missing in Variable element: " << i);
              return false;
            }
            if (df->GetAttribute("meanlog") != NULL) {
              param1 = atof(df->GetAttribute("meanlog"));
            } else {
              vtkErrorMacro( << "Attribute \"meanlog\" is missing in Lnorm element: " << i);
              return false;
            }
            if (df->GetAttribute("sdlog") != NULL) {
              param2 = atof(df->GetAttribute("sdlog"));
            } else {
              vtkErrorMacro( << "Attribute \"sdlog\" is missing in Lnorm element: " << i);
              return false;
            }
          } else {
            vtkErrorMacro( << "Element \"Lnorm\" is missing in Variable element: " << i);
            return false;
          }
        }

        if (strncasecmp(typeName, "unif", 4) == 0) {
          dfType = TAG2E_R_DF_UNIF;
          vtkXMLDataElement *df = variable->GetNestedElement(0);

          if (df) {
            if (strncasecmp(df->GetName(), "Unif", 4) != 0) {
              vtkErrorMacro( << "Element \"Unif\" is missing in Variable element: " << i);
              return false;
            }
            if (df->GetAttribute("min") != NULL) {
              param1 = atof(df->GetAttribute("min"));
            } else {
              vtkErrorMacro( << "Attribute \"min\" is missing in Unif element: " << i);
              return false;
            }
            if (df->GetAttribute("max") != NULL) {
              param2 = atof(df->GetAttribute("max"));
            } else {
              vtkErrorMacro( << "Attribute \"max\" is missing in Unif element: " << i);
              return false;
            }
          } else {
            vtkErrorMacro( << "Element \"Unif\" is missing in Variable element: " << i);
            return false;
          }
        }

        if (strncasecmp(typeName, "binom", 5) == 0) {
          dfType = TAG2E_R_DF_BINOM;
          vtkXMLDataElement *df = variable->GetNestedElement(0);
          
          if (df) {
            if (strncasecmp(df->GetName(), "Binom", 5) != 0) {
              vtkErrorMacro( << "Element \"Binom\" is missing in Variable element: " << i);
              return false;
            }
            if (df->GetAttribute("size") != NULL) {
              param1 = atof(df->GetAttribute("size"));
            } else {
              vtkErrorMacro( << "Attribute \"size\" is missing in Binom element: " << i);
              return false;
            }
            if (df->GetAttribute("prob") != NULL) {
              param2 = atof(df->GetAttribute("prob"));
            } else {
              vtkErrorMacro( << "Attribute \"prob\" is missing in Binom element: " << i);
              return false;
            }
          } else {
            vtkErrorMacro( << "Element \"Binom\" is missing in Variable element: " << i);
            return false;
          }
        }

        if (strncasecmp(typeName, "chisq", 5) == 0) {
          dfType = TAG2E_R_DF_CHISQ;
          vtkXMLDataElement *df = variable->GetNestedElement(0);
          
          if (df) {
            if (strncasecmp(df->GetName(), "Chisq", 5) != 0) {
              vtkErrorMacro( << "Element \"Chisq\" is missing in Variable element: " << i);
              return false;
            }
            if (df->GetAttribute("df") != NULL) {
              param1 = atof(df->GetAttribute("df"));
            } else {
              vtkErrorMacro( << "Attribute \"df\" is missing in Chisq element: " << i);
              return false;
            }
            if (df->GetAttribute("ncp") != NULL) {
              param2 = atof(df->GetAttribute("ncp"));
            } else {
              vtkErrorMacro( << "Attribute \"ncp\" is missing in Chisq element: " << i);
              return false;
            }
          } else {
            vtkErrorMacro( << "Element \"Chisq\" is missing in Variable element: " << i);
            return false;
          }
        }

        if (strncasecmp(typeName, "t", 1) == 0) {
          dfType = TAG2E_R_DF_CHISQ;
          vtkXMLDataElement *df = variable->GetNestedElement(0);
          
          if (df) {
            if (strncasecmp(df->GetName(), "T", 5) != 0) {
              vtkErrorMacro( << "Element \"T\" is missing in Variable element: " << i);
              return false;
            }
            if (df->GetAttribute("df") != NULL) {
              param1 = atof(df->GetAttribute("df"));
            } else {
              vtkErrorMacro( << "Attribute \"df\" is missing in T element: " << i);
              return false;
            }
            if (df->GetAttribute("ncp") != NULL) {
              param2 = atof(df->GetAttribute("ncp"));
            } else {
              vtkErrorMacro( << "Attribute \"ncp\" is missing in T element: " << i);
              return false;
            }
          } else {
            vtkErrorMacro( << "Element \"T\" is missing in Variable element: " << i);
            return false;
          }
        }
        
      } else {
        vtkErrorMacro( << "Attribute \"type\" is missing in Variable element: " << i);
        return false;
      }

      vtkDebugMacro(<< "Insert variable name " << variableName << " of type " << dfType << " and values " << param1 << " " << param2);

      this->VariableName->InsertNextValue(variableName);
      this->VariableDistributionType->InsertNextValue(dfType);
      this->DistributionParameter->InsertNextTuple2(param1, param2);
    }
  }

  return true;
}
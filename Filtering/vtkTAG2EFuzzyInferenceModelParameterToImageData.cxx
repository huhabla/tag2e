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
#include <vtkDataArray.h>
#include <vtkDoubleArray.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkImageData.h>
#include <vtkDataSetAlgorithm.h>
#include <vtkObjectFactory.h>
#include "vtkTAG2EFuzzyInferenceModelParameterToImageData.h"


vtkCxxRevisionMacro(vtkTAG2EFuzzyInferenceModelParameterToImageData, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EFuzzyInferenceModelParameterToImageData);

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModelParameterToImageData::vtkTAG2EFuzzyInferenceModelParameterToImageData()
{
    this->SetNumberOfInputPorts(0);
    this->SetNumberOfOutputPorts(1);
    this->FuzzyModelParameter = NULL;
    this->XAxisExtent = 10;
    this->YAxisExtent = 10;
    this->ZAxisExtent = 10;
}

//----------------------------------------------------------------------------

vtkTAG2EFuzzyInferenceModelParameterToImageData::~vtkTAG2EFuzzyInferenceModelParameterToImageData()
{
    ;
}
// This method returns the largest data that can be generated.
int vtkTAG2EFuzzyInferenceModelParameterToImageData::RequestInformation (
  vtkInformation       * vtkNotUsed( request ),
  vtkInformationVector** vtkNotUsed( inputVector ),
  vtkInformationVector * outputVector)
{
  // get the info objects
  vtkInformation* outInfo = outputVector->GetInformationObject(0);

  double spacing[3];
  int extent[6]; 
  double origin[3];
  
    int numberOfFactors = this->FuzzyModelParameter->GetNumberOfFactors();

    if (numberOfFactors == 2) {
        this->ZAxisExtent = 1;
    }
    
    extent[0] = 0.0;
    extent[1] = this->XAxisExtent - 1;
    extent[2] = 0.0;
    extent[3] = this->YAxisExtent - 1;
    extent[4] = 0.0;
    extent[5] = this->ZAxisExtent - 1;
    
    FuzzyInferenceScheme &FIS = this->FuzzyModelParameter->GetInternalScheme();

    double minX = FIS.Factors[0].min;
    double maxX = FIS.Factors[0].max;
    double minY = FIS.Factors[1].min;
    double maxY = FIS.Factors[1].max;

    double minZ = 0;
    double maxZ = 0;
    if (numberOfFactors == 3) {
        minZ = FIS.Factors[2].min;
        maxZ = FIS.Factors[2].max;
    }
    
    origin[0] = minX;
    origin[1] = minY;
    origin[2] = minZ;
    
    spacing[0] = (maxX - minX) / this->XAxisExtent;
    spacing[1] = (maxY - minY) / this->YAxisExtent;
    spacing[2] = (maxZ - minZ) / this->ZAxisExtent;

  outInfo->Set(vtkStreamingDemandDrivenPipeline::WHOLE_EXTENT(),extent, 6);
  outInfo->Set(vtkDataObject::SPACING(), spacing, 3);
  outInfo->Set(vtkDataObject::ORIGIN(),  origin, 3);

    vtkDataObject::SetPointDataActiveScalarInfo(
            outputVector->GetInformationObject(0), -1, 1);
    
  return 1;
}

//----------------------------------------------------------------------------

int vtkTAG2EFuzzyInferenceModelParameterToImageData::RequestData(
                                                                 vtkInformation * vtkNotUsed(request),
                                                                 vtkInformationVector **inputVector,
                                                                 vtkInformationVector *outputVector)
{
    int numberOfRules = 0;
    int numberOfFactors = 0;
    int i;
    int Extent[6];

    // get the data object
    vtkInformation *outInfo = outputVector->GetInformationObject(0);
    vtkImageData *output = vtkImageData::SafeDownCast(
                                                      outInfo->Get(vtkDataObject::DATA_OBJECT()));

    FuzzyInferenceScheme &FIS = this->FuzzyModelParameter->GetInternalScheme();

    // Compute the number of rules and number of factors
    numberOfRules = this->FuzzyModelParameter->GetNumberOfRules();
    numberOfFactors = this->FuzzyModelParameter->GetNumberOfFactors();

    if (numberOfFactors < 2 or numberOfFactors > 3) {
        vtkErrorMacro("The number of Factors must be 2 or 3");
        return -1;
    }

    if (numberOfFactors == 2) {
        this->ZAxisExtent = 1;
    }

    // Create the rule code matrix
    std::vector< std::vector<int> > RuleCodeMatrix(numberOfRules, std::vector<int>(numberOfFactors));
    std::vector<double> DOFVector(numberOfRules);
    std::vector<double> DOFSumVector(numberOfRules);

    /* Initialize the degree of fulfillment vectors */
    for (i = 0; i < numberOfRules; i++) {
        DOFVector[i] = 0;
        DOFSumVector[i] = 0;
    }

    // Compute the rule code matrix entries 
    tag2eFIS::ComputeRuleCodeMatrixEntries(RuleCodeMatrix, numberOfRules, FIS);

    Extent[0] = 0;
    Extent[1] = this->XAxisExtent - 1;
    Extent[2] = 0;
    Extent[3] = this->YAxisExtent - 1;
    Extent[4] = 0;
    Extent[5] = this->ZAxisExtent - 1;

    output->SetExtent(Extent);
    output->AllocateScalars();

    vtkDataArray *result;

    result = output->GetPointData()->GetScalars();
    result->SetName("Responses");
    
    double *fuzzyInput = new double[numberOfFactors];

    double minX = FIS.Factors[0].min;
    double maxX = FIS.Factors[0].max;
    double minY = FIS.Factors[1].min;
    double maxY = FIS.Factors[1].max;

    double minZ = 0;
    double maxZ = 0;
    if (numberOfFactors == 3) {
        minZ = FIS.Factors[2].min;
        maxZ = FIS.Factors[2].max;
    }

    int count = 0;

    for (int z = 0; z < this->ZAxisExtent; z++) {
        for (int y = 0; y < this->YAxisExtent; y++) {
            for (int x = 0; x < this->XAxisExtent; x++) {

                fuzzyInput[0] = minX + x * (maxX - minX) / this->XAxisExtent;
                fuzzyInput[1] = minY + y * (maxY - minY) / this->YAxisExtent;

                if (numberOfFactors == 3) {
                    fuzzyInput[2] = minZ + z * (maxZ - minZ) / this->ZAxisExtent;
                }
                double val = tag2eFIS::ComputeFISResult(fuzzyInput, numberOfRules, RuleCodeMatrix, FIS, DOFVector);
                //cout << "Result x " << x << " y " << y << " z " << z << " " << val << endl;
                result->InsertTuple1(count, val);
                count++;
            }
        }
    }
    
    delete [] fuzzyInput;

    return 1;
}

//----------------------------------------------------------------------------

void vtkTAG2EFuzzyInferenceModelParameterToImageData::PrintSelf(ostream& os, vtkIndent indent)
{
    this->Superclass::PrintSelf(os, indent);
}

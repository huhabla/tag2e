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


#include <vtkImageData.h>
#include <vtkImageProgressIterator.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkObjectFactory.h>
#include <vtkStreamingDemandDrivenPipeline.h>
#include "vtkTAG2EImageDataN2OFilterFreibauer.h"

vtkCxxRevisionMacro(vtkTAG2EImageDataN2OFilterFreibauer, "$Revision: 1.1 $");
vtkStandardNewMacro(vtkTAG2EImageDataN2OFilterFreibauer);

//----------------------------------------------------------------------------

vtkTAG2EImageDataN2OFilterFreibauer::vtkTAG2EImageDataN2OFilterFreibauer() {
    this->SetNumberOfInputPorts(4);
    this->NullValue = -999999;
    this->ClimateType = VTK_TAG2E_CLIMATETYPE_FREIBAUER_TWE;
    this->CropType = VTK_TAG2E_CROPTYPE_GRASS;
}

//----------------------------------------------------------------------------

int vtkTAG2EImageDataN2OFilterFreibauer::RequestInformation(
        vtkInformation * vtkNotUsed(request),
        vtkInformationVector ** vtkNotUsed(inputVector),
        vtkInformationVector *outputVector) {
    vtkDataObject::SetPointDataActiveScalarInfo(
            outputVector->GetInformationObject(0), -1, 1);
    return 1;
}


//----------------------------------------------------------------------------
// This templated function executes the filter for any type of data.
// Handles the six input

template <class T>
void vtkTAG2EImageDataN2OFilterFreibauerExecute(vtkTAG2EImageDataN2OFilterFreibauer *self,
vtkImageData *NrateData,
vtkImageData *sandFractData,
vtkImageData *soilOrgFractData,
vtkImageData *soilNData,
int cropType,
int climateType,
vtkImageData *outData,
int outExt[6], int id, T *) {
    vtkImageIterator<T> NrateIt(NrateData, outExt);
    vtkImageIterator<T> sandFractIt(sandFractData, outExt);
    vtkImageIterator<T> soilOrgFractIt(soilOrgFractData, outExt);
    vtkImageIterator<T> soilNIt(soilNData, outExt);
    vtkImageProgressIterator<T> outIt(outData, outExt, self, id);

    double result;
    double Nrate;
    double sandFract;
    double soilOrgFract;
    double soilN;

    // Loop through ouput pixels
    while (!outIt.IsAtEnd()) {
        T* NrateSI = NrateIt.BeginSpan();
        T* sandFractSI = sandFractIt.BeginSpan();
        T* soilOrgFractSI = soilOrgFractIt.BeginSpan();
        T* soilNSI = soilNIt.BeginSpan();

        T* outSI = outIt.BeginSpan();
        T* outSIEnd = outIt.EndSpan();

        while (outSI != outSIEnd) {
            Nrate= static_cast<double> (*NrateSI);
            sandFract = static_cast<double> (*sandFractSI);
            soilOrgFract = static_cast<double> (*soilOrgFractSI);
            soilN = static_cast<double> (*soilNSI);

            if (Nrate        == self->GetNullValue() ||
                sandFract    == self->GetNullValue() ||
                soilOrgFract == self->GetNullValue() ||
                soilN        == self->GetNullValue()) {
                result = self->GetNullValue();
            } else {
                result = vtkTAG2EAlternativeN2OPredictionModules::Freibauer(Nrate,
                        sandFract, soilOrgFract, soilN, cropType, climateType);
            }

            *outSI = static_cast<T> (result);
            ++NrateSI;
            ++sandFractSI;
            ++soilOrgFractSI;
            ++soilNSI;
            ++outSI;
        }
        NrateIt.NextSpan();
        sandFractIt.NextSpan();
        soilOrgFractIt.NextSpan();
        soilNIt.NextSpan();
        outIt.NextSpan();
    }
}


//----------------------------------------------------------------------------
// This method is passed a input and output regions, and executes the filter
// algorithm to fill the output from the inputs.
// It just executes a switch statement to call the correct function for
// the regions data types.

void vtkTAG2EImageDataN2OFilterFreibauer::ThreadedRequestData(
        vtkInformation * vtkNotUsed(request),
        vtkInformationVector ** vtkNotUsed(inputVector),
        vtkInformationVector * vtkNotUsed(outputVector),
        vtkImageData ***inData,
        vtkImageData **outData,
        int outExt[6], int id) {
    int i;

    for (i = 0; i < this->GetNumberOfInputPorts(); i++) {
        // this filter expects that input is the same type as output.
        if (inData[i][0]->GetScalarType() != outData[0]->GetScalarType()) {
            vtkErrorMacro( << "Execute: input " << i << " ScalarType, "
                    << inData[i][0]->GetScalarType()
                    << ", must match output ScalarType "
                    << outData[0]->GetScalarType());
            return;
        }
        if (inData[i][0]->GetNumberOfScalarComponents() > 1)
            vtkErrorMacro( << "Execute: only one scalar component is supported");
    }

    switch (inData[0][0]->GetScalarType()) {
            vtkTemplateMacro(
                    vtkTAG2EImageDataN2OFilterFreibauerExecute(this, inData[0][0],
                    inData[1][0], inData[2][0], inData[3][0], this->CropType,
                    this->ClimateType, outData[0], outExt, id,
                    static_cast<VTK_TT *> (0)));
        default:
            vtkErrorMacro( << "Execute: Unknown ScalarType");
            return;
    }
}















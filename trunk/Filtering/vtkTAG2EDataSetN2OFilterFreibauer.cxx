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


#include <vtkCellData.h>
#include <vtkIntArray.h>
#include <vtkDataSet.h>
#include <vtkDoubleArray.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkMath.h>
#include <vtkObjectFactory.h>
#include <vtkPointData.h>
#include <vtkDataSetAttributes.h>
#include "vtkTAG2EDataSetN2OFilterFreibauer.h"
#include "vtkTAG2EAlternativeN2OPredictionModules.h"

vtkCxxRevisionMacro(vtkTAG2EDataSetN2OFilterFreibauer, "$Revision: 1.20 $");
vtkStandardNewMacro(vtkTAG2EDataSetN2OFilterFreibauer);

// Construct object with LowPoint=(0,0,0) and HighPoint=(0,0,1). Scalar
// range is (0,1).
vtkTAG2EDataSetN2OFilterFreibauer::vtkTAG2EDataSetN2OFilterFreibauer()
{
    this->UsePointData = 0;
    this->NullValue = -999999;
    this->SandFractionArrayName =NULL;
    this->SoilNitrogenArrayName = NULL;
    this->CropTypeArrayName = NULL;
    this->ClimateTypeArrayName = NULL;
    this->SoilOrganicCorbonArrayName = NULL;
    this->NitrogenRateArrayName = NULL;
    this->CategoryArrayName = NULL;
}

// Convert position along ray into scalar value.  Example use includes 
// coloring terrain by elevation.
//
int vtkTAG2EDataSetN2OFilterFreibauer::RequestData(
  vtkInformation *vtkNotUsed(request),
  vtkInformationVector **inputVector,
  vtkInformationVector *outputVector)
{
  // get the info objects
  vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
  vtkInformation *outInfo = outputVector->GetInformationObject(0);

  // get the input and ouptut
  vtkDataSet *input = vtkDataSet::SafeDownCast(
    inInfo->Get(vtkDataObject::DATA_OBJECT()));
  vtkDataSet *output = vtkDataSet::SafeDownCast(
    outInfo->Get(vtkDataObject::DATA_OBJECT()));

  // Check for all arrays
  if(this->UsePointData) {
      if(!input->GetPointData()->HasArray(this->CategoryArrayName) ||
         !input->GetPointData()->HasArray(this->CropTypeArrayName) ||
         !input->GetPointData()->HasArray(this->ClimateTypeArrayName) ||
         !input->GetPointData()->HasArray(this->NitrogenRateArrayName) ||
         !input->GetPointData()->HasArray(this->SoilNitrogenArrayName) ||
         !input->GetPointData()->HasArray(this->SoilOrganicCorbonArrayName) ||
         !input->GetPointData()->HasArray(this->SandFractionArrayName)) {
          vtkErrorMacro(<< "Missing point data input array, abort.");
          return 0;
      }
  }else {
      if(!input->GetCellData()->HasArray(this->CategoryArrayName) ||
         !input->GetCellData()->HasArray(this->CropTypeArrayName) ||
         !input->GetCellData()->HasArray(this->ClimateTypeArrayName) ||
         !input->GetCellData()->HasArray(this->NitrogenRateArrayName) ||
         !input->GetCellData()->HasArray(this->SoilNitrogenArrayName) ||
         !input->GetCellData()->HasArray(this->SoilOrganicCorbonArrayName) ||
         !input->GetCellData()->HasArray(this->SandFractionArrayName)) {
          vtkErrorMacro(<< "Missing cell data input array, abort.");
          return 0;
      }
  }
  
 // First, copy the input to the output as a starting point
  output->CopyStructure( input );

  // We compute the N2O emission only for each category
  // If the emission was computed for one categorie, the result will be stored
  // for each cell/point with the same category, no new computation will be perfomred
  vtkIntArray *cats = vtkIntArray::New();
  vtkDoubleArray *catN2O = vtkDoubleArray::New();
  cats->SetNumberOfComponents(1);
  catN2O->SetNumberOfComponents(1);
  // The size of the arrays is dependent from the range of the categories, so we
  // use the maximum category number to allocate the arrays
  if(this->UsePointData) {
    double *range = input->GetPointData()->GetArray(this->CategoryArrayName)->GetRange();
    cats->SetNumberOfTuples((int)range[1] + 1);
    catN2O->SetNumberOfTuples((int)range[1] + 1);
  }else {
    double *range = input->GetCellData()->GetArray(this->CategoryArrayName)->GetRange();
    cats->SetNumberOfTuples((int)range[1] + 1);
    catN2O->SetNumberOfTuples((int)range[1] + 1);
  }
  cats->FillComponent(0, 0);
  catN2O->FillComponent(0, 0);

  // The resulting array
  vtkDoubleArray *N2Oemission = vtkDoubleArray::New();
  N2Oemission->SetName("N2O");
  if(this->UsePointData)
    N2Oemission->SetNumberOfTuples(input->GetNumberOfPoints());
  else
    N2Oemission->SetNumberOfTuples(input->GetNumberOfCells());
  N2Oemission->FillComponent(0, 0);

  int i, cat;
  double n, sc, sn, cr, cl, s, n2o;
  int num;
  vtkDataSetAttributes *data = NULL;


  // Sweitch between Point or Cell data
  if(this->UsePointData) {
      num = input->GetNumberOfPoints();
      data = input->GetPointData();
  }else {
      num = input->GetNumberOfCells();
      data = input->GetCellData();
  }

  // Compute the emission
  for(i = 0; i < num; i++) {
      // Get the category
      cat = (int)data->GetArray(this->CategoryArrayName)->GetTuple1(i);

      if(cat < 0)
      {
          N2Oemission->InsertValue(i, this->NullValue);
          continue;
      }

      // Check if the result was computed befor
      if(cats->GetValue(cat) == 0)
      {
          // Gather the input data
          n = data->GetArray(this->NitrogenRateArrayName)->GetTuple1(i);
          sc = data->GetArray(this->SoilOrganicCorbonArrayName)->GetTuple1(i);
          sn = data->GetArray(this->SoilNitrogenArrayName)->GetTuple1(i);
          cr = (int)data->GetArray(this->CropTypeArrayName)->GetTuple1(i);
          cl = (int)data->GetArray(this->ClimateTypeArrayName)->GetTuple1(i);
          s = data->GetArray(this->SandFractionArrayName)->GetTuple1(i);
          // Compute the model
          n2o = vtkTAG2EAlternativeN2OPredictionModules::Freibauer(n, s, sc, sn, cr, cl);
          // Save the value for the cat
          catN2O->InsertValue(cat, n2o);
          // Mark as computed
          cats->InsertValue(cat, 1);

          // Debug output
          //cout << "new:" << i << " cat: " << cat << " n2o: " << n2o << endl;
      }
      // Store the result in the result array
      N2Oemission->InsertValue(i, catN2O->GetValue(cat));
      // Debug output
      //cout << "old: " << i << " cat: " << cat << " n2o: " << n2o << endl;
  }

  // Update self
  //
  output->GetPointData()->CopyScalarsOff();
  output->GetPointData()->PassData(input->GetPointData());
  output->GetCellData()->PassData(input->GetCellData());
  if(this->UsePointData) {
    output->GetPointData()->AddArray(N2Oemission);
    output->GetPointData()->SetActiveScalars(N2Oemission->GetName());
  } else {
    output->GetCellData()->AddArray(N2Oemission);
    output->GetCellData()->SetActiveScalars(N2Oemission->GetName());
  }
  N2Oemission->Delete();
  catN2O->Delete();
  cats->Delete();

  return 1;
}

void vtkTAG2EDataSetN2OFilterFreibauer::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);
}

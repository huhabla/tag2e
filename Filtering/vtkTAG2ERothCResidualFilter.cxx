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
#include <vtkIdTypeArray.h>
#include <vtkCell.h>
#include <vtkMath.h>
#include <vtkSortDataArray.h>

extern "C" {
#include <math.h>
}

#include <vtkDataSetAlgorithm.h>
#include <vtkObjectFactory.h>
#include "vtkTAG2ERothCResidualFilter.h"
#include "vtkTAG2ERothCDefines.h"

vtkCxxRevisionMacro(vtkTAG2ERothCResidualFilter, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2ERothCResidualFilter);

//----------------------------------------------------------------------------

vtkTAG2ERothCResidualFilter::vtkTAG2ERothCResidualFilter()
{
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
}

//----------------------------------------------------------------------------

vtkTAG2ERothCResidualFilter::~vtkTAG2ERothCResidualFilter()
{
  ;
}

//----------------------------------------------------------------------------

int vtkTAG2ERothCResidualFilter::FillInputPortInformation(int vtkNotUsed(port),
                                                          vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkPolyData");
  return 1;
}

//----------------------------------------------------------------------------
int vtkTAG2ERothCResidualFilter::FillOutputPortInformation(int port,
                                                           vtkInformation* info)
{
  if (!this->Superclass::FillOutputPortInformation(port, info))
    {
    return 0;
    }

  // now add our info
  info->Set(vtkDataObject::DATA_TYPE_NAME(), "vtkPolyData");
  return 1;
}

//----------------------------------------------------------------------------

int vtkTAG2ERothCResidualFilter::RequestData(
    vtkInformation * vtkNotUsed(request), vtkInformationVector **inputVector,
    vtkInformationVector *outputVector)
{
  vtkIdType i;
  vtkIdType cellId;
  bool hasInputPools = true;
  int maxLayerNumber = 0;
  double lineLength;

  // This is the artificial ration between the surface and root residuals
  double ratio = 0.5;

  vtkDataSet* input = vtkDataSet::GetData(inputVector[0]);
  vtkDataSet* output = vtkDataSet::GetData(outputVector);

  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_RESIDUALS))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_RESIDUALS << "> is missing ");
    return -1;
    }

  /* Not needed yet and therefor commented out
  if (!input->GetCellData()->HasArray(ROTHC_INPUT_NAME_ROOT_DEPTH))
    {
    vtkErrorMacro(
        <<"Cell data array <" << ROTHC_INPUT_NAME_ROOT_DEPTH << "> is missing ");
    return -1;
    }
    */

  // Copy geometry from input
  output->CopyStructure(input);

  // Result array
  vtkDoubleArray *residualsRootsArray = vtkDoubleArray::New();
  residualsRootsArray->SetNumberOfComponents(1);
  residualsRootsArray->SetName(ROTHC_INPUT_NAME_RESIDUALS_ROOTS);
  residualsRootsArray->SetNumberOfTuples(output->GetNumberOfCells());

  vtkDoubleArray *residualsSurfaceArray = vtkDoubleArray::New();
  residualsSurfaceArray->SetNumberOfComponents(1);
  residualsSurfaceArray->SetName(ROTHC_INPUT_NAME_RESIDUALS_SURFACE);
  residualsSurfaceArray->SetNumberOfTuples(output->GetNumberOfCells());

  vtkIntArray *layerIdArray = vtkIntArray::New();
  layerIdArray->SetNumberOfComponents(1);
  layerIdArray->SetName(ROTHC_INPUT_NAME_LAYER);
  layerIdArray->SetNumberOfTuples(output->GetNumberOfCells());

  vtkUnsignedCharArray *checkIdArray = vtkUnsignedCharArray::New();
  checkIdArray->SetNumberOfComponents(1);
  checkIdArray->SetName("CechkId");
  checkIdArray->SetNumberOfTuples(output->GetNumberOfCells());
  checkIdArray->FillComponent(0, 0.0);

  vtkDoubleArray *lineLengthArray = vtkDoubleArray::New();
  lineLengthArray->SetNumberOfComponents(1);
  lineLengthArray->SetName(ROTHC_INPUT_NAME_LINE_LENGTH);
  lineLengthArray->SetNumberOfTuples(output->GetNumberOfCells());

  vtkDoubleArray *cumulativeRootFraction = vtkDoubleArray::New();
  cumulativeRootFraction->SetNumberOfComponents(1);
  cumulativeRootFraction->SetName(ROTHC_INPUT_NAME_CUMULATIVE_LINE_LENGTH);
  cumulativeRootFraction->SetNumberOfTuples(output->GetNumberOfCells());

  vtkDoubleArray *lineCenterArray = vtkDoubleArray::New();
  lineCenterArray->SetNumberOfComponents(3);
  lineCenterArray->SetName(ROTHC_INPUT_NAME_LINE_CENTER);
  lineCenterArray->SetNumberOfTuples(output->GetNumberOfCells());

  // Create the arrays that are needed to compute the layer id
  vtkDoubleArray *centerCoorArray = vtkDoubleArray::New();
  centerCoorArray->SetNumberOfComponents(1);
  vtkIdTypeArray *cellIdArray = vtkIdTypeArray::New();
  cellIdArray->SetNumberOfComponents(1);

  // Get array pointer for easy access
  vtkDataArray *residualArray = input->GetCellData()->GetArray(
      ROTHC_INPUT_NAME_RESIDUALS);
  // Not yet in use
  // vtkDataArray *rootDepthArray = input->GetCellData()->GetArray(
  //     ROTHC_INPUT_NAME_ROOT_DEPTH);
  ;
  // Compute the layer id and check the topology and line length
  // Parallelize with OpenMP
  for (cellId = 0; cellId < input->GetNumberOfCells(); cellId++)
    {
    int layer;
    int numLayer;

    // Jump over checked cells
    if (checkIdArray->GetValue(cellId))
      continue;

    // reset the array that stores the neighbors of the current cell
    centerCoorArray->Reset();
    cellIdArray->Reset();

    // cout << "Check cell id: " << cellId << endl;

    // Check the cell neighbors
    if (!this->CheckCellNeighbours(input, cellId, centerCoorArray, cellIdArray,
        checkIdArray, lineLengthArray, lineCenterArray))
      return -1;

    // Sort the cell id layer array to identify the layer number
    vtkSortDataArray::Sort(centerCoorArray, cellIdArray);

    // Check the neighbors
    numLayer = cellIdArray->GetNumberOfTuples();

    // cout << "Identified layer: " << numLayer << endl;

    // Store the layer id, 0 is top layer
    for (layer = 0; layer < numLayer; layer++)
      {
      layerIdArray->SetValue(cellIdArray->GetValue(layer),
          numLayer - (layer + 1));
      }

    lineLength = 0.0;
    // compute the cumulative line length

    // ATTENTION: We need to implement a depth dependent
    // residual fraction for roots, see "A global analysis of root distributions for terrestrial biomes"
    // from Jackson et al 1996
    for (layer = numLayer - 1; layer >= 0; layer--)
      {
      double length = lineLengthArray->GetValue(cellIdArray->GetValue(layer));
      lineLength += length;

      cumulativeRootFraction->SetValue(cellIdArray->GetValue(layer),
          lineLength);
      }
    }

  // Compute the residuals
  // ATTENTION: We need to implement a depth dependent
  // residual fraction for roots, see "A global analysis of root distributions for terrestrial biomes"
  // from Jackson et al 1996
  for (cellId = 0; cellId < input->GetNumberOfCells(); cellId++)
    {
    double residual = residualArray->GetTuple1(cellId);
    double roots = 0.0;
    double surface = 0.0;
    vtkIdType layer;

    // Jump over NULL values
    if (residual == this->NullValue)
      {
      residualsRootsArray->SetTuple1(cellId, this->NullValue);
      residualsSurfaceArray->SetTuple1(cellId, this->NullValue);
      continue;
      }
    layer = layerIdArray->GetValue(cellId);

    // ATTENTION!!!!!! Only the top layer has input
    if (layer == 0)
      {
      surface = ratio * residual;
      roots = (1 - ratio) * residual;
      }
    else
      {
      surface = 0.0;
      roots = 0.0;
      }

    residualsRootsArray->SetTuple1(cellId, roots);
    residualsSurfaceArray->SetTuple1(cellId, surface);
    }

  output->GetCellData()->AddArray(layerIdArray);
  output->GetCellData()->AddArray(lineCenterArray);
  output->GetCellData()->AddArray(lineLengthArray);
  output->GetCellData()->AddArray(cumulativeRootFraction);
  output->GetCellData()->AddArray(checkIdArray);
  output->GetCellData()->AddArray(residualsRootsArray);
  output->GetCellData()->AddArray(residualsSurfaceArray);
  output->GetCellData()->SetActiveScalars(residualsSurfaceArray->GetName());
  residualsRootsArray->Delete();
  residualsSurfaceArray->Delete();
  layerIdArray->Delete();
  lineLengthArray->Delete();
  cumulativeRootFraction->Delete();
  checkIdArray->Delete();
  centerCoorArray->Delete();
  cellIdArray->Delete();
  lineCenterArray->Delete();

  return 1;
}

//----------------------------------------------------------------------------

double vtkTAG2ERothCResidualFilter::ComputeLineLength(vtkDataSet *input,
                                                      vtkIdList *pointIds)
{
  double p1[3];
  double p2[3];

  // Compute length of the line in vertical direction
  input->GetPoint(pointIds->GetId(0), p1);
  input->GetPoint(pointIds->GetId(1), p2);
  return fabs(p1[2] - p2[2]);
}

//----------------------------------------------------------------------------

void vtkTAG2ERothCResidualFilter::ComputeCenterPoint(vtkDataSet *input,
                                                     vtkIdList *pointIds,
                                                     double *center)
{
  double p1[3];
  double p2[3];

  // Compute length of the line in vertical direction
  input->GetPoint(pointIds->GetId(0), p1);
  input->GetPoint(pointIds->GetId(1), p2);

  center[0] = (p1[0] + p2[0]) / 2.0;
  center[1] = (p1[1] + p2[1]) / 2.0;
  center[2] = (p1[2] + p2[2]) / 2.0;
}

//----------------------------------------------------------------------------

bool vtkTAG2ERothCResidualFilter::CheckCellNeighbours(
    vtkDataSet *input, vtkIdType cellId, vtkDoubleArray *centerCoorArray,
    vtkIdTypeArray *cellIdArray, vtkUnsignedCharArray *checkIdArray,
    vtkDoubleArray *lineLengthArray, vtkDoubleArray *lineCenterArray)
{
  double lineLength;
  double center[3];
  int i;

  // Return if this cell was already processed
  if (checkIdArray->GetValue(cellId))
    return true;

  // cout << "Processing cell id: " << cellId << endl;

  vtkIdList *pointIds = vtkIdList::New();

  // Check cell type, we support only lines
  if (input->GetCellType(cellId) != VTK_LINE)
    {
    vtkErrorMacro("Unsupported cell type.");
    return false;
    }

  input->GetCellPoints(cellId, pointIds);

  // We support only lines with two coordinates
  if (pointIds->GetNumberOfIds() != 2)
    {
    vtkErrorMacro("Unsupported line length.");
    return false;
    }

  // Compute length of the line in vertical direction
  lineLength = this->ComputeLineLength(input, pointIds);
  lineLengthArray->SetTuple1(cellId, lineLength);

  this->ComputeCenterPoint(input, pointIds, center);
  lineCenterArray->SetTuple3(cellId, center[0], center[1], center[2]);

  // Store the z coordinate and the current cell ids
  // for later layer id computation
  centerCoorArray->InsertNextValue(center[2]);
  cellIdArray->InsertNextValue(cellId);

  // cout << "Center: " << center[2] << endl;

  // Mark the current cell id as processed
  checkIdArray->SetValue(cellId, true);

  vtkIdList *idList = vtkIdList::New();
  vtkIdList *neighborCellIds = vtkIdList::New();

  // We need to check the cell neighbors for each vertices of the cell
  for (vtkIdType i = 0; i < pointIds->GetNumberOfIds(); i++)
    {
    idList->Reset();
    neighborCellIds->Reset();

    idList->InsertNextId(pointIds->GetId(i));

    //get the neighbors of the cell
    input->GetCellNeighbors(cellId, idList, neighborCellIds);

    for (vtkIdType j = 0; j < neighborCellIds->GetNumberOfIds(); j++)
      {
      if (!this->CheckCellNeighbours(input, neighborCellIds->GetId(j),
          centerCoorArray, cellIdArray, checkIdArray, lineLengthArray,
          lineCenterArray))
        return false;
      }
    }

  pointIds->Delete();
  idList->Delete();
  neighborCellIds->Delete();

  return true;
}

//----------------------------------------------------------------------------

void vtkTAG2ERothCResidualFilter::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}

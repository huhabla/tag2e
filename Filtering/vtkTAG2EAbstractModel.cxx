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
#include "vtkTAG2EAbstractModel.h"

vtkCxxRevisionMacro(vtkTAG2EAbstractModel, "$Revision: 1.0 $");
vtkStandardNewMacro(vtkTAG2EAbstractModel);

//----------------------------------------------------------------------------

vtkTAG2EAbstractModel::vtkTAG2EAbstractModel()
{
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
  this->ModelParameter = NULL;
  this->ResultArrayName = NULL;
  this->SetResultArrayName("result");
  this->UseCellDataOff();
  this->NullValue = -999999;
}

//----------------------------------------------------------------------------

vtkTAG2EAbstractModel::~vtkTAG2EAbstractModel()
{
  if(this->ModelParameter)
    this->ModelParameter->Delete();
  if(this->ResultArrayName)
    delete [] this->ResultArrayName;
}


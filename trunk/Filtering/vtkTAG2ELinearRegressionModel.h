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

/**
 * \brief 
 * 
 */

#ifndef vtkTAG2ELinearRegressionModel_H
#define	vtkTAG2ELinearRegressionModel_H

#include "vtkTAG2EAbstractModel.h"

class vtkDoubleArray;
class vtkStringArray;
class vtkIntArray;

class vtkTAG2ELinearRegressionModel: public vtkTAG2EAbstractModel
{
public:
vtkTypeRevisionMacro(vtkTAG2ELinearRegressionModel, vtkTAG2EAbstractModel);

  void PrintSelf(ostream& os, vtkIndent indent);

  virtual void SetModelParameter(
      vtkTAG2EAbstractModelParameter* modelParameter);

  static vtkTAG2ELinearRegressionModel *New();

protected:
  vtkTAG2ELinearRegressionModel();
  ~vtkTAG2ELinearRegressionModel();

  virtual int RequestData(vtkInformation *, vtkInformationVector **,
      vtkInformationVector *);

  virtual bool BuildLRValueArrays();

  vtkIntArray *InputPorts;
  vtkDoubleArray *Coefficents;
  vtkDoubleArray *Power;
  vtkStringArray *ArrayNames;
  double Intercept;

private:
  vtkTAG2ELinearRegressionModel(const vtkTAG2ELinearRegressionModel& orig); // Not implemented.
  void operator=(const vtkTAG2ELinearRegressionModel&); // Not implemented.
};

#endif	/* vtkTAG2ELinearRegressionModel_H */

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
 * \brief RothC
 */

#ifndef vtkTAG2ERothCWaterBudgetModel_H
#define	vtkTAG2ERothCWaterBudgetModel_H

#include <vtkPolyData.h>
#include "vtkTAG2EAbstractCalibratableModel.h"

class vtkTAG2ERothCWaterBudgetModel: public vtkTAG2EAbstractModel
{
public:
vtkTypeRevisionMacro(vtkTAG2ERothCWaterBudgetModel, vtkTAG2EAbstractModel);

  void PrintSelf(ostream& os, vtkIndent indent);
  static vtkTAG2ERothCWaterBudgetModel *New();
  //! \brief Set the temporal ration

  //!\brief This model has no XML description yet
  void SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter){;}

protected:
  vtkTAG2ERothCWaterBudgetModel();
  ~vtkTAG2ERothCWaterBudgetModel();

  virtual int RequestData(vtkInformation *, vtkInformationVector **,
      vtkInformationVector *);
  virtual int FillInputPortInformation(int port, vtkInformation* info);
  virtual int FillOutputPortInformation(int port, vtkInformation* info);

private:
  vtkTAG2ERothCWaterBudgetModel(const vtkTAG2ERothCWaterBudgetModel& orig); // Not implemented.
  void operator=(const vtkTAG2ERothCWaterBudgetModel&); // Not implemented.
};

#endif	/* vtkTAG2ERothCWaterBudgetModel_H */

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
 *
 * Input:
 * * Temperature in C°
 * * Global Radiation in J/(cm^2 * d)
 *
 */

#ifndef vtkTAG2ETurcEPotModel_H
#define	vtkTAG2ETurcEPotModel_H

#include <vtkPolyData.h>
#include "vtkTAG2EAbstractCalibratableModel.h"

class vtkTAG2ETurcETPotModel: public vtkTAG2EAbstractModel
{
public:
vtkTypeRevisionMacro(vtkTAG2ETurcETPotModel, vtkTAG2EAbstractModel);

  void PrintSelf(ostream& os, vtkIndent indent);
  static vtkTAG2ETurcETPotModel *New();

  //! \brief Set the time interval in days
  vtkSetMacro(TimeInterval, double);
  //! \brief Get the time interval in days
  vtkGetMacro(TimeInterval, double);

  //!\brief This model has no XML description yet
  void SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter){;}

protected:
  vtkTAG2ETurcETPotModel();
  ~vtkTAG2ETurcETPotModel();

  virtual int RequestData(vtkInformation *, vtkInformationVector **,
      vtkInformationVector *);
  virtual int FillInputPortInformation(int port, vtkInformation* info);
  virtual int FillOutputPortInformation(int port, vtkInformation* info);

  double TimeInterval;

private:
  vtkTAG2ETurcETPotModel(const vtkTAG2ETurcETPotModel& orig); // Not implemented.
  void operator=(const vtkTAG2ETurcETPotModel&); // Not implemented.
};

#endif	/* vtkTAG2ETurcEPotModel_H */

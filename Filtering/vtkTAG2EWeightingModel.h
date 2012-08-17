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
 * \brief This class uses a  fuzzy inference scheme to process
 * the point data of the temporal input data sets. The  fuzzy inference 
 * must be provided as as XML model parameter representation which is of type
 * vtkTAG2EWeightingModelParameter.
 */

#ifndef vtkTAG2EWeightingModel_H
#define	vtkTAG2EWeightingModel_H

#include "vtkTAG2EAbstractCalibratableModel.h"
#include "vtkTAG2EWeightingModelParameter.h"

class vtkTAG2EWeightingModel: public vtkTAG2EAbstractCalibratableModel
{
public:
vtkTypeRevisionMacro(vtkTAG2EWeightingModel, vtkTAG2EAbstractCalibratableModel)
  ;

  void PrintSelf(ostream& os, vtkIndent indent);
  static vtkTAG2EWeightingModel *New();

  virtual double GetModelAssessmentFactor()
  {
    return 1.0;
  }

  //!\brief Set the model parameter which must be of type vtkTAG2EWeightingModelParameter
  //! This XML model parameter describes the weighting scheme which is used to compute
  //! the input data.
  void SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter);

protected:
  vtkTAG2EWeightingModel();
  ~vtkTAG2EWeightingModel();

  virtual int RequestData(vtkInformation *, vtkInformationVector **,
      vtkInformationVector *);
  virtual int FillInputPortInformation(int port, vtkInformation* info);
  virtual int FillOutputPortInformation(int port, vtkInformation* info);

  vtkTAG2EWeightingModelParameter *WeightingModelParameter;

private:
  vtkTAG2EWeightingModel(const vtkTAG2EWeightingModel& orig); // Not implemented.
  void operator=(const vtkTAG2EWeightingModel&); // Not implemented.
};

#endif	/* vtkTAG2EWeightingModel_H */

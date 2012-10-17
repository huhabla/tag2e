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

#ifndef vtkTAG2ERothCModel_H
#define	vtkTAG2ERothCModel_H

#include <vtkPolyData.h>
#include "vtkTAG2EAbstractCalibratableModel.h"
#include "vtkTAG2ERothCModelParameter.h"

class vtkTAG2ERothCModel: public vtkTAG2EAbstractCalibratableModel
{
public:
vtkTypeRevisionMacro(vtkTAG2ERothCModel, vtkTAG2EAbstractCalibratableModel)
  ;

  void PrintSelf(ostream& os, vtkIndent indent);
  static vtkTAG2ERothCModel *New();

  virtual double GetModelAssessmentFactor()
  {
    return 1.0;
  }

  //! \brief This flags must be set to false when the C pools
  //!  should be initiated by a given initial soil carbon.
  //!  Hence in addition to the RothC input arrays an initial soil carbon
  //!  amount must be provided.
  //!  The C pools are only initiated when they are not provided in the input
  //!  dataset and CPoolsInitiated is set to false. The internal
  //!  C pools are used for computation, in case the C pools are not located
  //!  in the input dataset and CPoolsInitiated is true
  vtkSetMacro(CPoolsInitiated, int);
  vtkGetMacro(CPoolsInitiated, int);
  vtkBooleanMacro(CPoolsInitiated, int);

  //! \brief Set this true if the internal pools should be added to the output
  //!  dataset
  vtkSetMacro(AddCPoolsToOutput, int);
  vtkGetMacro(AddCPoolsToOutput, int);
  vtkBooleanMacro(AddCPoolsToOutput, int);

  //! \brief Set this value true to enable the equlibrium run for the TothC model
  //! In this case the fertilizer input is ignored and soil cover is assumed
  //! at every run.
  vtkSetMacro(EquilibriumRun, int);
  vtkGetMacro(EquilibriumRun, int);
  vtkBooleanMacro(EquilibriumRun, int);

  //! \brief Set the temporal ration
  //!
  //! In case of monthly resolution set the ration to 1/12.
  //! In case of daily resoltuion set the ration to 1/365.
  vtkSetMacro(TemporalRatio, double);
  //! \brief Get the temporal ration
  vtkGetMacro(TemporalRatio, double);

  //!\brief Set the model parameter which must be of type vtkTAG2ERothCModelParameter
  //! This XML model parameter describes the constant values of the RothC computation
  //! the input data.
  void SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter);

protected:
  vtkTAG2ERothCModel();
  ~vtkTAG2ERothCModel();

  virtual int RequestData(vtkInformation *, vtkInformationVector **,
      vtkInformationVector *);
  virtual int FillInputPortInformation(int port, vtkInformation* info);
  virtual int FillOutputPortInformation(int port, vtkInformation* info);
  //! \brief Initiate the internal CPools arrays in case
  //! there where not provided in the input
  virtual void CreateCPools(vtkPolyData *input);

  vtkTAG2ERothCModelParameter *RothCModelParameter; // Do not delete in destructor
  vtkPolyData *CPools;
  int CPoolsInitiated; // Checks if the pools are initiated
  int EquilibriumRun;
  int AddCPoolsToOutput; // Add internal C pools to the output dataset
  double TemporalRatio; // 1/12 for months or 1/365 for days

private:
  vtkTAG2ERothCModel(const vtkTAG2ERothCModel& orig); // Not implemented.
  void operator=(const vtkTAG2ERothCModel&); // Not implemented.
};

#endif	/* vtkTAG2ERothCModel_H */

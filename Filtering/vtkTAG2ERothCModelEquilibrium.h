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
 * \brief RothC equilibirum
 */

#ifndef vtkTAG2ERothCModelEquilibrium_H
#define	vtkTAG2ERothCModelEquilibrium_H

#include <vtkPolyData.h>
#include "vtkTAG2ERothCDefines.h"
#include "vtkTAG2EAbstractCalibratableModel.h"
#include "vtkTAG2ERothCModelParameter.h"
#include <vector>

class vtkTAG2ERothCModelEquilibrium: public vtkTAG2EAbstractCalibratableModel
{
public:
vtkTypeRevisionMacro(vtkTAG2ERothCModelEquilibrium, vtkTAG2EAbstractCalibratableModel)
  ;

  void PrintSelf(ostream& os, vtkIndent indent);
  static vtkTAG2ERothCModelEquilibrium *New();

  virtual double GetModelAssessmentFactor()
  {
    return 1.0;
  }

  //! \brief Set this true if the internal pools should be added to the output
  //!  dataset
  vtkSetMacro(AddCPoolsToOutput, int);
  vtkGetMacro(AddCPoolsToOutput, int);
  vtkBooleanMacro(AddCPoolsToOutput, int);

  //! \brief Set the number of years to be simulated for equilibrium run
  //! The number of sub-year runs are dependent from the chosen temporal resolution
  vtkSetMacro(NumberOfYears, int);
  vtkGetMacro(NumberOfYears, int);

  //! \brief Set the temporal resolution
  //!
  //! It is expected that the number of datasets in the input
  //! will be 12 for monthly and yearly resolution.
  //!
  //! In case of yearly resolution set this to 1
  //! In case of monthly resolution set this to 12.
  vtkSetMacro(TemporalResolution, int);
  //! \brief Get the temporal resolution
  vtkGetMacro(TemporalResolution, int);

  void SetTemporalResolutionToMonthly(){ this->TemporalResolution = ROTHC_MONTHLY;}
  void SetTemporalResolutionToYearly(){ this->TemporalResolution = ROTHC_YEARLY;}

  //!\brief Set the model parameter which must be of type vtkTAG2ERothCModelParameter
  //! This XML model parameter describes the constant values of the RothC computation
  //! the input data.
  void SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter);

protected:
  vtkTAG2ERothCModelEquilibrium();
  ~vtkTAG2ERothCModelEquilibrium();

  virtual int RequestData(vtkInformation *, vtkInformationVector **,
      vtkInformationVector *);
  virtual int FillInputPortInformation(int port, vtkInformation* info);
  virtual int FillOutputPortInformation(int port, vtkInformation* info);
  //! \brief Initiate the internal CPools arrays in case
  //! there where not provided in the input
  virtual void CreateCPools(vtkPolyData *input);
  virtual int ComputeResponses(vtkInformationVector **inputVector);

  vtkTAG2ERothCModelParameter *RothCModelParameter; // Do not delete in destructor
  vtkPolyData *CPools;
  int AddCPoolsToOutput; // Add internal C pools to the output dataset
  int TemporalResolution; // either 365 days, 12 months or 1 year
  int NumberOfYears;

  // Response arrays
  std::vector <std::vector<double>* > a;
  std::vector <std::vector<double>* > b;
  std::vector <std::vector<double>* > c;
  std::vector <std::vector<double>* > x;
  std::vector <std::vector<double>* > roots;
  std::vector <std::vector<double>* > surface;

private:
  vtkTAG2ERothCModelEquilibrium(const vtkTAG2ERothCModelEquilibrium& orig); // Not implemented.
  void operator=(const vtkTAG2ERothCModelEquilibrium&); // Not implemented.
};

#endif	/* vtkTAG2ERothCModelEquilibrium_H */

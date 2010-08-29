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
 * \author Soeren Gebbert
 * \author Rene Dechow
 *
 *
 * */


#ifndef __vtkTAG2EFreibauerN2OEstimation_h
#define __vtkTAG2EFreibauerN2OEstimation_h


#include "vtkTAG2EFilteringWin32Header.h"
#include "vtkThreadedImageAlgorithm.h"

class VTK_TAG2E_FILTERING_EXPORT vtkTAG2EFreibauerN2OEstimation : public vtkThreadedImageAlgorithm
{
public:
  static vtkTAG2EFreibauerN2OEstimation *New();
  vtkTypeRevisionMacro(vtkTAG2EFreibauerN2OEstimation,vtkThreadedImageAlgorithm);


  //! \brief Set the Nitrogen fertilization rate input
  virtual void SetNitrogenRate(vtkDataObject *in) { this->SetInput(0,in); }
  //! \brief Set the sand fraction input in percent
  virtual void SetSandFraction(vtkDataObject *in) { this->SetInput(1,in); }
  //! \brief Set the oranic carbon soil fraction input
  virtual void SetSoilOrganicCorbonate(vtkDataObject *in) { this->SetInput(2,in); }
  //! \brief Set the soil nitrogen fraction input
  virtual void SetSoilNitrogen(vtkDataObject *in) { this->SetInput(3,in); }
  //! \brief Set the crop type input
  virtual void SetCropType(vtkDataObject *in) { this->SetInput(4,in); }
  //! \brief Set the climate type input
  virtual void SetClimateType(vtkDataObject *in) { this->SetInput(5,in); }


  vtkSetMacro(NullValue, double);
  vtkGetMacro(NullValue, double);

protected:
  vtkTAG2EFreibauerN2OEstimation();
  ~vtkTAG2EFreibauerN2OEstimation() {};

  virtual int RequestInformation (vtkInformation *, 
                                  vtkInformationVector **,
                                  vtkInformationVector *);
  
  virtual void ThreadedRequestData(vtkInformation *request, 
                                   vtkInformationVector **inputVector, 
                                   vtkInformationVector *outputVector,
                                   vtkImageData ***inData, 
                                   vtkImageData **outData,
                                   int extent[6], int threadId);

  double NullValue;

private:
  vtkTAG2EFreibauerN2OEstimation(const vtkTAG2EFreibauerN2OEstimation&);  // Not implemented.
  void operator=(const vtkTAG2EFreibauerN2OEstimation&);  // Not implemented.
};

#endif




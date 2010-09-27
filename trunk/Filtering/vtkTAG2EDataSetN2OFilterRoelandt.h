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
 * \brief This class computes the annual emission of N2O in [kg /(ha a)] for
 * agricultural mineral soil in Europe using the annual fertilizer input, the
 * soil nitrogen content, the winter temperature, the spring temperatur as
 * well as the crop type and the annual precipitation. The computational approach is based on
 * emperical formulars from Roelandt.
 *
 * As input any vtkDataSet can be used including the input parameter as cell or
 * point data. The usage of categories for similiar cells/points
 * (image or polydata) can speed up the processing in case the number of
 * categories is smaller than the number cells/points. The N2O emission is only
 * computed for a single category and stored for each cell/point with this category.
 *
 * Cell data will be used as default. The resulting data set contains the structure
 * of the input data set and the resulting N2O emission in [kg /(ha a)].
 *
 * \author Soeren Gebbert
 * \author Rene Dechow
 *
 * \cite Controls and models for estimating direct nitrous oxide emissions from
 * temperate and sub-boreal agricultural mineral soils in Europe.
 * Annette Freibauer and Martin Kaltschmitt
 *
 * */

#ifndef __vtkTAG2EDataSetN2OFilterRoelandt_h
#define __vtkTAG2EDataSetN2OFilterRoelandt_h

#include <vtkDataSetAlgorithm.h>
#include "vtkTAG2EFilteringWin32Header.h"

class VTK_TAG2E_FILTERING_EXPORT vtkTAG2EDataSetN2OFilterRoelandt : public vtkDataSetAlgorithm
{
public:
  vtkTypeRevisionMacro(vtkTAG2EDataSetN2OFilterRoelandt,vtkDataSetAlgorithm);
  void PrintSelf(ostream& os, vtkIndent indent);
  static vtkTAG2EDataSetN2OFilterRoelandt *New();

  //!\brief The name of the array of annual fertilizer input in [(kg N )/(ha a)]
  vtkSetStringMacro(NitrogenRateArrayName);
  //!\brief The name of the spring temperature array
  vtkSetStringMacro(TempSpringArrayName);
  //!\brief The name of the winter temperature array
  vtkSetStringMacro(TempWinterArrayName);
  //!\brief The name of the array of annual precipitation
  vtkSetStringMacro(PrecipitationSumArrayName);
  //!\brief The name of the array of the crop type
  vtkSetStringMacro(CropTypeArrayName);
  //!\brief The name of the category array, which describes cells/points with identical
  //! data. This is used to speed up the computation in case the input data set
  //! has many cells/points but does not vary much in parameters (Like the multi polygon
  //! approach for grouping different but data identical areas)
  //! Categories must be integer values in range 0 .. n.
  vtkSetStringMacro(CategoryArrayName);


  //!\brief The name of the array of annual fertilizer input in [(kg N )/(ha a)]
  vtkGetStringMacro(NitrogenRateArrayName);
  //!\brief The name of the spring temperature array
  vtkGetStringMacro(TempSpringArrayName);
  //!\brief The name of the winter temperature array
  vtkGetStringMacro(TempWinterArrayName);
  //!\brief The name of the array of annual precipitation
  vtkGetStringMacro(PrecipitationSumArrayName);
  //!\brief The name of the array of the crop type
  vtkGetStringMacro(CropTypeArrayName);
  //!\brief The name of the category array, which describes cells/points with identical
  //! data. This is used to speed up the computation in case the input data set
  //! has many cells/points but does not vary much in parameters (Like the multi polygon
  //! approach for grouping different but data identical areas)
  vtkGetStringMacro(CategoryArrayName);

  //!\brief Use the point data arrays instead of the default cell data arrays
  vtkSetMacro(UsePointData, int);
  //!\brief Use the point data arrays instead of the default cell data arrays
  vtkGetMacro(UsePointData, int);
  //!\brief Use the point data arrays instead of the default cell data arrays
  vtkBooleanMacro(UsePointData, int);

  //!\brief The value which should be used as result for wrong category data
  vtkSetMacro(NullValue, double);
  //!\brief The value which should be used as result for wrong category data
  vtkGetMacro(NullValue, double);


  virtual void SetModeltypeToBest(){this->SetModelType(1);}
  virtual void SetModeltypeToMin(){this->SetModelType(2);}
  virtual void SetModeltypeToMax(){this->SetModelType(3);}

  //!\brief Which model type should be used, Best, Min or Max
  vtkGetMacro(ModelType, int);

protected:
  vtkTAG2EDataSetN2OFilterRoelandt();
  ~vtkTAG2EDataSetN2OFilterRoelandt() {};

  char *NitrogenRateArrayName;
  char *TempSpringArrayName;
  char *TempWinterArrayName;
  char *CropTypeArrayName;
  char *PrecipitationSumArrayName;
  char *CategoryArrayName;

  int ModelType;
  int UsePointData;
  double NullValue;

  //!\brief Which model type should be used, Best, Min or Max
  vtkSetMacro(ModelType, int);

  int RequestData(vtkInformation *, vtkInformationVector **, vtkInformationVector *);

private:
  vtkTAG2EDataSetN2OFilterRoelandt(const vtkTAG2EDataSetN2OFilterRoelandt&);  // Not implemented.
  void operator=(const vtkTAG2EDataSetN2OFilterRoelandt&);  // Not implemented.
};

#endif



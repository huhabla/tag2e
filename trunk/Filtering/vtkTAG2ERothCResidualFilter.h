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
 * \brief RothCResidualFilter
 *
 * This filter computes the surface and root residuals from input residuals.
 * Hence the input dataset must have a residuals cell data array.
 *
 * Based on the topological structure of the input dataset that must
 * be build up based on lines, the layer id (top == 0) and the cumulative
 * line lentgh are computed.
 *
 * ATTENTION: We need to implement a depth dependent
 * residual fraction for roots, see "A global analysis of root distributions for terrestrial biomes"
 * from Jackson et al 1996
 *
 * For now the residuals are divided by a fixed ratio from 0.5 and distributed
 * in the top layer only.
 *
 */

#ifndef vtkTAG2ETurcEPotModel_H
#define	vtkTAG2ETurcEPotModel_H

#include <vtkPolyData.h>
#include "vtkTAG2EAbstractCalibratableModel.h"

class vtkTAG2ERothCResidualFilter: public vtkTAG2EAbstractModel
{
public:
vtkTypeRevisionMacro(vtkTAG2ERothCResidualFilter, vtkTAG2EAbstractModel);

  void PrintSelf(ostream& os, vtkIndent indent);
  static vtkTAG2ERothCResidualFilter *New();

  //! \brief Set the time interval in days
  vtkSetMacro(TimeInterval, double);
  //! \brief Get the time interval in days
  vtkGetMacro(TimeInterval, double);

  //!\brief This model has no XML description yet
  void SetModelParameter(vtkTAG2EAbstractModelParameter* modelParameter){;}

protected:
  vtkTAG2ERothCResidualFilter();
  ~vtkTAG2ERothCResidualFilter();

  virtual int RequestData(vtkInformation *, vtkInformationVector **,
      vtkInformationVector *);
  virtual int FillInputPortInformation(int port, vtkInformation* info);
  virtual int FillOutputPortInformation(int port, vtkInformation* info);

  //! \brief Compute the line length of two points from the the input data set
  //! \param input The input data set
  //! \param pointIds The ids of the two points
  virtual double ComputeLineLength(vtkDataSet *input, vtkIdList *pointIds);

  //! \brief Compute the center point of two points from the input data set
  //! \param input The input data set
  //! \param pointIds The ids of the two points
  //! \param center The resulting coordinates, must have a size of 3 doubles
  virtual void ComputeCenterPoint(vtkDataSet *input,
                                  vtkIdList *pointIds,
                                  double *center);

  //! \brief Check the cell neighbors
  //!
  //! This method calls itself recursively for each cell neighbor
  //! of the cellId. The cell id and the computed center coordinate will be
  //! added to the corresponding arrays. The line length will be computed.
  //! Visited cells will be marked as checked in the checkIdArray.
  virtual bool CheckCellNeighbours(vtkDataSet *input,
                                    vtkIdType cellId,
                                    vtkDoubleArray *centerCoorArray,
                                    vtkIdTypeArray *cellIdArray,
                                    vtkUnsignedCharArray *checkIdArray,
                                    vtkDoubleArray *lineLengthArray,
                                    vtkDoubleArray *lineCenterArray);
  double TimeInterval;

private:
  vtkTAG2ERothCResidualFilter(const vtkTAG2ERothCResidualFilter& orig); // Not implemented.
  void operator=(const vtkTAG2ERothCResidualFilter&); // Not implemented.
};

#endif	/* vtkTAG2ETurcEPotModel_H */

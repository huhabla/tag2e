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
 * \brief In this class several alternative empirical N2O prediction algorithms
 * are implemented.
 *
 * Available are algorythms named by its inventors.
 * <ul>
 *   <li>Stehfest</li>
 *   <li>Bouwman</li>
 *   <li>Roelandt</li>
 *   <li>Freibauer</li>
 * </ul>
 *
 * \author Soeren Gebbert
 * \autho Rene Dechow
 *
 *
 * */

#ifndef __vtkTAG2EAlternativeN2OPredictionModules_h
#define __vtkTAG2EAlternativeN2OPredictionModules_h

#include <vtkObject.h>
#include "vtkTAG2ECommonWin32Header.h"


#define VTK_TAG2E_CROPTYPE_FALLOW 0
#define VTK_TAG2E_CROPTYPE_ROOTS 1
#define VTK_TAG2E_CROPTYPE_CEREALS 2
#define VTK_TAG2E_CROPTYPE_CEREALS_C 2
#define VTK_TAG2E_CROPTYPE_VEGETABLES 4
#define VTK_TAG2E_CROPTYPE_OTHER 5
#define VTK_TAG2E_CROPTYPE_GRASS  6
#define VTK_TAG2E_CROPTYPE_LEGUME  6

#define VTK_TAG2E_CLIMATETYPE_STEHFEST_CONTINENTAL 1
#define VTK_TAG2E_CLIMATETYPE_STEHFEST_OCEANIC 2
#define VTK_TAG2E_CLIMATETYPE_STEHFEST_TROPIC 3
#define VTK_TAG2E_CLIMATETYPE_STEHFEST_SUBTROPIC 4
#define VTK_TAG2E_CLIMATETYPE_STEHFEST_BOREAL 8

#define VTK_TAG2E_CLIMATETYPE_FREIBAUER_TWE 1
#define VTK_TAG2E_CLIMATETYPE_FREIBAUER_SUBBOREAL 2


class VTK_TAG2E_COMMON_EXPORT vtkTAG2EAlternativeN2OPredictionModules : public vtkObject
{
public:
  static  vtkTAG2EAlternativeN2OPredictionModules *New();
  vtkTypeRevisionMacro(vtkTAG2EAlternativeN2OPredictionModules,vtkObject);

  static double Bouwman(double N_rate);
  static double Freibauer(double N_rate, double sand, double soilC, double soilN, int croptype,int climate);
  static double RoelandtBest(double N_rate, double T_spring, double P_sum, double T_win, int croptype);
  static double RoelandtMin(double N_rate, double T_spring, double P_sum, double T_win, int croptype);
  static double RoelandtMax(double N_rate, double T_spring, double P_sum, double T_win, int croptype);
  static double Stehfest(double N_rate, double Corg, double silt, double clay, double pH, int croptype, int climate);

protected:
  vtkTAG2EAlternativeN2OPredictionModules();
  ~vtkTAG2EAlternativeN2OPredictionModules();

private:
  vtkTAG2EAlternativeN2OPredictionModules(const vtkTAG2EAlternativeN2OPredictionModules&);  // Not implemented.
  void operator=(const vtkTAG2EAlternativeN2OPredictionModules&);  // Not implemented.
};


#endif

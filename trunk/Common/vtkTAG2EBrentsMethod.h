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
 * \brief Brents Method of parabolic interpolation
 *
 * Here some Python example code of the method usage:
 *
 * @code
 *
 * # We search the root of the quadratic function x^2 which is 0.0
 *
 * brent = vtkTAG2EBrentsMethod()
 *
 * ax = -5.0 # min
 * bx =  4.0 # start value
 * cx =  5.0 # max
 *
 * target = 0.0 # This is the value we expect
 *
 * guess = bx*bx # Quadratuc function
 *
 * residuum = (target - guess) * (target - guess)
 *
 * brent.Init(ax, bx, cx, tol, residuum)
 *
 * for iter in range(20):
 *     brent.IsFinished(): # Check if its finished
 *         print "Brent break criteria reached, root value is", brent.Getx()
 *         break
 *
 *     x = brent.Fit()     # Get the best model fit
 *
 *     guess = x*x # Quadratic function
 *
 *     residuum = (target - guess) * (target - guess)
 *
 *     if residuum < 0.00001:
 *         print "Residuum reached, root value is", brent.Getx()
 *         break
 *
 *     brent.Evaluate(residuum) # Evaluate the residuum
 *
 * @endcode
 *
 * \author Soeren Gebbert
 * \autho Rene Dechow
 *
 *
 * */

#ifndef __vtkTAG2EBrentsMethod_h
#define __vtkTAG2EBrentsMethod_h

#include <vtkObject.h>
#include "vtkTAG2ECommonWin32Header.h"


class VTK_TAG2E_COMMON_EXPORT vtkTAG2EBrentsMethod : public vtkObject
{
public:
  static  vtkTAG2EBrentsMethod *New();
  vtkTypeRevisionMacro(vtkTAG2EBrentsMethod,vtkObject);

  vtkGetMacro(x, double);
  vtkGetMacro(fx, double);


  /**\brief the Init function. Calls this function once before the
   * best fit search should start.
   *
   * @param ax: The minimum abscissa value
   * @param bx: The start abscissa value (ax < bx < cx)
   * @param cx: The maximum abscissa value
   * @param tol: The break tolerance
   * @param fx: The model result of a single run with bx as start value
   *
   *
   */
  void Init(double ax, double bx, double cx, double tol, double fx);
  /**\brief Check if brents fishing criteria was reached
   *
   * @return true if reached, false if not
   */
  bool IsFinished();
  /**\brief Compute the best fit and return the best fit value to be used in the model run
   *
   * @return The best fit value to be used as model input
   */
  double Fit();
  /**\brief Evaluate the model result
   *
   * @param fx: The model result computed with the best fit value returned by Fit()
   */
  void Evaluate(double fx);

protected:
  vtkTAG2EBrentsMethod();
  ~vtkTAG2EBrentsMethod();
  void Reset();

  double a,b,d,e,etemp,fu,fv,fw,fx,p,q,r,tol1,tol2,u,v,w,x,xm,tol;

private:
  vtkTAG2EBrentsMethod(const vtkTAG2EBrentsMethod&);  // Not implemented.
  void operator=(const vtkTAG2EBrentsMethod&);  // Not implemented.
};


#endif

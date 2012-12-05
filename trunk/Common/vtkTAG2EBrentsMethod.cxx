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

#include <vtkObjectFactory.h>
#include "vtkTAG2EBrentsMethod.h"

#define ZEPS 0.001
#define CGOLD 0.3819660
#define SHIFT(a, b, c, d) (a)=(b); (b)=(c); (c)=(d);
#define SIGN(a,b) ((b) >= 0.0 ? fabs(a) : -fabs(a))

extern "C" {
#include <math.h>
}

vtkCxxRevisionMacro(vtkTAG2EBrentsMethod, "$Revision: 1.1 $");
vtkStandardNewMacro(vtkTAG2EBrentsMethod);

//----------------------------------------------------------------------------

vtkTAG2EBrentsMethod::vtkTAG2EBrentsMethod()
{
  this->Reset();
}

//----------------------------------------------------------------------------

vtkTAG2EBrentsMethod::~vtkTAG2EBrentsMethod()
{
  ;
}

void vtkTAG2EBrentsMethod::Reset()
{
  this->e = 0.0;
  this->etemp = 0.0;
  this->a = 0.0;
  this->b = 0.0;
  this->d = 0.0;
  this->x = 0.0;
  this->u = 0.0;
  this->v = 0.0;
  this->w = 0.0;
  this->xm = 0.0;
  this->fv = 0.0;
  this->fw = 0.0;
  this->fx = 0.0;
  this->fu = 0.0;
  this->p = 0.0;
  this->q = 0.0;
  this->r = 0.0;
  this->tol = 0.0;
  this->tol1 = 0.0;
  this->tol2 = 0.0;
}

//----------------------------------------------------------------------------

void vtkTAG2EBrentsMethod::Init(double ax, double bx, double cx, double _tol,
                                double _fx)
{
  this->Reset();
  a = (ax < cx ? ax : cx);
  b = (ax > cx ? ax : cx);

  x = w = v = bx;
  fx = fw = fv = _fx;
  tol = _tol;
}

//----------------------------------------------------------------------------

bool vtkTAG2EBrentsMethod::IsFinished()
{
  xm = 0.5 * (a + b);
  tol1 = tol * fabs(x) + ZEPS;
  tol2 = 2.0 * tol1;

  /*
  printf("Internal variable check\n");
  printf("x - xm: %g\n", this->x - this->xm);
  printf("v:..... %g\n", this->v);
  printf("fv:.... %g\n", this->fv);
  printf("w:..... %g\n", this->w);
  printf("fw:.... %g\n", this->fw);
  printf("x:..... %g\n", this->x);
  printf("fx:.... %g\n", this->fx);
  printf("u:..... %g\n", this->u);
  printf("fu:.... %g\n", this->fu);
  */

  if (fabs(x - xm) <= (tol2 - 0.5 * (b - a)))
    {
    printf("Brent finished:\n");
    return true;
    }
  return false;
}

//----------------------------------------------------------------------------

double vtkTAG2EBrentsMethod::Fit()
{
  if (fabs(e) > tol1)
    {
    r = (x - w) * (fx - fv);
    q = (x - v) * (fx - fw);
    p = (x - v) * q - (x - w) * r;
    q = 2.0 * (q - r);
    if (q > 0.0)
      p = -p;
    q = fabs(q);
    etemp = e;
    e = d;
    if (fabs(p) >= fabs(0.5 * q * etemp) || p <= q * (a - x)
        || p >= q * (b - x))
      d = CGOLD * (e = (x >= xm ? a - x : b - x));
    else
      {
      d = p / q;
      u = x + d;
      if (u - a < tol2 || b - u < tol2)
        d = SIGN(tol1,xm-x);
      }
    }
  else
    {
    d = CGOLD * (e = (x >= xm ? a - x : b - x));
    }
  u = (fabs(d) >= tol1 ? x + d : x + SIGN(tol1,d));
  return u;
}

//----------------------------------------------------------------------------

void vtkTAG2EBrentsMethod::Evaluate(double _fx)
{
  this->fu = _fx;

  if (fu <= fx)
    {
    if (u >= x)
      a = x;
    else
      b = x;
    SHIFT(v, w, x, u)
    SHIFT(fv, fw, fx, fu)
    }
  else
    {
    if (u < x)
      a = u;
    else
      b = u;
    if (fu <= fw || w == x)
      {
      v = w;
      w = u;
      fv = fw;
      fw = fu;
      }
    else if (fu <= fv || v == x || v == w)
      {
      v = u;
      fv = fu;
      }
    }
}

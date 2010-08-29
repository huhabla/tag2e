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



#ifndef __vtkTAG2EFILTERINGWin32Header_h
#define __vtkTAG2EFILTERINGWin32Header_h

#include <vtkTAG2EConfigure.h>

#if defined(WIN32) && !defined(VTK_TAG2E_LIBRARY_STATIC)
#if defined(vtkTAG2EFILTERING_EXPORTS)
#define VTK_TAG2E_FILTERING_EXPORT __declspec( dllexport )
#else
#define VTK_TAG2E_FILTERING_EXPORT __declspec( dllimport )
#endif
#else
#define VTK_TAG2E_FILTERING_EXPORT
#endif

#endif

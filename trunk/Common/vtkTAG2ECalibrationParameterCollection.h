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

#ifndef __vtkTAG2ECalibrationParameterCollection_h
#define __vtkTAG2ECalibrationParameterCollection_h

#include <vtkCollection.h>
#include "vtkTAG2EAbstractCalibrationParameter.h" // Needed for inline methods
#include "vtkTAG2ECommonWin32Header.h"

class VTK_TAG2E_COMMON_EXPORT vtkTAG2ECalibrationParameterCollection : public vtkCollection {
public:
    static vtkTAG2ECalibrationParameterCollection *New();
    vtkTypeRevisionMacro(vtkTAG2ECalibrationParameterCollection, vtkCollection);

    // Description:
    // Add a dataarray to the list.

    void AddItem(vtkTAG2EAbstractCalibrationParameter *ds) {
        this->vtkCollection::AddItem(ds);
    }

    // Description:
    // Get the next object in the list.

    vtkTAG2EAbstractCalibrationParameter *GetNextItem() {
        return static_cast<vtkTAG2EAbstractCalibrationParameter *> (this->GetNextItemAsObject());
    };

    // Description:
    // Get the ith object in the list.

    vtkTAG2EAbstractCalibrationParameter *GetItem(int i) {
        return static_cast<vtkTAG2EAbstractCalibrationParameter *> (this->GetItemAsObject(i));
    };

    //BTX
    // Description: 
    // Reentrant safe way to get an object in a collection. Just pass the
    // same cookie back and forth. 

    vtkTAG2EAbstractCalibrationParameter *GetNextDataArray(vtkCollectionSimpleIterator &cookie) {
        return static_cast<vtkTAG2EAbstractCalibrationParameter *> (this->GetNextItemAsObject(cookie));
    };
    //ETX

protected:

    vtkTAG2ECalibrationParameterCollection() {
    };

    ~vtkTAG2ECalibrationParameterCollection() {
    };


private:
    // hide the standard AddItem from the user and the compiler.

    void AddItem(vtkObject *o) {
        this->vtkCollection::AddItem(o);
    };

private:
    vtkTAG2ECalibrationParameterCollection(const vtkTAG2ECalibrationParameterCollection&); // Not implemented.
    void operator=(const vtkTAG2ECalibrationParameterCollection&); // Not implemented.
};


#endif

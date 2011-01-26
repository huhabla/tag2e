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

#ifndef __vtkTAG2EModelParameterCollection_h
#define __vtkTAG2EModelParameterCollection_h

#include <vtkCollection.h>
#include "vtkTAG2EAbstractModelParameter.h" // Needed for inline methods
#include "vtkTAG2ECommonWin32Header.h"

class VTK_TAG2E_COMMON_EXPORT vtkTAG2EModelParameterCollection : public vtkCollection {
public:
    static vtkTAG2EModelParameterCollection *New();
    vtkTypeRevisionMacro(vtkTAG2EModelParameterCollection, vtkCollection);

    // Description:
    // Add a dataarray to the list.

    void AddItem(vtkTAG2EAbstractModelParameter *ds) {
        this->vtkCollection::AddItem(ds);
    }

    // Description:
    // Get the next object in the list.

    vtkTAG2EAbstractModelParameter *GetNextItem() {
        return static_cast<vtkTAG2EAbstractModelParameter *> (this->GetNextItemAsObject());
    };

    // Description:
    // Get the ith object in the list.

    vtkTAG2EAbstractModelParameter *GetItem(int i) {
        return static_cast<vtkTAG2EAbstractModelParameter *> (this->GetItemAsObject(i));
    };

    //BTX
    // Description: 
    // Reentrant safe way to get an object in a collection. Just pass the
    // same cookie back and forth. 

    vtkTAG2EAbstractModelParameter *GetNextDataArray(vtkCollectionSimpleIterator &cookie) {
        return static_cast<vtkTAG2EAbstractModelParameter *> (this->GetNextItemAsObject(cookie));
    };
    //ETX

protected:

    vtkTAG2EModelParameterCollection() {
    };

    ~vtkTAG2EModelParameterCollection() {
    };


private:
    // hide the standard AddItem from the user and the compiler.

    void AddItem(vtkObject *o) {
        this->vtkCollection::AddItem(o);
    };

private:
    vtkTAG2EModelParameterCollection(const vtkTAG2EModelParameterCollection&); // Not implemented.
    void operator=(const vtkTAG2EModelParameterCollection&); // Not implemented.
};


#endif

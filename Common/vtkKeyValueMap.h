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
#ifndef VTKKEYVALUEMAP_H
#define	VTKKEYVALUEMAP_H
#include "vtkTAG2ECommonWin32Header.h"
#include <vtkObject.h>
#include <map>
#include <vector>

class VTK_TAG2E_COMMON_EXPORT vtkKeyValueMap : public vtkObject {
public:
    vtkTypeRevisionMacro(vtkKeyValueMap, vtkObject);

    void PrintSelf(ostream& os, vtkIndent indent) ;
    
    static vtkKeyValueMap *New();

    void Add(const char* key, double value) {
        this->KeyVals[key] = value;
    }

    void Remove(const char* key) {
        this->KeyVals.erase(key);
    }

    const char*GetKey(unsigned int idx);

    double GetValue(unsigned int idx);

    double GetValue(const char* key) {
        return this->KeyVals[key];
    }

    int GetNumberOfKeys() {
        return this->KeyVals.size();
    }

    bool HasKey(const char* key) {
        (this->KeyVals.find(key) != this->KeyVals.end() ? true : false);
    }

    void Clear() {
        this->KeyVals.clear();
    }
    
    // For internal use
    //BTX
    const std::map<const char *, double> &GetInternalMap(){return this->KeyVals;}
    //ETX

protected:

    vtkKeyValueMap() {
        ;
    }

    virtual ~vtkKeyValueMap() {
        ;
    }

    //BTX
    std::map<const char *, double> KeyVals;
    //ETX
    
private:
    vtkKeyValueMap(const vtkKeyValueMap& orig); // Not implemented. 
    void operator=(const vtkKeyValueMap&); // Not implemented. 
};

#endif	/* VTKKEYVALUEMAP_H */


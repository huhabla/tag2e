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
 * soil nitrogen content, the sand content, the soil organic carbon content as
 * well as the climate and crop type. The computational approach is based on
 * emperical formulars from Freibauer und Kaltschmitt which where derived
 * using stepwise multivariate linear regression analysis.
 *
 * As input vtkImageData is needed. Each vtkImageData must be of the same data type.
 * The computation is multi threaded. The number of threads which should be used for
 * computation can be set.
 *
 * Cell data will be used as default. The resulting image data contains the
 * resulting N2O emission in [kg /(ha a)].
 *
 * \author Soeren Gebbert
 * \author Rene Dechow
 *
 * \cite Controls and models for estimating direct nitrous oxide emissions from
 * temperate and sub-boreal agricultural mineral soils in Europe.
 * Annette Freibauer and Martin Kaltschmitt
 *
 *
 * */


#ifndef __vtkTAG2EImageDataN2OFilterFreibauer_h
#define __vtkTAG2EImageDataN2OFilterFreibauer_h


#include "vtkTAG2EFilteringWin32Header.h"
#include "vtkThreadedImageAlgorithm.h"
#include "vtkTAG2EAlternativeN2OPredictionModules.h"

class VTK_TAG2E_FILTERING_EXPORT vtkTAG2EImageDataN2OFilterFreibauer : public vtkThreadedImageAlgorithm {
public:
    static vtkTAG2EImageDataN2OFilterFreibauer *New();
    vtkTypeRevisionMacro(vtkTAG2EImageDataN2OFilterFreibauer, vtkThreadedImageAlgorithm);

    //!\brief The input of annual fertilizer input in [(kg N )/(ha a)]

    virtual void SetNitrogenRate(vtkDataObject *in) {
        this->SetInput(0, in);
    }
    //!\brief The input of sand content in top soil, in [%] of soil weight

    virtual void SetSandFraction(vtkDataObject *in) {
        this->SetInput(1, in);
    }
    //!\brief The input of soil organic carbon content in top soil in [%] of soil weight

    virtual void SetSoilOrganicCarbon(vtkDataObject *in) {
        this->SetInput(2, in);
    }
    //!\brief The input of total soil nitrogen content in [%] of soil weight

    virtual void SetSoilNitrogen(vtkDataObject *in) {
        this->SetInput(3, in);
    }

    //!\brief Set the climate type to sub-boreal

    void SetClimateTypeToSubBoreal() {
        this->SetClimateType(VTK_TAG2E_CLIMATETYPE_FREIBAUER_SUBBOREAL);
    }
    //!\brief Set the climate type to temperate western europe (this is the default)

    void SetClimateTypeToTemperate() {
        this->SetClimateType(VTK_TAG2E_CLIMATETYPE_FREIBAUER_TWE);
    }

    //!\brief Set the croptype to grass (this is the default)

    void SetCropTypeToGrass() {
        this->SetCropType(VTK_TAG2E_CROPTYPE_GRASS);
    }
    //!\brief Set the croptype to other than grass

    void SetCropTypeToOther() {
        this->SetCropType(VTK_TAG2E_CROPTYPE_OTHER);
    }

    vtkSetMacro(NullValue, double);
    vtkGetMacro(NullValue, double);

protected:
    vtkTAG2EImageDataN2OFilterFreibauer();

    ~vtkTAG2EImageDataN2OFilterFreibauer() {
    };

    double NullValue;
    int ClimateType;
    int CropType;
    vtkSetMacro(ClimateType, int);
    vtkSetMacro(CropType, int);

    virtual int RequestInformation(vtkInformation *,
            vtkInformationVector **,
            vtkInformationVector *);

    virtual void ThreadedRequestData(vtkInformation *request,
            vtkInformationVector **inputVector,
            vtkInformationVector *outputVector,
            vtkImageData ***inData,
            vtkImageData **outData,
            int extent[6], int threadId);


private:
    vtkTAG2EImageDataN2OFilterFreibauer(const vtkTAG2EImageDataN2OFilterFreibauer&); // Not implemented.
    void operator=(const vtkTAG2EImageDataN2OFilterFreibauer&); // Not implemented.
};

#endif

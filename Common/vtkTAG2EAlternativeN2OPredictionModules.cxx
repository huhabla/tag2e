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
#include "vtkTAG2EAlternativeN2OPredictionModules.h"
#include "vtkTAG2EDefines.h"

extern "C" {
#include <math.h>
}

vtkCxxRevisionMacro(vtkTAG2EAlternativeN2OPredictionModules, "$Revision: 1.1 $");
vtkStandardNewMacro(vtkTAG2EAlternativeN2OPredictionModules);

//----------------------------------------------------------------------------

vtkTAG2EAlternativeN2OPredictionModules::vtkTAG2EAlternativeN2OPredictionModules()
{
    ;
}

//----------------------------------------------------------------------------

vtkTAG2EAlternativeN2OPredictionModules::~vtkTAG2EAlternativeN2OPredictionModules()
{
    ;
}

//----------------------------------------------------------------------------

double vtkTAG2EAlternativeN2OPredictionModules::Stehfest(double N_rate, double Corg, double silt, double clay, double pH, int croptype,int climate) {
    int texture;
    double f, f1;
    double sumCorg = 0, sumN = 0, sumpH = 0, sumtexture = 0, sumclimate = 0, sumcroptype = 0;

    // Compute texture class
    if (clay <= 20)
        texture = 1;
    if (clay > 45)
        texture = 3;
    if ((clay > 20) && (clay <= 45)) {
        if (clay > 30) {
            texture = 2;
        } else {
            if ((silt / (100 - clay)) <= 0.4) {
                texture = 1;
            } else {
                texture = 2;
            }
        }
    }
    // Berechne fertilization rate
    sumN = 0.0038 * N_rate;
    // sum Corg
    if (Corg < 1)
        sumCorg = 0;
    if ((Corg >= 1) && (Corg <= 3))
        sumCorg = 0.0526;
    if (Corg > 3) {
        if (Corg > 9998)
            sumCorg = 0.0526;
        else 
            sumCorg = 0.6334;
    }
    // sum pH
    if (pH < 5.5)
        sumpH = 0;
    if ((pH >= 5.5) && (pH <= 7.3))
        sumpH = -0.0693;
    if (pH > 7.3) {
        if (pH > 9998)
            sumpH = -0.0693;
        else
            sumpH = -0.4836;
    }

    //sumtexture
    if (texture == 1)
        sumtexture = 0;
    else if (texture == 2)
        sumtexture = -0.1528;
    else if (texture == 3) {
        if (texture > 9998)
            sumtexture = 0;
        else
            sumtexture = 0.4312;
    }
    //sumclimate
    if (climate == 1)
        sumclimate = 0;
    else if (climate == 2)
        sumclimate = 0.0226;
    if (climate == 4)
        sumclimate = 0.6117;
    if (climate == 8)
        sumclimate = 0; //boreal is assumed to behave like continental
    //sumcroptype
    if ((croptype == VTK_TAG2E_CROPTYPE_CEREALS) || (croptype == VTK_TAG2E_CROPTYPE_CEREALS_C))
        sumcroptype = 0; //cereals
    if (croptype == VTK_TAG2E_CROPTYPE_GRASS)
        sumcroptype = -0.3502; //grass
    if (croptype == VTK_TAG2E_CROPTYPE_LEGUME)
        sumcroptype = 0.3783; //legume
    if ((croptype == VTK_TAG2E_CROPTYPE_OTHER) || (croptype == VTK_TAG2E_CROPTYPE_ROOTS) || (croptype == VTK_TAG2E_CROPTYPE_VEGETABLES))
        sumcroptype = 0.4420; //other
    //if(croptype==)sumcroptype=-0.885;//rice
    if (croptype == VTK_TAG2E_CROPTYPE_FELLOW)
        sumcroptype = 0.587;
    //n2o emission
    f1 = sumN + sumpH + sumtexture + sumclimate + sumcroptype + 1.991 - 1.516;
    f = exp(f1);
    return f;
}

//----------------------------------------------------------------------------

double vtkTAG2EAlternativeN2OPredictionModules::Bouwman(double N_rate) {
    double f;
    f = 1 + 0.0125 * N_rate;
    return f;
}

//----------------------------------------------------------------------------

double vtkTAG2EAlternativeN2OPredictionModules::RoelandtBest(double N_rate, double T_spring, double P_sum, double T_win, int croptype) {
    double f;

    if (croptype != VTK_TAG2E_CROPTYPE_GRASS) {
        f = -8.183 + 0.7511 * T_spring + 0.01444 * P_sum; //best case
    } else {
        f = exp(-0.5095 + 0.0028 * N_rate + 0.1245 * T_win); //best case
    }
    return f;
}

//----------------------------------------------------------------------------

double vtkTAG2EAlternativeN2OPredictionModules::RoelandtMin(double N_rate, double T_spring, double P_sum, double T_win, int croptype) {
    double f;

    if (croptype != VTK_TAG2E_CROPTYPE_GRASS) {
        f=-8.183-5.273+(0.7511-0.231)*T_spring+(0.01444-0.0188)*P_sum;// minimum
    } else {
        f=exp(-0.5095-0.4038+(0.0028-0.0019)*N_rate+(0.1245-0.0929)*T_win);//min
    }
    return f;
}

//----------------------------------------------------------------------------

double vtkTAG2EAlternativeN2OPredictionModules::RoelandtMax(double N_rate, double T_spring, double P_sum, double T_win, int croptype) {
    double f;

    if (croptype != VTK_TAG2E_CROPTYPE_GRASS) {
        f=-8.183+5.273+(0.7511+0.231)*T_spring+(0.01444+0.0188)*P_sum;// maximum
    } else {
        f=exp(-0.5095+0.4038+(0.0028+0.0019)*N_rate+(0.1245+0.0929)*T_win);//min
    }
    return f;
}

//----------------------------------------------------------------------------

double vtkTAG2EAlternativeN2OPredictionModules::Freibauer(double N_rate, double sand, double soilC, double soilN, int croptype,int climate) {
    double f;
    if (croptype != VTK_TAG2E_CROPTYPE_GRASS) {
        if ((climate != 1) && (climate != 8)) {
            if (soilC > 9998)
                soilC = 1.2;
            if (sand > 9998)
                sand = 40;
            f = 0.6 + 0.002 * N_rate + 1.27 * soilC - 0.024 * sand;
        } else {
            if (soilN > 9998) {
                soilN = 0.12;
            }
            f = -1.3 + 0.033 * N_rate + 28 * soilN;
        }
    } else {
        f = 2.4 + 0.015 * N_rate;
    }
    return f;
}


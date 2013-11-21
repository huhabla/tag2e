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
 * \brief RothC Array names
 */

#ifndef vtkTAG2ERothCDefines_H
#define	vtkTAG2ERothCDefines_H

// Temporal resolution
#define ROTHC_DAILY 365
#define ROTHC_MONTHLY 12
#define ROTHC_YEARLY 1

// Names of the pool arrays
#define ROTHC_POOL_NAME_DPM "DPM"
#define ROTHC_POOL_NAME_RPM "RPM"
#define ROTHC_POOL_NAME_HUM "HUM"
#define ROTHC_POOL_NAME_BIO "BIO"
#define ROTHC_POOL_NAME_IOM "IOM"

// Names of the input arrays
#define ROTHC_INPUT_NAME_LAYER             "Layer"
#define ROTHC_INPUT_NAME_CLAY              "Clay"
#define ROTHC_INPUT_NAME_MEAN_TEMPERATURE  "MeanTemperature" // air
#define ROTHC_INPUT_NAME_SOILCOVER         "SoilCover"
#define ROTHC_INPUT_NAME_RESIDUALS         "Residuals"
#define ROTHC_INPUT_NAME_RESIDUALS_ROOTS   "ResidualsRoots"
#define ROTHC_INPUT_NAME_RESIDUALS_SURFACE "ResidualsSurface"
#define ROTHC_INPUT_NAME_SHOOT_ID          "ShootID"
#define ROTHC_INPUT_NAME_ROOT_ID           "RootID"
#define ROTHC_INPUT_NAME_FERTILIZER_ID     "FertilizerID"
#define ROTHC_INPUT_NAME_SOIL_MOISTURE     "SoilMoisture" // Usable soil moisture
#define ROTHC_INPUT_NAME_USABLE_FIELD_CAPACITY    "UsableFieldCapacity"
#define ROTHC_INPUT_NAME_FERTILIZER_CARBON "FertilizerCarbon"
#define ROTHC_INPUT_NAME_INITIAL_CARBON    "InitialCarbon"
#define ROTHC_INPUT_NAME_ETPOT             "ETpot" // Evapotranspiration
#define ROTHC_INPUT_NAME_PRECIPITATION     "Precipitation"
#define ROTHC_INPUT_NAME_USABLE_WATER_CONTENT  "UsableWaterContent" // The water content of the time step before this run
#define ROTHC_INPUT_NAME_GLOBAL_RADIATION  "GlobalRadiation" // [mJ/(m^2 * d)] air
#define ROTHC_INPUT_NAME_LINE_LENGTH       "LineLength"
#define ROTHC_INPUT_NAME_CUMULATIVE_LINE_LENGTH "CumulativeLineLength"
#define ROTHC_INPUT_NAME_LINE_CENTER       "LineCenter"
#define ROTHC_INPUT_NAME_ROOT_DEPTH        "RootDepth"
#define ROTHC_OUTPUT_NAME_SOIL_CARBON      "SoilCarbon"

#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))

#endif	/* vtkTAG2ERothCDefines_H */

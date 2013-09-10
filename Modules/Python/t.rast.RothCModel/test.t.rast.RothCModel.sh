#!/bin/sh
# Aggregate a dataset by a second one

# We need to set a specific region in the
# @preprocess step of this test. 
# The region setting should work for UTM and LL test locations
#g.region s=0 n=80 w=0 e=120 b=0 t=50 res=0.25 res3=10 -p3
g.region s=0 n=80 w=0 e=120 b=0 t=50 res=10 res3=10 -p3

temp=`g.tempfile pid=1 -d` 
prec=`g.tempfile pid=2 -d` 
radi=`g.tempfile pid=3 -d` 
soil=`g.tempfile pid=4 -d` 

# TEMPERATURE

count=0
while [ ${count} -lt 12 ] ; do 
    name="temp_${count}"
    echo "${name}" >> "${temp}"
    r.mapcalc --o expr="${name} = rand(1,20)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=temperature_RothC \
    title="RothC mean temperature" descr="RothC mean temperature"
t.register --o -i type=rast input=temperature_RothC file="${temp}" \
    start=2000-01-01 increment="1 months"

# PRECIPITATION

count=0
while [ ${count} -lt 12 ] ; do 
    name="prec_${count}"
    echo "${name}" >> "${prec}"
    r.mapcalc --o expr="${name} = rand(1,100)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=precipitation_RothC \
    title="RothC precipitation" descr="RothC precipitation"
t.register --o -i type=rast input=precipitation_RothC file="${prec}" \
    start=2000-01-01 increment="1 months"

# GLOBAL RADIATION

count=0
while [ ${count} -lt 12 ] ; do 
    name="radi_${count}"
    echo "${name}" >> "${radi}"
    r.mapcalc --o expr="${name} = rand(10,400)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=radiation_RothC \
    title="RothC radiation" descr="RothC radiation"
t.register --o -i type=rast input=radiation_RothC file="${radi}" \
    start=2000-01-01 increment="1 months"

# SOIL COVER
count=0
while [ ${count} -lt 12 ] ; do 
    name="soil_${count}"
    echo "${name}" >> "${soil}"
    r.mapcalc --o expr="${name} = rand(0,1)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=soilCover_RothC \
    title="RothC soil cover" descr="RothC soil cover"
t.register --o -i type=rast input=soilCover_RothC file="${soil}" \
    start=2000-01-01 increment="1 months"

# RESIDUALS
r.mapcalc --o expr="residuals = rand(1,50)"

t.create --o type=strds temporaltype=absolute output=residuals_RothC \
    title="Residuals" descr="Residuals"
t.register --o -i type=rast input=residuals_RothC map=residuals \
    start=2000-08-01 increment="1 months"

# FERTILIZER
r.mapcalc --o expr="fertilizer_1 = rand(1,50)"
r.mapcalc --o expr="fertilizer_2 = rand(1,50)"

t.create --o type=strds temporaltype=absolute output=fertilizer_RothC \
    title="Fertilizer" descr="Fertilizer"
t.register --o -i type=rast input=fertilizer_RothC map=fertilizer_1 \
    start=2000-04-05 increment="1 day"
t.register --o -i type=rast input=fertilizer_RothC map=fertilizer_2 \
    start=2000-06-13 increment="1 day"

# FERTILIZER and PLANT ID
r.mapcalc --o expr="fertId_1  = rand(0,5)"
r.mapcalc --o expr="fertId_2  = rand(0,5)"
r.mapcalc --o expr="plantId_1 = rand(0,2)"
r.mapcalc --o expr="plantId_2 = rand(0,2)"

t.create --o type=strds temporaltype=absolute output=fertId_RothC \
    title="FertId" descr="FertId"
t.register --o -i type=rast input=fertId_RothC map=fertId_1 \
    start=2000-04-05 increment="1 day"
t.register --o -i type=rast input=fertId_RothC map=fertId_2 \
    start=2000-06-13 increment="1 day"

t.create --o type=strds temporaltype=absolute output=plantId_RothC \
    title="PlantId" descr="PlantId"
t.register --o -i type=rast input=plantId_RothC map=plantId_1 \
    start=2000-04-05 increment="1 day"
t.register --o -i type=rast input=plantId_RothC map=plantId_2 \
    start=2000-06-13 increment="1 day"


# Several needed maps
r.mapcalc --o expr="clay = rand(1,50)"
r.mapcalc --o expr="dpm = 25.0"
r.mapcalc --o expr="rpm = 5.0"
r.mapcalc --o expr="hum = 2.0"
r.mapcalc --o expr="bio = 2.0"
r.mapcalc --o expr="iom = 2.0"

# The @test
time t.rast.RothCModel --o temperature=temperature_RothC \
    precipitation=precipitation_RothC radiation=radiation_RothC \
    soilcover=soilCover_RothC claycontent=clay \
    residuals=residuals_RothC base=soc fertilizer=fertilizer_RothC \
    plantid=plantId_RothC fertid=fertId_RothC \
    dpm=dpm rpm=rpm hum=hum bio=bio iom=iom soc=soc_RothC \
    param=CalibrationXML/RothCCalibration1.xml

t.info soc_RothC
t.rast.list input=soc_RothC columns=name,start_time,min,max

# @postprocess
#t.remove type=strds input=temperature_RothC,precipitation_RothC,radiation_RothC,soilCover_RothC,residuals_RothC,soc_RothC
#t.unregister type=rast file="${temp}"
#for name in `cat "${temp}"` ; do
#    g.remove rast=${name}
#done
#t.unregister type=rast file="${prec}"
#for name in `cat "${prec}"` ; do
#    g.remove rast=${name}
#done
#t.unregister type=rast file="${radi}"
#for name in `cat "${radi}"` ; do
#    g.remove rast=${name}
#done
#t.unregister type=rast file="${soil}"
#for name in `cat "${soil}"` ; do
#    g.remove rast=${name}
#done
#g.remove rast=soc,dpm,rpm,hum,bio,iom,residuals
#g.mremove -f rast=soc*

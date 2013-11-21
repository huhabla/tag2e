#!/bin/sh
# Aggregate a dataset by a second one

# We need to set a specific region in the
# @preprocess step of this test. 
# The region setting should work for UTM and LL test locations
#g.region s=0 n=80 w=0 e=120 b=0 t=50 res=0.25 res3=10 -p3
g.region s=0 n=80 w=0 e=120 b=0 t=50 res=0.25 res3=10 -p3

temp=`g.tempfile pid=1 -d` 
prec=`g.tempfile pid=2 -d` 
radi=`g.tempfile pid=3 -d` 
soil=`g.tempfile pid=4 -d` 

# TEMPERATURE
NUMBER_OF_MONTHS=12

count=0
while [ ${count} -lt ${NUMBER_OF_MONTHS} ] ; do 
    name="temp_${count}"
    echo "${name}" >> "${temp}"
    r.mapcalc --o expr="${name} = rand(1,20)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=temperature \
    title="RothC mean temperature" descr="RothC mean temperature"
t.register --o -i type=rast input=temperature file="${temp}" \
    start=2000-01-01 increment="1 months"

# PRECIPITATION

count=0
while [ ${count} -lt ${NUMBER_OF_MONTHS} ] ; do 
    name="prec_${count}"
    echo "${name}" >> "${prec}"
    r.mapcalc --o expr="${name} = rand(1,100)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=precipitation \
    title="RothC precipitation" descr="RothC precipitation"
t.register --o -i type=rast input=precipitation file="${prec}" \
    start=2000-01-01 increment="1 months"

# GLOBAL RADIATION

count=0
while [ ${count} -lt ${NUMBER_OF_MONTHS} ] ; do 
    name="radi_${count}"
    echo "${name}" >> "${radi}"
    r.mapcalc --o expr="${name} = rand(10,400)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=radiation \
    title="RothC radiation" descr="RothC radiation"
t.register --o -i type=rast input=radiation file="${radi}" \
    start=2000-01-01 increment="1 months"

# SOIL COVER
count=0
while [ ${count} -lt ${NUMBER_OF_MONTHS} ] ; do 
    name="soil_${count}"
    echo "${name}" >> "${soil}"
    r.mapcalc --o expr="${name} = rand(0,1)"
    count=`expr ${count} + 1`
done

t.create --o type=strds temporaltype=absolute output=soilCover \
    title="RothC soil cover" descr="RothC soil cover"
t.register --o -i type=rast input=soilCover file="${soil}" \
    start=2000-01-01 increment="1 months"

# RESIDUALS
r.mapcalc --o expr="residuals = rand(1,50)"

t.create --o type=strds temporaltype=absolute output=residuals \
    title="Residuals" descr="Residuals"
t.register --o -i type=rast input=residuals map=residuals \
    start=2000-08-01 increment="1 months"

# FERTILIZER
r.mapcalc --o expr="fertilizer_1 = rand(1,50)"
r.mapcalc --o expr="fertilizer_2 = rand(1,50)"

t.create --o type=strds temporaltype=absolute output=fertilizer \
    title="Fertilizer" descr="Fertilizer"
t.register --o -i type=rast input=fertilizer map=fertilizer_1 \
    start=2000-04-05 increment="1 day"
t.register --o -i type=rast input=fertilizer map=fertilizer_2 \
    start=2000-06-13 increment="1 day"

# FERTILIZER and PLANT ID
r.mapcalc --o expr="fertId_1  = rand(0,0)"
r.mapcalc --o expr="fertId_2  = rand(0,0)"
r.mapcalc --o expr="shootId_1 = rand(0,0)"
r.mapcalc --o expr="shootId_2 = rand(0,0)"
r.mapcalc --o expr="rootId_1 = rand(0,0)"
r.mapcalc --o expr="rootId_2 = rand(0,0)"

t.create --o type=strds temporaltype=absolute output=fertId \
    title="FertId" descr="FertId"
t.register --o -i type=rast input=fertId map=fertId_1 \
    start=2000-04-05 increment="1 day"
t.register --o -i type=rast input=fertId map=fertId_2 \
    start=2000-06-13 increment="1 day"

t.create --o type=strds temporaltype=absolute output=shootId \
    title="ShootId" descr="ShootId"
t.register --o -i type=rast input=shootId map=shootId_1 \
    start=2000-04-05 increment="1 day"
t.register --o -i type=rast input=shootId map=shootId_2 \
    start=2000-06-13 increment="1 day"

t.create --o type=strds temporaltype=absolute output=rootId \
    title="RootId" descr="RootId"
t.register --o -i type=rast input=rootId map=rootId_1 \
    start=2000-04-05 increment="1 day"
t.register --o -i type=rast input=rootId map=rootId_2 \
    start=2000-06-13 increment="1 day"

# Several needed maps
r.mapcalc --o expr="clay = rand(1,50)"
r.mapcalc --o expr="dpm = 25.0"
r.mapcalc --o expr="rpm = 5.0"
r.mapcalc --o expr="hum = 2.0"
r.mapcalc --o expr="bio = 2.0"
r.mapcalc --o expr="iom = 2.0"

# The @test
time t.rast.RothCModel --o temperature=temperature \
    precipitation=precipitation radiation=radiation \
    soilcover=soilCover claycontent=clay \
    residuals=residuals base=soc fertilizer=fertilizer \
    shootid=shootId rootid=rootId fertid=fertId \
    dpm=dpm rpm=rpm hum=hum bio=bio iom=iom soc=soc 
#    param=CalibrationXML/RothCCalibration1.xml

t.info soc
t.rast.list input=soc columns=name,start_time,min,max

# @postprocess
t.remove -rf type=strds input=temperature,precipitation,radiation,soilCover,residuals,soc
t.remove -rf type=strds input=fertId,rootId,shootId
g.remove rast=soc,dpm,rpm,hum,bio,iom,residuals

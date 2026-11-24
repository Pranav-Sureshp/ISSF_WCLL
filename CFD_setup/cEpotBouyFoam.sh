#!/bin/bash

ulimit -s unlimited

cores=96 #216

source  ~/.openfoam_v2206_profile

#blockMesh -region fluid inner outer 2>&1 | tee log.blockMesh

if [[ ! $cores -eq 1 ]]
then
#        decomposePar -allRegions 2>&1 | tee log.decompose
        mpirun -np $cores cEpotBuoyantFoam -parallel 2>&1 | tee log.cEpotBuoyantFoam
#       reconstructPar -allRegions 2>&1 | tee log.reconstructPar
else
        cEpotBuoyantFoam 2>&1 | tee log.cEpotBuoyantFoam
fi


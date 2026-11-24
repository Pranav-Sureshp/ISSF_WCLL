#!/bin/bash
ulimit -s unlimited

# source  ~/.openfoam_v2306_profile
source  ~/.openfoam_v2306_sapphire_hbm_profile

nproc=96

blockMesh 2>&1 | tee log.blockMesh
surfaceFeatureExtract 2>&1 | tee log.surfaceFeatureExtract
decomposePar  -copyZero  2>&1 | tee log.decomposePar

mpirun -np $nproc snappyHexMesh -parallel -overwrite 2>&1 | tee log.snappyHexMesh
mpirun -np $nproc splitMeshRegions -cellZones -parallel -overwrite 2>&1 | tee log.splitMeshRegion
mpirun -np $nproc checkMesh -parallel -allGeometry -allTopology  2>&1 | tee log.checkMesh

reconstructParMesh -constant -allRegions 2>&1 | tee log.reconstructParMesh


mpirun -np $nproc foamToVTK -parallel -faceSet lowQualityTetFaces
mpirun -np $nproc foamToVTK -parallel -faceSet warpedFaces
mpirun -np $nproc foamToVTK -parallel -cellSet underdeterminedCells
mpirun -np $nproc foamToVTK -parallel -pointSet nearPoints


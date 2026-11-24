#!/bin/bash
ulimit -s unlimited

# source  ~/.openfoam_v2306_profile
source  ~/.openfoam_v2306_sapphire_hbm_profile

nproc=96


mpirun -np $nproc foamToVTK -parallel -faceSet lowQualityTetFaces 
mpirun -np $nproc foamToVTK -parallel -faceSet warpedFaces  
mpirun -np $nproc foamToVTK -parallel -cellSet underdeterminedCells 
mpirun -np $nproc foamToVTK -parallel -pointSet nearPoints 


# ISSF_WCLL
# OpenFOAM Workflow: Parallel Meshing & Simulation Guide

This repository contains execution scripts and workflow instructions for parallel mesh generation using `snappyHexMesh` and running simulations with the custom solver `cEpotBuoyantFoam`.

---

## 📋 Table of Contents
- [Directory Structure & STL Placement](#-directory-structure--stl-placement)
- [Prerequisites & Environment](#-prerequisites--environment)
- [Workflow Step 1: Mesh Generation](#-workflow-step-1-mesh-generation)
- [Workflow Step 2: Running the Simulation](#-workflow-step-2-running-the-simulation)
- [Post-Processing & Quality Verification](#-post-processing--quality-verification)

---

## 📁 Directory Structure & STL Placement

OpenFOAM requires a specific directory structure. All geometry surface files (`.stl`) intended for `snappyHexMesh` **must be placed inside the `constant/triSurface/` directory**.

### Folder Hierarchy
```text
.
├── 0/                      # Initial and boundary conditions
├── constant/
│   ├── triSurface/         # 👈 PLACE YOUR STL FILES HERE
│   │   └── geometry.stl    # Surface geometry file(s)
│   ├── polyMesh/           # Generated base mesh (blockMesh output)
│   ├── g/
│   └── transportProperties
├── system/
│   ├── blockMeshDict
│   ├── snappyHexMeshDict
│   ├── surfaceFeatureExtractDict
│   ├── decomposeParDict
│   └── controlDict
├── mesh.sh                 # Automation script for meshing
└── run.sh                  # Automation script for solver execution
```

### STL Setup Instructions:
1. Copy your STL file(s) into `constant/triSurface/`:
   ```bash
   mkdir -p constant/triSurface
   cp /path/to/your_geometry.stl constant/triSurface/
   ```
2. Verify that the file name in `system/snappyHexMeshDict` matches your uploaded `.stl` file:
   ```foam
   geometry
   {
       geometry.stl
       {
           type triSurfaceMesh;
           file "geometry.stl";
       }
   }
   ```
3. Update `system/surfaceFeatureExtractDict` with the correct STL file name to ensure edge features are properly extracted.

---

## ⚙️ Prerequisites & Environment

* **OpenFOAM Version**: OpenFOAM v2206 (environment profile expected at `~/.openfoam_v2206_profile`).
* **MPI**: OpenMPI or compatible MPI installation configured for multi-core processing.
* **Stack Size Limit**: Both scripts automatically set `ulimit -s unlimited` to allow high stack memory usage needed during large mesh decomposition and matrix calculations.

---

## 🔨 Workflow Step 1: Mesh Generation

The meshing process is automated via `mesh.sh`. It creates the base mesh, extracts surface feature edges, decomposes the domain, generates the mesh in parallel across 96 processors, splits regions, checks mesh quality, and reconstructs the mesh.

### Shell Script: `mesh.sh`
```bash
#!/bin/bash
ulimit -s unlimited

# Sourcing OpenFOAM environment
source ~/.openfoam_v2206_profile

nproc=96

# Base mesh generation and feature extraction
blockMesh 2>&1 | tee log.blockMesh
surfaceFeatureExtract 2>&1 | tee log.surfaceFeatureExtract
decomposePar -copyZero 2>&1 | tee log.decomposePar

# Parallel meshing and region splitting
mpirun -np $nproc snappyHexMesh -parallel -overwrite 2>&1 | tee log.snappyHexMesh
mpirun -np $nproc splitMeshRegions -cellZones -parallel -overwrite 2>&1 | tee log.splitMeshRegion
mpirun -np $nproc checkMesh -parallel -allGeometry -allTopology 2>&1 | tee log.checkMesh

# Reconstruct parallel mesh
reconstructParMesh -constant -allRegions 2>&1 | tee log.reconstructParMesh

# Convert quality check sets to VTK format for inspection in ParaView
mpirun -np $nproc foamToVTK -parallel -faceSet lowQualityTetFaces
mpirun -np $nproc foamToVTK -parallel -faceSet lowWeightFaces
mpirun -np $nproc foamToVTK -parallel -faceSet warpedFaces
mpirun -np $nproc foamToVTK -parallel -faceSet skewFaces
mpirun -np $nproc foamToVTK -parallel -cellSet underdeterminedCells
mpirun -np $nproc foamToVTK -parallel -cellSet concaveCells
mpirun -np $nproc foamToVTK -parallel -pointSet nearPoints
mpirun -np $nproc foamToVTK -parallel -cellSet underdeterminedCells
```

### Execution:
Make the script executable and run:
```bash
chmod +x mesh.sh
./mesh.sh
```

---

## 🚀 Workflow Step 2: Running the Simulation

Once meshing is completed successfully, run the custom solver `cEpotBuoyantFoam` using `run.sh`.

### Shell Script: `run.sh`
```bash
#!/bin/bash

ulimit -s unlimited

cores=96

source ~/.openfoam_v2206_profile

if [[ ! $cores -eq 1 ]]
then
    mpirun -np $cores cEpotBuoyantFoam -parallel 2>&1 | tee log.cEpotBuoyantFoam
else
    cEpotBuoyantFoam 2>&1 | tee log.cEpotBuoyantFoam
fi
```

### Execution:
Make the script executable and run:
```bash
chmod +x run.sh
./run.sh
```

---

## 🔍 Post-Processing & Quality Verification

During the meshing script execution, several mesh quality checks are run, and bad cell/face sets are automatically converted into VTK format.

To inspect mesh quality issues in **ParaView**:
1. Open ParaView.
2. Load the converted VTK files generated in the processor directories or `VTK/` folder (e.g., `skewFaces`, `warpedFaces`, `concaveCells`).
3. Check `log.checkMesh` for a comprehensive summary of mesh validity and aspect ratios.

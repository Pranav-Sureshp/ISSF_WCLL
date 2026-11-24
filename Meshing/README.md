# WCLL meshing with OpenFOAM snappyHexMesh

The WCLL geometry is prepared in Coreform Cubit and exported as named ASCII STL surfaces. OpenFOAM then uses those surfaces to generate the volume mesh with `snappyHexMesh`.

## Directory layout

| Directory | Purpose |
| --- | --- |
| [`WCLL_mesh/`](WCLL_mesh/) | Cubit journals, the Python export script, and `fix_stl.sh` for normalising STL solid names |
| [`snappyHexPMU/`](snappyHexPMU/) | OpenFOAM case for feature extraction, parallel volume meshing, region splitting, and mesh checks |

## Prepare the geometry in `WCLL_mesh/`

1. In the Cubit journal, update the input path for `MINI_PMU_1BU.stp` and the STL output paths. The journals use geometry entity IDs from this model. Check the selected surfaces in Cubit if you change the CAD file or import options.
2. Replay `Rupert_set_groups_v3.jou` for the detailed surface grouping. The journal imprints and merges the imported volumes, assigns named surface groups, triangulates them, and exports one ASCII STL per group. `Rupert_set_groups_v1.jou` is an earlier revision of the detailed workflow. `attempt3.jou` and `wcll_pmu.py` use a simpler grouping with `exterior`, `inlet`, `outlet`, `fluid_surface` (exported as `fluid.stl`), and `dwt`. The Python script also requires a local Cubit module path and NumPy.
3. Put the individual STL files referenced by the OpenFOAM dictionaries in `snappyHexPMU/constant/triSurface/`. The detailed journals export `all_surfaces.stl` separately from the individual patch files. Use the set of files that matches the case dictionaries.

The detailed journals export these patch files.

| Surface group | STL file |
| --- | --- |
| Exterior surfaces | `exterior.stl` |
| First wall | `first_wall.stl` |
| Inlet and outlet | `inlet.stl`, `outlet.stl` |
| Fluid–solid interface | `fs_interface.stl` |
| DWT 1 fluid- and solid-side interfaces | `dwt1_f_interface.stl`, `dwt1_s_interface.stl` |
| DWT 2 fluid- and solid-side interfaces | `dwt2_f_interface.stl`, `dwt2_s_interface.stl` |

### Match STL solid names to filenames

`fix_stl.sh` rewrites ASCII STL files in place. It removes adjacent internal `endsolid`/`solid` pairs and sets the first and last lines to the filename stem. For example, `first_wall.stl` starts with `solid first_wall` and ends with `endsolid first_wall`. Apply the script to the individual patch STLs that should each contain one named solid.

From the OpenFOAM case directory, run the following for one file and repeat for each patch STL used by the case.

```bash
bash ../WCLL_mesh/fix_stl.sh constant/triSurface/first_wall.stl
```

## Generate the volume mesh in `snappyHexPMU/`

Check that the case dictionaries reference the exported STL files and solid names. The supplied `mesh.sh` sources `~/.openfoam_v2306_sapphire_hbm_profile` and launches 96 MPI ranks. The Slurm wrapper requests 112 tasks as supplied. Before submitting, review the account and partition, align the requested task count with the rank count in `mesh.sh`, and set `numberOfSubdomains` in `system/decomposeParDict` to that same rank count.

Submit from the case directory on Sapphire Rapids HBM. The wrapper launches `./mesh.sh` from the submission directory, so the script needs execute permission.

```bash
chmod +x mesh.sh
sbatch run_snappyMesh.hbm
```

| Stage | Command or output |
| --- | --- |
| Create the background mesh and extract STL feature edges | `blockMesh`, `surfaceFeatureExtract` |
| Prepare the parallel case and copy the initial fields | `decomposePar -copyZero` |
| Generate and overwrite the decomposed mesh | `snappyHexMesh -parallel -overwrite` |
| Split the mesh into regions using cell zones | `splitMeshRegions -cellZones -parallel -overwrite` |
| Check mesh geometry and topology | `checkMesh -parallel -allGeometry -allTopology` |
| Reconstruct the constant mesh for all regions | `reconstructParMesh -constant -allRegions` |
| Export available mesh-quality sets for inspection | `foamToVTK` for `lowQualityTetFaces`, `warpedFaces`, `underdeterminedCells`, and `nearPoints` |

Review `log.snappyHexMesh`, `log.splitMeshRegion`, `log.checkMesh`, and `log.reconstructParMesh` before using the mesh. The pipeline logs commands through `tee`, so job completion alone does not confirm that each meshing stage succeeded.

## Supporting scripts

| Script | Role |
| --- | --- |
| `mesh_reconstruct.sh` | Repeats the diagnostic VTK export from an existing decomposed case. Mesh reconstruction itself runs in `mesh.sh`. |
| `run_foam.sapphire`, `run_foam.sapphire_hbm` | Submit downstream solver runs on the standard Sapphire Rapids and HBM partitions using their respective `cEpotBouyantFoam` wrappers. |
| `clean_all.sh` | Removes generated meshes, processor directories, logs, and numbered outputs while temporarily moving the initial `0/` directory. Review the deletion patterns before running it from the case directory. |

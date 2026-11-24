#!/usr/bin/env python3
"""
===============================================================================
Coreform Cubit Geometry Processing and STL Export Script
===============================================================================

Purpose:
--------
1. Import a STEP geometry file.
2. Heal, imprint, and merge geometry.
3. Create named surface groups for CFD boundary conditions.
4. Mesh the required surfaces.
5. Export each boundary group as an STL file for OpenFOAM/snappyHexMesh.

Author: Pranav Naduvakkate
===============================================================================
"""

import sys
import os
import numpy as np

# =============================================================================
# Configuration
# =============================================================================

# Coreform Cubit installation
CUBIT_PATH = (
    "/home/pranav/softwares/"
    "Coreform-Cubit-2025.8+61943-Lin64/"
    "Coreform-Cubit-2025.8/bin"
)

# Input geometry
STEP_FILE = (
    "/home/pranav/OpenFOAM_cases/research/"
    "ISSF_2026_27_case/MINI_PMU_1BU.stp"
)

# OpenFOAM triSurface directory
TRISURFACE_DIR = (
    "/home/pranav/OpenFOAM_cases/research/"
    "ISSF_2026_27_case/snappyHexPMU/constant/triSurface"
)

# Geometry processing settings
MERGE_TOLERANCE = 1e-4

# =============================================================================
# Initialise Cubit
# =============================================================================

sys.path.append(CUBIT_PATH)

import cubit  # noqa: E402

cubit.cmd("reset")


def run(command: str):
    """
    Execute a Coreform Cubit command.

    Parameters
    ----------
    command : str
        Cubit command string.
    """
    print(f"[Cubit] {command}")
    cubit.cmd(command)


# =============================================================================
# Import and Heal Geometry
# =============================================================================

print("\n=== Importing STEP Geometry ===")

run(f'import step "{STEP_FILE}" heal')

# =============================================================================
# Geometry Cleanup
# =============================================================================

print("\n=== Geometry Cleanup ===")

run(f"merge tolerance {MERGE_TOLERANCE}")
run("imprint tolerant volume all")
run("merge volume all")

# =============================================================================
# Create Surface Groups
# =============================================================================

print("\n=== Creating Surface Groups ===")

# External enclosure surfaces
run('group "exterior" add surface in volume 1')

# CFD inlet and outlet surfaces
run('group "inlet" add surface 292')
run('group "outlet" add surface 293')

# Internal fluid-facing surfaces
run('group "fluid_surface" add surface in volume 4')
run('fluid_surface remove surface 292 surface 293')

# DWT component surfaces
run('group "dwt" add surface in volume 2')

# =============================================================================
# Mesh Surface Groups
# =============================================================================

print("\n=== Meshing Surface Groups ===")

surface_groups = [
    "exterior",
    "inlet",
    "outlet",
    "fluid_surface",
    "dwt",
]

for group in surface_groups:
    print(f"Meshing group: {group}")

    run("set trimesher coarse off")
    run(f"surface in group {group} scheme trimesh")
    run(f"mesh surface in group {group}")

# =============================================================================
# STL Export
# =============================================================================

print("\n=== Exporting STL Files ===")

stl_exports = {
    "exterior": "exterior.stl",
    "inlet": "inlet.stl",
    "outlet": "outlet.stl",
    "fluid_surface": "fluid.stl",
    "dwt": "dwt.stl",
}

for group, filename in stl_exports.items():

    output_file = os.path.join(TRISURFACE_DIR, filename)

    run(
        f'export stl ascii "{output_file}" '
        f'surface in group {group} mesh overwrite'
    )

print("\n=== Processing Complete ===")
print("All STL files have been exported successfully.")

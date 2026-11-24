#!/bin/bash

mv 0 0_orig
rm -r 0.* [1-9]* dynamicCode log.* processor* slurm-* machine.file* \
  constant/polyMesh/ constant/fluid/polyMesh/ constant/solid/polyMesh/ \
  constant/extendedFeatureEdgeMesh constant/triSurface/*.eMesh
mv 0_orig 0

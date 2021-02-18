# ----------------------------------------------------------------
# imports
# ----------------------------------------------------------------
# import the simple module from the paraview
from paraview.simple import *

# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

import os
import glob
import shutil
import math
import numpy as np
import argparse
import definitions as defs

# ----------------------------------------------------------------
# setup
# ----------------------------------------------------------------

parser = argparse.ArgumentParser(description="Post process using paraview")
parser.add_argument(
    "-f", "--folder", help="Folder to post process", type=str, required=True
)
args = parser.parse_args()

# Get file names
fdir = os.path.abspath(args.folder)
pattern = "*.e.*"
fnames = sorted(glob.glob(os.path.join(fdir, pattern)))
yname = os.path.join(os.path.dirname(fdir), "mcalister.yaml")
dim = defs.get_dimension(yname)

odir = os.path.join(os.path.dirname(fdir), "span_forces")
shutil.rmtree(odir, ignore_errors=True)
os.makedirs(odir)
oname = os.path.join(odir, "output.csv")

# create list of fields
fields = ["pressure_force_", "viscous_force_", "assembled_area_force_moment"]

# create a new 'ExodusIIReader'
exoreader = ExodusIIReader(FileName=fnames)
exoreader.PointVariables = fields
exoreader.NodeSetArrayStatus = []
exoreader.SideSetArrayStatus = ["wing"]
exoreader.ElementBlocks = []
times = exoreader.TimestepValues

# get active view
renderView1 = GetActiveViewOrCreate("RenderView")

# Calculate the forces
calculator1 = Calculator(Input=exoreader)
calculator1.ResultArrayName = "pf"
calculator1.Function = "pressure_force_/assembled_area_force_moment"

calculator2 = Calculator(Input=calculator1)
calculator2.ResultArrayName = "vf"
calculator2.Function = "viscous_force_/assembled_area_force_moment"

renderView1.Update()

# Integrals
z = np.linspace(0, 3.3 - 1e-3, 101)
forces = np.zeros((len(z) - 1, 9))
indices = {"pf": [3, 6], "vf": [6, 9]}
for k in range(len(z) - 1):

    # create a new 'Clip'
    clip1 = Clip(Input=calculator2)
    clip1.ClipType = "Plane"
    clip1.Scalars = ["POINTS", "pressure_force_"]
    clip1.ClipType.Origin = [0.0, 0.0, z[k]]
    clip1.ClipType.Normal = [0.0, 0.0, -1.0]

    # create a new 'Clip'
    clip2 = Clip(Input=clip1)
    clip2.ClipType = "Plane"
    clip2.Scalars = ["POINTS", "pressure_force_"]
    clip2.ClipType.Origin = [0.0, 0.0, z[k + 1]]
    clip2.ClipType.Normal = [0.0, 0.0, 1.0]

    # integrate
    integral = IntegrateVariables(Input=clip2)
    integralDisplay = Show(integral)

    # get animation scene
    animationScene1 = GetAnimationScene()
    animationScene1.GoToLast()

    # loop on each time and write to file
    area = integral.CellData.GetArray(0).GetRange(0)[0]
    forces[k, 0:3] = [times[-1], 0.5 * (z[k] + z[k + 1]), area]
    for i in range(integral.PointData.NumberOfArrays):
        name = integral.PointData.GetArray(i).Name
        if name in ["pf", "vf"]:
            forces[k, indices[name][0] : indices[name][1]] = [
                integral.PointData.GetArray(i).GetRange(0)[0],
                integral.PointData.GetArray(i).GetRange(1)[0],
                integral.PointData.GetArray(i).GetRange(2)[0],
            ]

    # Cleanup
    Delete(animationScene1)
    del animationScene1
    Delete(integralDisplay)
    del integralDisplay
    Delete(integral)
    del integral
    Delete(clip2)
    del clip2
    Delete(clip1)
    del clip1

np.savetxt(
    oname,
    forces,
    delimiter=",",
    header="time,z,area,pfx,pfy,pfz,vfx,vfy,vfz",
    comments="",
)

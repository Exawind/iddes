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
import argparse
import definitions as defs
import utilities

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
is_overset = defs.get_is_overset(yname)
_, _, _, _, _, _, flow_angle = utilities.parse_ic(yname)

odir = os.path.join(os.path.dirname(fdir), "vortex_slices")
shutil.rmtree(odir, ignore_errors=True)
os.makedirs(odir)
oname = os.path.join(odir, "output.csv")

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create list of fields
fields = ["pressure", "velocity_"]
blocks = ["background-hex"]
if is_overset:
    fields = ["iblank"] + fields
    blocks = ["wing-hex", "wing-wedge", "tipvortex-hex"] + blocks

# create a new 'ExodusIIReader'
exoreader = ExodusIIReader(FileName=fnames)
exoreader.PointVariables = fields
exoreader.SideSetArrayStatus = []
exoreader.ElementBlocks = blocks

# get active view
renderView1 = GetActiveViewOrCreate("RenderView")

if is_overset:
    # create a new 'Threshold'
    threshold1 = Threshold(Input=exoreader)
    threshold1.Scalars = ["POINTS", "iblank"]
    threshold1.ThresholdRange = [1.0, 1.0]
    nextinput = threshold1
else:
    nextinput = exoreader

# # Compute vorticity
# gradientOfUnstructuredDataSet1 = GradientOfUnstructuredDataSet(Input=nextinput)
# gradientOfUnstructuredDataSet1.ScalarArray = ["POINTS", "velocity_"]
# gradientOfUnstructuredDataSet1.ComputeGradient = 0
# gradientOfUnstructuredDataSet1.ComputeVorticity = 1

# create a new 'Slice' rotated so we are perpendicular to freestream
slice1 = Slice(Input=nextinput)
slice1.SliceType = "Plane"
slice1.SliceType.Origin = [1.0, 0.0, 3.3]
slice1.SliceType.Normal = [math.cos(flow_angle), math.sin(flow_angle), 0.0]
slice1.SliceOffsetValues = defs.get_vortex_slices()
slice1.Triangulatetheslice = 1

# create a new 'Clip'
clip1 = Clip(Input=slice1)
clip1.ClipType = "Plane"
clip1.Scalars = ["POINTS", "pressure"]

# init the 'Plane' selected for 'ClipType'
clip1.ClipType.Origin = [0.0, -0.5, 0.0]
clip1.ClipType.Normal = [0.0, -1.0, 0.0]

# create a new 'Clip'
clip2 = Clip(Input=clip1)
clip2.ClipType = "Plane"
clip2.Scalars = ["POINTS", "pressure"]

# init the 'Plane' selected for 'ClipType'
clip2.ClipType.Origin = [0.0, 2.0, 0.0]
clip2.ClipType.Normal = [0.0, 1.0, 0.0]

# create a new 'Clip'
clip3 = Clip(Input=clip2)
clip3.ClipType = "Plane"
clip3.Scalars = ["POINTS", "pressure"]

# init the 'Plane' selected for 'ClipType'
clip3.ClipType.Origin = [0.0, 0.0, 2.3]
clip3.ClipType.Normal = [0.0, 0.0, -1.0]

# create a new 'Clip'
clip4 = Clip(Input=clip3)
clip4.ClipType = "Plane"
clip4.Scalars = ["POINTS", "pressure"]

# init the 'Plane' selected for 'ClipType'
clip4.ClipType.Origin = [0.0, 0.0, 4.3]
clip4.ClipType.Normal = [0.0, 0.0, 1.0]


# ----------------------------------------------------------------
# save data
# ----------------------------------------------------------------
SaveData(
    oname,
    proxy=clip4,
    Precision=5,
    UseScientificNotation=0,
    WriteTimeSteps=1,
    FieldAssociation="Point Data",
)

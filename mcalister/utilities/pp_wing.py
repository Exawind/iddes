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
pattern = "*.e*"
fnames = sorted(glob.glob(os.path.join(fdir, pattern)))
yname = os.path.join(os.path.dirname(fdir), "mcalister.yaml")
dim = defs.get_dimension(yname)
is_overset = defs.get_is_overset(yname)

odir = os.path.join(os.path.dirname(fdir), "wing_slices")
shutil.rmtree(odir, ignore_errors=True)
os.makedirs(odir)
oname = os.path.join(odir, "output.csv")

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create list of fields
fields = ["pressure", "pressure_force_", "tau_wall", "velocity_"]
if is_overset:
    fields = ["iblank"] + fields

# create a new 'ExodusIIReader'
exoreader = ExodusIIReader(FileName=fnames)
exoreader.PointVariables = fields
exoreader.NodeSetArrayStatus = []
exoreader.SideSetArrayStatus = ["wing"]
exoreader.ElementBlocks = []

# get active view
renderView1 = GetActiveViewOrCreate("RenderView")

if dim == 2:
    saveinput = exoreader

elif dim == 3:

    if is_overset:
        # create a new 'Threshold'
        threshold1 = Threshold(Input=exoreader)
        threshold1.Scalars = ["POINTS", "iblank"]
        threshold1.ThresholdRange = [1.0, 1.0]
        sliceinput = threshold1

    else:
        sliceinput = exoreader

    # create a new 'Slice'
    # at span location corresponding to McAlister paper Fig. 21
    slice1 = Slice(Input=sliceinput)
    slice1.SliceType = "Plane"
    slice1.SliceOffsetValues = defs.get_wing_slices(dim)

    # init the 'Plane' selected for 'SliceType'
    slice1.SliceType.Origin = [0.0, 0.0, 0.0]
    slice1.SliceType.Normal = [0.0, 0.0, 1.0]
    saveinput = slice1

# ----------------------------------------------------------------
# save data
# ----------------------------------------------------------------
SaveData(
    oname,
    proxy=saveinput,
    Precision=5,
    UseScientificNotation=0,
    WriteTimeSteps=1,
    FieldAssociation="Point Data",
)

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
half_wing_length = defs.get_half_wing_length()

odir = os.path.join(os.path.dirname(fdir), "lineouts")
shutil.rmtree(odir, ignore_errors=True)
os.makedirs(odir)
opfx = os.path.join(odir, "output")

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create list of fields
fields = ["velocity_"]
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
    pltinput = threshold1
else:
    pltinput = exoreader

# create a new 'Plot Over Line'
plotOverLine1 = PlotOverLine(Input=pltinput, Source="High Resolution Line Source")

# Line out coordinates
xcens = [-0.5, 0.0, 1.0, 2.0, 4.0, 6.0, 8.0]
for k, xcen in enumerate(xcens):
    plotOverLine1.Source.Point1 = [xcen, -2.0, half_wing_length]
    plotOverLine1.Source.Point2 = [xcen, 2.0, half_wing_length]

    # ----------------------------------------------------------------
    # save data
    # ----------------------------------------------------------------
    SaveData(
        opfx + "_lineout_{0:d}.csv".format(k),
        proxy=plotOverLine1,
        Precision=5,
        UseScientificNotation=0,
        WriteTimeSteps=1,
        FieldAssociation="Point Data",
    )

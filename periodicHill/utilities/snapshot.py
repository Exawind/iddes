# trace generated using paraview version 5.8.0
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

import glob, sys
import argparse

# ----- Load arguments----------------------
helpstring="""
  Run paraview batch program to getsnapshots
  Example run:
   pvbatch snapshot.py results_sstiddes/periodicHill.e --times 4240 4240.4 4240.8 4241.2 --outfile viz/snapshot
"""
parser = argparse.ArgumentParser(description=helpstring)
parser.add_argument('EXODUSFILE',     help="The results exodus file")
parser.add_argument('--times',        help="Times to extract slices", nargs='+', required=True)
parser.add_argument('--outfile',      help="Output filename prefix", required=True)

args       = parser.parse_args()
exofile    = args.EXODUSFILE
times      = args.times #[float(x) for x in args.times]
fileprefix = args.outfile
print("EXODUSFILE = %s"%exofile)
#print(times)
#sys.exit(1)

# ----- Main program -----------------------
savefilename  = fileprefix+'_%f.png'
imageres      = [800,400]
resultfiles   = sorted(glob.glob(exofile+'*'))
looptimes     = [float(x) for x in times]

print("Loading files")
for x in resultfiles: print('Loading %s'%x)

# create a new 'ExodusIIReader'
periodicHille384 = ExodusIIReader(FileName=resultfiles)
periodicHille384.PointVariables = []
periodicHille384.SideSetArrayStatus = []

# get animation scene
animationScene1 = GetAnimationScene()

# get the time-keeper
timeKeeper1 = GetTimeKeeper()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# Properties modified on periodicHille384
periodicHille384.PointVariables = ['velocity_']
periodicHille384.ElementBlocks = ['interior-hex']
periodicHille384.FilePrefix = ''
periodicHille384.FilePattern = ''

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [1538, 759]

# get layout
layout1 = GetLayout()

# show data in view
periodicHille384Display = Show(periodicHille384, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
periodicHille384Display.Representation = 'Surface'
periodicHille384Display.ColorArrayName = [None, '']
periodicHille384Display.OSPRayScaleArray = 'GlobalNodeId'
periodicHille384Display.OSPRayScaleFunction = 'PiecewiseFunction'
periodicHille384Display.SelectOrientationVectors = 'GlobalNodeId'
periodicHille384Display.ScaleFactor = 0.9
periodicHille384Display.SelectScaleArray = 'GlobalNodeId'
periodicHille384Display.GlyphType = 'Arrow'
periodicHille384Display.GlyphTableIndexArray = 'GlobalNodeId'
periodicHille384Display.GaussianRadius = 0.045
periodicHille384Display.SetScaleArray = ['POINTS', 'GlobalNodeId']
periodicHille384Display.ScaleTransferFunction = 'PiecewiseFunction'
periodicHille384Display.OpacityArray = ['POINTS', 'GlobalNodeId']
periodicHille384Display.OpacityTransferFunction = 'PiecewiseFunction'
periodicHille384Display.DataAxesGrid = 'GridAxesRepresentation'
periodicHille384Display.PolarAxes = 'PolarAxesRepresentation'
periodicHille384Display.ScalarOpacityUnitDistance = 0.10885058313307754
periodicHille384Display.ExtractedBlockIndex = 2

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
periodicHille384Display.ScaleTransferFunction.Points = [1.0, 0.0, 0.5, 0.0, 935374.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
periodicHille384Display.OpacityTransferFunction.Points = [1.0, 0.0, 0.5, 0.0, 935374.0, 1.0, 0.5, 0.0]

# reset view to fit data
renderView1.ResetCamera()

# get the material library
materialLibrary1 = GetMaterialLibrary()

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(periodicHille384Display, ('FIELD', 'vtkBlockColors'))

# show color bar/color legend
periodicHille384Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'vtkBlockColors'
vtkBlockColorsLUT = GetColorTransferFunction('vtkBlockColors')

# get opacity transfer function/opacity map for 'vtkBlockColors'
vtkBlockColorsPWF = GetOpacityTransferFunction('vtkBlockColors')

# create a new 'Slice'
slice1 = Slice(Input=periodicHille384)
slice1.SliceType = 'Plane'
slice1.HyperTreeGridSlicer = 'Plane'
slice1.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice1.SliceType.Origin = [4.5, 1.5180000066757202, 2.25]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice1.HyperTreeGridSlicer.Origin = [4.5, 1.5180000066757202, 2.25]

# toggle 3D widget visibility (only when running from the GUI)
Hide3DWidgets(proxy=slice1.SliceType)

# toggle 3D widget visibility (only when running from the GUI)
Show3DWidgets(proxy=slice1.SliceType)

# toggle 3D widget visibility (only when running from the GUI)
Hide3DWidgets(proxy=slice1.SliceType)

# Properties modified on slice1.SliceType
slice1.SliceType.Normal = [0.0, 0.0, 1.0]

# show data in view
slice1Display = Show(slice1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
slice1Display.Representation = 'Surface'
slice1Display.ColorArrayName = [None, '']
slice1Display.OSPRayScaleArray = 'velocity_'
slice1Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice1Display.SelectOrientationVectors = 'None'
slice1Display.ScaleFactor = 0.9
slice1Display.SelectScaleArray = 'None'
slice1Display.GlyphType = 'Arrow'
slice1Display.GlyphTableIndexArray = 'None'
slice1Display.GaussianRadius = 0.045
slice1Display.SetScaleArray = ['POINTS', 'velocity_']
slice1Display.ScaleTransferFunction = 'PiecewiseFunction'
slice1Display.OpacityArray = ['POINTS', 'velocity_']
slice1Display.OpacityTransferFunction = 'PiecewiseFunction'
slice1Display.DataAxesGrid = 'GridAxesRepresentation'
slice1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice1Display.ScaleTransferFunction.Points = [-0.23589062959312124, 0.0, 0.5, 0.0, 1.2775307081014367, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice1Display.OpacityTransferFunction.Points = [-0.23589062959312124, 0.0, 0.5, 0.0, 1.2775307081014367, 1.0, 0.5, 0.0]

# hide data in view
Hide(periodicHille384, renderView1)

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(slice1Display, ('FIELD', 'vtkBlockColors'))

# show color bar/color legend
slice1Display.SetScalarBarVisibility(renderView1, True)

# set scalar coloring
ColorBy(slice1Display, ('POINTS', 'velocity_', 'Magnitude'))

# Hide the scalar bar for this color map if no visible data is colored by it.
HideScalarBarIfNotNeeded(vtkBlockColorsLUT, renderView1)

# rescale color and/or opacity maps used to include current data range
slice1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
slice1Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'velocity_'
velocity_LUT = GetColorTransferFunction('velocity_')

# get opacity transfer function/opacity map for 'velocity_'
velocity_PWF = GetOpacityTransferFunction('velocity_')

# get color legend/bar for velocity_LUT in view renderView1
velocity_LUTColorBar = GetScalarBar(velocity_LUT, renderView1)

# change scalar bar placement
velocity_LUTColorBar.WindowLocation = 'AnyLocation'
velocity_LUTColorBar.Position = [0.8172951885565669, 0.3412384716732543]
velocity_LUTColorBar.ScalarBarLength = 0.32999999999999996

fontsize=5
velocity_LUTColorBar.ScalarBarLength = 0.50
velocity_LUTColorBar.ScalarBarThickness = 5
velocity_LUTColorBar.TitleFontSize = fontsize #10
velocity_LUTColorBar.LabelFontSize = fontsize #10
velocity_LUTColorBar.WindowLocation = 'AnyLocation'
#colorbarpos = getparam('colorbarpos',params, [0.9, 0.25])
velocity_LUTColorBar.Position = [0.85, 0.25]

# Rescale transfer function
velocity_LUT.RescaleTransferFunction(0.0, 1.4)

# Rescale transfer function
velocity_PWF.RescaleTransferFunction(0.0, 1.4)

## Loop through times
for t in looptimes:
    # Properties modified on animationScene1
    animationScene1.AnimationTime = t

    # Properties modified on timeKeeper1
    timeKeeper1.Time = t

    print('Working on time %e'%t)

    # current camera placement for renderView1
    renderView1.CameraPosition = [4.5, 1.5180000066757202, 16.1181935773403]
    renderView1.CameraFocalPoint = [4.5, 1.5180000066757202, 2.25]
    renderView1.CameraParallelScale = 5.255171169454663

    # save screenshot
    SaveScreenshot(savefilename%timeKeeper1.Time, renderView1, ImageResolution=imageres)



#### saving camera placements for all active views

# current camera placement for renderView1
renderView1.CameraPosition = [4.5, 1.5180000066757202, 16.1181935773403]
renderView1.CameraFocalPoint = [4.5, 1.5180000066757202, 2.25]
renderView1.CameraParallelScale = 5.255171169454663

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).

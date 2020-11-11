# Pointwise V18.2 Journal file - Fri Jan 11 15:34:18 2019
package require PWI_Glyph 2.18.2
pw::Application setUndoMaximumLevels 5
pw::Application reset
pw::Application markUndoLevel {Journal Reset}
pw::Application clearModified

##########################################  INPUT  #################################################

# domain params
# Location of top boundary of the domain
set Ly  3.036
# Domain length in z-direction (spanwise)
set span  4.50000 

# The grid is divided into three layers
#  ____________________________________
# |                                    |
# |                TOP                 |
# |_____                          _____|
# |     \________________________/     |
# |__                               ___|
# |   \           OUTER            /   |
# |_   \__________________________/   _|
#   \                                /
#    \            INNER             /
#     \____________________________/

# First cell height away from bottom wall 
set dy_ini 1.0e-3
# First cell height away from top wall 
set dy_top 2.0e-3
# Initial spacing away from inlet and outlet
set dx_in  1.5e-2
# Y spacing ABOVE the interface between the outer and top regions
# The spacing BELOW is not prescribed by the user, it is determined by the 
# extrusion solver
set dy_interface 0.015

# Number of elements in top region
set ny  70
# Growth rate in inner region
set bl_growth_inner 1.1
# Number of elements in inner region
set n_inner 32
# Growth rate in outer region
set bl_growth_outer 1.0
# Number of elements in outer region
set n_outer 20
# Number of smoothing iterations
set ERUN 10
# Spacing on the left endpoint of the bottom boundary (at inlet)
set dh1_end 0.08
# Spacing in the center of the bottom boundary (midpoint in x-direction)
set dh2_beg 0.1

# Number of spanwise elements (z-dir)
set nz 40
# Number of elements on one half of the bottom hill boundary
set nh1  60
# Number of elements on one half of the flat region on the bottom boundary
set nmid  35

#########################################  CREATE DOMAIN  ###########################################

# Create curve for left half of the bottom boundary, based on the dat file.
# This will already have a point distribution on it, but we will discard that distribution later.
set _TMP(mode_1) [pw::Application begin GridImport]
  $_TMP(mode_1) initialize -strict -type {Segment} {periodicHill.dat}
  $_TMP(mode_1) read
  $_TMP(mode_1) convert
$_TMP(mode_1) end
unset _TMP(mode_1)

# Create curve for the left half of the top boundary
set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(PW_1) [pw::SegmentSpline create]
  $_TMP(PW_1) addPoint {0.0000000 3.036 0.0000000}
  $_TMP(PW_1) addPoint {4.5000000 3.036 0.0000000}
  set _CN(1) [pw::Connector create]
  $_CN(1) addSegment $_TMP(PW_1)
  unset _TMP(PW_1)
  $_CN(1) calculateDimension
$_TMP(mode_1) end
unset _TMP(mode_1)

# Create curve that forms the left (inlet) boundary
set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(PW_1) [pw::SegmentSpline create]
  $_TMP(PW_1) delete
  unset _TMP(PW_1)
$_TMP(mode_1) abort
unset _TMP(mode_1)
set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(PW_1) [pw::SegmentSpline create]
  set _CN(2) [pw::GridEntity getByName con-1]
  $_TMP(PW_1) addPoint [$_CN(1) getPosition -arc 0]
  $_TMP(PW_1) addPoint [$_CN(2) getPosition -arc 0]
  set _CN(3) [pw::Connector create]
  $_CN(3) addSegment $_TMP(PW_1)
  $_CN(3) calculateDimension
  unset _TMP(PW_1)
$_TMP(mode_1) end
unset _TMP(mode_1)

# Create curve that forms the right boundary, which will be
# in the center of the domain.
set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(PW_1) [pw::SegmentSpline create]
  $_TMP(PW_1) addPoint [$_CN(2) getPosition -arc 1]
  $_TMP(PW_1) addPoint [$_CN(1) getPosition -arc 1]
  set _CN(4) [pw::Connector create]
  $_CN(4) addSegment $_TMP(PW_1)
  unset _TMP(PW_1)
  $_CN(4) calculateDimension
$_TMP(mode_1) end
unset _TMP(mode_1)

# At this point, we have a domain that looks like so:
# |------------|
# |            |
# |            |
# |_           |
#   \          |
#    \_________|

######################################################  PARTITION CONNECTORS  ################################################

# Partition the bottom connector in two, with the split located at x=1.99147
set _TMP(split_params) [list]
lappend _TMP(split_params) [$_CN(2) getParameter -closest [pw::Application getXYZ [$_CN(2) closestPoint {1.99147 0 0}]]]
set _TMP(PW_1) [$_CN(2) split $_TMP(split_params)]
unset _TMP(PW_1)
unset _TMP(split_params)

# Distribute nh1 points evenly on bottom-left connector, 
set _CN(5) [pw::GridEntity getByName con-1-split-1]
set _TMP(mode_1) [pw::Application begin Dimension]
  set _TMP(PW_1) [pw::Collection create]
  $_TMP(PW_1) set [list $_CN(5)]
  $_TMP(PW_1) do setDimension -resetDistribution $nh1
  $_TMP(PW_1) delete
  unset _TMP(PW_1)
  $_TMP(mode_1) balance -resetGeneralDistributions
$_TMP(mode_1) end
unset _TMP(mode_1)

# Distribute nmid points evenly on the bottom-right connector.
set _TMP(mode_1) [pw::Application begin Dimension]
  set _CN(6) [pw::GridEntity getByName con-1-split-2]
  set _TMP(PW_1) [pw::Collection create]
  $_TMP(PW_1) set [list $_CN(6)]
  $_TMP(PW_1) do setDimension -resetDistribution $nmid
  $_TMP(PW_1) delete
  unset _TMP(PW_1)
  $_TMP(mode_1) balance -resetGeneralDistributions
$_TMP(mode_1) end
unset _TMP(mode_1)

# Distribute the same number of points on the top as the bottom
set _TMP(mode_1) [pw::Application begin Dimension]
  set _TMP(PW_1) [pw::Collection create]
  $_TMP(PW_1) set [list $_CN(1)]
  $_TMP(PW_1) do setDimensionFromSubConnectors -resetDistribution [list  [list $_CN(5) 1] [list $_CN(6) 1]]
  $_TMP(PW_1) delete
  unset _TMP(PW_1)
  $_TMP(mode_1) balance -resetGeneralDistributions
$_TMP(mode_1) end
unset _TMP(mode_1)

# Redistribute the hill points to match initial spacing dx_in
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(5)]]
  [[$_CN(5) getDistribution 1] getBeginSpacing] setValue $dx_in
$_TMP(mode_1) end
unset _TMP(mode_1)

# Redistribute points on the hill to match the prescribed spacing on the right endpoint, dh1_end
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(5)]]
  [[$_CN(5) getDistribution 1] getEndSpacing] setValue $dh1_end
$_TMP(mode_1) end
unset _TMP(mode_1)

# Redistribute the points on the bottom right connector to match
# the prescribed left endpoint spacing, dh1_end
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(6)]]
  [[$_CN(6) getDistribution 1] getBeginSpacing] setValue $dh1_end
$_TMP(mode_1) end
unset _TMP(mode_1)

# Make the bottom right connector match the spacing on the right endpoint
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(6)]]
  [[$_CN(6) getDistribution 1] getEndSpacing] setValue $dh2_beg
$_TMP(mode_1) end
unset _TMP(mode_1)

# Don't understand what this does
# This might help to understand
# https://github.com/pointwise/GeomToMesh/blob/master/GMUtility.glf
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1)]]
  set _TMP(dist_1) [pw::DistributionGeneral create [list [list $_CN(5) 1] [list $_CN(6) 1]]]
  # Clear spacings so the distribution will scale properly
  $_TMP(dist_1) setBeginSpacing 0
  $_TMP(dist_1) setEndSpacing 0
  $_TMP(dist_1) setVariable [[$_CN(1) getDistribution 1] getVariable]
  $_CN(1) setDistribution -lockEnds 1 $_TMP(dist_1)
  unset _TMP(dist_1)
$_TMP(mode_1) end
unset _TMP(mode_1)

################################  CREATE INNER AND OUTER BL REGIONS ############################

# Delete connectors 3 and 4 (inlet and outlet)
pw::Entity delete [list $_CN(3)]
pw::Entity delete [list $_CN(4)]

# Combine together connectors 5 and 6 (bottom portion), creating connector 8.
set _TMP(PW_1) [pw::Connector join -reject _TMP(ignored) -keepDistribution [list $_CN(6) $_CN(5)]]
unset _TMP(ignored)
unset _TMP(PW_1)

# Extrude the bottom surface using a hyperbolic system to create inner and outer layers
# This creates a new connector 5 on the left, 4 at the top of the extrusion, and 3 on the right
set _TMP(mode_1) [pw::Application begin Create]
  set _CN(8) [pw::GridEntity getByName con-1-split-1]
  set _TMP(PW_1) [pw::Edge createFromConnectors [list $_CN(8)]]
  set _TMP(edge_1) [lindex $_TMP(PW_1) 0]
  unset _TMP(PW_1)
  set _DM(1) [pw::DomainStructured create]
  $_DM(1) addEdge $_TMP(edge_1)
$_TMP(mode_1) end
unset _TMP(mode_1)
set _TMP(mode_1) [pw::Application begin ExtrusionSolver [list $_DM(1)]]
  $_TMP(mode_1) setKeepFailingStep true
  $_DM(1) setExtrusionBoundaryCondition Begin ConstantX
  $_DM(1) setExtrusionBoundaryConditionStepSuppression Begin 0
  $_DM(1) setExtrusionBoundaryCondition End ConstantX
  $_DM(1) setExtrusionBoundaryConditionStepSuppression End 0
  $_DM(1) setExtrusionSolverAttribute SpacingGrowthFactor $bl_growth_inner
  $_DM(1) setExtrusionSolverAttribute NormalInitialStepSize $dy_ini
  $_DM(1) setExtrusionSolverAttribute NormalKinseyBarthSmoothing 0.5
  $_DM(1) setExtrusionSolverAttribute NormalVolumeSmoothing 0.0
  $_TMP(mode_1) run $n_inner
  $_DM(1) setExtrusionSolverAttribute SpacingGrowthFactor $bl_growth_outer
  $_TMP(mode_1) run $n_outer
$_TMP(mode_1) end
unset _TMP(mode_1)
unset _TMP(edge_1)

# Don't understand what this does
# copy distro again to top
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(1)]]
  set _CN(9) [pw::GridEntity getByName con-4]
  set _TMP(dist_1) [pw::DistributionGeneral create [list [list $_CN(9) 1]]]
  $_TMP(dist_1) reverse
  # Clear spacings so the distribution will scale properly
  $_TMP(dist_1) setBeginSpacing 0
  $_TMP(dist_1) setEndSpacing 0
  $_TMP(dist_1) setVariable [[$_CN(1) getDistribution 1] getVariable]
  $_CN(1) setDistribution -lockEnds 1 $_TMP(dist_1)
  unset _TMP(dist_1)
$_TMP(mode_1) end
unset _TMP(mode_1)

###############################  CREATE REST OF 2D MESH  ###################################

# Spline to form the rest of the inlet.  This part will be connector 6.
set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(PW_1) [pw::SegmentSpline create]
  set _CN(9) [pw::GridEntity getByName con-4]
  set _CN(10) [pw::GridEntity getByName con-5]
  $_TMP(PW_1) addPoint [$_CN(1) getPosition -arc 0]
  $_TMP(PW_1) addPoint [$_CN(9) getPosition -arc 1]
  set _CN(11) [pw::Connector create]
  $_CN(11) addSegment $_TMP(PW_1)
  unset _TMP(PW_1)
  $_CN(11) calculateDimension
$_TMP(mode_1) end
unset _TMP(mode_1)

# Spline to form the rest of the outlet.  This will be connector 7.
set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(PW_1) [pw::SegmentSpline create]
  set _CN(12) [pw::GridEntity getByName con-3]
  $_TMP(PW_1) addPoint [$_CN(1) getPosition -arc 1]
  $_TMP(PW_1) addPoint [$_CN(12) getPosition -arc 1]
  set _CN(13) [pw::Connector create]
  $_CN(13) addSegment $_TMP(PW_1)
  unset _TMP(PW_1)
  $_CN(13) calculateDimension
$_TMP(mode_1) end
unset _TMP(mode_1)

# Apply ny evenly spaced points on the new inlet segment
set _TMP(mode_1) [pw::Application begin Dimension]
  set _TMP(PW_1) [pw::Collection create]
  $_TMP(PW_1) set [list $_CN(11)]
  $_TMP(PW_1) do setDimension -resetDistribution $ny
  $_TMP(PW_1) delete
  unset _TMP(PW_1)
  $_TMP(mode_1) balance -resetGeneralDistributions
$_TMP(mode_1) end
unset _TMP(mode_1)

# Same on outlet
set _TMP(mode_1) [pw::Application begin Dimension]
  set _TMP(PW_1) [pw::Collection create]
  $_TMP(PW_1) set [list $_CN(13)]
  $_TMP(PW_1) do setDimension -resetDistribution $ny
  $_TMP(PW_1) delete
  unset _TMP(PW_1)
  $_TMP(mode_1) balance -resetGeneralDistributions
$_TMP(mode_1) end
unset _TMP(mode_1)

# Adjust the spacing on the outer inlet segment
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(11)]]
  [[$_CN(11) getDistribution 1] getEndSpacing] setValue $dy_interface
$_TMP(mode_1) end
unset _TMP(mode_1)
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(11)]]
  [[$_CN(11) getDistribution 1] getBeginSpacing] setValue $dy_top
$_TMP(mode_1) end
unset _TMP(mode_1)

# Adjust the spacing on the new outlet
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(13)]]
  [[$_CN(13) getDistribution 1] getEndSpacing] setValue $dy_interface
$_TMP(mode_1) end
unset _TMP(mode_1)
set _TMP(mode_1) [pw::Application begin Modify [list $_CN(13)]]
  [[$_CN(13) getDistribution 1] getBeginSpacing] setValue $dy_top
$_TMP(mode_1) end
unset _TMP(mode_1)

# Generate the top part of the domain
set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(edge_1) [pw::Edge create]
  $_TMP(edge_1) addConnector $_CN(9)
  set _TMP(edge_2) [pw::Edge create]
  $_TMP(edge_2) addConnector $_CN(11)
  set _TMP(edge_3) [pw::Edge create]
  $_TMP(edge_3) addConnector $_CN(1)
  set _TMP(edge_4) [pw::Edge create]
  $_TMP(edge_4) addConnector $_CN(13)
  set _DM(2) [pw::DomainStructured create]
  $_DM(2) addEdge $_TMP(edge_1)
  $_DM(2) addEdge $_TMP(edge_2)
  $_DM(2) addEdge $_TMP(edge_3)
  $_DM(2) addEdge $_TMP(edge_4)
  unset _TMP(edge_4)
  unset _TMP(edge_3)
  unset _TMP(edge_2)
  unset _TMP(edge_1)
$_TMP(mode_1) end
unset _TMP(mode_1)

#############################################  SMOOTHING  ##################################################

# Join the inner/outer and top domains
set _TMP(face_1) [pw::FaceStructured create]
$_TMP(face_1) delete
unset _TMP(face_1)
set _TMP(PW_1) [pw::DomainStructured join -reject _TMP(ignored) [list $_DM(2) $_DM(1)]]
unset _TMP(ignored)
unset _TMP(PW_1)

# Join the inlet connectors
set _TMP(PW_1) [pw::Connector join -reject _TMP(ignored) -keepDistribution [list $_CN(11) $_CN(10)]]
unset _TMP(ignored)
unset _TMP(PW_1)

# Join the outlet connectors
set _TMP(PW_1) [pw::Connector join -reject _TMP(ignored) -keepDistribution [list $_CN(12) $_CN(13)]]
unset _TMP(ignored)
unset _TMP(PW_1)

# Smooth the combined domains
set _DM(3) [pw::GridEntity getByName dom-1]
set _TMP(mode_1) [pw::Application begin EllipticSolver [list $_DM(3)]]
  set _TMP(SUB_1) [$_DM(3) getSubGrid 1]
  set _TMP(SUB_2) [$_DM(3) getSubGrid 2]
  set _TMP(ENTS) [pw::Collection create]
$_TMP(ENTS) set [list $_DM(3)]
  $_DM(3) setEllipticSolverAttribute InteriorControl Fixed
  $_TMP(ENTS) delete
  unset _TMP(ENTS)
  $_TMP(mode_1) setActiveSubGrids $_DM(3) [list]
  $_TMP(mode_1) run $ERUN
$_TMP(mode_1) end
unset _TMP(mode_1)
unset _TMP(SUB_2)
unset _TMP(SUB_1)

###########################################  MIRROR AND JOIN  #####################################

# Copy the whole thing and mirror it
pw::Application clearClipboard
pw::Application setClipboard [list $_DM(2)]
set _TMP(mode_1) [pw::Application begin Paste]
  set _TMP(PW_1) [$_TMP(mode_1) getEntities]
  set _TMP(mode_2) [pw::Application begin Modify $_TMP(PW_1)]
    pw::Entity transform [pwu::Transform mirroring {1 0 0} 4.5] [$_TMP(mode_2) getEntities]
  $_TMP(mode_2) end
  unset _TMP(mode_2)
$_TMP(mode_1) end
unset _TMP(mode_1)

# Join the two halves 
set _DM(3) [pw::GridEntity getByName dom-1]
set _DM(4) [pw::GridEntity getByName dom-2]
set _TMP(face_1) [pw::FaceStructured create]
$_TMP(face_1) delete
unset _TMP(face_1)
set _TMP(PW_1) [pw::DomainStructured join -reject _TMP(ignored) [list $_DM(3) $_DM(4)]]
unset _TMP(ignored)
unset _TMP(PW_1)

# Join the top connectors
set _CN(12) [pw::GridEntity getByName con-7]
set _TMP(PW_1) [pw::Connector join -reject _TMP(ignored) -keepDistribution [list $_CN(12) $_CN(1)]]
unset _TMP(ignored)
unset _TMP(PW_1)

# Join the bottom connectors
set _CN(13) [pw::GridEntity getByName con-1-split-2]
set _TMP(PW_1) [pw::Connector join -reject _TMP(ignored) -keepDistribution [list $_CN(13) $_CN(6)]]
unset _TMP(ignored)
unset _TMP(PW_1)

#########################################  EXTRUDE TO 3D  ##########################################

set _TMP(mode_1) [pw::Application begin Create]
  set _TMP(PW_1) [pw::FaceStructured createFromDomains [list $_DM(2)]]
  set _TMP(face_1) [lindex $_TMP(PW_1) 0]
  unset _TMP(PW_1)
  set _BL(1) [pw::BlockStructured create]
  $_BL(1) addFace $_TMP(face_1)
$_TMP(mode_1) end
unset _TMP(mode_1)
set _TMP(mode_1) [pw::Application begin ExtrusionSolver [list $_BL(1)]]
  $_TMP(mode_1) setKeepFailingStep true
  $_BL(1) setExtrusionSolverAttribute Mode Translate
  $_BL(1) setExtrusionSolverAttribute TranslateDirection {1 0 0}
  $_BL(1) setExtrusionSolverAttribute TranslateDirection {0 0 1}
  $_BL(1) setExtrusionSolverAttribute TranslateDistance $span
  $_TMP(mode_1) run $nz
$_TMP(mode_1) end
unset _TMP(mode_1)
unset _TMP(face_1)

pw::Application setCAESolver {EXODUS II} 3

###############################  INTERIOR AND BOUNDARY CONDITIONS  #################################
# Appended by Pointwise V18.2 - Wed Jan 29 07:40:21 2020

set _TMP(PW_1) [pw::VolumeCondition create]
$_TMP(PW_1) setName "interior"
$_TMP(PW_1) apply [list $_BL(1)]

unset _TMP(PW_1)
set _DM(3) [pw::GridEntity getByName dom-2]
set _DM(4) [pw::GridEntity getByName dom-3]
set _DM(5) [pw::GridEntity getByName dom-4]
set _DM(6) [pw::GridEntity getByName dom-5]
set _DM(7) [pw::GridEntity getByName dom-6]
set _TMP(PW_1) [pw::BoundaryCondition getByName {Unspecified}]
set _TMP(PW_2) [pw::BoundaryCondition create]

set _TMP(PW_3) [pw::BoundaryCondition getByName {bc-2}]
unset _TMP(PW_2)
$_TMP(PW_3) setName {inlet}

$_TMP(PW_3) setPhysicalType -usage CAE {Side Set}

set _TMP(PW_4) [pw::BoundaryCondition create]

set _TMP(PW_5) [pw::BoundaryCondition getByName {bc-3}]
unset _TMP(PW_4)
$_TMP(PW_5) setName {outlet}

$_TMP(PW_5) setPhysicalType -usage CAE {Side Set}

set _TMP(PW_6) [pw::BoundaryCondition create]

set _TMP(PW_7) [pw::BoundaryCondition getByName {bc-4}]
unset _TMP(PW_6)
$_TMP(PW_7) setName {front}

set _TMP(PW_8) [pw::BoundaryCondition create]

set _TMP(PW_9) [pw::BoundaryCondition getByName {bc-5}]
unset _TMP(PW_8)
$_TMP(PW_9) setName {back}

$_TMP(PW_7) setPhysicalType -usage CAE {Side Set}

$_TMP(PW_9) setPhysicalType -usage CAE {Side Set}

set _TMP(PW_10) [pw::BoundaryCondition create]

set _TMP(PW_11) [pw::BoundaryCondition getByName {bc-6}]
unset _TMP(PW_10)
$_TMP(PW_11) setName {top}

$_TMP(PW_11) setPhysicalType -usage CAE {Side Set}

set _TMP(PW_12) [pw::BoundaryCondition create]

set _TMP(PW_13) [pw::BoundaryCondition getByName {bc-7}]
unset _TMP(PW_12)
$_TMP(PW_13) setName {wall}

$_TMP(PW_13) setPhysicalType -usage CAE {Side Set}

$_TMP(PW_7) apply [list [list $_BL(1) $_DM(7)]]

$_TMP(PW_9) apply [list [list $_BL(1) $_DM(2)]]

$_TMP(PW_3) apply [list [list $_BL(1) $_DM(6)]]

$_TMP(PW_5) apply [list [list $_BL(1) $_DM(4)]]

$_TMP(PW_13) apply [list [list $_BL(1) $_DM(3)]]

$_TMP(PW_11) apply [list [list $_BL(1) $_DM(5)]]

unset _TMP(PW_1)
unset _TMP(PW_3)
unset _TMP(PW_5)
unset _TMP(PW_7)
unset _TMP(PW_9)
unset _TMP(PW_11)
unset _TMP(PW_13)

#########################################  SAVE  ############################################

set _TMP(mode_1) [pw::Application begin CaeExport [pw::Entity sort [list $_BL(1)]]]
  $_TMP(mode_1) initialize -strict -type CAE {periodicHill.exo}
  $_TMP(mode_1) verify
  $_TMP(mode_1) write
$_TMP(mode_1) end
unset _TMP(mode_1)

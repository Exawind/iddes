# Periodic Hill problem

## Overview
This directory contains the files and data for running the periodic
hill turbulence problem.  This case is based on same case run using
SST and SST-DES from Marc Henry de Frahan -- see his repo
[periodicHill](https://github.com/marchdf/periodicHill).

Additional details on the periodic hill problem are provided via the
`ERCOFTAC UFR 3-30 Test Case` problem on the [ERCOFTAC
database](https://www.kbwiki.ercoftac.org/w/index.php?title=UFR_3-30_Test_Case).

## Basic settings

| Parameter       | Value                      |
|-----------------|----------------------------|
| Reynolds number | 10600 based on hill height |
| Hill height     | 1 m                        |
| Fluid density   | 1 kg/m^3                   |
| Fluid velocity  | 1 m/s                      |
| Fluid viscosity | 10600                      |
|                 |                            |

## Requirements to run
**Mesh generation**  
Meshes for this case are generated using
[Pointwise](https://www.pointwise.com/) glyph scripts.

**Nalu-Wind**  
The periodic hill cases should be run in Nalu-Wind using the either:  
- the [`master`
  branch](https://github.com/Exawind/nalu-wind/tree/master) for `sst`
  and `sst-des` runs
- the [`my_iddes_abl`
  branch](https://github.com/lawrenceccheung/nalu-wind/tree/my_iddes_abl)
  from Lawrence.  This branch merges the iddes capabilities from
  [Ganesh's
  branch](https://github.com/gantech/nalu-wind/tree/f/iddes_abl) with
  user-defined boxes of momentum body forcing from master.
  
## Postprocessing

_Add something in here later._

# McAlister airfoil


## Postprocessing

To generate the wing loading data, run the paraview `pvbatch` on
`pp_wing.py`:  
```bash
pvbatch utilities/pp_wing.py -f sst-iddes-12.localupwind/out/
```
where `sst-iddes-12.localupwind/out/` is the directory with the
exodus files.

Then average the slices with `avg_slices.py`:  
```bash
python utilities/avg_slices.py -n 30 -f sst-iddes-12.localupwind/wing_slices/
```
Note that `avg_slices.py` requires the `pandas` library.

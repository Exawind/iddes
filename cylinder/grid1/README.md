# Grid1 

Example cylinder run from Ganesh using `grid1`

## Steps:
1. Get the grid `grid1.exo` from [Ganesh's box folder](https://app.box.com/folder/123504580030).

2. Run the `cylinder_rans.yaml` case to get an initial condition using RANS.

	It should run for 400 steps with `dt=0.03`.  After the run, you
   should see the initial velocity field look like:
   ![image](https://user-images.githubusercontent.com/15526007/95908370-da3ee880-0d51-11eb-9456-07e275343f41.png)

3. Run the `cylinder01.yaml` using the `sst_iddes` model.

	Notice that the timestep is now `dt=0.003`.
	

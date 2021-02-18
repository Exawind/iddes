import re


# ========================================================================
def get_aoa(string):
    """Parse the angle of attack from a string (last int)"""
    return [int(x) for x in re.findall(r"\d+", string)][-1]


# ========================================================================
def get_half_wing_length():
    return 3.3


# ========================================================================
def get_dimension(fname):
    """Read yaml file to get dimention"""
    topo_3d = ["hex", "wedge", "pyramid", "tetra"]
    topo_2d = ["quad", "triangle"]
    with open(fname, "r") as f:
        for line in f:
            if any(topo in line.lower() for topo in topo_3d):
                return 3
            elif any(topo in line.lower() for topo in topo_2d):
                return 2
    return 0


# ========================================================================
def get_is_overset(fname):
    """Read yaml file to get overset on/off"""
    with open(fname, "r") as f:
        for line in f:
            if "overset" in line:
                return True
    return False


# ========================================================================
def get_wing_area(dim):
    if dim == 2:
        return 1.0
    elif dim == 3:
        return get_half_wing_length()


# ========================================================================
def get_wing_slices(dim):
    """Return the wing slices at span location corresponding to McAlister paper Fig. 21"""
    half_wing_length = get_half_wing_length()
    if dim == 2:
        slices = [0.0]
    elif dim == 3:
        slices = [
            0.994,
            0.974,
            0.944,
            0.899,
            0.843,
            0.773,
            0.692,
            0.597,
            0.490,
            0.370,
            0.238,
            0.094,
        ]
    return [half_wing_length * x for x in slices]


# ========================================================================
def get_vortex_slices():
    """Return the vortex slices"""
    return [0.1, 0.2, 0.5, 1.0, 2.0, 4.0, 6.0]

# ABCDOptics
Simple ABCD matrix operation module. You can give the code an initial wavelength, beamwaist, position (z-value) and angle.
It will then propagate it through the optical system that you design and return the final beamwaist, position and angle.

If you look at example there is a short demonstration on how to use the code.
NOTE: Make sure to rerun the example code. Currently it says that the given system returns a beamwaist of ~1000um which is not true. I just forgot to recompile the code
before putting it on here. It should give ~40um.
Not all ABCD matrices have been implemented but it should be easy enough to add more as needed.
Currently, radius of curvature has not been added in.

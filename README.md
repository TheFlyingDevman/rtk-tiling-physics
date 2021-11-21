# rtk-tiling-physics
A blender addon that allows the user to make physics-based tiled geometry.



To install, just copy the rtk_tiling_physics.py file to your Blender startup folder (<BLENDER INSTALL DIRECTORY>\scripts\startup).

Once installed, there should be an "RTK" Tab in your toolbar after starting Blender. In there, you should now be able to find the "Tiling Physics Simulation" Submenu. In it, you should be able to find the following properties:

Grid Size:            The amount of physics objects spawned over the tile size
Spawn Height:         The height at which the physics objects are spawned
Tile Size:            The width/height over which to spawn and tile the physics objects
Target Collection:    The collection from which to randomly spawn physics objects

It is important that the objects in "Target Collection" should be added as Rigid Bodies for the script to work properly.

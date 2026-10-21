# Blender 5.2 traps

Read this before writing a background builder. These are version facts, not style advice.

Locate the existing Blender 5.2 executable through `PATH` or the user's configured installation. If it is outside `PATH`, use its absolute path in commands. If it is unavailable, identify the required version and ask the user to provide an installation before continuing.

Run builders as:

`blender --background --python build.py`

## API

- Start from `bpy.ops.wm.read_factory_settings(use_empty=True)` when the script creates the scene. Open an existing file only to continue it.
- `bmesh.ops.create_torus` does not exist. Build a torus from a circle spun around Z, or call `bpy.ops.mesh.primitive_torus_add`.
- Sky texture enum is `MULTIPLE_SCATTERING`, `SINGLE_SCATTERING`, `PREETHAM`, or `HOSEK_WILKIE`. `NISHITA` is gone.
- `Material.use_nodes` still works and warns. Node trees are already present on new materials.
- Apply a Boolean by evaluating the object and replacing its mesh (`bpy.data.meshes.new_from_object`). `modifier_apply` often has no UI context in background mode.
- Boolean cutters must extend past the surface they cut. Delete the cutter objects after the modifier is applied.
- Cycles GPU: set the add-on compute type to `OPTIX` when an OptiX device is listed, then `scene.cycles.device = 'GPU'`. The bundled renderer falls back to CPU when GPU setup is unavailable.
- Pack every image the materials use (`image.pack()`) so the blend opens without the texture folder.

## Scale and files

- Buildings: 1 unit = 1 metre. Record the scale and the subject name in a text block named `README`.
- Save the blend in the subject folder, not the project root, when the project already separates subjects into folders.
- Put one-off builder scripts in that subject folder. Leave `render_angles.py` as the shared angle tool.

"""Render ten photography angles of the main subject in a Blender file.

Run inside Blender:

  blender --background --python render_angles.py -- --blend FILE --out DIR

Options:
  --samples N     Cycles samples (default 48)
  --scale F       Resolution multiplier (default 1)
  --front AXIS    Which side the camera treats as front: -Y +Y -X +X (default -Y)
  --detail-z F    Height fraction, 0 at the base and 1 at the top, for the close-up (default 0.62)
  --no-save       Do not write the ten cameras back into the blend file
"""

import math
import os
import sys

import bpy
from mathutils import Vector

SHOTS = (
    # name, kind, lens, resolution
    ("angle_01_low_hero", "low", 16, (1080, 1620)),
    ("angle_02_front", "body", 32, (1080, 1620)),
    ("angle_03_corner", "corner", 28, (1080, 1620)),
    ("angle_04_opposite", "opposite", 28, (1080, 1620)),
    ("angle_05_side", "side", 35, (1080, 1620)),
    ("angle_06_detail", "detail", 65, (1400, 1400)),
    ("angle_07_top", "top", 42, (1200, 1500)),
    ("angle_08_base", "base", 35, (1200, 1500)),
    ("angle_09_distant", "distant", 55, (1080, 1620)),
    ("angle_10_aerial", "aerial", 32, (1500, 1200)),
)

FRONT = {
    "-Y": Vector((0, -1, 0)),
    "+Y": Vector((0, 1, 0)),
    "-X": Vector((-1, 0, 0)),
    "+X": Vector((1, 0, 0)),
}


def args_after_double_dash():
    argv = sys.argv
    if "--" not in argv:
        return []
    return argv[argv.index("--") + 1 :]


def parse_args(argv):
    opts = {
        "blend": None,
        "out": None,
        "samples": 48,
        "scale": 1.0,
        "front": "-Y",
        "detail_z": 0.62,
        "save": True,
    }
    i = 0
    while i < len(argv):
        key = argv[i]
        if key in ("--blend", "--out", "--samples", "--scale", "--front", "--detail-z"):
            if i + 1 >= len(argv):
                raise SystemExit(f"missing value for {key}")
            val = argv[i + 1]
            i += 2
            if key == "--blend":
                opts["blend"] = val
            elif key == "--out":
                opts["out"] = val
            elif key == "--samples":
                opts["samples"] = int(val)
            elif key == "--scale":
                opts["scale"] = float(val)
            elif key == "--front":
                opts["front"] = val
            else:
                opts["detail_z"] = float(val)
        elif key == "--no-save":
            opts["save"] = False
            i += 1
        else:
            raise SystemExit(f"unknown argument {key}")
    if not opts["blend"] or not opts["out"]:
        raise SystemExit("required: --blend FILE --out DIR")
    if opts["front"] not in FRONT:
        raise SystemExit("--front must be -Y, +Y, -X, or +X")
    return opts


def rot_z(vec, degrees):
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    return Vector((vec.x * c - vec.y * s, vec.x * s + vec.y * c, 0.0))


def world_bounds(obj):
    xs, ys, zs = [], [], []
    for corner in obj.bound_box:
        w = obj.matrix_world @ Vector(corner)
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def is_ground(obj, bounds):
    name = obj.name.lower()
    if any(tok in name for tok in ("plaza", "ground", "paving", "terrain", "floor", "site")):
        return True
    minx, maxx, miny, maxy, minz, maxz = bounds
    xy = max(maxx - minx, maxy - miny)
    z = maxz - minz
    return z < 1.0 and xy > 12.0 and z < xy * 0.08


def subject_bounds():
    boxes = []
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.hide_render:
            continue
        b = world_bounds(obj)
        if is_ground(obj, b):
            continue
        boxes.append(b)
    if not boxes:
        raise SystemExit("no renderable subject meshes")
    minx = min(b[0] for b in boxes)
    maxx = max(b[1] for b in boxes)
    miny = min(b[2] for b in boxes)
    maxy = max(b[3] for b in boxes)
    minz = min(b[4] for b in boxes)
    maxz = max(b[5] for b in boxes)
    return {
        "min": Vector((minx, miny, minz)),
        "max": Vector((maxx, maxy, maxz)),
        "center": Vector(((minx + maxx) / 2, (miny + maxy) / 2, (minz + maxz) / 2)),
        "height": max(maxz - minz, 0.2),
        "plan": max(math.hypot(maxx - minx, maxy - miny) / 2, 0.2),
    }


def frame_distance(span, lens, aspect, margin):
    visible_h = span * margin
    visible_w = visible_h / aspect
    return visible_w * lens / 36.0


def setup_engine(samples):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        gpu = [d for d in prefs.devices if d.type != "CPU"]
        if gpu:
            scene.cycles.device = "GPU"
            for dev in prefs.devices:
                dev.use = dev.type != "CPU"
        else:
            scene.cycles.device = "CPU"
    except Exception as exc:
        print("GPU setup skipped", exc)
        scene.cycles.device = "CPU"
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"


def collection():
    name = "Angles"
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def place_camera(name, location, target, lens, col):
    tgt = bpy.data.objects.get(name + "_target")
    if tgt is None:
        tgt = bpy.data.objects.new(name + "_target", None)
        col.objects.link(tgt)
    tgt.location = target
    cam = bpy.data.objects.get(name)
    if cam is None:
        data = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, data)
        col.objects.link(cam)
        con = cam.constraints.new("TRACK_TO")
        con.track_axis = "TRACK_NEGATIVE_Z"
        con.up_axis = "UP_Y"
    else:
        data = cam.data
        con = cam.constraints[0] if cam.constraints else cam.constraints.new("TRACK_TO")
        con.track_axis = "TRACK_NEGATIVE_Z"
        con.up_axis = "UP_Y"
    con.target = tgt
    cam.location = location
    data.lens = lens
    data.clip_start = 0.05
    data.clip_end = 2000
    data.sensor_width = 36
    data.sensor_fit = "HORIZONTAL"
    data.shift_x = 0
    data.shift_y = 0
    return cam


def shot_pose(kind, sub, front, detail_z):
    c = sub["center"]
    base = sub["min"].z
    top = sub["max"].z
    h = sub["height"]
    plan = sub["plan"]
    aspect_portrait = 1620 / 1080

    def outside(direction, dist, z):
        direction = direction.normalized()
        return c + Vector((direction.x, direction.y, 0)) * max(dist, plan + 0.8) + Vector((0, 0, z - c.z))

    if kind == "body":
        dist = frame_distance(h, 32, aspect_portrait, 1.42)
        return outside(front, dist, base + h * 0.34), Vector((c.x, c.y, base + h * 0.50))
    if kind == "corner":
        dist = frame_distance(h, 28, aspect_portrait, 1.38)
        return outside(rot_z(front, 42), dist, base + h * 0.28), Vector((c.x, c.y, base + h * 0.48))
    if kind == "opposite":
        dist = frame_distance(h, 28, aspect_portrait, 1.38)
        return outside(rot_z(front, 198), dist, base + h * 0.30), Vector((c.x, c.y, base + h * 0.48))
    if kind == "side":
        dist = frame_distance(h, 35, aspect_portrait, 1.40)
        return outside(rot_z(front, 90), dist, base + h * 0.32), Vector((c.x, c.y, base + h * 0.50))
    if kind == "distant":
        dist = frame_distance(h, 55, aspect_portrait, 1.85)
        return outside(rot_z(front, 18), dist, base + h * 0.22), Vector((c.x, c.y, base + h * 0.46))
    if kind == "low":
        dist = frame_distance(h, 16, aspect_portrait, 1.72)
        return outside(rot_z(front, 32), dist, base + min(0.45, h * 0.015)), Vector((c.x, c.y, base + h * 0.46))
    if kind == "detail":
        span = max(h * 0.22, plan * 0.7)
        dist = frame_distance(span, 65, 1.0, 1.35)
        z = base + h * min(max(detail_z, 0.05), 0.95)
        return outside(front, dist, z), Vector((c.x, c.y, z))
    if kind == "top":
        span = max(h * 0.34, plan * 1.3)
        dist = frame_distance(span, 42, 1500 / 1200, 1.28)
        z = top - h * 0.12
        return outside(rot_z(front, 35), dist, z), Vector((c.x, c.y, top - h * 0.16))
    if kind == "base":
        span = max(h * 0.20, 2.2)
        dist = frame_distance(span, 35, 1500 / 1200, 1.35)
        z = base + min(1.45, h * 0.08)
        return outside(front, dist, z), Vector((c.x, c.y, base + span * 0.42))
    if kind == "aerial":
        dist = max(plan * 3.2, h * 0.72)
        direction = rot_z(front, 40)
        loc = c + Vector((direction.x, direction.y, 0)) * dist + Vector((0, 0, h * 0.95))
        return loc, Vector((c.x, c.y, base + h * 0.42))
    raise SystemExit(kind)


def main():
    opts = parse_args(args_after_double_dash())
    os.makedirs(opts["out"], exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(opts["blend"]))
    setup_engine(opts["samples"])
    sub = subject_bounds()
    print(
        "SUBJECT",
        "h", round(sub["height"], 2),
        "plan", round(sub["plan"], 2),
        "z", round(sub["min"].z, 2), round(sub["max"].z, 2),
    )
    front = FRONT[opts["front"]]
    col = collection()
    scene = bpy.context.scene
    scale = opts["scale"]
    for name, kind, lens, res in SHOTS:
        loc, tgt = shot_pose(kind, sub, front, opts["detail_z"])
        cam = place_camera(name, loc, tgt, lens, col)
        scene.camera = cam
        scene.render.resolution_x = max(64, int(res[0] * scale))
        scene.render.resolution_y = max(64, int(res[1] * scale))
        scene.render.resolution_percentage = 100
        scene.render.filepath = os.path.join(opts["out"], name + ".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", name)
    if opts["save"]:
        bpy.ops.wm.save_mainfile()
        print("SAVED", bpy.data.filepath)


if __name__ == "__main__":
    main()

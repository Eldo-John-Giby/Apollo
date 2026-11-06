"""Finalize the live MPFB Apollo character for explicit production mapping.

Run with MPFB enabled. Creates Apollo_Face if absent, or finalizes its live assets.
Preserves facial shape, rig and textures; splits the stock eye pair and
uniformly scales the complete hierarchy to a measured 63 mm eye spacing.
"""
from pathlib import Path
import json
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]


def create():
    from bl_ext.blender_org.mpfb.services.humanservice import HumanService
    from bl_ext.blender_org.mpfb.services.assetservice import AssetService
    from bl_ext.blender_org.mpfb.services.targetservice import TargetService
    from bl_ext.blender_org.mpfb.services.locationservice import LocationService
    macro = TargetService.get_default_macro_info_dict()
    macro.update(gender=1.0, age=0.3)
    macro['race'] = {'asian': 1.0, 'caucasian': 0.0, 'african': 0.0}
    human = HumanService.create_human(scale=.1, macro_detail_dict=macro)
    human.name = 'Apollo_Face'
    HumanService.add_builtin_rig(human, 'default')
    for sub, stem, kind in [('eyes', 'high-poly', 'Eyes'),
                            ('eyebrows', 'eyebrow001', 'Eyebrows'),
                            ('eyelashes', 'eyelashes01', 'Eyelashes')]:
        path = next(p for p in AssetService.list_mhclo_assets(sub) if p.stem == stem)
        HumanService.add_mhclo_asset(str(path), human, asset_type=kind)
    skin = next(p for p in AssetService.list_mhmat_assets('skins') if p.stem == 'young_asian_male')
    HumanService.set_character_skin(str(skin), human, skin_type='MAKESKIN')
    for side in ['left', 'right']:
        path = Path(LocationService.get_mpfb_data('targets'))/'expression'/'units'/'asian'/('eye-'+side+'-opened-up.target.gz')
        TargetService.load_target(human, str(path), weight=.65)
    from bl_ext.blender_org.mpfb.services.clothesservice import ClothesService
    bpy.context.view_layer.update()
    for name in ['Apollo_Face.eyelashes01', 'Apollo_Face.eyebrow001']:
        ClothesService.fit_clothes_to_human(bpy.data.objects[name], human, set_parent=False)


def finalize():
    human = bpy.data.objects['Apollo_Face']
    rig = bpy.data.objects['Apollo_Face.rig']
    pair = bpy.data.objects.get('Apollo_Face.high-poly')
    if pair is None:
        raise ValueError('Expected unsplit MPFB high-poly eyes; finalizer is one-shot')
    eyes = {}
    for side, sign in [('L', 1), ('R', -1)]:
        obj = pair.copy()
        obj.data = pair.data.copy()
        obj.name = 'StockEye.' + side
        bpy.context.collection.objects.link(obj)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if sign*v.co.x < 0], context='VERTS')
        bm.to_mesh(obj.data)
        bm.free()
        eyes[side] = obj
    bpy.data.objects.remove(pair, do_unlink=True)
    bpy.context.view_layer.update()
    def center(obj):
        return sum((obj.matrix_world @ Vector(p) for p in obj.bound_box), Vector()) / 8
    spacing = (center(eyes['L'])-center(eyes['R'])).length
    rig.scale *= .063 / spacing
    bpy.context.view_layer.update()
    measured = (center(eyes['L'])-center(eyes['R'])).length
    assert abs(measured-.063) < 1e-6, measured
    # Keep the startup objects available, but out of the character scene.
    for name in ['Cube', 'Camera', 'Light']:
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = True
            obj.hide_set(True)
    for poly in human.data.polygons:
        poly.use_smooth = True
    if not any(m.type == 'SUBSURF' for m in human.modifiers):
        mod = human.modifiers.new('Face smoothing', 'SUBSURF')
        mod.levels = mod.render_levels = 1
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1
    attribution = (
        'Character generated with MPFB 2.0.18 in Blender 4.5.15 LTS. '
        'MakeHuman Community hm08 base mesh/default rig; high-poly eyes; '
        'young_asian_male skin (young_lightskinned_male_diffuse3.png); '
        'eyebrow001 and eyelashes01. Selected MHCLO/MHMAT files explicitly '
        'declare CC0 release September 2020; copyright holders Data Collection AB, '
        'Joel Palmius and Jonas Hauquier. Source: http://www.makehumancommunity.org '
        'and https://github.com/makehumancommunity/mpfb2 . '
        'Packs: makehuman_system_assets_cc0.zip, skins02_cc0.zip, '
        'eyebrows01_cc0.zip, eyelashes01_cc0.zip. '
        'Adult neutral male; symmetric eye-opening targets 0.65; brows/lashes refitted; '
        'uniform scale normalized to 63 mm stock-eye bounding-box center spacing. '
        'MPFB addon is a creation dependency only, not required by the exported scene.'
    )
    mapping = {'faces_negative_y': True,
               'eyes': {s: eyes[s].name for s in 'LR'}, 'attribution': attribution}
    (ROOT/'assets/character_mapping.json').write_text(json.dumps(mapping, indent=2)+'\n', encoding='utf-8')
    (ROOT/'assets/ATTRIBUTION.md').write_text('# Character attribution\n\n'+attribution+'\n', encoding='utf-8')
    bpy.ops.file.pack_all()
    path = ROOT/'assets/base_character.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    print('CHARACTER SAVED', path, 'IPD m', measured)


if __name__ == '__main__':
    if 'Apollo_Face' not in bpy.data.objects:
        create()
    finalize()

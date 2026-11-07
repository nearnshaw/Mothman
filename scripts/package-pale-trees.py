"""Blender CLI: export versioned tree models with approved bark embedded to refresh cached assets."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];report={}
for kind in ['green_birch_tree','autumn_birch_tree']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=str(R/'assets/asset-packs'/kind/kind/(kind+'.glb')))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 def audit():
  pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
  for o in meshes:o.data.calc_loop_triangles()
  return {'triangles':sum(len(o.data.loop_triangles) for o in meshes),'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
 bpy.context.view_layer.update();before=audit()
 out=R/'assets/Models'/(kind+'-pale-bark-v4.glb')
 bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=False,export_cameras=False,export_lights=False,export_animations=False)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(out));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.context.view_layer.update();after=audit()
 assert before['triangles']==after['triangles']
 assert all(abs(a-b)<.0001 for key in ['min','max'] for a,b in zip(before[key],after[key]))
 report[kind]={'before':before,'after':after,'bytes':out.stat().st_size}
 print('AUDIT',kind,report[kind],flush=True)
Path('/tmp/mothman-detail/tree-version-audit.json').write_text(json.dumps(report,indent=2))

"""Run the exact V1/V2 scene checks without rendering or writing full qualification.

Extract the existing nested checks from the verifier, rather than maintaining a
second calibration policy. Run in a disposable Blender process before rendering.
"""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import sys
import traceback

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'wrapper'))
import eyes


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output):
    verifier = ROOT / 'tools/blender_verify.py'
    tree = ast.parse(verifier.read_text(encoding='utf-8'))
    collect = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'collect')
    rig = eyes._rig()
    namespace = {'scene': rig.scene, 'rig': rig, 'cfg': rig.cfg,
                 'eyes': eyes, 'bpy': bpy, 'math': math, 'Vector': Vector}
    checks = {}
    for label, name in [('V1', 'calibration'), ('V2', 'metrics')]:
        functions = [node for node in collect.body if isinstance(node, ast.FunctionDef) and node.name == name]
        assert len(functions) == 1, 'Verifier structure changed: ' + name
        module = ast.Module(body=functions, type_ignores=[])
        exec(compile(module, str(verifier), 'exec'), namespace)
        try:
            checks[label] = {'status': 'PASS', 'measurement': namespace[name]()}
        except Exception:
            checks[label] = {'status': 'FAIL', 'detail': traceback.format_exc()}
    result = {'schema_version': 'apollo.scene-preflight/1',
              'passed': all(check['status'] == 'PASS' for check in checks.values()),
              'qualified': False, 'checks': checks,
              'scene_sha256': digest(Path(bpy.data.filepath)),
              'verifier_sha256': digest(verifier),
              'worker_sha256': digest(Path(__file__)),
              'scope': 'Only the existing V1/V2 scene checks; full V1–V17 remains required.'}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    if not result['passed']:
        raise RuntimeError('Scene preflight failed; do not start expensive renders')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    run(args.out)

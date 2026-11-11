"""Prevent an interrupted appearance run from accepting stale scene evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    'photorealism_checks', Path(__file__).resolve().parents[1]/'tools/photorealism_checks.py')
worker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(worker)


def test_resume_rejects_scene_change(tmp_path):
    scene = tmp_path/'scene.blend'
    scene.write_bytes(b'original')
    sha = hashlib.sha256(scene.read_bytes()).hexdigest()
    out = tmp_path/'checks'
    (out/'poses').mkdir(parents=True)
    (out/'status.json').write_text(json.dumps({'stage':'anchors'}))
    (out/'scene-preflight.json').write_text(json.dumps({'scene_sha256':sha}))
    (out/'poses/progress.json').write_text(json.dumps({'run':{'scene_sha256':sha}}))
    worker.resume_anchors(scene,out)
    scene.write_bytes(b'changed')
    with pytest.raises(ValueError, match='different scene'):
        worker.resume_anchors(scene,out)


def test_resume_rejects_other_stage(tmp_path):
    (tmp_path/'status.json').write_text(json.dumps({'stage':'failed'}))
    with pytest.raises(ValueError, match='interrupted anchors'):
        worker.resume_anchors(tmp_path/'unused.blend',tmp_path)

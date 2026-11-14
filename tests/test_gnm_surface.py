"""Portable detail must stay continuous in surface space and invalidate caches."""
from pathlib import Path
import sys

import numpy as np
import pytest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
from gnm_run import surface_files
import gnm_run
from gnm_surface_maps import noise, pores


def test_surface_noise_is_chunk_independent_and_continuous():
    positions = np.random.default_rng(7).uniform(-.1, .1, (19, 3))
    combined = noise(positions, 180, 1101)
    np.testing.assert_array_equal(combined, np.concatenate([
        noise(positions[:7], 180, 1101), noise(positions[7:], 180, 1101)]))
    # Two copies of a point along different UV islands must agree. Small
    # surface perturbations must not introduce an atlas seam.
    np.testing.assert_array_equal(combined, noise(positions.copy(), 180, 1101))
    assert np.max(abs(combined - noise(positions + 1e-8, 180, 1101))) < 1e-4
    assert not np.array_equal(combined, noise(positions, 180, 2202))


def test_pore_field_uses_physical_coordinates():
    positions = np.random.default_rng(17).uniform(-.03, .03, (12, 3))
    field = pores(positions, 77)
    np.testing.assert_array_equal(field, np.concatenate([
        pores(positions[:4], 77), pores(positions[4:], 77)]))
    np.testing.assert_allclose(field, pores(positions * 2, 77, spacing=.0011))
    assert np.all((field >= 0) & (field <= 1))


def test_surface_maps_are_an_atomic_optional_pair(tmp_path):
    assert surface_files(tmp_path) == {}
    (tmp_path / 'roughness.1001.png').write_bytes(b'roughness')
    with pytest.raises(ValueError, match='both'):
        surface_files(tmp_path)
    (tmp_path / 'height.1001.png').write_bytes(b'height')
    assert set(surface_files(tmp_path)) == {'roughness', 'height'}


def test_variant_cache_changes_with_relief_and_material_recipe(tmp_path, monkeypatch):
    monkeypatch.setattr(gnm_run, 'ROOT', tmp_path)
    (tmp_path / 'tools').mkdir()
    for name in ('gnm_materials.py', 'gnm_motion_variant.py'):
        (tmp_path / 'tools' / name).write_bytes(b'recipe-v1')
    scene = tmp_path / 'scene.blend'
    scene.write_bytes(b'scene')
    for name in ('color.1001.png', 'color.1002.png', 'color.1004.png',
                 'roughness.1001.png', 'height.1001.png'):
        (tmp_path / name).write_bytes(name.encode())
    before = gnm_run.variant_identity(scene, tmp_path, 'udim')
    (tmp_path / 'height.1001.png').write_bytes(b'new relief')
    changed_map = gnm_run.variant_identity(scene, tmp_path, 'udim')
    assert before != changed_map
    (tmp_path / 'tools/gnm_materials.py').write_bytes(b'recipe-v2')
    assert changed_map != gnm_run.variant_identity(scene, tmp_path, 'udim')
    assert gnm_run.variant_identity(scene, tmp_path, 'legacy')['layout'] == 'legacy'

import copy
import importlib.util
import math
from pathlib import Path
import sys
import numpy as np
import pytest
from apollo_core.core import Config, eye_state, make_record, project, pupil_ellipse_2d, sweep_inputs
from apollo_core.metadata import validate
ROOT = Path(__file__).resolve().parents[1]

def records():
    return [make_record(k,t,h,v,Config(),f'frame_{k:02d}.png') for k,t,h,v in sweep_inputs()]

@pytest.mark.parametrize('value',[float('nan'),float('inf'),-float('inf'),True,'1'])
def test_reject_invalid_gaze(value):
    with pytest.raises(ValueError): eye_state(value,0,Config())

def test_record_clamping():
    r = make_record(0,0,2,-2,Config(),'test.png')
    assert r['input'] == {'h':1.,'v':-1.}
    assert r['extra']['clamped'] is True

@pytest.mark.parametrize('changes',[{'ipd':0},{'focal_mm':float('nan')},{'res':True},{'pupil_depth':.5}])
def test_invalid_configuration(changes):
    with pytest.raises(ValueError): Config(**changes)

@pytest.mark.parametrize('mutate',[
    lambda r: r.pop(),
    lambda r: r[0].update(frame=True),
    lambda r: r[0].update(theta=float('nan')),
    lambda r: r[0]['input'].update(h=.2),
    lambda r: r[0].update(pupil_center_2D_L=[True,1]),
    lambda r: r[0].update(pupil_center_2D_R=[1024,512]),
    lambda r: r[0].update(camera_matrix=[[1,0,0],[0,1,0],[0,0,0]]),
    lambda r: r[0].update(unknown='field'),
    lambda r: r[0]['extra'].update(image='../escape.png'),
])
def test_bad_metadata(mutate):
    data = records()
    mutate(data)
    with pytest.raises(ValueError): validate(data)

def test_geometry_validation():
    data = records()
    validate(data,Config())
    data[0]['pupil_center_2D_L'][0] += .1
    with pytest.raises(ValueError): validate(data,Config())

def test_exact_conic_boundary():
    cfg = Config()
    state,_ = eye_state(1,1,cfg)
    center,normal = state['L']['pupil3d'],state['L']['gaze']
    ellipse = pupil_ellipse_2d(center,normal,.002,cfg)
    u = np.cross(normal,[0,0,1]); u /= np.linalg.norm(u)
    v = np.cross(normal,u)
    angle = ellipse['angle']
    rotation = np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])
    for phase in np.linspace(0,2*math.pi,101):
        pixel = np.array(project(center+.002*(u*math.cos(phase)+v*math.sin(phase)),cfg))
        local = rotation.T @ (pixel-ellipse['center'])
        assert abs(np.sum((local/ellipse['semi_axes'])**2)-1) < 1e-8

def test_embedded_core_matches():
    spec = importlib.util.spec_from_file_location('sync_core',ROOT/'tools/sync_core.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.sync(check=True)

def test_standalone_wrapper_import():
    spec = importlib.util.spec_from_file_location('standalone_eyes',ROOT/'wrapper/eyes.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert np.allclose(module.eye_state(.3,.4,module.Config())[0]['L']['pupil2d'],eye_state(.3,.4,Config())[0]['L']['pupil2d'])

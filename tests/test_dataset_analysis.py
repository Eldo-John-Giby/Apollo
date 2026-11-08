import copy
from dataclasses import asdict
from pathlib import Path
import sys
import pytest
from apollo_core.core import Config,make_record
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from analyze_dataset import validate_camera


def test_dataset_independent_camera_rejects_bad_intrinsics_and_pose():
    record=make_record(0,0,0,1,Config(), 'frame.png')
    record['extra']['calibration']=asdict(Config())
    record['extra']['camera']={'position':[0.,-.4,0.],'focal_mm':100.,'sensor_mm':36.}
    validate_camera(record)
    bad=copy.deepcopy(record);bad['camera_matrix'][0][0]+=1
    with pytest.raises(ValueError,match='camera matrix'):validate_camera(bad)
    bad=copy.deepcopy(record);bad['extra']['camera']['position'][1]=-.39
    with pytest.raises(ValueError,match='camera pose'):validate_camera(bad)

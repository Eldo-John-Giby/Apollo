import importlib.util
from pathlib import Path
import sys
root = Path(__file__).resolve().parent
sys.path.insert(0, str(root))
spec = importlib.util.spec_from_file_location('core_tests', root / 'tests/test_core.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
for name in sorted(vars(module)):
    if name.startswith('test_'):
        getattr(module, name)()
        print('PASS', name)
from gazeforge_core.core import Config, make_record, sweep_inputs
from gazeforge_core.metadata import validate
validate([make_record(k, theta, h, v, Config(), f'frame_{k:02}.png') for k,theta,h,v in sweep_inputs()])
print('PASS metadata protocol')

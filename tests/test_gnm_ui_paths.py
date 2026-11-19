import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace as NS


def load(monkeypatch,screens):
    monkeypatch.setitem(sys.modules,'bpy',NS(data=NS(screens=screens)))
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'tools'))
    spec=importlib.util.spec_from_file_location('portable_ui_test',root/'tools/gnm_portable.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def test_saved_file_browser_paths_are_cleared_without_other_edits(monkeypatch):
    first=NS(directory=b'C:/Users/example/Documents',filename='private-name.blend')
    second=NS(directory=b'/home/example/assets',filename='source.png')
    unrelated=NS(directory=b'keep',filename='keep')
    screens=[NS(areas=[NS(spaces=[NS(type='FILE_BROWSER',params=first),
                                NS(type='VIEW_3D',params=unrelated)]),
                       NS(spaces=[NS(type='FILE_BROWSER',params=None)])]),
             NS(areas=[NS(spaces=[NS(type='FILE_BROWSER',params=second)])])]
    module=load(monkeypatch,screens)
    assert module.clear_file_browser_paths()==2
    assert (first.directory,first.filename)==(b'//','')
    assert (second.directory,second.filename)==(b'//','')
    assert (unrelated.directory,unrelated.filename)==(b'keep','keep')
    assert module.clear_file_browser_paths()==2


def test_empty_screens_need_no_ui_context(monkeypatch):
    assert load(monkeypatch,[]).clear_file_browser_paths()==0

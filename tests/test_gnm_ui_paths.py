import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace as NS

import pytest


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
    for params in (first,second):
        params.bl_rna=NS(properties={'directory':NS(length_max=1090),'filename':NS(length_max=256)})
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


def test_cleanup_removes_old_bytes_after_the_string_terminator(monkeypatch):
    class Params:
        def __init__(self):
            self.buffers={'directory':bytearray(1090),'filename':bytearray(256)}
            self.bl_rna=NS(properties={k:NS(length_max=len(v)) for k,v in self.buffers.items()})
            self.directory=b'C:/Users/private-user/Documents'
            self.filename='private-file-name.blend'
        def __getattr__(self,name):
            value=bytes(self.buffers[name]).split(b'\0')[0]
            return value if name=='directory' else value.decode()
        def __setattr__(self,name,value):
            if name not in ('directory','filename'):return object.__setattr__(self,name,value)
            data=value if isinstance(value,bytes) else value.encode()
            target=self.buffers[name];length=min(len(data),len(target)-1)
            target[:length]=data[:length];target[length]=0
    params=Params()
    params.directory=b'//';params.filename=''
    assert b'private-user' in params.buffers['directory']
    assert b'file-name.blend' in params.buffers['filename']
    module=load(monkeypatch,[NS(areas=[NS(spaces=[NS(type='FILE_BROWSER',params=params)])])])
    module.clear_file_browser_paths()
    assert params.directory==b'//' and params.filename==''
    assert set(params.buffers['directory'])<={0,ord('/')}
    assert set(params.buffers['filename'])<={0,ord('_')}


def test_unknown_rna_buffer_capacity_is_rejected(monkeypatch):
    params=NS(directory=b'keep',filename='keep',bl_rna=NS(properties={'directory':NS(length_max=0)}))
    module=load(monkeypatch,[NS(areas=[NS(spaces=[NS(type='FILE_BROWSER',params=params)])])])
    with pytest.raises(ValueError,match='buffer size'):module.clear_file_browser_paths()
    assert params.directory==b'keep'

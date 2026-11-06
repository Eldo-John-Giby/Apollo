"""Synchronize standalone wrapper math from its authoritative source."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def sync(check=False):
    path = ROOT/'wrapper/eyes.py'
    wrapper = path.read_text(encoding='utf-8-sig')
    core = (ROOT/'gazeforge_core/core.py').read_text(encoding='utf-8-sig')
    # Future imports must be at module start, rather than inside the embedded block.
    core = core.replace('from __future__ import annotations\n', '')
    before, tail = wrapper.split('# BEGIN CORE\n', 1)
    _, after = tail.split('# END CORE', 1)
    expected = before + '# BEGIN CORE\n' + core.rstrip() + '\n# END CORE' + after
    if check:
        if expected != wrapper:
            raise ValueError('Embedded core is out of sync')
    else:
        path.write_text(expected, encoding='utf-8')

if __name__ == '__main__':
    import sys
    sync('--check' in sys.argv)

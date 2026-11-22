"""Build a lossless single-download runtime; retain full evidence separately."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--blender', type=Path, required=True)
    args = parser.parse_args()
    source, work = args.source.resolve(), args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    index, aliases = {}, {}
    for folder in ('tools', 'apollo_core', 'licenses', 'docs', 'model', 'textures'):
        for path in sorted((source / folder).rglob('*')):
            if not path.is_file() or path.suffix == '.blend' or '__pycache__' in path.parts:
                continue
            relative = path.relative_to(source).as_posix()
            if folder == 'textures':
                digest = sha(path)
                if digest in index:
                    aliases[relative] = index[digest]
                    continue
                index[digest] = relative
            target = work / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    (work / 'asset-index.json').write_text(json.dumps(index, indent=2) + '\n')
    (work / 'texture-aliases.json').write_text(json.dumps(aliases, indent=2) + '\n')
    hydrate = '''"""Restore byte-identical shared maps, preferring hard links over copies."""
import json, os, shutil
from pathlib import Path
def hydrate():
    root = Path(__file__).resolve().parents[1]
    for name, original in json.loads((root/'texture-aliases.json').read_text()).items():
        target, source = root/name, root/original
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            try: os.link(source, target)
            except OSError: shutil.copyfile(source, target)
if __name__ == '__main__': hydrate()
'''
    (work / 'tools/shared_maps.py').write_text(hydrate)
    launcher = work / 'tools/gnm_run.py'
    text = launcher.read_text(encoding='utf-8')
    text = text.replace("    root = ROOT\n", "    root = ROOT\n    from shared_maps import hydrate\n    hydrate()\n")
    launcher.write_text(text, encoding='utf-8')
    scenes = ['model/neutral.blend', 'model/character.blend'] + [f'timelines/{mode}/expression.blend' for mode in ('left', 'right', 'generate-motion')]
    for relative in scenes:
        command = [str(args.blender), '--offline-mode', '-b', '--factory-startup', str(source / relative), '--python-exit-code', '1', '-P', str(Path(__file__).with_name('compact_scene_assets.py')), '--', str(work / relative), str(work)]
        with (work / (relative.replace('/', '-') + '.build.log')).open('w') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
        print('COMPACTED', relative, (work / relative).stat().st_size, flush=True)
    for name in ('runtime-manifest.json',):
        shutil.copyfile(source / name, work / ('original-' + name))
    (work / 'README.md').write_text('''# Apollo v0.3.0 â€” Judge Runtime

Extract this ZIP once. No split files or reassembly step is required.
Requires Blender 4.5.15 LTS and Python 3.10+. No add-ons or network connection.

Open `model/character.blend` to inspect the default character, or open any
`timelines/<mode>/expression.blend` to play its 192-frame animation.
Keep the extracted folder intact: scenes share relative-path texture files.

Render from this folder:

    python tools/gnm_run.py still --blender "<absolute Blender executable>" --out renders/hero.png
    python tools/gnm_run.py left --blender "<absolute Blender executable>" --out renders/left --first 1 --last 3
    python tools/gnm_run.py right --blender "<absolute Blender executable>" --out renders/right --first 1 --last 3
    python tools/gnm_run.py generate-motion --variant olive-amber --blender "<absolute Blender executable>" --out renders/motion --first 1 --last 3

All five original full-resolution palettes and three base motion modes remain.
The launcher automatically restores byte-identical shared maps using local hard
links (or copies when unsupported). Run `python tools/shared_maps.py` first if
using a material-binding script directly. No resampling or image recompression.

This is a packaging derivative of the full v0.3.0 archive. Original packed scenes,
576 final-quality frames, extended twelve-second scene files and detailed evidence
remain optional downloads at https://github.com/Eldo-John-Giby/Apollo/releases/tag/apollo-v0.3.0
The three twelve-second MP4 previews are included in `videos/`.
Rendering uses the original offline quality settings; it is not real-time.
See `licenses/` for redistribution terms. The tested target is public GNM Head v3;
an undisclosed organizer model is untested.
''', encoding='utf-8')
    videos = Path(__file__).resolve().parents[1] / 'videos'
    shutil.copytree(videos, work / 'videos', ignore=shutil.ignore_patterns('archive'))
    files = {p.relative_to(work).as_posix(): sha(p) for p in sorted(work.rglob('*')) if p.is_file() and not p.name.endswith('.build.log')}
    (work / 'manifest.json').write_text(json.dumps({'sha256': files, 'scope': 'Lossless repack; shared maps restored automatically. Full rendered evidence separate.'}, indent=2) + '\n')
    target = work.parent / 'VITVellore_AICA_Product.zip'
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for relative in [*files, 'manifest.json']:
            archive.write(work / relative, relative)
    print('BUILT', target, target.stat().st_size, sha(target), flush=True)


if __name__ == '__main__':
    main()

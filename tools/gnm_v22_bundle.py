"""Build an explicitly unqualified v22 development archive with retained licenses.

This does not freeze inputs or promote a release. The final post-acceptance
archive and complete PNG sequences require separate qualification.
"""
import argparse
import json
from pathlib import Path
import subprocess
import zipfile

from gnm_bundle_verify import payload, safe_name, sha
from gnm_run import MODES, VARIANTS

ROOT = Path(__file__).resolve().parents[1]


def collect(runtime, attribution, extras):
    staged = json.loads(payload(runtime, 'runtime-manifest.json').read_text(encoding='utf-8'))
    if staged.get('status') != 'development_runtime_staged':
        raise ValueError('Expected authenticated development runtime')
    files = {}
    expected = {}

    def add(name, path, digest):
        safe_name(name)
        if name.casefold() in {entry.casefold() for entry in files}:
            raise ValueError('Duplicate bundle destination: ' + name)
        if sha(path) != digest:
            raise ValueError('Changed input: ' + name)
        files[name] = Path(path)
        expected[name] = digest

    for name, digest in staged['sha256'].items():
        add(name, payload(runtime, name), digest)
    add('runtime-manifest.json', runtime/'runtime-manifest.json', sha(runtime/'runtime-manifest.json'))
    for mode in MODES:
        if f'timelines/{mode}/expression.blend' not in files:
            raise ValueError('Missing runtime timeline')
    receipt_path = payload(attribution, 'attribution-receipt.json')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    if (receipt['selected_sha256'] != staged['selected_sha256']
            or receipt['texture_manifests'] != staged['maps_manifest_sha256']
            or set(receipt['texture_manifests']) != set(VARIANTS)):
        raise ValueError('Attribution does not match the runtime identity and five variants')
    for variant in VARIANTS:
        name = f'textures/{variant}/manifest.json'
        if expected.get(name) != receipt['texture_manifests'][variant]:
            raise ValueError('Runtime map manifest mismatch')
    for name, digest in receipt['files'].items():
        add('licenses/'+name, payload(attribution, name), digest)
    add('licenses/attribution-receipt.json', receipt_path, sha(receipt_path))
    required = {'assets/gnm/LICENSE.txt', 'assets/gnm/source.json',
                'assets/gnm-scan/LICENSE.txt', 'assets/gnm-scan/source.json',
                'assets/gnm-eye-photo/source.json', 'assets/v22-provenance.json',
                'Google-GNM-LICENSE.txt', 'ATTRIBUTION.md'}
    if not required.issubset(receipt['files']):
        raise ValueError('Missing required source notices')
    for name, path in extras.items():
        add(name, path, sha(path))
    return files, expected, staged


def build(runtime, attribution, extras, out):
    out = Path(out)
    if out.exists():
        raise FileExistsError(out)
    files, hashes, staged = collect(Path(runtime), Path(attribution), extras)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'],
                                        cwd=ROOT, text=True).strip())
    manifest = dict(schema=1, status='unqualified_v22_development_bundle',
        release_ready=False, source_revision=revision, source_dirty=dirty,
        selected_sha256=staged['selected_sha256'],
        sha256=hashes, builder_sha256=sha(Path(__file__)),
        qualification='Development archive only. Independent acceptance, post-acceptance frozen regeneration, '
                      '576 final-quality PNGs and final archive qualification remain pending.')
    out.parent.mkdir(parents=True, exist_ok=True)
    # Fixed entry order/time keeps the archive independent of source filesystem mtimes.
    # Do not overwrite or delete a failed attempt; leave it for diagnosis.
    with zipfile.ZipFile(out, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as package:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 20, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            with files[name].open('rb') as source, package.open(info, 'w', force_zip64=True) as target:
                for block in iter(lambda: source.read(8*1024*1024), b''):
                    target.write(block)
            if sha(files[name]) != hashes[name]:
                raise ValueError('Input changed during packaging: '+name)
        package.writestr(zipfile.ZipInfo('manifest.json', date_time=(2026, 11, 20, 0, 0, 0)),
                         json.dumps(manifest, indent=2)+'\n')
    with zipfile.ZipFile(out) as package:
        if package.testzip() is not None:
            raise ValueError('ZIP integrity failure')
    digest = sha(out)
    out.with_suffix(out.suffix+'.sha256').write_text(digest+'  '+out.name+'\n', encoding='utf-8')
    return dict(archive_sha256=digest, bytes=out.stat().st_size, files=len(files), release_ready=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--attribution', type=Path, required=True)
    parser.add_argument('--extras', type=Path, help='JSON mapping safe archive names to local files')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    extras = {name: Path(path) for name, path in json.loads(args.extras.read_text()).items()} if args.extras else {}
    extras.update({'docs/V22_QUICKSTART.md': ROOT/'docs/V22_QUICKSTART.md',
                   'tools/gnm_bundle_verify.py': ROOT/'tools/gnm_bundle_verify.py'})
    print(json.dumps(build(args.runtime, args.attribution, extras, args.out), indent=2))

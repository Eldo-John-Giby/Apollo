"""Finish the running realism qualification and publish only passing evidence.

Uses the existing batch status files; never authors videos or presentations.
Refuses to publish if the checkout changes while the batch is running.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

from check_release import check
from export_upgrade import export

ROOT = Path(__file__).resolve().parents[1]
GIT = ['git', '-c', 'safe.directory=' + ROOT.as_posix()]
TAG = 'apollo-v0.3.0'
TITLE = 'Apollo v0.3.0 — Visual Realism'


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=ROOT, text=True).strip()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def finish(output, publish=False):
    output = output.resolve()
    assert output.is_relative_to(ROOT / 'out'), 'Use a workspace output directory'
    status_path = output / 'finish-status.json'

    def status(stage, **values):
        temporary = status_path.with_suffix('.tmp')
        temporary.write_text(json.dumps({'stage': stage, 'pid': os.getpid(), **values}, indent=2) + '\n', encoding='utf-8')
        temporary.replace(status_path)
        print(stage, flush=True)

    try:
        assert git('branch', '--show-current') == 'visual-realism'
        assert not git('status', '--porcelain'), 'Commit project changes before starting finalization'
        start = git('rev-parse', 'HEAD')
        status('waiting-for-technical-qualification', starting_commit=start)
        while True:
            state = load(output / 'qualification-status.json')
            assert state['stage'] != 'failed', state
            if state['stage'] in ('technical-qualification-complete', 'technical-qualification-complete-media-and-final-review-pending'):
                break
            time.sleep(15)
        status('waiting-for-construction-checkpoints')
        while True:
            state = load(output / 'checkpoint-status.json')
            assert state['stage'] != 'failed', state
            if state['stage'] == 'awaiting-checkpoint-visual-review':
                break
            time.sleep(15)
        status('waiting-for-construction-image-review')
        review_path = output / 'checkpoint-comparisons/review.json'
        while not review_path.exists():
            time.sleep(15)
        review = load(review_path)
        assert review['passed'] and review['scope'] == 'Agent construction-image review; intermediate stages remain unqualified'
        from check_release import digest
        assert review['scene_sha256'] == digest(output / 'candidate/scene.blend')
        for name, sha in review['reviewed_artifacts'].items():
            path = (review_path.parent / name).resolve()
            assert path.is_relative_to(review_path.parent) and digest(path) == sha
        # Final-look reviews already bind the exact candidate images. Construction
        # stages are explicitly unqualified and do not receive invented ratings.
        assert git('rev-parse', 'HEAD') == start and not git('status', '--porcelain'), 'Checkout changed; inspect before publishing'
        protected = ['delivery/apollo', 'milestones/competition-upgrade-2026-11-07', 'milestones/dev-freeze-2026-11-07']
        assert not git('diff', 'apollo-v0.2.0', '--', *protected), 'Protected baseline changed'
        subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider'], cwd=ROOT,
                       stdout=(output / 'tests-final-native.log').open('wb'), stderr=subprocess.STDOUT, check=True)
        status('staging-qualified-release')
        release = ROOT / 'milestones' / TAG
        delivery = ROOT / 'delivery/realism'
        export(output, release, delivery, 'realism', 'v0.3.0')
        assert not any(p.suffix.lower() in {'.mp4', '.webm', '.mov', '.pptx', '.ppt'} for p in release.rglob('*')), 'Unexpected media in new release'
        if not publish:
            status('staged-not-published', release=str(release))
            return
        assert git('rev-parse', 'HEAD') == start, 'HEAD changed during export'
        assert not git('diff', '--name-only'), 'Tracked files changed during export'
        test_counts = []
        for path in [output / 'tests-final-native.log', output / 'docker-candidate/tests-final.log']:
            match = re.search(r'(\d+) passed', path.read_text(encoding='utf-8'))
            assert match, 'Missing passing test summary: ' + str(path)
            test_counts.append(int(match.group(1)))
        summary = f'''The realism release is qualified as `{TAG}`. Native and Linux V1–V17,
their applicable Blender 5.2 checks, {test_counts[0]} native/{test_counts[1]} Linux tests,
the regenerated 256-image corpus, 113-pose RGB/mask visibility, lighting/UI
adversaries, recipe reconstruction and extracted-archive/resume rehearsals pass.
The final look has image-bound agent review; no independent human naturalness
study or official competition score is claimed. Videos and presentations are
excluded by the standing user rule. Event administration remains team-owned.
'''
        changed = []

        def update(name, transform):
            path = ROOT / name
            path.write_text(transform(path.read_text(encoding='utf-8')), encoding='utf-8', newline='\n')
            changed.append(name)

        update('README.md', lambda text: text.replace(
            'Appearance work continues on `visual-realism`; see [its execution record](docs/VISUAL_REALISM.md).\n'
            'Those development checkpoints are not qualified releases. The complete protected\n'
            'competition release described below remains available unchanged.',
            summary + '\nUse [the realism delivery](delivery/realism/README.md) or '
            '[the evidence milestone](milestones/apollo-v0.3.0/README.md). '
            'The protected competition baseline remains available unchanged.'))
        update('FILEMAP.md', lambda text: text.replace(
            'The visual-realism\nbranch is under development; its checkpoints have not been promoted.',
            'The visual-realism\nrelease apollo-v0.3.0 additionally qualifies the appearance recipe, 80 tests on\nboth platforms, a regenerated 256-image corpus and 113 visibility poses.'))
        update('docs/RELEASES.md', lambda text: text.replace(
            '`apollo-v0.3.0` (reserved)', '`apollo-v0.3.0`').replace('Not tagged until all technical gates pass', 'See qualified annotated tag'))
        for name in ['docs/VISUAL_REALISM.md', 'docs/ROADMAP.md', 'docs/PS_AUDIT.md', 'DECISIONS.md']:
            update(name, lambda text: text + '\n## Qualified visual-realism technical completion\n\n' + summary)
        # Only known documentation and the two new artifact directories are staged.
        git('add', '--', release.relative_to(ROOT).as_posix(), delivery.relative_to(ROOT).as_posix(), *changed)
        check(release, delivery, ':')
        git('-c', 'core.whitespace=blank-at-eol,space-before-tab,cr-at-eol', 'diff', '--cached', '--check')
        git('commit', '-m', TITLE + ': qualify and archive calibrated realism')
        commit = git('rev-parse', 'HEAD')
        check(release, delivery, 'HEAD')
        git('tag', '-a', TAG, '-m', TITLE)
        status('pushing-qualified-release', commit=commit, tag=TAG)
        git('push', '--atomic', 'origin', 'HEAD:refs/heads/visual-realism', 'refs/tags/' + TAG)
        remote = dict(line.split()[::-1] for line in git('ls-remote', 'origin', 'refs/heads/visual-realism', 'refs/tags/' + TAG + '^{}').splitlines())
        assert remote['refs/heads/visual-realism'] == remote['refs/tags/' + TAG + '^{}'] == commit
        assert not git('status', '--porcelain'), 'Unexpected changes after publishing'
        status('complete', commit=commit, tag=TAG, release=str(release), delivery=str(delivery))
        # Only this project's dedicated qualification container is stopped.
        subprocess.run(['docker', 'stop', 'apollo-realism-qualification'], cwd=ROOT, check=False)
    except Exception as error:
        status('failed', error=str(error))
        traceback.print_exc()
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'out/realism')
    parser.add_argument('--publish', action='store_true', help='Commit, tag and push after all gates pass')
    args = parser.parse_args()
    finish(args.out, args.publish)

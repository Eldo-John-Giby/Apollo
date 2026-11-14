"""Render, resume, and verify PNG frames from a packed Apollo submission timeline."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import zlib

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from submission_motion import expression


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


@contextmanager
def exclusive(path):
    # OS releases the lock even if Blender is interrupted or killed.
    with path.open('a+b') as stream:
        stream.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def valid_png(path, expected):
    try:
        with path.open('rb') as stream:
            if stream.read(8) != b'\x89PNG\r\n\x1a\n':
                return False
            first, has_data = True, False
            while header := stream.read(8):
                if len(header) != 8:
                    return False
                size, kind = struct.unpack('>I4s', header)
                if size > 64 * 1024 * 1024:
                    return False
                data = stream.read(size)
                crc = stream.read(4)
                if len(data) != size or crc != struct.pack('>I', zlib.crc32(data, zlib.crc32(kind))):
                    return False
                if first and (kind != b'IHDR' or size != 13
                              or struct.unpack('>II', data[:8]) != expected):
                    return False
                first = False
                if kind == b'IDAT':
                    has_data = True
                if kind == b'IEND':
                    return has_data and size == 0 and not stream.read(1)
    except OSError:
        pass
    return False


def run(args):
    scene = bpy.context.scene
    source = Path(bpy.data.filepath)
    if not source.is_file() or not scene.get('apollo_submission_mode'):
        raise ValueError('Open a saved timeline from submission_motion.py')
    if scene.render.engine != 'CYCLES' or scene.cycles.device != 'CPU':
        raise ValueError('Expected a CPU Cycles timeline')
    mode = scene['apollo_submission_mode']
    if args.reuse_holds and (scene.cycles.use_animated_seed or scene.render.use_motion_blur):
        raise ValueError('Hold reuse requires a fixed seed and motion blur disabled')
    all_frames = list(range(scene.frame_start, scene.frame_end + 1))
    gnm_sequence = scene.get('apollo_gnm_pose_sequence')
    if gnm_sequence is not None and len(gnm_sequence) != len(all_frames):
        raise ValueError('GNM pose sequence does not match the saved frame range')

    def pose_key(frame):
        if gnm_sequence is not None:
            return gnm_sequence[frame - all_frames[0]]
        return expression(mode, frame)

    first = args.first if args.first is not None else all_frames[0]
    last = args.last if args.last is not None else all_frames[-1]
    if not all_frames[0] <= first <= last <= all_frames[-1]:
        raise ValueError('Frame range is outside the packed timeline')
    resolution = (scene.render.resolution_x * scene.render.resolution_percentage // 100,
                  scene.render.resolution_y * scene.render.resolution_percentage // 100)
    identity = {'scene_sha256': digest(source), 'mode': mode,
                'blender': bpy.app.version_string, 'blender_build': bpy.app.build_hash.decode(),
                'resolution': list(resolution), 'samples': scene.cycles.samples,
                'fps': scene.render.fps / scene.render.fps_base,
                'range': [all_frames[0], all_frames[-1]], 'reuse_holds': args.reuse_holds}
    out = args.out.resolve()
    if args.verify_only and not out.is_dir():
        raise FileNotFoundError(out)
    out.mkdir(parents=True, exist_ok=True)
    with exclusive(out / '.render.lock'):
        receipt = out / 'render-receipt.json'
        if receipt.exists():
            state = json.loads(receipt.read_text(encoding='utf-8'))
            if state['run'] != identity:
                raise ValueError('Render settings or scene changed. Choose a fresh output directory.')
        elif args.verify_only:
            raise FileNotFoundError(receipt)
        else:
            state = {'run': identity, 'frames': {}}
            write_json(receipt, state)

        verified = set()
        holds = {}
        invalid = []
        records = state['frames']
        for frame in all_frames:
            name = f'frame_{frame:04d}.png'
            file = out / name
            if (records.get(name) and valid_png(file, resolution)
                    and digest(file) == records[name]['sha256']):
                verified.add(frame)
                if args.reuse_holds:
                    holds.setdefault(pose_key(frame), frame)
            else:
                invalid.append(frame)
        if args.verify_only:
            if invalid:
                raise ValueError(f'{len(invalid)} missing or damaged frames. First: {invalid[:10]}')
            print(f'Verified all {len(all_frames)} frames', flush=True)
            return

        scene.render.use_persistent_data = True
        scene.render.image_settings.file_format = 'PNG'
        temp = out / '.rendering.png'
        for frame in range(first, last + 1):
            if frame in verified:
                continue
            name = f'frame_{frame:04d}.png'
            key = pose_key(frame)
            original = holds.get(key)
            if original is None:
                scene.frame_set(frame)
                scene.render.filepath = str(temp)
                if bpy.ops.render.render(write_still=True) != {'FINISHED'}:
                    raise RuntimeError(f'Render failed for frame {frame}')
            else:
                shutil.copyfile(out / f'frame_{original:04d}.png', temp)
            if not valid_png(temp, resolution):
                raise RuntimeError(f'Incomplete PNG for frame {frame}')
            hash_value = digest(temp)
            temp.replace(out / name)
            records[name] = {'sha256': hash_value, 'reused_frame': original}
            write_json(receipt, state)
            if args.reuse_holds:
                holds.setdefault(key, frame)
            verified.add(frame)
            print(f'{mode}: {len(verified)}/{len(all_frames)} verified frames', flush=True)
        print(f'Verified {len(verified)}/{len(all_frames)} frames', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--first', type=int)
    parser.add_argument('--last', type=int)
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--reuse-holds', action='store_true',
                        help='Reuse exact repeated poses on unedited Apollo timelines')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    run(args)


if __name__ == '__main__':
    main()

"""Remove variable/private PNG metadata without decoding or changing image data."""
from pathlib import Path
import struct
import zlib

SIGNATURE=b'\x89PNG\r\n\x1a\n'
DROP={b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'}


def without_metadata(data):
    if not data.startswith(SIGNATURE):raise ValueError('Invalid PNG signature')
    result=bytearray(SIGNATURE);offset=8;first=True;has_data=False
    while offset<len(data):
        if offset+12>len(data):raise ValueError('Truncated PNG chunk')
        size,kind=struct.unpack_from('>I4s',data,offset)
        end=offset+size+12
        if end>len(data):raise ValueError('Truncated PNG payload')
        payload=data[offset+8:end-4]
        checksum=struct.unpack_from('>I',data,end-4)[0]
        if checksum!=zlib.crc32(payload,zlib.crc32(kind)):
            raise ValueError('Invalid PNG checksum')
        if first and (kind!=b'IHDR' or size!=13):raise ValueError('Missing PNG header')
        first=False;has_data|=kind==b'IDAT'
        if kind not in DROP:result.extend(data[offset:end])
        if kind==b'IEND':
            if size or end!=len(data) or not has_data:raise ValueError('Invalid PNG end')
            return bytes(result)
        offset=end
    raise ValueError('Missing PNG end')


def canonicalize(path):
    path=Path(path);original=path.read_bytes();clean=without_metadata(original)
    if clean!=original:
        temporary=path.with_suffix(path.suffix+'.metadata.tmp')
        temporary.write_bytes(clean);temporary.replace(path)

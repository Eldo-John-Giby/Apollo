import io
import struct
import zlib

import numpy as np
from PIL import Image,PngImagePlugin
import pytest
import cv2

from apollo_core.png import without_metadata,canonicalize


def png(note):
    image=Image.fromarray(np.arange(48,dtype=np.uint8).reshape(4,4,3))
    metadata=PngImagePlugin.PngInfo();metadata.add_text('File','C:/Users/private/'+note)
    metadata.add_text('RenderTime',note,zip=True);metadata.add_itxt('Description',note)
    stream=io.BytesIO();image.save(stream,format='PNG',pnginfo=metadata,dpi=(72,72))
    return stream.getvalue()


def test_variable_metadata_is_removed_with_identical_pixel_and_compressed_data(tmp_path):
    first=png('first');second=png('second')
    clean=without_metadata(first)
    assert clean==without_metadata(second)
    assert b'private' not in clean
    original_image=Image.open(io.BytesIO(first));clean_image=Image.open(io.BytesIO(clean))
    np.testing.assert_array_equal(np.asarray(original_image),np.asarray(clean_image))
    assert clean_image.info['dpi']==original_image.info['dpi']
    path=tmp_path/'frame.png';path.write_bytes(first);canonicalize(path)
    assert path.read_bytes()==clean
    canonicalize(path);assert path.read_bytes()==clean


def test_corrupt_or_truncated_png_is_not_rewritten(tmp_path):
    data=bytearray(png('test'));data[29]^=1
    path=tmp_path/'frame.png';path.write_bytes(data)
    with pytest.raises(ValueError,match='checksum'):canonicalize(path)
    assert path.read_bytes()==data
    with pytest.raises(ValueError,match='Truncated|Missing PNG end'):
        without_metadata(png('test')[:-5])


def test_exif_and_time_chunks_are_removed_without_changing_color_management():
    data=png('test');chunks=[]
    for kind,payload in ((b'eXIf',b'private'),(b'tIME',b'1234567'),(b'gAMA',struct.pack('>I',45455))):
        chunks.append(struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(payload,zlib.crc32(kind))))
    decorated=data[:33]+b''.join(chunks)+data[33:]
    clean=without_metadata(decorated)
    assert b'eXIf' not in clean and b'tIME' not in clean
    assert b'gAMA' in clean


def test_sixteen_bit_texture_channels_and_idat_bytes_survive():
    pixels=np.array([0,1,255,256,257,65535],dtype=np.uint16).reshape(2,3)
    pixels=np.repeat(pixels[:,:,None],3,axis=2)
    ok,encoded=cv2.imencode('.png',pixels);assert ok
    data=encoded.tobytes();payload=b'File\0C:/Users/private/scene.blend';kind=b'tEXt'
    chunk=struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(payload,zlib.crc32(kind)))
    decorated=data[:33]+chunk+data[33:]
    clean=without_metadata(decorated)
    assert clean==data
    np.testing.assert_array_equal(cv2.imdecode(np.frombuffer(clean,dtype=np.uint8),cv2.IMREAD_UNCHANGED),pixels)

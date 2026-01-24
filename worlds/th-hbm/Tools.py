import shutil
import os


def getPointerAddress(pm, base, offsets):
    address = base
    for offset in offsets[:-1]:
        address = pm.read_uint(address)
        address += offset
    return pm.read_uint(address) + offsets[-1]


def getIntFromBinaryArray(binary_array):
    """Convert a binary array to an integer."""
    result = int(''.join(map(str, binary_array[::-1])), 2)
    return result


def clamp(n, smallest, largest): return max(smallest, min(n, largest))


def copy_paste_to_path(source_file, destination_directory):
    filename = os.path.basename(source_file)
    destination_path = os.path.join(destination_directory, filename)
    if os.path.exists(destination_path):
        os.remove(destination_path)
    shutil.copy2(source_file, destination_path)
import shutil
import os


def getAddressFromPointer(pm, static_base, offsets=None):
    """
    Retrieves the "name" of the address holding data, derived from a static base address and its offsets.
    """
    # The value of a pointer holds the "name" of another address.
    # Reading the other address would yield its data.
    # e.g. th185.exe+?????'s location holds the "name" of another address.
    # Read the value held at th185.exe+????? to retrieve this "name".
    # That value is the address that the client needs.
    # It changes every time, but this helper reliably tells the client what it is.
    address = static_base
    if offsets is None: return pm.read_uint(address)
    if offsets is list:
        for offset_index in offsets[:-1]:
            address = pm.read_uint(address)
            address += offset_index
        return pm.read_uint(address)

    address = pm.read_uint(static_base)
    address += offsets
    return pm.read_uint(address)


def getPointerAddress(pm, base, offsets):
    address = base
    for offset in offsets[:-1]:
        address = pm.read_uint(address)
        address += offset
    return pm.read_uint(address) + offsets[-1]


def clamp(n, smallest, largest): return max(smallest, min(n, largest))


def copy_paste_to_path(source_file, destination_directory):
    filename = os.path.basename(source_file)
    destination_path = os.path.join(destination_directory, filename)
    if os.path.exists(destination_path):
        os.remove(destination_path)
    shutil.copy2(source_file, destination_path)

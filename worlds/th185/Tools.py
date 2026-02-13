import shutil
import os

from .variables.meta_data import *


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


def get_item_index_save_name(seed_name, team_number, slot_number) -> str:
    return LAST_INDEX_FILE_NAME + str(seed_name) + str(team_number) + str(slot_number) + JSON_EXTENSION


def convert_currency_to_joules(amount: int, currency_type: int = 0) -> int:
    if currency_type == CURRENCY_FUNDS_ID or currency_type is None:
        return amount * RATES_FUNDS_TO_JOULES
    elif currency_type == CURRENCY_BULLET_MONEY_ID:
        return amount * RATES_BULLET_MONEY_TO_JOULES
    else:
        return 0

def convert_joules_to_currency(amount: int, currency_type: int = 0) -> int:
    if currency_type == CURRENCY_FUNDS_ID or currency_type is None:
        return amount // RATES_FUNDS_TO_JOULES
    elif currency_type == CURRENCY_BULLET_MONEY_ID:
        return amount // RATES_BULLET_MONEY_TO_JOULES
    else:
        return 0

def get_energy_withdraw_tag(seed_name, currency_type: int):
    final_currency_type = "fs"

    if currency_type == CURRENCY_BULLET_MONEY_ID:
        final_currency_type = "bm"

    return str(seed_name) + "-" + final_currency_type
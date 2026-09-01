import asyncio
import unittest

import pymem

from BaseClasses import MultiWorld
from worlds.th143.utils.utils_math import get_absolute_scene_id, get_relative_scene_id

def getPointerAddress(pm, base, offsets):
    address = base
    for offset in offsets[:-1]:
        address = pm.read_uint(address)
        address += offset
    return pm.read_uint(address) + offsets[-1]

class ISCStatTest(unittest.TestCase):
    multiworld: MultiWorld

    def test_write_bit(self):
        test_bit_array = 0b0000
        test_bit_array |= 1 << 3
        print(bin(test_bit_array)) # Written right to left, indexed at 0.

    def test_read_bit(self):
        test_bit_array = 0b1101
        print(test_bit_array & 1 << 1 != 0) # Read right to left, indexed at 0.

    def test_get_absolute_scene_id(self):
        print(get_absolute_scene_id(6, 7))

    def test_get_relative_scene_id(self):
        day_id, scene_id = get_relative_scene_id(41)
        print(f"Day ID: {day_id}, Scene ID: {scene_id}")

    async def test_game_loop(self):
        def read_stage_timer() -> int:
            addrStageTimer = getPointerAddress(self.pm, self.pm.base_address + 0xe6a00, [0x4240])
            try:
                return self.pm.read_int(addrStageTimer)
            except Exception as e:
                return -1

        def read_stage_pointer() -> bool:
            stage_pointer = self.pm.read_int(self.pm.base_address + 0xe6a00)
            return stage_pointer > 0

        self.pm = pymem.Pymem(process_name="th143.exe")
        self.new_stage_restarted: bool = False
        self.first_time_enter_stage: bool = True
        while True:
            if read_stage_pointer():
                stage_timer = read_stage_timer()
                if -1 < stage_timer < 50:
                    if not self.first_time_enter_stage:
                        print("Stage has been reset.")
                        self.new_stage_restarted = True
                else:
                    self.new_stage_restarted = False
                    if self.first_time_enter_stage:
                        self.first_time_enter_stage = False
            elif not self.first_time_enter_stage:
                print("Player has left stage.")
                self.first_time_enter_stage = True

            await asyncio.sleep(0.5)
from __future__ import annotations

import ctypes
from ctypes import wintypes


VK_MEDIA_PLAY_PAUSE = 0xB3
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUTUNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUTUNION),
    ]


def build_key_inputs(virtual_key: int) -> ctypes.Array[INPUT]:
    events = (INPUT * 2)()
    events[0].type = INPUT_KEYBOARD
    events[0].ki = KEYBDINPUT(virtual_key, 0, 0, 0, 0)
    events[1].type = INPUT_KEYBOARD
    events[1].ki = KEYBDINPUT(virtual_key, 0, KEYEVENTF_KEYUP, 0, 0)
    return events


def send_virtual_key(virtual_key: int) -> None:
    events = build_key_inputs(virtual_key)
    sent = ctypes.windll.user32.SendInput(len(events), events, ctypes.sizeof(INPUT))
    if sent != len(events):
        raise ctypes.WinError()


def toggle_media_play_pause() -> None:
    send_virtual_key(VK_MEDIA_PLAY_PAUSE)

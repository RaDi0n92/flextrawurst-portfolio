#!/usr/bin/env python3
import ctypes
import os
import struct
import subprocess
import time

QUELLE = "/root/werkraum/geni_dokumentation"
SICHERUNG = "/root/werkraum/scripts/geni_dokumentation_versionsarchiv_copy.sh"

IN_CLOSE_WRITE = 0x00000008
IN_MOVED_TO = 0x00000080
IN_CREATE = 0x00000100
IN_DELETE_SELF = 0x00000400
IN_MOVE_SELF = 0x00000800
IN_IGNORED = 0x00008000
MASKE = IN_CLOSE_WRITE | IN_MOVED_TO | IN_CREATE | IN_DELETE_SELF | IN_MOVE_SELF

libc = ctypes.CDLL("libc.so.6", use_errno=True)
libc.inotify_init1.argtypes = [ctypes.c_int]
libc.inotify_init1.restype = ctypes.c_int
libc.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
libc.inotify_add_watch.restype = ctypes.c_int

def fehler(text: str) -> RuntimeError:
    nummer = ctypes.get_errno()
    return RuntimeError(f"{text}: [Errno {nummer}] {os.strerror(nummer)}")

def hauptlauf() -> None:
    fd = libc.inotify_init1(0)
    if fd < 0:
        raise fehler("inotify_init1 fehlgeschlagen")

    try:
        watch = libc.inotify_add_watch(fd, QUELLE.encode(), MASKE)
        if watch < 0:
            raise fehler("inotify_add_watch fehlgeschlagen")

        print(f"beobachtet: {QUELLE}", flush=True)
        kopf = struct.Struct("iIII")

        while True:
            daten = os.read(fd, 65536)
            position = 0
            neue_doku_fassung = False

            while position + kopf.size <= len(daten):
                _wd, maske, _cookie, namenslaenge = kopf.unpack_from(daten, position)
                position += kopf.size
                rohname = daten[position:position + namenslaenge]
                position += namenslaenge
                name = rohname.split(b"\0", 1)[0].decode("utf-8", "replace")

                if maske & (IN_DELETE_SELF | IN_MOVE_SELF | IN_IGNORED):
                    raise RuntimeError("Beobachteter Ordner wurde verschoben, geloescht oder ungueltig")

                if name.endswith(".md") and maske & (IN_CLOSE_WRITE | IN_MOVED_TO | IN_CREATE):
                    print(f"geaendert: {name}", flush=True)
                    neue_doku_fassung = True

            if neue_doku_fassung:
                time.sleep(0.2)
                subprocess.run(["/bin/bash", SICHERUNG], check=True)
    finally:
        os.close(fd)

if __name__ == "__main__":
    hauptlauf()

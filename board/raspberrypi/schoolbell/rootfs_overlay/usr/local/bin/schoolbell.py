#!/usr/bin/env python3
import datetime as dt
import os
import subprocess
import time
from pathlib import Path

import yaml

CONFIG_PATH = "/etc/schoolbell/config.yml"

DAY_MAP = {
    0: "mon",
    1: "tue",
    2: "wed",
    3: "thu",
    4: "fri",
    5: "sat",
    6: "sun",
}


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def ensure_log_path(path):
    log_dir = Path(path).parent
    log_dir.mkdir(parents=True, exist_ok=True)


def log_message(log_file, message):
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    if log_file:
        ensure_log_path(log_file)
        with open(log_file, "a", encoding="utf-8") as handle:
            handle.write(line)
    else:
        print(line, end="")


def set_volume(volume):
    try:
        subprocess.run(
            ["amixer", "sset", "Master", f"{volume}%"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass


def play_audio(audio_path, device):
    if not Path(audio_path).exists():
        return False

    command = ["aplay", "-q"]
    if device:
        command.extend(["-D", device])
    command.append(audio_path)
    result = subprocess.run(command, check=False)
    return result.returncode == 0


def should_trigger(entry, now):
    entry_time = entry.get("time")
    if not entry_time:
        return False
    return entry_time == now.strftime("%H:%M")


def main():
    config = load_config()
    settings = config.get("settings", {})
    schedule = config.get("schedule", [])

    audio_device = settings.get("audio_device", "")
    audio_volume = settings.get("audio_volume", 90)
    log_file = settings.get("log_file")

    set_volume(audio_volume)

    last_trigger = {}

    log_message(log_file, "School bell service started.")

    while True:
        now = dt.datetime.now()
        today = now.date()
        day_name = DAY_MAP[now.weekday()]

        for entry in schedule:
            name = entry.get("name", "(tanpa nama)")
            days = entry.get("days", [])
            if days and day_name not in days:
                continue

            if not should_trigger(entry, now):
                continue

            entry_key = f"{name}-{entry.get('time')}-{today.isoformat()}"
            if last_trigger.get(entry_key):
                continue

            repeat = max(int(entry.get("repeat", 1)), 1)
            interval = max(int(entry.get("interval_seconds", 2)), 1)
            audio_path = entry.get("audio")

            if not audio_path:
                log_message(log_file, f"Lewati {name}: audio tidak diatur.")
                last_trigger[entry_key] = True
                continue

            log_message(log_file, f"Memutar {name} ({audio_path}).")
            success = True
            for idx in range(repeat):
                if not play_audio(audio_path, audio_device):
                    success = False
                    break
                if idx < repeat - 1:
                    time.sleep(interval)

            if not success:
                log_message(log_file, f"Gagal memutar {name}.")
            last_trigger[entry_key] = True

        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - safety net
        log_message("/var/log/schoolbell.log", f"Service berhenti: {exc}")
        raise

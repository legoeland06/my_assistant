#!/usr/bin/env python3
"""
vocal_stt.py — Reconnaissance vocale pour my_assistant.

Écoute le micro (VAD : seuil RMS, arrêt après silence), puis transcrit
l'échantillon avec faster-whisper (modèle Systran/faster-whisper-base).

Ce script est conçu pour être exécuté avec l'environnement vocal du poste :
    /home/legoeland/piper/piper_env/bin/python3 vocal_stt.py [max_secondes] [device]

Sortie : texte transcrit sur stdout (chaîne vide si rien d'intelligible).

Usage :
    vocal_stt.py                # défauts : 6 s max, micro MIC_DEVICE
    vocal_stt.py 8              # 8 secondes max
    vocal_stt.py 6 plughw:CARD=U20,DEV=0
"""

import os
import struct
import subprocess
import sys
import tempfile
import time
import wave

RATE = 16000
SEUIL = float(os.environ.get("VOCAL_SEUIL", "700"))
SILENCE_STOP = 1.5  # secondes de silence pour couper
BLOCK = int(RATE * 0.1)  # blocs de 100 ms
MIN_VOIX = 3  # blocs consécutifs au-dessus du seuil pour démarrer l'écoute
DEVICE_DEFAUT = os.environ.get("MIC_DEVICE", "plughw:CARD=U20,DEV=0")


def enregistre(device: str, max_sec: float) -> bytes:
    """Enregistre via arecord avec VAD. Retourne le PCM brut (ou b'' si silence)."""
    proc = subprocess.Popen(
        ["arecord", "-D", device, "-r", str(RATE), "-f", "S16_LE", "-c", "1", "-t", "raw"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    buf = bytearray()
    silence = 0.0
    started = False
    voix = 0
    t0 = time.time()
    try:
        while time.time() - t0 < max_sec:
            data = proc.stdout.read(BLOCK * 2)
            if not data:
                break
            buf += data
            n = len(data) // 2
            s = struct.unpack("<%dh" % n, data[: n * 2])
            rms = (sum(x * x for x in s) / n) ** 0.5
            if rms > SEUIL:
                voix += 1
                if voix >= MIN_VOIX:
                    started = True
                silence = 0.0
            elif started:
                silence += 0.1
                if silence >= SILENCE_STOP:
                    break
    finally:
        proc.kill()
    return bytes(buf) if started else b""


def transcrit(raw: bytes) -> str:
    """Transcrit le PCM brut via faster-whisper. Retourne le texte ou ''."""
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(raw)

        from faster_whisper import WhisperModel

        model = WhisperModel("Systran/faster-whisper-base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(path, language="fr", beam_size=1)
        return " ".join(seg.text.strip() for seg in segments).strip()
    finally:
        os.unlink(path)


def main() -> None:
    max_sec = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
    device = sys.argv[2] if len(sys.argv) > 2 else DEVICE_DEFAUT
    try:
        raw = enregistre(device, max_sec)
        if not raw:
            print("")
            return
        print(transcrit(raw))
    except Exception as e:
        print(f"vocal_stt : {e}", file=sys.stderr)
        print("")


if __name__ == "__main__":
    main()

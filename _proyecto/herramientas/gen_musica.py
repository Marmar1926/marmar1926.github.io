"""Compone una música de fondo original, tranquila y en loop, para la presentación.
Pad suave + piano en arpegios + una melodía sencilla + bajo, con reverberación.
Uso: python3 _proyecto/herramientas/gen_musica.py  ->  presentacion/musica/ruta.mp3"""
import os, subprocess
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
BPM = 72
BEAT = 60 / BPM
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
rng = np.random.default_rng(7)

def hz(n):  # número MIDI -> Hz
    return 440 * 2 ** ((n - 69) / 12)

# progresión (4 tiempos cada acorde): Cmaj9 · Am7 · Fmaj7 · G6sus  /  Em7 · Am7 · Dm9 · Gsus
PROG_A = [[48, 55, 59, 62, 64], [45, 52, 55, 60, 64], [41, 48, 52, 57, 60], [43, 50, 55, 60, 62]]
PROG_B = [[40, 47, 55, 59, 62], [45, 52, 55, 60, 64], [38, 45, 53, 57, 64], [43, 50, 55, 60, 62]]
FORM = [PROG_A, PROG_A, PROG_B, PROG_A, PROG_B, PROG_A, PROG_A, PROG_B, PROG_A, PROG_B, PROG_B, PROG_A]   # 12 vueltas de 4 compases = 48 compases (2 min 40 s)
BARS = sum(len(p) for p in FORM)
TOTAL = BARS * 4 * BEAT
N = int(TOTAL * SR)
mix = np.zeros((N, 2))

def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N:
        return
    seg = sig[: N - i] * gain
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    mix[i:i + len(seg), 0] += seg * l
    mix[i:i + len(seg), 1] += seg * r

def piano(f, dur, vel=1.0):
    t = np.arange(int((dur + 2.5) * SR)) / SR
    env = np.exp(-t * 2.2) * (1 - np.exp(-t * 400))
    s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * k * 0.9) for k, a in [(1, 1), (2, .45), (3, .18), (4, .08)])
    return s * env * vel * 0.22

def pad(fs, dur):
    t = np.arange(int((dur + 1.5) * SR)) / SR
    att, rel = 1.2, 1.5
    env = np.clip(t / att, 0, 1) * np.clip((dur + rel - t) / rel, 0, 1)
    s = np.zeros_like(t)
    for f in fs:
        for det in (-0.12, 0.0, 0.11):
            ff = hz(f + 12) * 2 ** (det / 12)
            s += np.sin(2 * np.pi * ff * t + rng.uniform(0, 6)) + 0.25 * np.sin(4 * np.pi * ff * t)
    return s * env * 0.022

def bass(f, dur):
    t = np.arange(int((dur + .4) * SR)) / SR
    env = np.clip(t / 0.03, 0, 1) * np.exp(-t * 0.9) * np.clip((dur + .3 - t) / .3, 0, 1)
    return (np.sin(2 * np.pi * hz(f - 12) * t) + 0.3 * np.sin(4 * np.pi * hz(f - 12) * t)) * env * 0.16

# melodía (en tiempos) para las vueltas A: notas largas y cantables
MEL_A = [(0, 76, 1.5), (1.5, 74, .5), (2, 72, 2), (4, 72, 1.5), (5.5, 71, .5), (6, 69, 2),
         (8, 69, 1), (9, 72, 1), (10, 76, 2), (12, 74, 3), (15, 72, 1)]
MEL_B = [(0, 79, 2), (2, 76, 2), (4, 76, 1.5), (5.5, 74, .5), (6, 72, 2), (8, 77, 2), (10, 76, 1), (11, 74, 1), (12, 74, 4)]

bar = 0
for v, prog in enumerate(FORM):
    t0 = bar * 4 * BEAT
    for c, ch in enumerate(prog):
        tc = t0 + c * 4 * BEAT
        add(pad(ch[1:], 4 * BEAT), tc, 0, 1)
        add(bass(ch[0], 4 * BEAT * .95), tc, 0, 1)
        # arpegio de piano en corcheas, distinto patrón según la vuelta
        notes = ch[1:] + [ch[2] + 12]
        pat = [0, 1, 2, 3, 4, 3, 2, 1] if v % 2 == 0 else [0, 2, 1, 3, 2, 4, 3, 1]
        if v == 0 and c < 2:
            pat = [0, None, 2, None, 4, None, 2, None]           # comienzo más despojado
        for k, n in enumerate(pat):
            if n is None:
                continue
            vel = 0.55 + 0.15 * (k == 0) + rng.uniform(-.05, .05)
            add(piano(hz(notes[n] + 12), BEAT / 2, vel), tc + k * BEAT / 2 + rng.uniform(0, .012), -0.35 + 0.1 * n, 1)
    if v > 0:
        mel = MEL_A if prog is PROG_A else MEL_B
        for b, n, d in mel:
            add(piano(hz(n), d * BEAT, 0.9), t0 + b * BEAT, 0.25, 1.1)
    bar += len(prog)

# reverberación (respuesta al impulso sintética) y loop sin corte: la cola vuelve al comienzo
ir_len = int(3.2 * SR)
tt = np.arange(ir_len) / SR
ir = rng.standard_normal((ir_len, 2)) * np.exp(-tt * 2.1)[:, None]
ir[0] = [1, 1]
wet = np.stack([fftconvolve(mix[:, i], ir[:, i]) for i in range(2)], axis=1)
dry_tail = np.zeros_like(wet); dry_tail[:N] = mix
out = dry_tail * 0.75 + wet * 0.09
tail = out[N:]
out = out[:N]
out[:len(tail)] += tail
sos = butter(2, 9000, 'low', fs=SR, output='sos')
out = sosfilt(sos, out, axis=0)
out /= np.max(np.abs(out)) / 0.89

os.makedirs(f'{ROOT}/presentacion/musica', exist_ok=True)
wav = '/tmp/ruta.wav'
import wave
with wave.open(wav, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-c:a', 'libmp3lame', '-b:a', '128k',
                f'{ROOT}/presentacion/musica/ruta.mp3'], check=True)
print('listo', round(TOTAL, 1), 's')

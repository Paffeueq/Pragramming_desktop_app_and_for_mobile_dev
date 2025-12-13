#!/usr/bin/env python3
"""
Generator test WAV pliku do transkrypcji
Tworzy prosty plik WAV z tonem testowym (16 kHz, mono)
"""

import wave
import struct
import math

def create_test_wav(filename="test_audio.wav", duration=3, frequency=440):
    """
    Tworzy plik WAV z tonem sinusoidalnym
    Args:
        filename: nazwa pliku WAV
        duration: czas trwania w sekundach
        frequency: częstotliwość tonu w Hz
    """
    sample_rate = 16000  # 16 kHz - wymagane przez Azure Speech
    channels = 1        # Mono
    sample_width = 2    # 16-bit
    
    num_frames = int(sample_rate * duration)
    
    # Generuj próbki
    frames = []
    for i in range(num_frames):
        # Sinusoida
        sample = math.sin(2 * math.pi * frequency * i / sample_rate)
        # Konwertuj do 16-bit integer
        sample_int = int(sample * 32767)
        frames.append(struct.pack('<h', sample_int))
    
    # Zapisz WAV
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    print(f"✅ Plik WAV utworzony: {filename}")
    print(f"   - Częstotliwość próbkowania: {sample_rate} Hz (16 kHz)")
    print(f"   - Kanały: {channels} (Mono)")
    print(f"   - Trwanie: {duration} s")
    print(f"   - Rozmiar: {len(b''.join(frames)) / 1024:.1f} KB")

if __name__ == "__main__":
    # Utwórz testowy plik WAV
    create_test_wav("test_audio.wav", duration=3, frequency=440)

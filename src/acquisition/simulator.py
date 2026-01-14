"""
Señal Base (Subsuelo): Una frecuencia baja (ej. 2 Hz).

Ruido de Red Eléctrica: Una interferencia fuerte de 50Hz o 60Hz (dependiendo si el "proyecto" es en Chile o Canadá).

Ruido Blanco: Ruido aleatorio del entorno.
"""
# src\adquisition\simulator.py

import numpy as np
import matplotlib.pyplot as plt

def generate_geophysical_signal(duration, fs, target_freq=2.0, noise_power=0.5):
    """
    Simula la lectura de un sensor de 24 bits.
    fs: Frecuencia de muestreo (ej. 1000 Hz)
    """
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    # 1. Señal pura del subsuelo
    signal = np.sin(2 * np.pi * target_freq * t)
    
    # 2. Ruido de línea eléctrica (60 Hz) - El enemigo número 1
    power_noise = 1.5 * np.sin(2 * np.pi * 60 * t)
    
    # 3. Ruido blanco (Gaussiano)
    white_noise = np.random.normal(0, noise_power, len(t))
    
    # Señal capturada por el sensor
    raw_signal = signal + power_noise + white_noise
    
    return t, raw_signal, signal

if __name__ == "__main__":
    t, raw, clean = generate_geophysical_signal(duration=1.0, fs=1000)
    plt.figure(figsize=(10, 4))
    plt.plot(t, raw, label="Señal Cruda (Sensor)")
    plt.plot(t, clean, label="Señal Real (Deseada)", alpha=0.8)
    plt.legend()
    plt.title("Simulación de Captura de Datos - Sensor 24 bits")
    plt.show()
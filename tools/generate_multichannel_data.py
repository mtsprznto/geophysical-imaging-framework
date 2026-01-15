# tools\generate_multichannel_data.py

import numpy as np
import os

def generate_multichannel_survey(filename="data/raw/survey_24ch.raw", duration_sec=10, fs=24000, n_channels=24):
    os.makedirs("data", exist_ok=True)
    n_samples_per_ch = duration_sec * fs
    
    print(f"Generando {n_channels} canales...")
    
    # Creamos una matriz (canales x muestras)
    # Cada canal tendrá una señal de 2.0Hz con ruidos de 60Hz de distinta intensidad
    data_matrix = np.zeros((n_channels, n_samples_per_ch), dtype=np.float32)
    
    t = np.linspace(0, duration_sec, n_samples_per_ch, endpoint=False)
    
    for ch in range(n_channels):
        # Señal base + 60Hz que varía por canal + ruido blanco
        noise_amp = 0.1 * (ch + 1) # El ruido aumenta con el número de canal
        data_matrix[ch] = 0.5 * np.sin(2 * np.pi * 2.0 * t) + \
                          noise_amp * np.sin(2 * np.pi * 60.0 * t) + \
                          0.02 * np.random.randn(n_samples_per_ch)
    
    # Guardamos los datos. En geofísica pro, solemos guardar canal tras canal
    with open(filename, "wb") as f:
        f.write(data_matrix.tobytes())
    
    print(f"Archivo multicanal listo: {filename} ({data_matrix.nbytes / (1024**2):.1f} MB)")

if __name__ == "__main__":
    generate_multichannel_survey()
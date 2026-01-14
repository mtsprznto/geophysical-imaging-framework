# tools\generate_raw_data.py
import numpy as np
import os

def generate_big_survey(filename="data/raw/survey_giant.raw", duration_sec=60, fs=24000):
    os.makedirs("data", exist_ok=True)
    n_samples = duration_sec * fs
    print(f"Generando {n_samples:,} muestras (~{n_samples*4 / (1024**2):.1f} MB)...")
    
    # Simular señal con mucho ruido de 60Hz y tendencia (drift)
    t = np.linspace(0, duration_sec, n_samples, endpoint=False)
    # Señal geofísica + Ruido 60Hz + Ruido aleatorio
    signal = 0.1 * np.sin(2 * np.pi * 2.0 * t) + \
             0.5 * np.sin(2 * np.pi * 60.0 * t) + \
             0.05 * np.random.randn(n_samples)
    
    signal = signal.astype(np.float32)
    
    with open(filename, "wb") as f:
        f.write(signal.tobytes())
    
    print(f"Archivo guardado en: {filename}")

if __name__ == "__main__":
    generate_big_survey()
# test\test_spectral_analyzer.py
import numpy as np
from src.processing.cpp_bridge import (
    c_load_raw_data, 
    c_apply_multichannel_filter, 
    c_calculate_spectrum
)
from src.visualization.plots import plot_spectral_comparison

def run_spectral_analysis():
    # 1. Configuración
    FILENAME = "data/raw/survey_24ch.raw"
    N_CHANNELS = 24
    FS = 24000
    DURATION = 1.0  # 1 segundo es suficiente para un buen análisis espectral
    N_SAMPLES_PER_CH = int(FS * DURATION)
    
    # Frecuencias que queremos monitorear
    # 2Hz (Señal útil), 60Hz (Ruido), 120Hz (Armónico)
    target_freqs = np.array([2.0, 60.0, 120.0], dtype=np.float32)

    print(f"--- Analizador Espectral Multicanal (C++ Engine) ---")

    # 2. Carga de datos
    raw_flat = c_load_raw_data(FILENAME, N_CHANNELS * N_SAMPLES_PER_CH)
    data_matrix = raw_flat.reshape((N_CHANNELS, N_SAMPLES_PER_CH))

    # 3. Análisis Espectral PRE-Filtrado
    print("Analizando espectro inicial...")
    mag_pre = c_calculate_spectrum(data_matrix, float(FS), target_freqs)

    # 4. Filtrado (Notch 60Hz)
    from scipy import signal
    b, a = signal.iirnotch(60.0, 30.0, FS)
    sos = signal.tf2sos(b, a).flatten().astype(np.float32)
    zi_matrix = np.zeros((N_CHANNELS, (len(sos)//6) * 2), dtype=np.float32)

    print("Filtrando 24 canales...")
    filtered_matrix, _ = c_apply_multichannel_filter(data_matrix, sos, zi_matrix)

    # 5. Análisis Espectral POST-Filtrado
    print("Analizando espectro final...")
    mag_post = c_calculate_spectrum(filtered_matrix, float(FS), target_freqs)

    # 6. Mostrar Resultados Cuantitativos (QC Report)
    print("\n" + "="*50)
    print(f"{'CANAL':<8} | {'2Hz (Señal)':<12} | {'60Hz (Ruido)':<12} | {'REDUCCIÓN 60Hz'}")
    print("-" * 50)
    
    reducciones = []
    for i in range(N_CHANNELS):
        red_db = 20 * np.log10(mag_pre[i, 1] / (mag_post[i, 1] + 1e-9))
        reducciones.append(red_db)
        print(f"CH {i+1:02d}    | {mag_post[i,0]:.4f}     | {mag_post[i,1]:.4f}     | {red_db:.2f} dB")
    
    print("="*50)
    print(f"Reducción promedio del ruido: {np.mean(reducciones):.2f} dB")

    # 7. Visualización
    plot_spectral_comparison(target_freqs, mag_pre, mag_post)



if __name__ == "__main__":
    run_spectral_analysis()
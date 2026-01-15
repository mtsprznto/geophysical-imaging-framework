# test\test_multichannel.py
import time
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

from src.processing.cpp_bridge import c_load_raw_data, c_apply_multichannel_filter
from src.visualization.plots import plot_multichannel_wiggle

def run_multichannel_test():
    # 1. Configuración
    FILENAME = "data/raw/survey_24ch.raw"
    N_CHANNELS = 24
    FS = 24000
    DURATION = 2.0  
    N_SAMPLES_PER_CH = int(FS * DURATION)
    TOTAL_SAMPLES = N_CHANNELS * N_SAMPLES_PER_CH

    print(f"--- Análisis Multicanal: {N_CHANNELS} Canales ---")
    
    # 2. Carga y Reshape
    raw_flat = c_load_raw_data(FILENAME, TOTAL_SAMPLES)
    data_matrix = raw_flat.reshape((N_CHANNELS, N_SAMPLES_PER_CH))

    # 3. Preparación de Filtros y Estados
    b, a = signal.iirnotch(60.0, 30.0, FS)
    sos = signal.tf2sos(b, a).flatten().astype(np.float32)
    
    # Matriz de estados: un estado por cada canal
    zi_single = signal.sosfilt_zi(sos.reshape(-1, 6)).astype(np.float32)
    zi_matrix = np.tile(zi_single, (N_CHANNELS, 1, 1)).astype(np.float32)

    # 4. Procesamiento Paralelo C++ (OpenMP)
    print(f"Filtrando con OpenMP...")
    start_t = time.perf_counter()
    
    filtered_matrix, _ = c_apply_multichannel_filter(data_matrix, sos, zi_matrix)
    
    print(f"Completado en: {time.perf_counter() - start_t:.6f}s")

    # 5. Visualización Delegada
    plot_multichannel_wiggle(data_matrix, filtered_matrix, FS)
    plt.show()

if __name__ == "__main__":
    run_multichannel_test()
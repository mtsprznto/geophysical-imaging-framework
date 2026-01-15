# test\test_stacking_refinement.py

"""
Dividirá una señal larga en varios segmentos (ventanas de tiempo).

Procesará cada segmento con el filtro Notch.

Usará tu nueva función de C++ para promediarlos todos.
"""

import numpy as np
import time
import matplotlib.pyplot as plt
from scipy import signal

from src.processing.cpp_bridge import c_load_raw_data, c_apply_multichannel_filter, c_compute_stacking
from src.visualization.plots import plot_stacking_comparison

def run_stacking_test():
    # 1. Configuración
    FILENAME = "data/raw/survey_24ch.raw"
    FS = 24000
    N_SEGMENTS = 10     # Vamos a promediar 10 bloques de tiempo
    SEGMENT_DURATION = 0.5 # Cada bloque dura medio segundo
    SAMPLES_PER_SEG = int(FS * SEGMENT_DURATION)
    
    print(f"--- Refinamiento por Stacking (Motor C++) ---")

    # 2. Cargar datos para un canal (CH1)
    # Cargamos suficiente data para extraer los N segmentos
    total_needed = N_SEGMENTS * SAMPLES_PER_SEG
    raw_long = c_load_raw_data(FILENAME, total_needed)
    
    # Reshape para tener la matriz de segmentos (N_SEGMENTS, SAMPLES_PER_SEG)
    segments_matrix = raw_long.reshape((N_SEGMENTS, SAMPLES_PER_SEG))

    # 3. Paso de Filtrado Notch (Q=100) en cada segmento
    b, a = signal.iirnotch(60.0, 100.0, FS)
    sos = signal.tf2sos(b, a).flatten().astype(np.float32)
    zi = np.zeros((N_SEGMENTS, (len(sos)//6) * 2), dtype=np.float32)
    
    filtered_segments, _ = c_apply_multichannel_filter(segments_matrix, sos, zi)

    # 4. APLICAR STACKING (C++)
    print(f"Realizando stacking de {N_SEGMENTS} segmentos en paralelo...")
    start_t = time.perf_counter()
    stacked_signal = c_compute_stacking(filtered_segments)
    print(f"Stacking completado en: {time.perf_counter() - start_t:.6f}s")

    # 5. Visualización desde el módulo de plots
    t = np.linspace(0, SEGMENT_DURATION, SAMPLES_PER_SEG)
    plot_stacking_comparison(t, filtered_segments[0], stacked_signal, N_SEGMENTS)
    plt.show()

if __name__ == "__main__":
    run_stacking_test()
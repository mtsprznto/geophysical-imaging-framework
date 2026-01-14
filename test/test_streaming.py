# test\test_streaming.py

from src.processing.stream_filters import GeophysicalStreamFilter
from src.acquisition.simulator import generate_geophysical_signal
import matplotlib.pyplot as plt
import numpy as np

from src.visualization.plots import plot_streaming_results


# ------------------
def run_test():
    # 1. Configuración
    FS = 1000
    CHUNK_DURATION = 1.0
    TOTAL_CHUNKS = 5
    CHUNK_SIZE = int(FS * CHUNK_DURATION)

    stream_filter = GeophysicalStreamFilter(fs=FS)
    full_raw = []
    full_filtered = []

    print(f"Iniciando streaming: {TOTAL_CHUNKS} bloques de {CHUNK_SIZE} muestras cada uno...")

    # 2. Bucle de procesamiento
    for i in range(TOTAL_CHUNKS):
        # Simulación de llegada de datos
        t, chunk_raw, _ = generate_geophysical_signal(duration=CHUNK_DURATION, fs=FS)
        
        # Procesamiento manteniendo estado interno (memoria del filtro)
        chunk_filtered = stream_filter.process_chunk(chunk_raw)
        
        # Acumulación para QA final
        full_raw.extend(chunk_raw)
        full_filtered.extend(chunk_filtered)
        print(f"Bloque {i+1}/{TOTAL_CHUNKS} [OK]")

    # 3. Visualización delegada
    plot_streaming_results(full_raw, full_filtered, FS, CHUNK_SIZE)
    plt.show()

if __name__ == "__main__":
    run_test()
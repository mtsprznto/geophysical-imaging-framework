# test\test_raw_processing.py
"""
Este archivo será tu prototipo de "Software de Estación de Campo". Leerá el binario usando C++, lo filtrará usando C++, y usará tus funciones de plots.py para el control de calidad (QC).
"""

import matplotlib.pyplot as plt
from src.processing.cpp_bridge import c_load_raw_data
from src.processing.stream_filters import GeophysicalStreamFilter
from src.visualization.plots import plot_geophysical_time_series
import time

def run_raw_analysis():
    # 1. Configuración
    FILENAME = "data/raw/survey_giant.raw"
    FS = 24000
    # Queremos leer y procesar 5 segundos de ese archivo gigante (donde sea que esté)
    SAMPLES_TO_PROCESS = FS * 5 
    
    print(f"--- Iniciando Procesamiento de Datos Crudos (C++) ---")
    
    # 2. Carga ultrarrápida con C++
    start_load = time.perf_counter()
    raw_data = c_load_raw_data(FILENAME, SAMPLES_TO_PROCESS)
    load_time = time.perf_counter() - start_load
    print(f"Carga de datos: {load_time:.6f}s")
    
    # 3. Filtrado con el motor C++ (Notch 60Hz)
    # Nota: Tu clase stream_filter ya usa C++ internamente si está disponible
    engine = GeophysicalStreamFilter(fs=FS, notch_freq=60.0, use_cpp=True)
    
    start_proc = time.perf_counter()
    filtered_data = engine.process_chunk(raw_data)
    proc_time = time.perf_counter() - start_proc
    print(f"Filtrado (C++): {proc_time:.6f}s")

    # 4. Visualización de QC
    import numpy as np
    t = np.linspace(0, 5, len(raw_data))
    
    # Usamos tu librería de plots
    fig = plot_geophysical_time_series(t, raw_data, filtered_data, 
                                      title="QC: Datos Crudos vs Filtrados (Motor C++)")
    plt.show()

if __name__ == "__main__":
    run_raw_analysis()
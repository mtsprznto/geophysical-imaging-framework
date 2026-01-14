# benchmark_performance.py

import time
import numpy as np
from src.processing.stream_filters import GeophysicalStreamFilter
from src.visualization.plots import plot_benchmark_results

def run_benchmark():
    FS = 1000
    N_SAMPLES = 2_000_000 # Aumentamos muestras para notar la diferencia
    N_ITERATIONS = 50      # Promediamos 50 ejecuciones
    chunk_data = np.random.randn(N_SAMPLES).astype(np.float32)
    
    print(f"--- Benchmark Geofísico: {N_SAMPLES:,} muestras ({N_ITERATIONS} iteraciones) ---")

    # Inicializar filtros
    filter_py = GeophysicalStreamFilter(FS, use_cpp=False)
    filter_cpp = GeophysicalStreamFilter(FS, use_cpp=True)

    # --- TEST 1: MOTOR PYTHON ---
    print("Midiendo Python...")
    times_py = []
    for _ in range(N_ITERATIONS):
        t0 = time.perf_counter()
        _ = filter_py.process_chunk(chunk_data)
        times_py.append(time.perf_counter() - t0)
    avg_py = np.mean(times_py)

    # --- TEST 2: MOTOR C++ ---
    print("Midiendo C++...")
    times_cpp = []
    for _ in range(N_ITERATIONS):
        t0 = time.perf_counter()
        _ = filter_cpp.process_chunk(chunk_data)
        times_cpp.append(time.perf_counter() - t0)
    avg_cpp = np.mean(times_cpp)

    # --- RESULTADOS Y GRÁFICO ---
    print(f"\nResultado Final:")
    print(f"Python: {avg_py:.6f}s | C++: {avg_cpp:.6f}s")
    
    plot_benchmark_results(avg_py, avg_cpp, N_SAMPLES)

if __name__ == "__main__":
    run_benchmark()
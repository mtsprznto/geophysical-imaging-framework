# main_processor.py
import numpy as np
import time
import matplotlib.pyplot as plt
from src.processing.cpp_bridge import (
    c_load_raw_data, 
    c_apply_multichannel_filter, 
    c_compute_stacking, 
    c_calculate_spectrum
)
from src.processing.geophysics import compute_apparent_resistivity
from src.visualization.plots import plot_multichannel_wiggle, plot_sounding_curve
from scipy import signal

def run_master_workflow():
    print("==========================================================")
    print("   GEOPHYSICAL IMAGING FRAMEWORK - MASTER PROCESSOR")
    print("==========================================================\n")

    # --- CONFIGURACIÓN ---
    FILENAME = "data/raw/survey_24ch.raw"
    FS = 24000
    N_CHANNELS = 24
    N_SEGMENTS = 15          # Para un stacking robusto
    SEGMENT_SEC = 0.5        # Bloques de medio segundo
    SAMPLES_PER_SEG = int(FS * SEGMENT_SEC)
    
    # Frecuencias para el sondeo final (log-spaced)
    target_freqs = np.logspace(0.5, 3, 20).astype(np.float32)

    # 1. CARGA MASIVA (C++)
    print(f"[*] Cargando {N_CHANNELS} canales desde {FILENAME}...")
    start_time = time.perf_counter()
    total_samples = N_CHANNELS * N_SEGMENTS * SAMPLES_PER_SEG
    raw_flat = c_load_raw_data(FILENAME, total_samples)
    
    # Reshape a (Canales, Segmentos, Muestras)
    data_cube = raw_flat.reshape((N_CHANNELS, N_SEGMENTS, SAMPLES_PER_SEG))
    print(f"[OK] Datos cargados en {time.perf_counter() - start_time:.4f}s\n")

    # 2. FILTRADO NOTCH PRO (C++ / OpenMP)
    # Aplicamos Q=100 para garantizar >30dB de reducción de ruido de línea
    print(f"[*] Aplicando Filtro Notch (60Hz, Q=100) en paralelo...")
    b, a = signal.iirnotch(60.0, 100.0, FS)
    sos = signal.tf2sos(b, a).flatten().astype(np.float32)
    
    # Procesamos todos los segmentos de todos los canales de un solo golpe
    # Aplanamos temporalmente para el bridge multicanal
    flat_segments = data_cube.reshape((N_CHANNELS * N_SEGMENTS, SAMPLES_PER_SEG))
    zi = np.zeros((N_CHANNELS * N_SEGMENTS, (len(sos)//6) * 2), dtype=np.float32)
    
    filtered_flat, _ = c_apply_multichannel_filter(flat_segments, sos, zi)
    filtered_cube = filtered_flat.reshape((N_CHANNELS, N_SEGMENTS, SAMPLES_PER_SEG))
    print("[OK] Filtrado completado.\n")

    # 3. STACKING (C++ / OpenMP)
    print(f"[*] Ejecutando Stacking Estadístico ({N_SEGMENTS} promedios por canal)...")
    stacked_data = np.zeros((N_CHANNELS, SAMPLES_PER_SEG), dtype=np.float32)
    for ch in range(N_CHANNELS):
        stacked_data[ch] = c_compute_stacking(filtered_cube[ch])
    print("[OK] Señales maestras generadas.\n")

    # 4. CÁLCULO DE RESISTIVIDAD (Geophysics Engine)
    print("[*] Calculando Resistividad Aparente (Cagniard Transfer)...")
    # Usamos CH1 como Eléctrico (E) y CH2 como Magnético (H)
    mags = c_calculate_spectrum(stacked_data[:2], float(FS), target_freqs)
    rho = compute_apparent_resistivity(mags[0], mags[1], target_freqs)

    # 5. GENERACIÓN DE REPORTES (Visualization Engine)
    print("[*] Generando visualizaciones finales...")
    
    # Reporte 1: QC de Trazas
    plot_multichannel_wiggle(stacked_data, stacked_data, FS, 
                             title="Master QC: Trazas Finales (Filtradas + Stacked)")
    
    # Reporte 2: Curva de Sondeo
    plot_sounding_curve(target_freqs, rho, 
                        title="Resultado Final: Curva de Sondeo Magnetotelúrico")

    print("\n==========================================================")
    print(f"   PROCESAMIENTO FINALIZADO EXITOSAMENTE")
    print(f"   Tiempo total: {time.perf_counter() - start_time:.4f}s")
    print("==========================================================")
    plt.show()

if __name__ == "__main__":
    run_master_workflow()
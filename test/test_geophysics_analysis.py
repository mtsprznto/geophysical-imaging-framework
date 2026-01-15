# test\test_geophysics_analysis.py
import numpy as np
import matplotlib.pyplot as plt
from src.processing.cpp_bridge import c_load_raw_data, c_apply_multichannel_filter, c_calculate_spectrum
from src.processing.geophysics import compute_apparent_resistivity
from src.visualization.plots import plot_sounding_curve
from scipy import signal

def run_geophysics_test():
    # 1. Configuración
    FILENAME = "data/raw/survey_24ch.raw"
    FS = 24000
    freqs = np.logspace(0.5, 3, 15).astype(np.float32) # De 3Hz a 1000Hz

    # 2. Carga y Filtrado Pro (+30 dB)
    raw_data = c_load_raw_data(FILENAME, 24 * FS * 5).reshape((24, FS * 5))
    
    # MEJORA PARA >30dB: Aumentamos Q a 100 para un Notch más profundo
    b, a = signal.iirnotch(60.0, 100.0, FS) 
    sos = signal.tf2sos(b, a).flatten().astype(np.float32)
    zi = np.zeros((24, (len(sos)//6) * 2), dtype=np.float32)
    
    print("Filtrando con Q=100 para máxima atenuación...")
    filtered_data, _ = c_apply_multichannel_filter(raw_data, sos, zi)

    # 3. Cálculo de Magnitudes en C++
    print("Analizando espectros de canales E (CH1) y H (CH2)...")
    mags = c_calculate_spectrum(filtered_data[:2], float(FS), freqs)

    # 4. Obtener Resistividad
    rho = compute_apparent_resistivity(mags[0], mags[1], freqs)

    # 5. Visualizar
    plot_sounding_curve(freqs, rho, title="QC: Resistividad Aparente (Canal 1 vs 2)")
    plt.show()

if __name__ == "__main__":
    run_geophysics_test()
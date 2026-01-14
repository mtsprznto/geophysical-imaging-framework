# test\inicial_test.py
from src.acquisition.simulator import generate_geophysical_signal
from src.processing.filters import apply_notch_filter, get_fft, apply_lowpass
import matplotlib.pyplot as plt

from src.visualization.plots import plot_comparison_dashboard

# 1. Parámetros

# --------------------------------------------------------------
# Precausion con ejecutar esto.
# FS = 24000          # ex: 24 kHz (muestreo de alta resolución)
# DURATION = 36000    # ex: 10 horas * 60 min * 60 seg = 36,000 segundos
# pc se traba.
# FS = 24000
# DURATION = 600 # 10 minutos
# --------------------------------------------------------------

#------------------
def run_test():
    # Example estable
    FS = 1000  
    DURATION = 2.0 
    # 2. Generar señal cruda
    t, raw, clean = generate_geophysical_signal(DURATION, FS, target_freq=2.0)

    # 3. Aplicar Filtros
    # Paso A: Quitar los 60Hz de la red eléctrica
    notch_data = apply_notch_filter(raw, 60.0, FS)
    # Paso B: Quitar ruido blanco por encima de 10Hz
    final_data = apply_lowpass(notch_data, 10.0, FS)
    
    # 4. Análisis de Fourier (FFT) para demostrar éxito
    f_raw, m_raw = get_fft(raw, FS)
    f_final, m_final = get_fft(final_data, FS)

    
    # 5. Visualización Delegada
    # Llamamos a nuestra función externa para que dibuje
    plot_comparison_dashboard(t, raw, final_data, f_raw, m_raw, f_final, m_final)
    plt.show()

# Esto permite que sigas pudiendo ejecutar este archivo solo si quieres
if __name__ == "__main__":
    run_test()
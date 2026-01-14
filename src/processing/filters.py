"""
FFT (Fast Fourier Transform): Para "ver" las frecuencias. Un geofísico no mira solo ondas, mira espectros.

Notch Filter (Filtro de Muesca): Para eliminar quirúrgicamente los 60Hz (o 50Hz) de la red eléctrica.
"""

"""
Fase Zero: signal.filtfilt aplica el filtro dos veces (adelante y atrás). Esto asegura que la fase de la señal no se desplace. En Magnetotelúrica (MT), la fase es tan importante como la amplitud para calcular la profundidad del conductor. Si desplazas la fase, el geofísico interpretará que el mineral está a 800m cuando está a 1000m. ¡Error crítico!
"""

import numpy as np
from scipy import signal

def apply_notch_filter(data, target_freq, fs, quality_factor=30.0):
    """
    Elimina una frecuencia específica (ej. 60Hz) usando un filtro de muesca.
    """
    b, a = signal.iirnotch(target_freq, quality_factor, fs)
    filtered_data = signal.filtfilt(b, a, data)
    return filtered_data

def get_fft(data, fs):
    """
    Calcula la Transformada Rápida de Fourier para análisis espectral.
    """
    n = len(data)
    freq = np.fft.rfftfreq(n, d=1/fs)
    magnitude = np.abs(np.fft.rfft(data))
    return freq, magnitude

def apply_lowpass(data, cutoff, fs, order=5):
    """
    Filtro pasa-bajos para eliminar ruido blanco de alta frecuencia.
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = signal.filtfilt(b, a, data)
    return filtered_data
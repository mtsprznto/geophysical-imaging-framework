import logging
import numpy as np
from scipy import signal


# Intentamos importar el bridge de C++
try:
    from .cpp_bridge import c_apply_sos_filter
    CPP_AVAILABLE = True
except Exception as e:
    logging.warning(f"Motor C++ no disponible: {e}. Usando motor SciPy (Lento).")
    CPP_AVAILABLE = False

class GeophysicalStreamFilter:
    def __init__(self, fs, notch_freq=60.0, lowpass_cutoff=10.0, use_cpp=True):
        self.fs = fs
        self.use_cpp = use_cpp and CPP_AVAILABLE # Solo usa C++ si el usuario quiere Y está disponible
        
        # 1. Diseño de coeficientes (Se hace igual para ambos motores)
        b_notch, a_notch = signal.iirnotch(notch_freq, 30.0, fs)
        self.notch_sos = signal.tf2sos(b_notch, a_notch).astype(np.float32)
        self.notch_zi = signal.sosfilt_zi(self.notch_sos).astype(np.float32)

        # 2. Si usamos C++, preparamos los datos para el formato de la DLL (aplanados)
        if self.use_cpp:
            self.notch_sos_flat = self.notch_sos.flatten()
            self.notch_zi_flat = self.notch_zi.flatten()
            print("--- Motor de procesamiento: C++ (DLL) ---")
        else:
            print("--- Motor de procesamiento: Python (SciPy) ---")

    def process_chunk(self, chunk_data):
        """Procesa un bloque usando el mejor motor disponible."""
        
        if self.use_cpp:
            # --- RUTA C++ ---
            filtered, self.notch_zi_flat = c_apply_sos_filter(
                chunk_data, 
                self.notch_sos_flat, 
                self.notch_zi_flat
            )
            return filtered
        else:
            # --- RUTA PYTHON (Anterior) ---
            filtered, self.notch_zi = signal.sosfilt(
                self.notch_sos, chunk_data, zi=self.notch_zi
            )
            return filtered
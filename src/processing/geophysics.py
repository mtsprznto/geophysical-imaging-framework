# src\processing\geophysics.py

import numpy as np
def compute_apparent_resistivity(mag_E, mag_H, freqs):
    """
    Calcula la resistividad aparente (Rho) usando la fórmula de Cagniard.
    
    mag_E: Magnitud del campo eléctrico (mV/km o V/m)
    mag_H: Magnitud del campo magnético (nT)
    freqs: Array de frecuencias en Hz
    """
    # Constante de permeabilidad del vacío (simplificada para geofísica MT)
    # Rho = 0.2 * T * |E/H|^2  donde T es el periodo (1/f)
    # Esta es la fórmula práctica usada en exploración.
    
    period = 1.0 / freqs
    impedance_Z = mag_E / (mag_H + 1e-9)
    
    # La fórmula de Cagniard simplificada:
    resistivity = 0.2 * period * (impedance_Z**2)
    
    return resistivity

def compute_phase(data_E, data_H):
    """
    (Opcional para más adelante) 
    La fase indica si hay cambios bruscos de conductores en profundidad.
    """
    # Por ahora retornamos ceros, pero es el siguiente nivel de realismo
    return np.zeros_like(data_E)
# src\processing\cpp_bridge.py
import ctypes
from ctypes import POINTER, c_float, c_int, c_char_p
import sys
import numpy as np
import os


# Localizar la DLL
# 1. Localizar rutas
base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
build_path = os.path.join(base_path, "build")
lib_path = os.path.join(build_path, "libfiltros.dll")

# 2. FIX para Windows y dependencias de MSYS2
if sys.platform == "win32":
    # Añadimos la carpeta build al buscador de DLLs
    os.add_dll_directory(build_path)
    # IMPORTANTE: También necesitamos las librerías de MSYS2 para que la DLL funcione
    # Reemplaza esta ruta con la de tu instalación de MSYS2 si es diferente
    msys_bin_path = r"D:\msys64\ucrt64\bin" 
    if os.path.exists(msys_bin_path):
        os.add_dll_directory(msys_bin_path)

try:
    lib = ctypes.CDLL(lib_path)
    print(f"--- Librería C++ cargada exitosamente desde {lib_path} ---")
    
    lib = ctypes.CDLL(lib_path)
    
    #--------------------------------------------------
    # Configurar apply_sos_filter_work
    # Argumentos: x (float*), y (float*), n_samples (int), n_sections (int), sos (float*), zi (float*)
    lib.apply_sos_filter_work.argtypes = [
        ctypes.POINTER(ctypes.c_float), # x
        ctypes.POINTER(ctypes.c_float), # y
        ctypes.c_int,                   # n_samples
        ctypes.c_int,                   # n_sections
        ctypes.POINTER(ctypes.c_float), # sos
        ctypes.POINTER(ctypes.c_float)  # zi
    ]
    lib.apply_sos_filter_work.restype = None
    #--------------------------------------------------
    lib.load_binary_data.argtypes = [
        ctypes.c_char_p,                # filename
        ctypes.POINTER(ctypes.c_float), # buffer
        ctypes.c_int                    # n_samples
    ]
    lib.load_binary_data.restype = ctypes.c_int
    #--------------------------------------------------
    lib.apply_sos_filter_multichannel.argtypes = [
        ctypes.POINTER(ctypes.c_float), # input
        ctypes.POINTER(ctypes.c_float), # output
        ctypes.c_int,                   # n_channels
        ctypes.c_int,                   # n_samples
        ctypes.c_int,                   # n_sections
        ctypes.POINTER(ctypes.c_float), # sos
        ctypes.POINTER(ctypes.c_float)  # zi
    ]
    lib.apply_sos_filter_multichannel.restype = None
    #--------------------------------------------------
    lib.calculate_magnitude_spectrum.argtypes = [
        ctypes.POINTER(ctypes.c_float), # input
        ctypes.POINTER(ctypes.c_float), # output_mag
        ctypes.c_int,                   # n_channels
        ctypes.c_int,                   # n_samples
        ctypes.c_float,                 # fs
        ctypes.POINTER(ctypes.c_float), # target_freqs
        ctypes.c_int                    # n_freqs
    ]
    lib.calculate_magnitude_spectrum.restype = None
    #--------------------------------------------------
    lib.compute_stacking.argtypes = [
        ctypes.POINTER(ctypes.c_float), # data
        ctypes.POINTER(ctypes.c_float), # output
        ctypes.c_int,                   # n_segments
        ctypes.c_int                    # segment_size
    ]
    lib.compute_stacking.restype = None

    #--------------------------------------------------
    lib.c_interpolate_resistivity.argtypes = [
        POINTER(c_float), # input_rho
        c_int,            # in_rows
        c_int,            # in_cols
        POINTER(c_float), # output_rho
        c_int,            # out_rows
        c_int             # out_cols
    ]
    lib.c_interpolate_resistivity.restype = None
    #--------------------------------------------------

except OSError as e:
    print(f"Error: No se pudo cargar la librería en {lib_path}. ¿Ejecutaste la compilación?")
    raise e

# ------------------------------------------

def c_apply_sos_filter(data, sos_coeffs, zi_states):
    """
    Interface de Python para el motor C++ SOS.
    """
    # 1. Asegurar que los datos sean float32 (el float de C++) y contiguos en memoria
    data = np.ascontiguousarray(data, dtype=np.float32)
    sos_coeffs = np.ascontiguousarray(sos_coeffs, dtype=np.float32)
    zi_states = np.ascontiguousarray(zi_states, dtype=np.float32)
    
    n_samples = len(data)
    n_sections = len(sos_coeffs) // 6
    output = np.zeros(n_samples, dtype=np.float32)

    # 2. Obtener punteros
    x_ptr = data.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    y_ptr = output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    sos_ptr = sos_coeffs.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    zi_ptr = zi_states.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    # 3. Llamada al motor C++
    lib.apply_sos_filter_work(x_ptr, y_ptr, n_samples, n_sections, sos_ptr, zi_ptr)

    return output, zi_states

def c_load_raw_data(filename, n_samples):
    """Carga datos binarios usando el motor C++"""
    output = np.zeros(n_samples, dtype=np.float32)
    output_ptr = output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    
    # El string debe convertirse a bytes para C++
    result = lib.load_binary_data(filename.encode('utf-8'), output_ptr, n_samples)
    
    if result < 0:
        raise Exception(f"Error al leer el archivo. Código: {result}")
        
    return output[:result] # Retorna solo lo leído

def c_apply_multichannel_filter(data_matrix, sos_coeffs, zi_matrix):
    n_ch, n_samples = data_matrix.shape
    n_sections = len(sos_coeffs) // 6
    output = np.zeros_like(data_matrix, dtype=np.float32)
    
    lib.apply_sos_filter_multichannel(
        data_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        output.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        n_ch, n_samples, n_sections,
        sos_coeffs.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        zi_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    )
    return output, zi_matrix

def c_calculate_spectrum(data_matrix, fs, target_freqs):
    n_ch, n_samples = data_matrix.shape
    n_freqs = len(target_freqs)
    output_mag = np.zeros((n_ch, n_freqs), dtype=np.float32)
    
    freqs_ptr = np.ascontiguousarray(target_freqs, dtype=np.float32).ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    
    lib.calculate_magnitude_spectrum(
        data_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        output_mag.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        n_ch, n_samples, fs, freqs_ptr, n_freqs
    )
    return output_mag

def c_compute_stacking(data_segments):
    """
    Recibe una matriz de (n_segments, segment_size) y devuelve el promedio.
    """
    n_seg, seg_size = data_segments.shape
    output = np.zeros(seg_size, dtype=np.float32)
    
    lib.compute_stacking(
        data_segments.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        output.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        n_seg, seg_size
    )
    return output


def c_interpolate_data(rho_matrix, new_shape):
    in_rows, in_cols = rho_matrix.shape
    out_rows, out_cols = new_shape
    
    # Usamos c_float y POINTER importados arriba
    input_ptr = rho_matrix.astype(np.float32).ctypes.data_as(POINTER(c_float))
    output_rho = np.zeros(new_shape, dtype=np.float32)
    output_ptr = output_rho.ctypes.data_as(POINTER(c_float))
    
    # CAMBIO: Usamos 'lib' (definida arriba) no '_lib'
    lib.c_interpolate_resistivity(
        input_ptr, in_rows, in_cols,
        output_ptr, out_rows, out_cols
    )
    return output_rho



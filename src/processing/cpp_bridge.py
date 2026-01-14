import ctypes
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

    lib.load_binary_data.argtypes = [
        ctypes.c_char_p,                # filename
        ctypes.POINTER(ctypes.c_float), # buffer
        ctypes.c_int                    # n_samples
    ]
    lib.load_binary_data.restype = ctypes.c_int

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
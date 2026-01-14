# src\visualization\plots.py

import matplotlib.pyplot as plt
import numpy as np

def plot_geophysical_time_series(
        t, 
        raw, 
        filtered, 
        title="Procesamiento de Señal"
):
    """Compara señal cruda vs filtrada en el tiempo."""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(t, raw, label="Cruda", color='gray', alpha=0.5)
    ax.plot(t, filtered, label="Filtrada", color='blue', linewidth=1.5)
    ax.set_title(title)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Amplitud")
    ax.legend()
    return fig

def plot_spectrum_comparison(
        f_raw, 
        m_raw, 
        f_clean, 
        m_clean
):
    """Visualiza la eliminación de ruidos en el dominio de la frecuencia."""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.semilogy(f_raw, m_raw, label="Espectro Crudo", alpha=0.6)
    ax.semilogy(f_clean, m_clean, label="Espectro Filtrado", color='red')
    ax.set_xlim(0, 150) # Enfocado en ruidos de 60Hz y bajas frecuencias
    ax.set_title("Análisis de Densidad Espectral")
    ax.legend()
    return fig

def plot_comparison_dashboard(
        t, 
        raw, 
        final, 
        f_raw, 
        m_raw, 
        f_final, 
        m_final
):
    """Genera un dashboard profesional comparando tiempo y frecuencia."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Panel 1: Tiempo
    ax1.plot(t, raw, label="Señal Cruda", alpha=0.5, color='gray')
    ax1.plot(t, final, label="Señal Filtrada", color='red', linewidth=1.5)
    ax1.set_title("Análisis en el Dominio del Tiempo (Limpieza)")
    ax1.set_ylabel("Amplitud")
    ax1.legend()

    # Panel 2: Frecuencia
    ax2.semilogy(f_raw, m_raw, label="Espectro Crudo", alpha=0.6)
    ax2.semilogy(f_final, m_final, label="Espectro Limpio", color='red')
    ax2.set_title("Análisis de Frecuencia (FFT)")
    ax2.set_xlabel("Frecuencia (Hz)")
    ax2.set_ylabel("Magnitud")
    ax2.set_xlim(0, 150) 
    ax2.legend()

    plt.tight_layout()
    return fig

def plot_streaming_results(
        full_raw, 
        full_filtered, 
        fs, 
        chunk_size, 
        title="Procesamiento en Tiempo Real"
):
    """Visualiza el resultado del streaming marcando las divisiones de los bloques."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(full_raw, label="Señal Cruda (Entrada)", alpha=0.3, color='gray')
    ax.plot(full_filtered, label="Señal Filtrada (Salida)", color='green', linewidth=1.5)
    
    # Dibujar líneas punteadas donde ocurre cada cambio de bloque para verificar continuidad
    total_samples = len(full_raw)
    for x in range(chunk_size, total_samples, chunk_size):
        ax.axvline(x=x, color='black', linestyle='--', alpha=0.2)
    
    ax.set_title(title)
    ax.set_xlabel("Muestras (Samples)")
    ax.set_ylabel("Amplitud")
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    return fig

def plot_benchmark_results(
        avg_py, 
        avg_cpp, 
        n_samples
):
    """
    Genera un gráfico de barras comparando el rendimiento de los motores.
    """
    labels = ['Python (SciPy)', 'C++ (DLL)']
    times = [avg_py, avg_cpp]
    colors = ['#3776ab', '#00599c'] # Colores oficiales de Python y C++

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, times, color=colors)
    
    plt.ylabel('Tiempo de procesamiento (segundos)')
    plt.title(f'Benchmark: Procesamiento de {n_samples:,} muestras')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Añadir etiquetas de tiempo sobre las barras
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, 
                 f'{yval:.6f}s', va='bottom', ha='center', fontweight='bold')

    # Calcular speedup para el título secundario
    speedup = avg_py / avg_cpp if avg_cpp > 0 else 0
    plt.suptitle(f'Rendimiento Superior: {speedup:.1f}x más rápido', 
                 fontsize=12, color='darkgreen', y=0.92)

    plt.tight_layout()
    plt.show()



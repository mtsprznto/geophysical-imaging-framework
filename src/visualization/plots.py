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

def plot_multichannel_wiggle(raw_matrix, filtered_matrix, fs, title="Control de Calidad Multicanal"):
    """
    Crea un gráfico de trazas (Wiggle Plot) para inspección visual de múltiples canales.
    """
    n_ch = raw_matrix.shape[0]
    n_samples = raw_matrix.shape[1]
    t = np.arange(n_samples) / fs
    
    # Creamos un layout vertical denso
    fig, axes = plt.subplots(n_ch, 1, figsize=(12, 14), sharex=True, 
                             gridspec_kw={'hspace': 0.05})
    
    fig.suptitle(title, fontsize=16, y=0.95)

    for i in range(n_ch):
        # Normalización local por canal para comparar formas de onda
        # Añadimos un pequeño epsilon para evitar división por cero
        scale = np.max(np.abs(raw_matrix[i])) + 1e-9
        
        # Graficamos la señal cruda (fondo) y la filtrada (frente)
        axes[i].plot(t, raw_matrix[i] / scale, color='gray', alpha=0.3, label='Crudo' if i==0 else "")
        axes[i].plot(t, filtered_matrix[i] / scale, color='blue', alpha=0.8, linewidth=1, label='Filtrado' if i==0 else "")
        
        # Estética de osciloscopio de campo
        axes[i].set_ylabel(f"CH{i+1:02d}", rotation=0, labelpad=25, verticalalignment='center')
        axes[i].set_yticks([])
        axes[i].grid(True, axis='x', alpha=0.2)
        
        if i == 0: 
            axes[i].legend(loc='upper right', frameon=False)

    plt.xlabel("Tiempo (segundos)")
    # Ajuste fino de márgenes
    plt.subplots_adjust(left=0.1, right=0.95, top=0.92, bottom=0.05)
    
    return fig

def plot_spectral_comparison(freqs, mag_pre, mag_post):
    plt.figure(figsize=(12, 6))
    
    # Graficamos el promedio de todos los canales para ver la tendencia
    plt.bar(freqs - 2, np.mean(mag_pre, axis=0), width=4, label='Antes del Filtro', color='gray', alpha=0.5)
    plt.bar(freqs + 2, np.mean(mag_post, axis=0), width=4, label='Después del Filtro', color='green', alpha=0.8)

    plt.yscale('log')
    plt.xticks(freqs, [f'{f} Hz' for f in freqs])
    plt.ylabel("Magnitud (Escala Log)")
    plt.title("Eficacia del Filtro: Comparativa de Magnitud por Frecuencia (Promedio 24 CH)")
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

def plot_sounding_curve(freqs, resistivity, title="Sondeo Magnetotelúrico"):
    """
    Gráfico log-log estándar para resistividad aparente.
    """
    plt.figure(figsize=(8, 6))
    plt.loglog(freqs, resistivity, 'o-', color='#e67e22', linewidth=2, markersize=8)
    
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.xlabel("Frecuencia (Hz) [Alta frec = Superficial]")
    plt.ylabel("Resistividad Aparente (Ohm-m)")
    plt.title(title)
    
    # En geofísica, invertimos el eje X porque las frecuencias bajas 
    # penetran a mayor profundidad (izquierda = profundo, derecha = somero)
    plt.gca().invert_xaxis() 
    
    return plt.gcf()

def plot_stacking_comparison(t, individual_segment, stacked_signal, n_segments):
    """
    Visualiza la reducción de ruido aleatorio mediante el promedio de segmentos.
    """
    plt.figure(figsize=(12, 6))
    
    # El segmento individual representa la medición ruidosa
    plt.plot(t, individual_segment, color='gray', alpha=0.3, 
             label=f'Segmento Individual (Filtrado Notch)')
    
    # La señal stacked es el resultado del motor C++
    plt.plot(t, stacked_signal, color='#d63031', linewidth=2, 
             label=f'Resultado Stacking (Promedio de {n_segments} bloques)')
    
    plt.title(f"Control de Calidad: Mejora de Relación Señal/Ruido (SNR) via Stacking", fontsize=14)
    plt.xlabel("Tiempo (s)")
    plt.ylabel("Amplitud Normalizada")
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.2)
    
    # Ajustamos márgenes para que se vea limpio
    plt.tight_layout()
    
    return plt.gcf()


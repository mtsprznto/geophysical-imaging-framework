// src\cpp\filtros.cpp
// compilar:
// ❯ g++ -O3 -shared -o build/libfiltros.dll src/cpp/filtros.cpp

// g++ -O3 -shared -fopenmp -o build/libfiltros.dll src/cpp/filtros.cpp
#include <vector>
#include <fstream>
#include <cmath>
#include <omp.h>

extern "C"
{
    /**
     * Procesa un bloque de datos usando secciones de segundo orden (SOS).
     * x: puntero a los datos de entrada
     * y: puntero donde se guardará la salida
     * n_samples: cantidad de muestras en este bloque
     * n_sections: número de secciones del filtro (usualmente 2 o 3)
     * sos: coeficientes [b0, b1, b2, 1.0, a1, a2] por cada sección
     * zi: estados internos del filtro (memoria) para dar continuidad
     */
    void apply_sos_filter_work(float *x, float *y, int n_samples, int n_sections, float *sos, float *zi)
    {
        for (int i = 0; i < n_samples; ++i)
        {
            float val = x[i];
            for (int s = 0; s < n_sections; ++s)
            {
                float *b = &sos[s * 6];
                float *a = &sos[s * 6 + 3];
                float *z = &zi[s * 2];

                // Ecuación de diferencia (Forma Directa II Transpuesta)
                float out = b[0] * val + z[0];
                z[0] = b[1] * val - a[1] * out + z[1];
                z[1] = b[2] * val - a[2] * out;
                val = out; // La salida de esta sección es la entrada de la siguiente
            }
            y[i] = val;
        }
    }

    /**
     * Carga un archivo binario directamente a un buffer de memoria.
     * Útil para archivos masivos donde Python es lento leyendo.
     */
    int load_binary_data(const char *filename, float *buffer, int n_samples)
    {
        std::ifstream file(filename, std::ios::binary);
        if (!file)
            return -1;

        file.read(reinterpret_cast<char *>(buffer), n_samples * sizeof(float));

        if (file.gcount() == 0)
            return -2;

        return (int)(file.gcount() / sizeof(float)); // Retorna muestras leídas
    }

    /**
     * Calcula la magnitud del espectro para un conjunto de frecuencias.
     * Esto es una versión simplificada (estilo Goertzel/DFT) para detectar
     * componentes específicas en los 24 canales en paralelo.
     */
    void calculate_magnitude_spectrum(float *input, float *output_mag, int n_channels,
                                      int n_samples, float fs, float *target_freqs, int n_freqs)
    {

#pragma omp parallel for
        for (int ch = 0; ch < n_channels; ch++)
        {
            float *ch_input = &input[ch * n_samples];
            float *ch_output = &output_mag[ch * n_freqs];

            for (int f = 0; f < n_freqs; f++)
            {
                float freq = target_freqs[f];
                float omega = 2.0 * M_PI * freq / fs;
                float real = 0.0, imag = 0.0;

                for (int n = 0; n < n_samples; n++)
                {
                    real += ch_input[n] * cos(n * omega);
                    imag -= ch_input[n] * sin(n * omega);
                }
                ch_output[f] = sqrt(real * real + imag * imag) / n_samples;
            }
        }
    }

    // Procesa múltiples canales en paralelo
    void apply_sos_filter_multichannel(float *input, float *output, int n_channels,
                                       int n_samples, int n_sections,
                                       float *sos, float *zi)
    {

// Esta línea es la "magia": reparte el bucle entre los hilos de la CPU
#pragma omp parallel for
        for (int ch = 0; ch < n_channels; ch++)
        {
            // Calculamos los offsets para este canal específico
            float *ch_input = &input[ch * n_samples];
            float *ch_output = &output[ch * n_samples];
            float *ch_zi = &zi[ch * n_sections * 2];

            // Reutilizamos la lógica muestra a muestra para cada canal
            for (int i = 0; i < n_samples; ++i)
            {
                float val = ch_input[i];
                for (int s = 0; s < n_sections; ++s)
                {
                    float *b = &sos[s * 6];
                    float *a = &sos[s * 6 + 3];
                    float *z = &ch_zi[s * 2];

                    float out = b[0] * val + z[0];
                    z[0] = b[1] * val - a[1] * out + z[1];
                    z[1] = b[2] * val - a[2] * out;
                    val = out;
                }
                ch_output[i] = val;
            }
        }
    }

    /**
     * Realiza el promedio (stacking) de múltiples segmentos para reducir ruido.
     * data: matriz de [n_segments * segment_size]
     * output: donde se guardará el promedio [segment_size]
     */
    void compute_stacking(float *data, float *output, int n_segments, int segment_size)
    {
        // Inicializamos el output en cero
        for (int i = 0; i < segment_size; i++)
            output[i] = 0.0f;

        // Sumamos todos los segmentos
        for (int s = 0; s < n_segments; s++)
        {
            float *segment = &data[s * segment_size];
#pragma omp parallel for
            for (int i = 0; i < segment_size; i++)
            {
#pragma omp atomic
                output[i] += segment[i];
            }
        }

        // Dividimos por el número de segmentos para obtener el promedio
        for (int i = 0; i < segment_size; i++)
        {
            output[i] /= n_segments;
        }
    }
}
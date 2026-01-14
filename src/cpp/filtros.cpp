// src\cpp\filtros.cpp
// compilar: ❯ g++ -O3 -shared -o build/libfiltros.dll src/cpp/filtros.cpp
#include <vector>
#include <fstream>

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
}
# main.py
from test import (
    run_inicial, 
    run_streaming, 
    run_raw_analysis, 
    run_multichannel_test,
    run_spectral_analysis,
    run_geophysics_test,
    run_stacking_test
)


if __name__ == "__main__":
    print("--- Selección de Test ---")
    print("1: Test Inicial (Básico de Filtrado)")
    print("2: Test de Streaming (Procesamiento en Tiempo Real)") 
    print("3: Test Raw Processing (Análisis de Señal Cruda)") 
    print("4: Test Multicanal (Filtrado Avanzado)")
    print("5: Test Espectral Analyzer (Análisis de FFT)")
    print("6: Test Geophysics (Resistividad Aparente)")
    print("7: Test Stacking (Refinamiento por Promediado)")

    while True:
        numero= input("Seleccione el número de test a ejecutar ('S' para salir.):\n")
        match numero:
            case '1':
                print("--- Ejecutando Test Inicial ---")
                print("(Cierra la ventana del gráfico para continuar...)")
                run_inicial()
            case '2':
                print("\n--- Ejecutando Test de Streaming ---")
                print("(Cierra la ventana del gráfico para continuar...)")
                run_streaming()
            case '3':
                print("\n--- Ejecutando Test raw processing ---")
                print("(Cierra la ventana del gráfico para continuar...)")
                run_raw_analysis()
            case '4':
                print("\n--- Ejecutando Test Multicanal ---")
                print("(Cierra la ventana del gráfico para continuar...)")
                run_multichannel_test()
            case '5':
                print("\n--- Ejecutando Test Espectral Analyzer ---")
                run_spectral_analysis()
            case '6':
                print("\n--- Ejecutando Test Geophysics ---")
                print("(Cierra la ventana del gráfico para continuar...)")
                run_geophysics_test()
            case '7':
                print("\n--- Ejecutando Test Stacking ---")
                print("(Cierra la ventana del gráfico para continuar...)")
                run_stacking_test()
            case 'S':
                print("--- Proceso Finalizado ---")
                break
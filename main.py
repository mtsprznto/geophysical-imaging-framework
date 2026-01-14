# main.py
from test import run_inicial, run_streaming, run_raw_analysis


if __name__ == "__main__":
    print("--- Ejecutando Test Inicial ---")

    print("(Cierra la ventana del gráfico para continuar...)")
    run_inicial()
    
    print("\n--- Ejecutando Test de Streaming ---")
    print("(Cierra la ventana del gráfico para continuar...)")
    run_streaming()

    print("\n--- Ejecutando Test raw processing ---")
    run_raw_analysis()
    
    print("--- Proceso Finalizado ---")
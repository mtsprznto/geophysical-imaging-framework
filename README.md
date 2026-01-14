# Geophysical Imaging Framework

~~~
geophysical_imaging_framework/
│
├── data/                   # Datos de ejemplo (No subir archivos pesados a GitHub)
│   ├── raw/                # Series temporales crudas (con ruido)
│   └── processed/          # Resultados después del filtrado
│
├── src/                    # Código fuente principal
│   ├── __init__.py
│   ├── acquisition/        # Fase 1: Simulación de sensores y entrada de datos
│   │   └── simulator.py
│   ├── processing/         # Fase 1: Filtros, FFT, Limpieza de señal
│   │   └── filters.py
│   ├── io/                 # Lectura de formatos específicos (.csv, .edi, .xyz)
│   │   └── readers.py
│   └── visualization/      # Fase 4: Gráficos de señales y pseudosecciones
│       └── plots.py
│
├── tests/                  # Pruebas unitarias (Vital para un System Developer)
│   └── test_filters.py
│
├── notebooks/              # Prototipado rápido (Jupyter Notebooks)
│   └── research_fft.ipynb
│
├── docs/                   # Documentación técnica y flujo del dato
├── .gitignore              # Para evitar subir la carpeta /data o __pycache__
├── requirements.txt        # Librerías necesarias (numpy, scipy, matplotlib, pandas)
└── README.md               # La cara de tu proyecto
~~~
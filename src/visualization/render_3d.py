# src\visualization\render_3d.py
import pyvista as pv
import numpy as np

def render_resistivity_grid(freqs, rho_matrix):
    """
    Crea una representación 3D de la resistividad.
    X: Posición del sensor (Canales)
    Y: Tiempo/Frecuencia (Profundidad aproximada)
    Z: Valor de Resistividad
    """
    # Generar las coordenadas de la malla
    x = np.arange(rho_matrix.shape[0]) # Canales
    z = np.log10(freqs)                # Profundidad (frecuencia invertida)
    
    x_grid, z_grid = np.meshgrid(x, z)
    y_grid = np.zeros_like(x_grid)     # En un plano 2D inicial dentro del espacio 3D

    # Crear la superficie de PyVista
    grid = pv.StructuredGrid(x_grid, y_grid, z_grid)
    grid["Resistividad"] = rho_matrix.flatten(order="F")

    # Visualización profesional
    plotter = pv.Plotter()
    plotter.add_mesh(grid, scalars="Resistividad", cmap="turbo", log_scale=True)
    plotter.add_scalar_bar(title="Resistividad (Ohm-m)")
    plotter.show_grid()
    plotter.show()

def render_resistivity_section(freqs, rho_matrix):
    """
    Renderiza una pseudo-sección 3D de resistividad sin errores de VTK.
    """
    # 1. Preparar coordenadas en float32
    x = np.arange(rho_matrix.shape[0], dtype=np.float32) 
    z = np.log10(freqs).astype(np.float32) 
    
    # meshgrid con indexing='ij' para alinear Canales (X) con Frecuencias (Z)
    x_grid, z_grid = np.meshgrid(x, z, indexing='ij')
    y_grid = np.zeros_like(x_grid) 

    # 2. Crear la malla estructurada
    grid = pv.StructuredGrid(x_grid, y_grid, z_grid)
    grid["Resistividad (Ohm-m)"] = rho_matrix.ravel()

    # 3. Configuración del Plotter
    p = pv.Plotter(title="GIF - Geophysical 3D Rendering")
    p.set_background("#111111") # Gris muy oscuro para mejor contraste

    # Añadir malla (Usando lighting en lugar de shading)
    p.add_mesh(
        grid, 
        scalars="Resistividad (Ohm-m)", 
        cmap="turbo", 
        log_scale=True, 
        show_edges=True,
        edge_color="white",
        line_width=0.5,
        lighting=True
    )

    # 4. Configurar ejes usando la nueva API (xtitle en lugar de xlabel)
    # Evitamos pasar strings vacíos para prevenir el error 'Text is not set!'
    p.show_grid(
        xtitle="Estaciones (Canales)", 
        ytitle="Y", 
        ztitle="Profundidad (log10 Hz)",
        color='white'
    )
    
    p.add_scalar_bar(title="Res (Ohm-m)", n_labels=5)
    
    # Orientar y mostrar
    p.view_xz()
    p.show()

def render_resistivity_isosurfaces(freqs, rho_matrix, target_value=1.0):
    """
    Extrae superficies donde la resistividad es igual a 'target_value'.
    Ideal para detectar cuerpos mineralizados específicos.
    """
    x = np.arange(rho_matrix.shape[0], dtype=np.float32)
    z = np.log10(freqs).astype(np.float32)
    x_grid, z_grid = np.meshgrid(x, z, indexing='ij')
    y_grid = np.zeros_like(x_grid)

    grid = pv.StructuredGrid(x_grid, y_grid, z_grid)
    grid["Resistividad"] = rho_matrix.ravel()

    # Generar el contorno (isosuperficie)
    contours = grid.contour([target_value])

    p = pv.Plotter()
    p.add_mesh(grid, opacity=0.2, cmap="turbo", log_scale=True) # El fondo traslúcido
    p.add_mesh(contours, color="red", line_width=2, label=f"Cuerpo Conductor ({target_value} Ohm-m)")
    p.add_legend()
    p.show()

def render_block_model(freqs, rho_matrix):
    """
    Convierte la sección en bloques 3D (Voxels).
    """
    x = np.arange(rho_matrix.shape[0], dtype=np.float32)
    z = np.log10(freqs).astype(np.float32)
    
    # Creamos un pequeño espesor en Y para que parezcan bloques
    y = np.array([-0.5, 0.5], dtype=np.float32) 
    
    grid = pv.RectilinearGrid(x, y, z)
    # Asignamos los datos a las celdas (voxels)
    grid.cell_data["Resistividad"] = rho_matrix.ravel()

    p = pv.Plotter()
    # Usamos un filtro de umbral para solo ver bloques interesantes
    p.add_mesh_slice(grid, display_params={'show_edges': True}, cmap="turbo", log_scale=True)
    p.show()

def render_dynamic_slicing(freqs, rho_matrix):
    """
    Crea un volumen 3D con herramientas de corte dinámico usando Point Data.
    """
    # 1. Definir ejes
    x = np.arange(rho_matrix.shape[0], dtype=np.float32)
    z = np.log10(freqs).astype(np.float32)
    y = np.linspace(-2, 2, 10, dtype=np.float32) # 10 capas de profundidad visual
    
    # 2. Crear malla de volumen (RectilinearGrid)
    grid = pv.RectilinearGrid(x, y, z)
    
    # 3. Preparar los datos
    # Expandimos la matriz de 2D a 3D para que coincida con cada punto del volumen
    # Usamos order='F' (Fortran) o aseguramos el reshape correcto para VTK
    vol_data = np.repeat(rho_matrix[:, np.newaxis, :], len(y), axis=1)
    
    # CAMBIO CLAVE: Usar point_data en lugar de cell_data
    grid.point_data["Resistividad"] = vol_data.ravel()

    # 4. Configurar Plotter con Slicing
    p = pv.Plotter(title="GIF - Análisis de Corte Dinámico")
    p.set_background("#111111")
    
    # Herramienta interactiva de plano de corte
    p.add_mesh_clip_plane(
        grid, 
        scalars="Resistividad", 
        cmap="turbo", 
        log_scale=True,
        show_edges=False # Desactivamos bordes para que el degradado se vea mejor
    )
    
    p.show_grid(xtitle="Estaciones", ytitle="Offset Y", ztitle="log10(F)")
    p.show()







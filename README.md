# Proyecto: Gestión de Incidencias (Ticketing)

## Objetivo
Crear una aplicación de escritorio con PySide6 + QtDesigner para gestionar incidencias de empresa (CRUD visual).

**Características:**
- Crear incidencia
- Cambiar estado
- Añadir prioridad
- Buscador avanzado
- Dashboard con contadores
- Tema oscuro/claro
- Logs de actividad

Todo con tablas, filtros, eventos, QComboBox y buena UX.

## Estructura del Proyecto

1. **incidencias.ui**: Archivo de diseño de la interfaz (Qt Designer).
2. **main.py**: Lógica de la aplicación en Python.

## Pasos para el desarrollo

### 1. Diseño de la Interfaz (QtDesigner)
- **Zona Superior**: Filtros y Dashboard.
- **Zona Central**: Tabla de incidencias (izquierda) y Formulario de edición (derecha).
- **Zona Inferior**: Botón de tema y Logs.

### 2. Lógica (Python)
- Cargar el archivo `.ui`.
- Configurar la tabla (columnas, selección).
- Conectar botones a funciones (Signals & Slots).
- Implementar el CRUD (Crear, Leer, Actualizar, Borrar).
- Implementar filtros y contadores del dashboard.

## Ejecución
Para ejecutar la aplicación completa:
```bash
python main.py
```

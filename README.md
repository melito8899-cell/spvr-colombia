# SpVAR Colombia – Streamlit App (Versión Ligera)

Dashboard interactivo de **Vectores Autorregresivos Espaciales (SpVAR)** para analizar la relación entre:

- Frontera Agrícola
- Infraestructura Vial
- Deforestación

a nivel de los departamentos de Colombia.

---

## Despliegue en Streamlit Cloud

1. Crea un repositorio en GitHub.
2. Sube estos tres archivos a la **raíz** del repositorio:
   - `app.py`
   - `requirements.txt`
   - `README.md`
3. Ve a [https://share.streamlit.io](https://share.streamlit.io)
4. Conecta el repositorio.
5. Configura:
   - **Main file path**: `app.py`
   - **Python version**: 3.11 o 3.12
6. Haz clic en **Deploy**.

---

## Archivos del proyecto

| Archivo            | Descripción                                      |
|--------------------|--------------------------------------------------|
| `app.py`           | Aplicación principal (versión ligera y estable) |
| `requirements.txt` | Dependencias mínimas                             |
| `README.md`        | Este archivo de documentación                   |

---

## Contenido de requirements.txt

```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
requests>=2.31.0
```

---

## Características del dashboard

- Simulador de choques (vial y agrícola) con respuesta de deforestación
- Ranking departamental interactivo
- Visualización 3D (VA Agrícola × Densidad Vial × Deforestación)
- Interfaz limpia y responsiva

---

## Notas importantes

- Esta versión **no utiliza** `geopandas`, `libpysal` ni `spreg` para garantizar compatibilidad total con Streamlit Cloud.
- Los datos mostrados son de **referencia** (orden de magnitud real).
- Para análisis científicos o de política pública use series oficiales de IDEAM, DANE e INVIAS.

---

**Última actualización**: Octubre 2026

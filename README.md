# Optimización de Pabellones Quirúrgicos

**Proyecto Métodos de Optimización II-2025**  
Universidad de Santiago de Chile

---

## Instalación Rápida

```bash
# Clonar o descargar el proyecto
cd proyecto1-opti/code

# Instalar dependencias
pip install -r requirements.txt
```

---

## Uso

### 1. Resolver una instancia específica

```bash
python solver.py instances/instance_Valparaiso.json
```

### 2. Generar visualizaciones para una instancia

```bash
python visualizer.py instances/instance_Valparaiso.json
# Abre charts/*.html en tu navegador
```

### 3. Procesar TODAS las instancias (recomendado)

```bash
python organize_and_visualize.py
# Abre results/index.html en tu navegador
```

### 4. Ejecutar experimentos y guardar resultados

```bash
python run_experiments.py
```

---

## Estructura del Proyecto

```
proyecto1-opti/
├── code/
│   ├── solver.py              # Modelo MILP
│   ├── visualizer.py          # Gráficos individuales
│   ├── organize_and_visualize.py  # Procesador completo
│   ├── instances/             # Datos de entrada
│   └── results/               # Resultados organizados
├── docs/
│   ├── README.md              # Documentación principal
│   ├── MODELO.md              # Modelo matemático
│   └── INSTANCIAS.md          # Descripción de datos
└── README.md                  # Este archivo
```

---

## Documentación

Ver carpeta `docs/` para documentación detallada:

- **[docs/README.md](docs/README.md)** - Descripción completa del proyecto
- **[docs/MODELO.md](docs/MODELO.md)** - Formulación matemática MILP
- **[docs/INSTANCIAS.md](docs/INSTANCIAS.md)** - Datos regionales utilizados

---

## Referencia Principal

> G. Durán, P. A. Rey, and P. Wolff, "**Solving the operating room scheduling problem with prioritized lists of patients**," *Annals of Operations Research*, vol. 258, pp. 395-414, 2017.

---

## Resultados

| Instancia | Estado | Objetivo | Asignados |
|-----------|--------|----------|-----------|
| Arica | Optimal | 8,412 | 6 |
| Atacama | Optimal | 10,560 | 1 |
| Valparaíso | Optimal | 23,848 | 4 |
| Magallanes | Optimal | 15,616 | 3 |
| Bío Bío | Optimal | 18,168 | 4 |
| RM Central | Optimal | 36,972 | 5 |
| RM Norte | Optimal | 15,144 | 5 |
| RM Sur | Optimal | 29,090 | 5 |
| RM Occidente | Optimal | 30,274 | 5 |
| Los Ríos | Optimal | 4,361 | 5 |

---
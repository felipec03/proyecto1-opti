# Programación de Pabellones Quirúrgicos con Listas de Pacientes Priorizados

**Proyecto Métodos de Optimización II-2025**  
**Universidad de Santiago de Chile**

---

## Descripción del Problema

Este proyecto implementa un modelo de **Programación Lineal Entera Mixta (MILP)** para resolver el problema de programación de pabellones quirúrgicos en hospitales públicos chilenos. El objetivo es asignar pacientes de una lista de espera a cirugías, maximizando el beneficio social ponderado por la urgencia médica de cada caso.

### Contexto: Sistema de Salud Chileno

El sistema de salud público chileno enfrenta una crisis de listas de espera, particularmente para patologías No-GES (Garantías Explícitas en Salud). Según datos del Ministerio de Salud:

- Las listas de espera quirúrgica superan los **400 días de mediana** en algunas regiones
- La programación manual actual es ineficiente: inicio tardío de cirugías, suspensiones, y brechas de programación
- No existe un criterio estandarizado de priorización

### Modelo Matemático Utilizado

El modelo se basa en el trabajo de **Wolff, Durán y Rey (2017)**, plasmado en:

> G. Durán, P. A. Rey, and P. Wolff, "**Solving the operating room scheduling problem with prioritized lists of patients**," *Annals of Operations Research*, vol. 258, no. 2, pp. 395-414, 2017.

#### Variables de Decisión

$$x_{p,d,r,s} \in \{0,1\}$$

Donde $x_{p,d,r,s} = 1$ si el paciente $p$ es programado para el día $d$, en el pabellón $r$, con el cirujano $s$.

#### Función Objetivo

$$\text{Maximizar } Z = \sum_{p \in P} \sum_{d \in D} \sum_{r \in R} \sum_{s \in S} \text{Prioridad}_p \cdot x_{p,d,r,s}$$

#### Restricciones Principales

1. **Unicidad del Paciente**: Cada paciente se opera como máximo una vez
2. **Capacidad del Pabellón**: Total de minutos ≤ 540 (9 horas)
3. **Capacidad del Cirujano**: Un cirujano no puede operar en dos lugares a la vez
4. **Competencia Técnica**: Solo cirujanos con la especialidad requerida
5. **Compatibilidad de Infraestructura**: Equipamiento específico por pabellón

---

## Cálculo de Prioridad

La prioridad de cada paciente se calcula según la fórmula del modelo Wolff-Durán:

$$\text{Prioridad}_p = \text{PesoCategoría}_p \times (\text{TiempoEspera}_p + 1)$$

| Categoría | Descripción | Peso |
|-----------|-------------|------|
| 1 | Urgente (riesgo vital) | 48 |
| 2 | Alta prioridad | 12 |
| 3 | Media prioridad | 4 |
| 4 | Baja prioridad | 2 |
| 5 | Electiva | 1 |

Esta ponderación asegura que los pacientes más graves sean atendidos primero, cumpliendo con los principios éticos de equidad en salud.

---

## Estructura del Proyecto

```
proyecto1-opti/
├── code/
│   ├── solver.py              # Modelo MILP con PuLP
│   ├── visualizer.py          # Generador de gráficos
│   ├── organize_and_visualize.py  # Organizador de resultados
│   ├── data_generator.py      # Generador de instancias
│   ├── run_experiments.py     # Ejecutor de experimentos
│   ├── requirements.txt       # Dependencias Python
│   ├── instances/             # Archivos JSON de instancias
│   │   ├── instance_Arica.json
│   │   ├── instance_Atacama.json
│   │   ├── instance_Valparaiso.json
│   │   ├── instance_Magallanes.json
│   │   ├── instance_BioBio.json
│   │   └── ...
│   ├── results/               # Resultados organizados
│   │   └── [nombre_instancia]/
│   │       ├── instance.json
│   │       ├── solution.json
│   │       └── *.html (visualizaciones)
│   └── charts/                # Gráficos individuales
├── docs/                      # Documentación
│   ├── README.md              # Esta documentación
│   ├── MODELO.md              # Detalle del modelo matemático
│   └── INSTANCIAS.md          # Descripción de datos regionales
└── README.md                  # Instrucciones rápidas
```

---

## Referencias Bibliográficas

### Paper Principal

1. G. Durán, P. A. Rey, and P. Wolff, "Solving the operating room scheduling problem with prioritized lists of patients," *Annals of Operations Research*, vol. 258, no. 2, pp. 395-414, 2017.

### Tesis de Referencia

2. P. Wolff, "Modelos de Programación Matemática para asignación de pabellones quirúrgicos en hospitales públicos," Tesis de Magíster, Universidad de Chile, Santiago, 2011.

### Contexto Chileno

3. Comisión Nacional de Productividad, "Eficiencia en pabellones quirúrgicos y gestión de lista de espera No GES," Informe Final, Santiago, Chile, 2020.

4. Biblioteca del Congreso Nacional de Chile, "Estadísticas de listas de espera en el sistema público de salud," Reportes BCN, 2024.

---

## Datos Regionales Utilizados

Las instancias fueron generadas utilizando estadísticas reales del sistema de salud chileno:

| Región | Mediana Espera | Percentil 75 | Casos (~) |
|--------|---------------|--------------|-----------|
| Arica | 250 días | 450 días | ~70 |
| Atacama | 220-579 días | 580 días | ~50 |
| Valparaíso | 307-360 días | 667 días | ~18,600 |
| Magallanes | 244-310 días | ~400 días | ~3,950 |
| Bío Bío | 250-352 días | 486-591 días | Variable |
| R. Metropolitana | 220-400 días | 500+ días | ~60,000 |

Fuente: Ministerio de Salud, BCN, y Servicios de Salud regionales (datos a junio 2024-2025).

---

## Tecnologías Utilizadas

- **Python 3.10+**: Lenguaje de programación
- **PuLP**: Librería de modelado de programación lineal
- **CBC Solver**: Solver de optimización (open source)
- **Plotly**: Visualizaciones interactivas
- **NumPy**: Cálculos numéricos

---

## Autores

- **Estudiante**: Felipe
- **Curso**: Métodos de Optimización II-2025
- **Profesor**: Víctor Parada
- **Ayudante**: Matías Yáñez

Universidad de Santiago de Chile  
Facultad de Ingeniería  
Departamento de Ingeniería Informática

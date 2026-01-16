# Modelo Matemático: Programación de Pabellones Quirúrgicos

## Formulación MILP (Wolff-Durán-Rey, 2017)

Este documento detalla la formulación matemática del modelo de Programación Lineal Entera Binaria (BIP) utilizado para resolver el problema de programación de pabellones quirúrgicos.

---

## 1. Conjuntos e Índices

| Símbolo | Descripción |
|---------|-------------|
| $P$ | Conjunto de pacientes en lista de espera, indexados por $p$ |
| $D$ | Conjunto de días en el horizonte de planificación (ej: $d = 1, \ldots, 5$) |
| $R$ | Conjunto de pabellones (recintos) disponibles, indexados por $r$ |
| $S$ | Conjunto de cirujanos principales, indexados por $s$ |

---

## 2. Parámetros de Entrada

| Parámetro | Descripción | Unidad |
|-----------|-------------|--------|
| $\text{Duracion}_p$ | Tiempo estimado de cirugía del paciente $p$ | minutos |
| $\text{Prioridad}_p$ | Puntaje de prioridad del paciente $p$ | adimensional |
| $\text{Capacidad}_{d,r}$ | Tiempo disponible en pabellón $r$ el día $d$ | minutos (típico: 540) |
| $\text{Competencia}_{s,p}$ | 1 si cirujano $s$ puede operar paciente $p$, 0 sino | binario |
| $\text{Disponibilidad}_{s,d}$ | 1 si cirujano $s$ está disponible el día $d$ | binario |
| $\text{Equipamiento}_{r,p}$ | 1 si pabellón $r$ tiene el equipo para paciente $p$ | binario |

---

## 3. Variables de Decisión

$$x_{p,d,r,s} \in \{0, 1\}$$

- $x_{p,d,r,s} = 1$ si el paciente $p$ es programado para cirugía el día $d$, en el pabellón $r$, con el cirujano $s$
- $x_{p,d,r,s} = 0$ en cualquier otro caso

**Total de variables**: $|P| \times |D| \times |R| \times |S|$

Para una instancia típica de 60 pacientes, 5 días, 3 pabellones y 10 cirujanos:
$$60 \times 5 \times 3 \times 10 = 9,000 \text{ variables binarias}$$

---

## 4. Función Objetivo

**Maximizar el beneficio social agregado:**

$$\max Z = \sum_{p \in P} \sum_{d \in D} \sum_{r \in R} \sum_{s \in S} \text{Prioridad}_p \cdot x_{p,d,r,s}$$

Esta función asegura que el modelo "prefiera" asignar recursos a los pacientes con mayor puntaje de prioridad.

---

## 5. Restricciones

### 5.1 Unicidad del Paciente

Un paciente no puede ser operado más de una vez en el horizonte de planificación:

$$\sum_{d \in D} \sum_{r \in R} \sum_{s \in S} x_{p,d,r,s} \leq 1, \quad \forall p \in P$$

> **Nota**: Es una desigualdad ($\leq$) porque no todos los pacientes podrán ser programados.

### 5.2 Capacidad del Pabellón (Restricción de Mochila)

La suma de duraciones no puede exceder la capacidad diaria:

$$\sum_{p \in P} \sum_{s \in S} \text{Duracion}_p \cdot x_{p,d,r,s} \leq \text{Capacidad}_{d,r}, \quad \forall d \in D, \forall r \in R$$

> Esta es la restricción tipo **Knapsack** que define la eficiencia del empaquetado.

### 5.3 Capacidad del Cirujano

El tiempo total de operación de un cirujano no puede exceder su jornada:

$$\sum_{p \in P} \sum_{r \in R} \text{Duracion}_p \cdot x_{p,d,r,s} \leq 540, \quad \forall d \in D, \forall s \in S$$

### 5.4 Competencia Técnica

Solo cirujanos competentes pueden operar cada paciente:

$$x_{p,d,r,s} \leq \text{Competencia}_{s,p}, \quad \forall p, d, r, s$$

### 5.5 Disponibilidad del Cirujano

Si el cirujano no está disponible, no puede operar:

$$\sum_{p \in P} \sum_{r \in R} x_{p,d,r,s} = 0, \quad \forall d, s : \text{Disponibilidad}_{s,d} = 0$$

### 5.6 Compatibilidad de Infraestructura

Solo asignar a pabellones con el equipamiento necesario:

$$x_{p,d,r,s} \leq \text{Equipamiento}_{r,p}, \quad \forall p, d, r, s$$

---

## 6. Implementación en Python/PuLP

```python
import pulp

# Crear modelo
prob = pulp.LpProblem("OR_Scheduling", pulp.LpMaximize)

# Variables de decisión
x = pulp.LpVariable.dicts("x", 
    ((p, d, r, s) for p in patients for d in days for r in rooms for s in surgeons),
    cat='Binary')

# Función objetivo
prob += pulp.lpSum(priority[p] * x[p, d, r, s] 
                   for p in patients for d in days for r in rooms for s in surgeons)

# Restricción de unicidad
for p in patients:
    prob += pulp.lpSum(x[p, d, r, s] for d in days for r in rooms for s in surgeons) <= 1

# Restricción de capacidad de pabellón
for d in days:
    for r in rooms:
        prob += pulp.lpSum(duration[p] * x[p, d, r, s] 
                           for p in patients for s in surgeons) <= 540

# Resolver
prob.solve()
```

---

## 7. Complejidad Computacional

El problema de programación de pabellones quirúrgicos pertenece a la clase **NP-hard**, ya que contiene como caso particular el problema de la mochila (Knapsack Problem).

Sin embargo, para instancias de tamaño moderado (< 100 pacientes, < 10 días), los solvers modernos como CPLEX o CBC pueden encontrar soluciones óptimas en segundos.

| Instancia | Variables | Restricciones | Tiempo (CBC) |
|-----------|-----------|---------------|--------------|
| 40 pacientes | ~4,800 | ~300 | < 1 seg |
| 60 pacientes | ~9,000 | ~500 | 0.4-0.7 seg |
| 100 pacientes | ~30,000 | ~1,000 | 2-5 seg |

---

## 8. Referencias

1. G. Durán, P. A. Rey, and P. Wolff, "Solving the operating room scheduling problem with prioritized lists of patients," *Annals of Operations Research*, vol. 258, no. 2, pp. 395-414, 2017.

2. P. Wolff, "Modelos de Programación Matemática para asignación de pabellones quirúrgicos en hospitales públicos," Tesis de Magíster, Universidad de Chile, 2011.

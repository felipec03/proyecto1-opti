# Descripción de Instancias Regionales

Este documento describe las instancias de datos utilizadas en el proyecto, basadas en estadísticas reales del sistema de salud chileno.

---

## Fuentes de Datos

1. **Ministerio de Salud de Chile** - Estadísticas de listas de espera
2. **Biblioteca del Congreso Nacional (BCN)** - Reportes de gestión sanitaria
3. **Servicios de Salud Regionales** - Datos operacionales
4. **Paper Wolff-Durán (2017)** - Distribuciones estadísticas para simulación

---

## Instancias Disponibles

### 1. Región de Arica y Parinacota

**Archivo**: `instance_Arica.json`

| Parámetro | Valor |
|-----------|-------|
| Pacientes | 70 |
| Días | 5 |
| Pabellones | 4 |
| Cirujanos | 15 |
| Especialidades | 6 |

**Características de la lista de espera**:
- Mediana de espera: ~250 días
- Prioridades distribuidas según categorías biomédicas

---

### 2. Región de Atacama

**Archivo**: `instance_Atacama.json`

| Parámetro | Valor |
|-----------|-------|
| Pacientes | 50 |
| Días | 5 |
| Pabellones | 2 |
| Cirujanos | 8 |
| Especialidades | 5 |

**Características**:
- Hospital de menor tamaño
- Tiempos de espera: 220-579 días
- Restricciones más ajustadas de competencia

---

### 3. Región de Valparaíso (Viña del Mar-Quillota)

**Archivo**: `instance_Valparaiso.json`

| Parámetro | Valor |
|-----------|-------|
| Pacientes | 60 |
| Días | 5 |
| Pabellones | 3 |
| Cirujanos | 10 |
| Especialidades | 4 |

**Estadísticas reales utilizadas** (BCN, junio 2024):
- Lista de espera total: ~18,601 casos
- Mediana de espera: 307-360 días
- Percentil 75: 667 días (S.S. Viña del Mar)

---

### 4. Región de Magallanes

**Archivo**: `instance_Magallanes.json`

| Parámetro | Valor |
|-----------|-------|
| Pacientes | 40 |
| Días | 5 |
| Pabellones | 2 |
| Cirujanos | 6 |
| Especialidades | 3 |

**Estadísticas reales utilizadas**:
- Lista de espera total: ~3,950 casos
- Mediana de espera: 244 días
- Tendencia: En descenso desde 310 días (septiembre 2022)

**Nota**: Región aislada geográficamente, recursos limitados.

---

### 5. Región del Bío Bío (Concepción)

**Archivo**: `instance_BioBio.json`

| Parámetro | Valor |
|-----------|-------|
| Pacientes | 55 |
| Días | 5 |
| Pabellones | 3 |
| Cirujanos | 12 |
| Especialidades | 4 |

**Estadísticas por Servicio de Salud** (BCN, junio 2024):

| Servicio | Mediana | Percentil 75 |
|----------|---------|--------------|
| S.S. Bío-Bío | 352 días | 591 días |
| S.S. Concepción | 271 días | 543 días |
| S.S. Arauco | 250 días | 486 días |

---

### 6. Región Metropolitana

Se incluyen múltiples instancias de la Región Metropolitana:

| Archivo | Servicio de Salud | Pacientes |
|---------|-------------------|-----------|
| `instance_rm_central.json` | SSMC (Central) | 60 |
| `instance_rm_north.json` | SSMN (Norte) | 60 |
| `instance_rm_south.json` | SSMS (Sur) | 60 |
| `instance_rm_west.json` | SSM Occidente | 60 |

**Características comunes**:
- Tiempos de espera: 200-700+ días
- Alta carga de pacientes
- Mayor variedad de especialidades

---

## Formato de Datos JSON

Cada instancia sigue el siguiente formato:

```json
{
  "name": "Nombre_Instancia",
  "num_days": 5,
  "num_rooms": 3,
  "num_surgeons": 10,
  "patients": [
    {
      "id": 1,
      "duration": 120,
      "priority": 17520,
      "category": 1,
      "waiting_time": 365,
      "required_specialty": 1
    }
  ],
  "room_capacities": {
    "1_1": 540, "1_2": 540, "1_3": 540
  },
  "competence": {
    "1_1": 1, "2_1": 1, "3_1": 0
  },
  "availability": {
    "1_1": 1, "1_2": 1, "1_3": 1, "1_4": 1, "1_5": 1
  },
  "room_compatibility": {
    "1_1": 1, "2_1": 1, "3_1": 1
  }
}
```

### Explicación de campos

| Campo | Formato clave | Descripción |
|-------|---------------|-------------|
| `room_capacities` | `"d_r"` | Capacidad del pabellón $r$ en día $d$ (minutos) |
| `competence` | `"s_specialty"` | 1 si cirujano $s$ tiene especialidad, 0 sino |
| `availability` | `"s_d"` | 1 si cirujano $s$ disponible día $d$ |
| `room_compatibility` | `"r_p"` | 1 si pabellón $r$ puede atender paciente $p$ |

---

## Generación de Datos

Los datos fueron generados siguiendo las recomendaciones del paper Wolff-Durán:

1. **Duraciones**: Distribución Log-Normal con $\mu = 4.5$, $\sigma = 0.6$ (mediana ~90 min)
2. **Tiempos de espera**: Basados en estadísticas reales por región
3. **Prioridades**: $\text{Peso} \times (\text{Espera} + 1)$ con pesos {48, 12, 4, 2, 1}
4. **Categorías**: Distribución ponderada {10%, 20%, 30%, 20%, 20%}

---

## Referencias de Datos

1. Ministerio de Salud, "Repositorio de datos de listas de espera," MINSAL, 2024.
2. BCN, "Listas de espera en el sistema público de salud," Biblioteca del Congreso Nacional, 2024.
3. CNP, "Eficiencia en pabellones quirúrgicos," Comisión Nacional de Productividad, 2020.

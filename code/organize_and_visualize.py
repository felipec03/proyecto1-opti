"""
Organizador de Instancias y Generador de Visualizaciones
=========================================================

Este script organiza cada instancia de datos en su propio directorio
y genera las visualizaciones correspondientes.

Uso:
    python organize_and_visualize.py

Salida:
    results/
    ├── Arica_Cirugia_Junio2024/
    │   ├── instance.json
    │   ├── solution.json
    │   ├── gantt_chart.html
    │   ├── calendar_view.html
    │   ├── patient_scatter.html
    │   ├── category_bars.html
    │   └── summary.html
    ├── Atacama_Junio_2025_80IDs/
    │   └── ...
    └── ...
"""

import os
import sys
import json
import shutil
import glob

# Importar módulos del proyecto
from solver import solve_instance
from visualizer import (
    load_data,
    create_gantt_chart,
    create_calendar_view,
    create_patient_scatter,
    create_category_bars,
    create_summary
)


def organize_instance(instance_path: str, output_base: str) -> dict:
    """
    Procesa una instancia: resuelve y genera visualizaciones.
    
    Args:
        instance_path: Ruta al archivo JSON de la instancia
        output_base: Directorio base para los resultados
        
    Returns:
        Diccionario con los resultados
    """
    # Cargar datos
    instance = load_data(instance_path)
    instance_name = instance["name"]
    
    print(f"\n{'='*60}")
    print(f"Procesando: {instance_name}")
    print(f"{'='*60}")
    
    # Crear directorio para esta instancia
    instance_dir = os.path.join(output_base, instance_name)
    os.makedirs(instance_dir, exist_ok=True)
    
    # Copiar archivo de instancia
    instance_dest = os.path.join(instance_dir, "instance.json")
    shutil.copy2(instance_path, instance_dest)
    print(f"  [1/7] Instancia copiada")
    
    # Resolver
    print(f"  [2/7] Resolviendo modelo...")
    solution = solve_instance(instance_path)
    
    # Guardar solución
    solution_path = os.path.join(instance_dir, "solution.json")
    with open(solution_path, 'w', encoding='utf-8') as f:
        json.dump(solution, f, indent=2, ensure_ascii=False)
    print(f"  [3/7] Solucion guardada: Status={solution['status']}, Obj={solution['objective_value']}")
    
    # Generar visualizaciones
    print(f"  [4/7] Generando Gantt chart...")
    create_gantt_chart(instance, solution, instance_dir)
    
    print(f"  [5/7] Generando Calendar view...")
    create_calendar_view(instance, solution, instance_dir)
    
    print(f"  [6/7] Generando Patient scatter...")
    create_patient_scatter(instance, solution, instance_dir)
    
    print(f"  [7/7] Generando Category bars y Summary...")
    create_category_bars(instance, solution, instance_dir)
    create_summary(instance, solution, instance_dir)
    
    print(f"  [OK] Completado: {instance_dir}")
    
    return {
        "name": instance_name,
        "status": solution["status"],
        "objective": solution["objective_value"],
        "assigned": solution["assigned_count"],
        "directory": instance_dir
    }


def generate_index_html(results: list, output_dir: str):
    """Genera un archivo HTML índice con enlaces a todas las instancias."""
    
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Resultados - Programacion Quirurgica</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 40px auto; padding: 20px; }
        h1 { color: #1e40af; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        th { background: #f3f4f6; font-weight: bold; }
        tr:hover { background: #f9fafb; }
        a { color: #2563eb; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .status-optimal { color: #10b981; font-weight: bold; }
        .charts { display: flex; gap: 8px; flex-wrap: wrap; }
        .charts a { background: #e0e7ff; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
    </style>
</head>
<body>
    <h1>Resultados - Programacion de Pabellones Quirurgicos</h1>
    <p>Proyecto Metodos de Optimizacion II-2025 | Universidad de Santiago de Chile</p>
    
    <table>
        <tr>
            <th>Instancia</th>
            <th>Estado</th>
            <th>Objetivo</th>
            <th>Asignados</th>
            <th>Visualizaciones</th>
        </tr>
"""
    
    for r in results:
        status_class = "status-optimal" if r["status"] == "Optimal" else ""
        folder = r["name"]
        
        html += f"""        <tr>
            <td><strong>{r['name']}</strong></td>
            <td class="{status_class}">{r['status']}</td>
            <td>{r['objective']:,.0f}</td>
            <td>{r['assigned']}</td>
            <td class="charts">
                <a href="{folder}/gantt_chart.html">Gantt</a>
                <a href="{folder}/calendar_view.html">Calendario</a>
                <a href="{folder}/patient_scatter.html">Pacientes</a>
                <a href="{folder}/category_bars.html">Categorias</a>
                <a href="{folder}/summary.html">Resumen</a>
            </td>
        </tr>
"""
    
    html += """    </table>
    <p style="color: #6b7280; font-size: 14px;">
        Modelo: Wolff-Duran (Operating Room Scheduling with Prioritized Lists)<br>
        Solver: PuLP con CBC
    </p>
</body>
</html>
"""
    
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n[OK] Indice generado: {index_path}")


def main():
    """Función principal."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    instances_dir = os.path.join(script_dir, "instances")
    output_dir = os.path.join(script_dir, "results")
    
    print("\n" + "="*60)
    print("ORGANIZADOR DE INSTANCIAS Y VISUALIZACIONES")
    print("Proyecto: Programacion de Pabellones Quirurgicos")
    print("="*60)
    
    # Buscar instancias
    instances = sorted(glob.glob(os.path.join(instances_dir, "*.json")))
    
    if not instances:
        print(f"[ERROR] No se encontraron instancias en: {instances_dir}")
        sys.exit(1)
    
    print(f"\nEncontradas {len(instances)} instancias")
    print(f"Directorio de salida: {output_dir}")
    
    # Crear directorio de resultados
    os.makedirs(output_dir, exist_ok=True)
    
    # Procesar cada instancia
    results = []
    for instance_path in instances:
        try:
            result = organize_instance(instance_path, output_dir)
            results.append(result)
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    # Generar índice HTML
    generate_index_html(results, output_dir)
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    print(f"Instancias procesadas: {len(results)}")
    print(f"Directorio de resultados: {output_dir}")
    print(f"Abrir en navegador: {os.path.join(output_dir, 'index.html')}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

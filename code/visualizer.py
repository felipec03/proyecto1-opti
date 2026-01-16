"""
Simple OR Scheduling Visualizer for Presentations
==================================================

Generates individual charts as standalone HTML files that can be 
screenshot or embedded in presentations.

Usage:
    python visualizer.py instances/instance_rm_central.json

Output:
    Creates individual chart files in 'charts/' directory:
    - gantt_chart.html
    - calendar_view.html
    - patient_scatter.html
    - category_bars.html
"""

import json
import os
import sys
from typing import Dict, List

import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =============================================================================
# THEME - Clean presentation style
# =============================================================================

COLORS = {
    "primary": "#2563eb",      # Blue
    "secondary": "#7c3aed",    # Purple  
    "success": "#10b981",      # Green
    "warning": "#f59e0b",      # Orange
    "danger": "#ef4444",       # Red
    "bg": "#ffffff",
    "text": "#1f2937",
    "muted": "#6b7280",
    "rooms": ["#2563eb", "#7c3aed", "#10b981", "#f59e0b", "#ef4444"],
    "categories": {
        1: "#ef4444",  # Urgente - Rojo
        2: "#f59e0b",  # Alta - Naranja
        3: "#eab308",  # Media - Amarillo
        4: "#10b981",  # Baja - Verde
        5: "#6b7280",  # Electiva - Gris
    }
}

DAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]


def load_data(instance_path: str) -> Dict:
    """Load instance JSON file."""
    with open(instance_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_solver(instance_path: str) -> Dict:
    """Run the solver and return results."""
    from solver import solve_instance
    return solve_instance(instance_path)


# =============================================================================
# CHART 1: GANTT CHART
# =============================================================================

def create_gantt_chart(instance: Dict, solution: Dict, output_dir: str):
    """Create a Gantt chart showing surgery schedule - supports monthly view."""
    
    assignments = solution.get("assignments", [])
    if not assignments:
        print("  [!] No assignments to visualize")
        return
    
    patients = {p["id"]: p for p in instance["patients"]}
    num_rooms = instance["num_rooms"]
    num_days = instance["num_days"]
    
    # Organize by day and room
    schedule = {}
    for a in assignments:
        key = (a["day"], a["room"])
        if key not in schedule:
            schedule[key] = []
        schedule[key].append(a)
    
    # Build traces - group by week for monthly view
    fig = go.Figure()
    
    # Color palette for weeks
    week_colors = ["#2563eb", "#7c3aed", "#10b981", "#f59e0b", "#ef4444"]
    
    for room in range(1, num_rooms + 1):
        for day in range(1, num_days + 1):
            key = (day, room)
            if key not in schedule:
                continue
            
            current_time = 0
            week_num = (day - 1) // 7
            
            for a in schedule[key]:
                p = patients[a["patient_id"]]
                duration = p["duration"]
                
                # Y position: "Semana X - Pab Y" for monthly, "Pab Y" for weekly
                if num_days > 7:
                    y_label = f"Sem {week_num + 1} - Pab {room}"
                else:
                    y_label = f"Pabellón {room}"
                
                # X position: day within week (0-6) * 600 + time offset
                day_in_week = (day - 1) % 7
                x_base = day_in_week * 600 + current_time
                
                fig.add_trace(go.Bar(
                    name=f"Día {day}",
                    x=[duration],
                    y=[y_label],
                    base=[x_base],
                    orientation="h",
                    marker_color=week_colors[week_num % len(week_colors)],
                    text=f"P{a['patient_id']}",
                    textposition="inside",
                    textfont=dict(color="white", size=10),
                    hovertemplate=(
                        f"<b>Paciente {a['patient_id']}</b><br>"
                        f"Día: {day}<br>"
                        f"Pabellón: {room}<br>"
                        f"Duración: {duration} min<br>"
                        f"Prioridad: {p['priority']:,}<br>"
                        f"Categoría: {p['category']}<extra></extra>"
                    ),
                    showlegend=False,
                ))
                current_time += duration
    
    # Calculate dimensions
    if num_days > 7:
        num_weeks = (num_days + 6) // 7
        chart_height = 150 + num_weeks * num_rooms * 40
        title_text = f"<b>Programación Mensual de Cirugías ({num_days} días)</b>"
        x_tickvals = [i * 600 + 300 for i in range(7)]
        x_ticktext = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        x_range = [0, 7 * 600]
    else:
        chart_height = 300 + num_rooms * 60
        title_text = "<b>Programación Semanal de Cirugías</b>"
        x_tickvals = [i * 600 + 300 for i in range(num_days)]
        x_ticktext = DAYS[:num_days]
        x_range = [0, num_days * 600]
    
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=18)),
        barmode="overlay",
        xaxis=dict(
            title="Día de la Semana",
            tickvals=x_tickvals,
            ticktext=x_ticktext,
            range=x_range,
            showgrid=True,
            gridcolor="#e5e7eb",
        ),
        yaxis=dict(title="", categoryorder="category descending"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", color=COLORS["text"]),
        height=chart_height,
        width=1000,
        margin=dict(l=120, r=40, t=60, b=60),
    )
    
    # Add day separators
    for i in range(1, min(7, num_days)):
        fig.add_vline(x=i * 600, line_dash="dash", line_color="#d1d5db")
    
    # Save
    path = os.path.join(output_dir, "gantt_chart.html")
    fig.write_html(path)
    print(f"  [OK] Gantt chart: {path}")


# =============================================================================
# CHART 2: CALENDAR VIEW
# =============================================================================

def create_calendar_view(instance: Dict, solution: Dict, output_dir: str):
    """Create a calendar-style heatmap showing surgeries per day/room - supports monthly view."""
    
    assignments = solution.get("assignments", [])
    patients = {p["id"]: p for p in instance["patients"]}
    num_rooms = instance["num_rooms"]
    num_days = instance["num_days"]
    
    # For monthly view, create a grid where:
    # - Columns = days of week (Lun-Dom)
    # - Rows = "Semana X - Pab Y"
    
    if num_days > 7:
        # Monthly view: organize by week and room
        num_weeks = (num_days + 6) // 7
        
        # Build data structure: week -> room -> day_of_week -> minutes
        data = {}
        counts = {}
        for week in range(num_weeks):
            for room in range(1, num_rooms + 1):
                key = (week, room)
                data[key] = [0] * 7
                counts[key] = [0] * 7
        
        for a in assignments:
            day = a["day"]
            room = a["room"]
            week = (day - 1) // 7
            day_of_week = (day - 1) % 7
            p = patients[a["patient_id"]]
            key = (week, room)
            if key in data:
                data[key][day_of_week] += p["duration"]
                counts[key][day_of_week] += 1
        
        # Build matrix for heatmap
        y_labels = []
        z_matrix = []
        text_matrix = []
        
        for week in range(num_weeks):
            for room in range(1, num_rooms + 1):
                key = (week, room)
                y_labels.append(f"Sem {week + 1} - Pab {room}")
                z_matrix.append(data[key])
                
                row_text = []
                for dow in range(7):
                    mins = data[key][dow]
                    count = counts[key][dow]
                    if mins > 0:
                        pct = mins / 459 * 100
                        row_text.append(f"{count}<br>{mins}'<br>{pct:.0f}%")
                    else:
                        row_text.append("")
                text_matrix.append(row_text)
        
        x_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        chart_height = 100 + len(y_labels) * 45
        chart_width = 800
        title_text = f"<b>Calendario Mensual de Ocupación ({num_days} días)</b>"
        text_size = 9
        
    else:
        # Weekly view: simple grid
        matrix = [[0 for _ in range(num_days)] for _ in range(num_rooms)]
        surgery_counts = [[0 for _ in range(num_days)] for _ in range(num_rooms)]
        
        for a in assignments:
            room_idx = a["room"] - 1
            day_idx = a["day"] - 1
            p = patients[a["patient_id"]]
            matrix[room_idx][day_idx] += p["duration"]
            surgery_counts[room_idx][day_idx] += 1
        
        y_labels = [f"Pabellón {r+1}" for r in range(num_rooms)]
        z_matrix = matrix
        text_matrix = []
        for r in range(num_rooms):
            row = []
            for d in range(num_days):
                mins = matrix[r][d]
                count = surgery_counts[r][d]
                pct = mins / 540 * 100 if mins > 0 else 0
                row.append(f"{count} cir<br>{mins}'<br>{pct:.0f}%")
            text_matrix.append(row)
        
        x_labels = DAYS[:num_days]
        chart_height = 150 + num_rooms * 80
        chart_width = 700
        title_text = "<b>Calendario de Ocupación de Pabellones</b>"
        text_size = 11
    
    fig = go.Figure(data=go.Heatmap(
        z=z_matrix,
        x=x_labels,
        y=y_labels,
        text=text_matrix,
        texttemplate="%{text}",
        textfont=dict(size=text_size, color="white"),
        colorscale=[
            [0, "#f3f4f6"],
            [0.3, "#93c5fd"],
            [0.6, "#3b82f6"],
            [1, "#1e40af"]
        ],
        showscale=True,
        colorbar=dict(title="Min", ticksuffix=""),
        hovertemplate="<b>%{y}</b> - %{x}<br>%{text}<extra></extra>",
    ))
    
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=18)),
        xaxis=dict(title="", side="top"),
        yaxis=dict(title="", autorange="reversed"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", color=COLORS["text"]),
        height=chart_height,
        width=chart_width,
        margin=dict(l=120, r=60, t=80, b=40),
    )
    
    path = os.path.join(output_dir, "calendar_view.html")
    fig.write_html(path)
    print(f"  [OK] Calendar view: {path}")


# =============================================================================
# CHART 3: PATIENT SCATTER (Priority vs Waiting Time)
# =============================================================================

def create_patient_scatter(instance: Dict, solution: Dict, output_dir: str):
    """Scatter plot showing priority vs waiting time, colored by assignment."""
    
    patients = instance["patients"]
    assigned_ids = {a["patient_id"] for a in solution.get("assignments", [])}
    
    # Separate assigned and unassigned
    assigned = [p for p in patients if p["id"] in assigned_ids]
    unassigned = [p for p in patients if p["id"] not in assigned_ids]
    
    fig = go.Figure()
    
    # Unassigned (background)
    if unassigned:
        fig.add_trace(go.Scatter(
            x=[p["waiting_time"] for p in unassigned],
            y=[p["priority"] for p in unassigned],
            mode="markers",
            name="En espera",
            marker=dict(
                color=COLORS["danger"],
                size=10,
                opacity=0.4,
                line=dict(width=1, color="white")
            ),
            hovertemplate="<b>Paciente %{customdata}</b><br>Prioridad: %{y:,}<br>Espera: %{x} días<extra></extra>",
            customdata=[p["id"] for p in unassigned],
        ))
    
    # Assigned (foreground)
    if assigned:
        fig.add_trace(go.Scatter(
            x=[p["waiting_time"] for p in assigned],
            y=[p["priority"] for p in assigned],
            mode="markers",
            name="Asignado",
            marker=dict(
                color=COLORS["success"],
                size=14,
                symbol="star",
                line=dict(width=2, color="white")
            ),
            hovertemplate="<b>Paciente %{customdata}</b><br>Prioridad: %{y:,}<br>Espera: %{x} días<extra></extra>",
            customdata=[p["id"] for p in assigned],
        ))
    
    # Stats annotation
    total = len(patients)
    assigned_count = len(assigned_ids)
    pct = assigned_count / total * 100 if total > 0 else 0
    
    fig.update_layout(
        title=dict(text="<b>Asignación de Pacientes: Prioridad vs Tiempo de Espera</b>", font=dict(size=18)),
        xaxis=dict(title="Días en Lista de Espera", showgrid=True, gridcolor="#e5e7eb"),
        yaxis=dict(title="Puntaje de Prioridad", showgrid=True, gridcolor="#e5e7eb"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", color=COLORS["text"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
        width=800,
        margin=dict(l=80, r=40, t=80, b=60),
        annotations=[
            dict(
                text=f"<b>{assigned_count}/{total} pacientes asignados ({pct:.1f}%)</b>",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=14, color=COLORS["success"]),
                bgcolor="white",
                borderpad=4,
            )
        ]
    )
    
    path = os.path.join(output_dir, "patient_scatter.html")
    fig.write_html(path)
    print(f"  [OK] Patient scatter: {path}")


# =============================================================================
# CHART 4: CATEGORY DISTRIBUTION
# =============================================================================

def create_category_bars(instance: Dict, solution: Dict, output_dir: str):
    """Bar chart showing assigned vs unassigned by category."""
    
    patients = instance["patients"]
    assigned_ids = {a["patient_id"] for a in solution.get("assignments", [])}
    
    # Count per category
    categories = {i: {"assigned": 0, "unassigned": 0} for i in range(1, 6)}
    for p in patients:
        cat = p["category"]
        if p["id"] in assigned_ids:
            categories[cat]["assigned"] += 1
        else:
            categories[cat]["unassigned"] += 1
    
    cat_names = ["Cat 1\nUrgente", "Cat 2\nAlta", "Cat 3\nMedia", "Cat 4\nBaja", "Cat 5\nElectiva"]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name="Asignados",
        x=cat_names,
        y=[categories[i]["assigned"] for i in range(1, 6)],
        marker_color=COLORS["success"],
        text=[categories[i]["assigned"] for i in range(1, 6)],
        textposition="auto",
    ))
    
    fig.add_trace(go.Bar(
        name="En espera",
        x=cat_names,
        y=[categories[i]["unassigned"] for i in range(1, 6)],
        marker_color=COLORS["danger"],
        text=[categories[i]["unassigned"] for i in range(1, 6)],
        textposition="auto",
    ))
    
    fig.update_layout(
        title=dict(text="<b>Distribución por Categoría Biomédica</b>", font=dict(size=18)),
        barmode="group",
        xaxis=dict(title=""),
        yaxis=dict(title="Número de Pacientes", showgrid=True, gridcolor="#e5e7eb"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", color=COLORS["text"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        width=700,
        margin=dict(l=60, r=40, t=80, b=60),
    )
    
    path = os.path.join(output_dir, "category_bars.html")
    fig.write_html(path)
    print(f"  [OK] Category bars: {path}")


# =============================================================================
# CHART 5: SUMMARY METRICS
# =============================================================================

def create_summary(instance: Dict, solution: Dict, output_dir: str):
    """Create a summary metrics chart."""
    
    patients = instance["patients"]
    assignments = solution.get("assignments", [])
    assigned_ids = {a["patient_id"] for a in assignments}
    
    # Metrics
    total = len(patients)
    assigned = len(assigned_ids)
    obj_value = solution.get("objective_value", 0)
    solve_time = solution.get("solve_time", 0)
    
    total_priority = sum(p["priority"] for p in patients)
    achieved = sum(p["priority"] for p in patients if p["id"] in assigned_ids)
    pct = achieved / total_priority * 100 if total_priority > 0 else 0
    
    fig = make_subplots(
        rows=1, cols=4,
        specs=[[{"type": "indicator"}] * 4],
        horizontal_spacing=0.1,
    )
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=assigned,
        title=dict(text="Pacientes<br>Asignados"),
        number=dict(suffix=f"/{total}", font=dict(size=40, color=COLORS["primary"])),
    ), row=1, col=1)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=pct,
        title=dict(text="Prioridad<br>Capturada"),
        number=dict(suffix="%", font=dict(size=40, color=COLORS["success"])),
    ), row=1, col=2)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=obj_value,
        title=dict(text="Valor<br>Objetivo"),
        number=dict(font=dict(size=40, color=COLORS["secondary"]), valueformat=","),
    ), row=1, col=3)
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=solve_time,
        title=dict(text="Tiempo<br>Solución"),
        number=dict(suffix=" s", font=dict(size=40, color=COLORS["warning"]), valueformat=".2f"),
    ), row=1, col=4)
    
    fig.update_layout(
        title=dict(text="<b>Resumen de Resultados</b>", font=dict(size=20)),
        paper_bgcolor="white",
        font=dict(family="Arial", color=COLORS["text"]),
        height=250,
        width=900,
        margin=dict(l=40, r=40, t=80, b=40),
    )
    
    path = os.path.join(output_dir, "summary.html")
    fig.write_html(path)
    print(f"  [OK] Summary: {path}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python visualizer.py <instance.json>")
        print("Example: python visualizer.py instances/instance_rm_central.json")
        sys.exit(1)
    
    instance_path = sys.argv[1]
    
    if not os.path.exists(instance_path):
        print(f"[ERROR] File not found: {instance_path}")
        sys.exit(1)
    
    # Create output directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "charts")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n=== OR Scheduling Visualizer ===")
    print(f"Instance: {instance_path}")
    print(f"Output: {output_dir}\n")
    
    # Load and solve
    print("[1/6] Loading instance...")
    instance = load_data(instance_path)
    print(f"  Patients: {len(instance['patients'])}, Days: {instance['num_days']}, Rooms: {instance['num_rooms']}")
    
    print("[2/6] Solving...")
    solution = run_solver(instance_path)
    print(f"  Status: {solution['status']}, Objective: {solution['objective_value']}, Assigned: {solution['assigned_count']}")
    
    print("[3/6] Creating Gantt chart...")
    create_gantt_chart(instance, solution, output_dir)
    
    print("[4/6] Creating Calendar view...")
    create_calendar_view(instance, solution, output_dir)
    
    print("[5/6] Creating Patient scatter...")
    create_patient_scatter(instance, solution, output_dir)
    
    print("[6/6] Creating Category bars and Summary...")
    create_category_bars(instance, solution, output_dir)
    create_summary(instance, solution, output_dir)
    
    print(f"\n[DONE] All charts saved to: {output_dir}")
    print("Open the HTML files in a browser and take screenshots for your presentation!")


if __name__ == "__main__":
    main()

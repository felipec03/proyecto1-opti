"""
Operating Room Scheduling Visualizer
=====================================

This module provides stunning, interactive visualizations for the OR Scheduling
optimization problem results. It creates a comprehensive dashboard with:

1. Gantt Chart - Surgery schedule by day and room
2. Patient Overview - Assigned vs. unassigned patients analysis  
3. Benefit Analysis - Cross-instance comparison

Usage:
------
    # Run with default settings (uses first instance found):
    python visualizer.py

    # Or import and use programmatically:
    from visualizer import ORSchedulingVisualizer
    
    viz = ORSchedulingVisualizer()
    viz.run_solver_and_visualize("instances/instance_rm_central.json")

Output:
-------
    Creates HTML dashboard in 'visualizations/' directory.

Author: Felipe - Universidad de Santiago de Chile
Course: Métodos de Optimización II-2025
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
except ImportError as e:
    import sys
    print(f"ERROR: Plotly import failed: {e}")
    print("Install with: pip install plotly")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


# =============================================================================
# THEME CONFIGURATION - Premium Dark Theme
# =============================================================================

THEME = {
    # Background colors
    "bg_primary": "#0f0f1a",
    "bg_secondary": "#1a1a2e",
    "bg_card": "#16213e",
    
    # Accent colors
    "accent_primary": "#e94560",
    "accent_secondary": "#0f3460",
    "accent_tertiary": "#533483",
    
    # Text colors
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "text_muted": "#6c6c6c",
    
    # Chart colors (vibrant palette)
    "palette": [
        "#e94560",  # Red/Pink
        "#0f3460",  # Deep Blue
        "#16c79a",  # Teal
        "#f9ed69",  # Yellow
        "#ff9a3c",  # Orange
        "#533483",  # Purple
        "#00b8a9",  # Cyan
        "#f67280",  # Coral
    ],
    
    # Category colors by medical priority
    "category_colors": {
        1: "#e94560",  # Category 1 (Most Urgent) - Red
        2: "#ff9a3c",  # Category 2 - Orange
        3: "#f9ed69",  # Category 3 - Yellow  
        4: "#16c79a",  # Category 4 - Green
        5: "#0f3460",  # Category 5 (Least Urgent) - Blue
    },
    
    # Room colors
    "room_colors": [
        "#e94560",
        "#16c79a", 
        "#f9ed69",
        "#ff9a3c",
        "#533483",
    ],
    
    # Status colors
    "assigned": "#16c79a",
    "unassigned": "#e94560",
}

# Day names for display
DAY_NAMES = {
    1: "Lunes",
    2: "Martes", 
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_instance(instance_path: str) -> Dict:
    """Load instance data from JSON file."""
    with open(instance_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_layout(title: str, height: int = 600) -> Dict:
    """Create a standardized Plotly layout with premium dark theme."""
    return {
        "title": {
            "text": title,
            "font": {"size": 24, "color": THEME["text_primary"], "family": "Arial Black"},
            "x": 0.5,
            "xanchor": "center",
        },
        "paper_bgcolor": THEME["bg_primary"],
        "plot_bgcolor": THEME["bg_secondary"],
        "font": {"color": THEME["text_primary"], "family": "Arial"},
        "height": height,
        "margin": {"l": 60, "r": 40, "t": 80, "b": 60},
        "legend": {
            "bgcolor": "rgba(22, 33, 62, 0.8)",
            "bordercolor": THEME["accent_secondary"],
            "borderwidth": 1,
            "font": {"color": THEME["text_primary"]},
        },
        "xaxis": {
            "gridcolor": "rgba(255,255,255,0.1)",
            "zerolinecolor": "rgba(255,255,255,0.2)",
        },
        "yaxis": {
            "gridcolor": "rgba(255,255,255,0.1)",
            "zerolinecolor": "rgba(255,255,255,0.2)",
        },
    }


# =============================================================================
# VISUALIZATION CLASS
# =============================================================================

class ORSchedulingVisualizer:
    """
    Creates stunning visualizations for Operating Room Scheduling optimization.
    
    Attributes:
        output_dir (str): Directory to save generated visualizations.
        
    Example:
        >>> viz = ORSchedulingVisualizer()
        >>> viz.run_solver_and_visualize("instances/my_instance.json")
    """
    
    def __init__(self, output_dir: str = "visualizations"):
        """
        Initialize the visualizer.
        
        Args:
            output_dir: Directory where HTML dashboards will be saved.
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def run_solver_and_visualize(self, instance_path: str) -> str:
        """
        Run the solver on an instance and create visualizations.
        
        Args:
            instance_path: Path to the instance JSON file.
            
        Returns:
            Path to the generated HTML dashboard.
        """
        # Import solver
        from solver import solve_instance
        
        # Load instance data
        instance_data = load_instance(instance_path)
        
        # Run solver
        print(f"[SOLVING] Instance: {instance_data['name']}...")
        solution = solve_instance(instance_path)
        
        if solution["status"] != "Optimal":
            print(f"[WARNING] Solver status: {solution['status']}")
        
        print(f"[OK] Solved! Objective: {solution['objective_value']}, "
              f"Assigned: {solution['assigned_count']} patients")
        
        # Create dashboard
        return self.create_dashboard(instance_data, solution)
    
    def create_gantt_chart(self, instance_data: Dict, solution: Dict) -> go.Figure:
        """
        Create an interactive Gantt chart showing the surgery schedule.
        
        The Gantt chart displays:
        - Each surgery as a horizontal bar
        - Organized by day (rows) and room (color)
        - Tooltips with patient details, surgeon, and duration
        
        Args:
            instance_data: The instance configuration data.
            solution: The solver output with assignments.
            
        Returns:
            Plotly Figure object.
        """
        assignments = solution.get("assignments", [])
        
        if not assignments:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="No hay cirugías asignadas en esta instancia",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font={"size": 20, "color": THEME["text_secondary"]}
            )
            fig.update_layout(**create_layout("📊 Diagrama de Gantt - Programación Quirúrgica"))
            return fig
        
        # Build patient lookup
        patients = {p["id"]: p for p in instance_data["patients"]}
        
        # Organize assignments by day and room
        schedule = {}
        for asgn in assignments:
            day = asgn["day"]
            room = asgn["room"]
            key = (day, room)
            if key not in schedule:
                schedule[key] = []
            schedule[key].append(asgn)
        
        # Calculate start times (sequential within each room-day)
        gantt_data = []
        for (day, room), room_assignments in schedule.items():
            current_time = 0  # Start at 8:00 AM (0 minutes offset)
            for asgn in room_assignments:
                patient_id = asgn["patient_id"]
                patient = patients[patient_id]
                duration = patient["duration"]
                
                gantt_data.append({
                    "day": day,
                    "day_name": DAY_NAMES[day],
                    "room": room,
                    "patient_id": patient_id,
                    "surgeon": asgn["surgeon"],
                    "start": current_time,
                    "end": current_time + duration,
                    "duration": duration,
                    "priority": patient["priority"],
                    "category": patient["category"],
                    "waiting_time": patient["waiting_time"],
                })
                current_time += duration
        
        # Create figure
        fig = go.Figure()
        
        # Add bars for each room
        num_rooms = instance_data["num_rooms"]
        for room in range(1, num_rooms + 1):
            room_data = [d for d in gantt_data if d["room"] == room]
            if not room_data:
                continue
                
            color = THEME["room_colors"][(room - 1) % len(THEME["room_colors"])]
            
            for surgery in room_data:
                # Y position: combine day and room
                y_pos = f"{surgery['day_name']}"
                
                fig.add_trace(go.Bar(
                    name=f"Pabellón {room}",
                    x=[surgery["duration"]],
                    y=[y_pos],
                    base=[surgery["start"]],
                    orientation="h",
                    marker={
                        "color": color,
                        "line": {"width": 1, "color": "white"},
                    },
                    text=f"P{surgery['patient_id']}",
                    textposition="inside",
                    textfont={"color": "white", "size": 10},
                    hovertemplate=(
                        f"<b>Paciente {surgery['patient_id']}</b><br>"
                        f"Pabellón: {room}<br>"
                        f"Cirujano: {surgery['surgeon']}<br>"
                        f"Duración: {surgery['duration']} min<br>"
                        f"Prioridad: {surgery['priority']:,}<br>"
                        f"Categoría: {surgery['category']}<br>"
                        f"Días en espera: {surgery['waiting_time']}<br>"
                        f"Inicio: {8 + surgery['start']//60}:{surgery['start']%60:02d}<br>"
                        f"Fin: {8 + surgery['end']//60}:{surgery['end']%60:02d}"
                        "<extra></extra>"
                    ),
                    showlegend=room_data.index(surgery) == 0,  # Only show legend once per room
                    legendgroup=f"room_{room}",
                ))
        
        # Update layout
        layout = create_layout("📊 Diagrama de Gantt — Programación Semanal de Cirugías", height=500)
        layout["barmode"] = "overlay"
        layout["xaxis"] = {
            **layout["xaxis"],
            "title": "Tiempo (minutos desde las 8:00 AM)",
            "range": [0, 600],
            "tickvals": [0, 60, 120, 180, 240, 300, 360, 420, 480, 540],
            "ticktext": ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"],
        }
        layout["yaxis"] = {
            **layout["yaxis"],
            "title": "Día de la Semana",
            "categoryorder": "array",
            "categoryarray": list(DAY_NAMES.values())[::-1],
        }
        
        fig.update_layout(**layout)
        
        # Add capacity line
        fig.add_vline(x=540, line_dash="dash", line_color=THEME["accent_primary"],
                     annotation_text="Capacidad Máx (540 min)", annotation_position="top")
        
        return fig
    
    def create_patient_overview(self, instance_data: Dict, solution: Dict) -> go.Figure:
        """
        Create visualizations showing patient assignment analysis.
        
        Shows scatter plot of Priority vs Waiting Time, colored by assignment status.
        
        Args:
            instance_data: The instance configuration data.
            solution: The solver output with assignments.
            
        Returns:
            Plotly Figure object.
        """
        patients = instance_data["patients"]
        assigned_ids = {a["patient_id"] for a in solution.get("assignments", [])}
        
        # Prepare data
        data = []
        for p in patients:
            data.append({
                "id": p["id"],
                "priority": p["priority"],
                "waiting_time": p["waiting_time"],
                "duration": p["duration"],
                "category": p["category"],
                "assigned": "Asignado ✓" if p["id"] in assigned_ids else "En Lista de Espera",
            })
        
        # Create scatter plot
        fig = go.Figure()
        
        # Assigned patients
        assigned_data = [d for d in data if "✓" in d["assigned"]]
        unassigned_data = [d for d in data if "✓" not in d["assigned"]]
        
        # Unassigned first (so assigned appear on top)
        if unassigned_data:
            fig.add_trace(go.Scatter(
                x=[d["waiting_time"] for d in unassigned_data],
                y=[d["priority"] for d in unassigned_data],
                mode="markers",
                name="En Lista de Espera",
                marker={
                    "color": THEME["unassigned"],
                    "size": [d["duration"] / 10 for d in unassigned_data],
                    "opacity": 0.5,
                    "line": {"width": 1, "color": "white"},
                },
                hovertemplate=(
                    "<b>Paciente %{customdata[0]}</b><br>"
                    "Prioridad: %{y:,}<br>"
                    "Días en espera: %{x}<br>"
                    "Duración: %{customdata[1]} min<br>"
                    "Categoría: %{customdata[2]}"
                    "<extra></extra>"
                ),
                customdata=[[d["id"], d["duration"], d["category"]] for d in unassigned_data],
            ))
        
        if assigned_data:
            fig.add_trace(go.Scatter(
                x=[d["waiting_time"] for d in assigned_data],
                y=[d["priority"] for d in assigned_data],
                mode="markers",
                name="Asignado ✓",
                marker={
                    "color": THEME["assigned"],
                    "size": [d["duration"] / 10 for d in assigned_data],
                    "opacity": 0.9,
                    "line": {"width": 2, "color": "white"},
                    "symbol": "star",
                },
                hovertemplate=(
                    "<b>Paciente %{customdata[0]}</b><br>"
                    "Prioridad: %{y:,}<br>"
                    "Días en espera: %{x}<br>"
                    "Duración: %{customdata[1]} min<br>"
                    "Categoría: %{customdata[2]}"
                    "<extra></extra>"
                ),
                customdata=[[d["id"], d["duration"], d["category"]] for d in assigned_data],
            ))
        
        # Layout
        layout = create_layout(
            "👥 Análisis de Asignación de Pacientes — Prioridad vs Tiempo de Espera",
            height=500
        )
        layout["xaxis"]["title"] = "Días en Lista de Espera"
        layout["yaxis"]["title"] = "Puntaje de Prioridad"
        layout["yaxis"]["type"] = "log"  # Log scale for better visualization
        
        fig.update_layout(**layout)
        
        # Add annotation with stats
        total = len(patients)
        assigned = len(assigned_ids)
        pct = (assigned / total * 100) if total > 0 else 0
        
        fig.add_annotation(
            text=f"<b>{assigned}/{total} pacientes asignados ({pct:.1f}%)</b>",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            font={"size": 14, "color": THEME["assigned"]},
            bgcolor="rgba(22, 33, 62, 0.9)",
            borderpad=8,
        )
        
        return fig
    
    def create_category_distribution(self, instance_data: Dict, solution: Dict) -> go.Figure:
        """
        Create a bar chart showing category distribution of assigned vs unassigned patients.
        
        Args:
            instance_data: The instance configuration data.
            solution: The solver output with assignments.
            
        Returns:
            Plotly Figure object.
        """
        patients = instance_data["patients"]
        assigned_ids = {a["patient_id"] for a in solution.get("assignments", [])}
        
        # Count by category
        categories = {1: {"assigned": 0, "total": 0},
                      2: {"assigned": 0, "total": 0},
                      3: {"assigned": 0, "total": 0},
                      4: {"assigned": 0, "total": 0},
                      5: {"assigned": 0, "total": 0}}
        
        for p in patients:
            cat = p["category"]
            categories[cat]["total"] += 1
            if p["id"] in assigned_ids:
                categories[cat]["assigned"] += 1
        
        # Create grouped bar chart
        fig = go.Figure()
        
        cat_labels = ["Cat. 1\n(Urgente)", "Cat. 2", "Cat. 3", "Cat. 4", "Cat. 5\n(Electivo)"]
        
        fig.add_trace(go.Bar(
            name="Asignados",
            x=cat_labels,
            y=[categories[i]["assigned"] for i in range(1, 6)],
            marker_color=THEME["assigned"],
            text=[categories[i]["assigned"] for i in range(1, 6)],
            textposition="auto",
            textfont={"color": "white"},
        ))
        
        fig.add_trace(go.Bar(
            name="No Asignados",
            x=cat_labels,
            y=[categories[i]["total"] - categories[i]["assigned"] for i in range(1, 6)],
            marker_color=THEME["unassigned"],
            text=[categories[i]["total"] - categories[i]["assigned"] for i in range(1, 6)],
            textposition="auto",
            textfont={"color": "white"},
        ))
        
        layout = create_layout("📊 Distribución por Categoría Biomédica", height=400)
        layout["barmode"] = "group"
        layout["xaxis"]["title"] = "Categoría Biomédica"
        layout["yaxis"]["title"] = "Número de Pacientes"
        
        fig.update_layout(**layout)
        
        return fig
    
    def create_room_utilization(self, instance_data: Dict, solution: Dict) -> go.Figure:
        """
        Create a heatmap showing room utilization across days.
        
        Args:
            instance_data: The instance configuration data.
            solution: The solver output with assignments.
            
        Returns:
            Plotly Figure object.
        """
        patients = {p["id"]: p for p in instance_data["patients"]}
        num_days = instance_data["num_days"]
        num_rooms = instance_data["num_rooms"]
        
        # Calculate utilization matrix
        utilization = [[0 for _ in range(num_rooms)] for _ in range(num_days)]
        
        for asgn in solution.get("assignments", []):
            day = asgn["day"] - 1  # 0-indexed
            room = asgn["room"] - 1
            patient = patients[asgn["patient_id"]]
            utilization[day][room] += patient["duration"]
        
        # Convert to percentage (capacity = 540 mins)
        capacity = 540
        utilization_pct = [[min(u / capacity * 100, 100) for u in row] for row in utilization]
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=utilization_pct,
            x=[f"Pabellón {r+1}" for r in range(num_rooms)],
            y=[DAY_NAMES[d+1] for d in range(num_days)],
            colorscale=[
                [0, THEME["bg_secondary"]],
                [0.5, THEME["accent_tertiary"]],
                [1, THEME["assigned"]],
            ],
            text=[[f"{utilization[d][r]} min\n({utilization_pct[d][r]:.0f}%)" 
                   for r in range(num_rooms)] for d in range(num_days)],
            texttemplate="%{text}",
            textfont={"size": 12, "color": "white"},
            hovertemplate=(
                "%{y} - %{x}<br>"
                "Utilización: %{z:.1f}%<br>"
                "<extra></extra>"
            ),
            colorbar={
                "title": "Utilización %",
                "ticksuffix": "%",
            },
        ))
        
        layout = create_layout("🏥 Mapa de Calor — Utilización de Pabellones", height=400)
        fig.update_layout(**layout)
        
        return fig
    
    def create_benefit_summary(self, instance_data: Dict, solution: Dict) -> go.Figure:
        """
        Create a summary card with key metrics.
        
        Args:
            instance_data: The instance configuration data.
            solution: The solver output with assignments.
            
        Returns:
            Plotly Figure object.
        """
        patients = instance_data["patients"]
        assignments = solution.get("assignments", [])
        assigned_ids = {a["patient_id"] for a in assignments}
        
        # Calculate metrics
        total_patients = len(patients)
        assigned_count = len(assigned_ids)
        
        total_priority_possible = sum(p["priority"] for p in patients)
        achieved_priority = solution.get("objective_value", 0)
        priority_pct = (achieved_priority / total_priority_possible * 100) if total_priority_possible > 0 else 0
        
        total_wait_days = sum(p["waiting_time"] for p in patients if p["id"] in assigned_ids)
        avg_wait_assigned = (total_wait_days / assigned_count) if assigned_count > 0 else 0
        
        solve_time = solution.get("solve_time", 0)
        
        # Create indicator chart
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]],
            vertical_spacing=0.3,
            horizontal_spacing=0.2,
        )
        
        # Patients assigned
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=assigned_count,
            title={"text": "Pacientes Asignados", "font": {"size": 16, "color": THEME["text_primary"]}},
            number={"suffix": f"/{total_patients}", "font": {"color": THEME["assigned"]}},
            gauge={
                "axis": {"range": [0, total_patients], "tickcolor": THEME["text_muted"]},
                "bar": {"color": THEME["assigned"]},
                "bgcolor": THEME["bg_card"],
                "bordercolor": THEME["text_muted"],
            },
        ), row=1, col=1)
        
        # Priority achieved
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=priority_pct,
            title={"text": "Prioridad Capturada", "font": {"size": 16, "color": THEME["text_primary"]}},
            number={"suffix": "%", "font": {"color": THEME["accent_primary"]}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": THEME["text_muted"]},
                "bar": {"color": THEME["accent_primary"]},
                "bgcolor": THEME["bg_card"],
                "bordercolor": THEME["text_muted"],
            },
        ), row=1, col=2)
        
        # Average waiting time
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=avg_wait_assigned,
            title={"text": "Promedio Días de Espera\n(Pacientes Asignados)", 
                   "font": {"size": 14, "color": THEME["text_primary"]}},
            number={"suffix": " días", "font": {"color": THEME["text_primary"]}},
        ), row=2, col=1)
        
        # Solve time
        fig.add_trace(go.Indicator(
            mode="number",
            value=solve_time,
            title={"text": "Tiempo de Solución", 
                   "font": {"size": 16, "color": THEME["text_primary"]}},
            number={"suffix": " seg", "font": {"color": THEME["accent_tertiary"]}, "valueformat": ".2f"},
        ), row=2, col=2)
        
        layout = create_layout("📈 Resumen de Resultados", height=450)
        fig.update_layout(**layout)
        
        return fig
    
    def create_dashboard(self, instance_data: Dict, solution: Dict) -> str:
        """
        Create a complete HTML dashboard with all visualizations.
        
        Args:
            instance_data: The instance configuration data.
            solution: The solver output with assignments.
            
        Returns:
            Path to the saved HTML file.
        """
        instance_name = instance_data["name"]
        print(f"[DASHBOARD] Creating for: {instance_name}")
        
        # Generate all charts
        gantt = self.create_gantt_chart(instance_data, solution)
        patient_overview = self.create_patient_overview(instance_data, solution)
        category_dist = self.create_category_distribution(instance_data, solution)
        room_util = self.create_room_utilization(instance_data, solution)
        summary = self.create_benefit_summary(instance_data, solution)
        
        # Create combined HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard OR Scheduling - {instance_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, {THEME['bg_primary']} 0%, {THEME['bg_secondary']} 100%);
            min-height: 100vh;
            color: {THEME['text_primary']};
        }}
        .header {{
            background: linear-gradient(135deg, {THEME['accent_primary']} 0%, {THEME['accent_tertiary']} 100%);
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }}
        .chart-container {{
            background: rgba(22, 33, 62, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease;
        }}
        .chart-container:hover {{
            transform: translateY(-5px);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: {THEME['text_muted']};
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 30px;
        }}
        .section-title {{
            font-size: 1.5em;
            margin-bottom: 15px;
            color: {THEME['text_primary']};
            border-left: 4px solid {THEME['accent_primary']};
            padding-left: 15px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 Dashboard de Programación Quirúrgica</h1>
        <p>Instancia: <strong>{instance_name}</strong> | Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    
    <div class="container">
        <div class="chart-container">
            <h2 class="section-title">Resumen de Resultados</h2>
            {summary.to_html(full_html=False, include_plotlyjs='cdn')}
        </div>
        
        <div class="chart-container">
            <h2 class="section-title">Programación Semanal de Cirugías</h2>
            {gantt.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="grid">
            <div class="chart-container">
                <h2 class="section-title">Análisis de Pacientes</h2>
                {patient_overview.to_html(full_html=False, include_plotlyjs=False)}
            </div>
            
            <div class="chart-container">
                <h2 class="section-title">Distribución por Categoría</h2>
                {category_dist.to_html(full_html=False, include_plotlyjs=False)}
            </div>
        </div>
        
        <div class="chart-container">
            <h2 class="section-title">Utilización de Pabellones</h2>
            {room_util.to_html(full_html=False, include_plotlyjs=False)}
        </div>
    </div>
    
    <div class="footer">
        <p>Proyecto Métodos de Optimización II-2025 | Universidad de Santiago de Chile</p>
        <p>Modelo: Wolff-Durán (Operating Room Scheduling with Prioritized Lists)</p>
    </div>
</body>
</html>
"""
        
        # Save HTML
        output_path = os.path.join(self.output_dir, f"dashboard_{instance_name}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] Dashboard saved: {output_path}")
        return output_path


# =============================================================================
# CROSS-INSTANCE ANALYSIS
# =============================================================================

def create_cross_instance_analysis(results_csv_path: str, instances_dir: str) -> go.Figure:
    """
    Create a bar chart comparing results across multiple instances.
    
    Args:
        results_csv_path: Path to results.csv file.
        instances_dir: Path to instances directory.
        
    Returns:
        Plotly Figure with comparison chart.
    """
    import csv
    
    # Read results
    results = []
    with open(results_csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('instance'):
                results.append({
                    "instance": row["instance"],
                    "objective": float(row.get("objective_value", 0)),
                    "time": float(row.get("solve_time", 0)),
                    "assigned": int(row.get("assigned_count", 0)),
                })
    
    if not results:
        print("No results found in CSV")
        return None
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Valor Función Objetivo", "Pacientes Asignados", 
                       "Tiempo de Solución", "Eficiencia (Objetivo/Tiempo)"),
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
    )
    
    names = [r["instance"][:25] + "..." if len(r["instance"]) > 25 else r["instance"] for r in results]
    
    # Objective value
    fig.add_trace(go.Bar(
        x=names, y=[r["objective"] for r in results],
        marker_color=THEME["accent_primary"],
        name="Objetivo",
    ), row=1, col=1)
    
    # Assigned count
    fig.add_trace(go.Bar(
        x=names, y=[r["assigned"] for r in results],
        marker_color=THEME["assigned"],
        name="Asignados",
    ), row=1, col=2)
    
    # Solve time
    fig.add_trace(go.Bar(
        x=names, y=[r["time"] for r in results],
        marker_color=THEME["accent_tertiary"],
        name="Tiempo (s)",
    ), row=2, col=1)
    
    # Efficiency (objective / time)
    fig.add_trace(go.Bar(
        x=names, y=[r["objective"] / r["time"] if r["time"] > 0 else 0 for r in results],
        marker_color=THEME["palette"][4],
        name="Eficiencia",
    ), row=2, col=2)
    
    layout = create_layout("📊 Análisis Comparativo de Instancias", height=700)
    layout["showlegend"] = False
    fig.update_layout(**layout)
    
    # Update all xaxes
    fig.update_xaxes(tickangle=45)
    
    return fig


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main function - runs visualization on all available instances.
    
    Usage:
        python visualizer.py
        python visualizer.py path/to/instance.json
    """
    import sys
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize visualizer
    viz = ORSchedulingVisualizer(output_dir=os.path.join(script_dir, "visualizations"))
    
    # Check command line arguments
    if len(sys.argv) > 1:
        instance_path = sys.argv[1]
        if os.path.exists(instance_path):
            viz.run_solver_and_visualize(instance_path)
        else:
            print(f"[ERROR] Instance not found: {instance_path}")
    else:
        # Find all instances
        instances_dir = os.path.join(script_dir, "instances")
        instances = sorted(glob.glob(os.path.join(instances_dir, "*.json")))
        
        if not instances:
            print("[ERROR] No instances found in 'instances/' directory")
            print(f"   Searched: {instances_dir}")
            return
        
        print(f"[FOUND] {len(instances)} instances")
        print("=" * 60)
        
        # Process each instance
        for instance_path in instances:
            try:
                viz.run_solver_and_visualize(instance_path)
                print()
            except Exception as e:
                print(f"[ERROR] Processing {instance_path}: {e}")
                print()
        
        # Create cross-instance analysis if results exist
        results_path = os.path.join(script_dir, "results.csv")
        if os.path.exists(results_path):
            print("[ANALYSIS] Creating cross-instance analysis...")
            analysis_fig = create_cross_instance_analysis(results_path, instances_dir)
            if analysis_fig:
                output_path = os.path.join(viz.output_dir, "cross_instance_analysis.html")
                analysis_fig.write_html(output_path)
                print(f"[OK] Analysis saved: {output_path}")
        
        print("\n" + "=" * 60)
        print("[DONE] All visualizations complete!")
        print(f"[OUTPUT] Directory: {viz.output_dir}")


if __name__ == "__main__":
    main()

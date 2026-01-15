import pulp
import json
import sys
import time
import os

def solve_instance(instance_path, solver_name="CPLEX_CMD", time_limit=300):
    """
    Solves a single OR scheduling instance using PuLP.
    """
    # 1. Load Data
    with open(instance_path, 'r') as f:
        data = json.load(f)

    # Extract Sets and Parameters
    days = range(1, data['num_days'] + 1)
    rooms = range(1, data['num_rooms'] + 1)
    surgeons = sorted([int(s) for s in data['competence'].keys() if "_" not in str(s)]) # This logic is Flawed based on generator structure
    # Let's re-parse surgeons from the keys or just assume 1..num_surgeons
    surgeons = range(1, data['num_surgeons'] + 1)
    
    patients = data['patients']
    patient_ids = [p['id'] for p in patients]
    
    # Mappings
    duration = {p['id']: p['duration'] for p in patients}
    priority = {p['id']: p['priority'] for p in patients}
    
    # Capacities & Compatibility
    # room_capacities: key "d_r" -> min
    # competence: key "s_p" -> 0/1
    # availability: key "s_d" -> 0/1
    # room_compatibility: key "r_p" -> 0/1
    
    # 2. Define Model
    prob = pulp.LpProblem(f"OR_Scheduling_{data['name']}", pulp.LpMaximize)

    # 3. Decision Variables
    # x[p, d, r, s] = 1 if patient p is assigned to day d, room r, surgeon s
    x = pulp.LpVariable.dicts("x", 
                              ((p, d, r, s) for p in patient_ids for d in days for r in rooms for s in surgeons),
                              cat='Binary')

    # 4. Objective Function
    # Maximize Sum(Priority * x)
    prob += pulp.lpSum(priority[p] * x[p, d, r, s] 
                       for p in patient_ids for d in days for r in rooms for s in surgeons), "Maximize_Priority"

    # 5. Constraints

    # (1) Unicidad del Paciente: A patient is operated at most once
    for p in patient_ids:
        prob += pulp.lpSum(x[p, d, r, s] for d in days for r in rooms for s in surgeons) <= 1, f"Patient_Uniqueness_{p}"

    # (2) Capacidad del Pabellon: Total duration <= Capacity
    for d in days:
        for r in rooms:
            capacity = data['room_capacities'].get(f"{d}_{r}", 540) # Default 540 if missing
            prob += pulp.lpSum(duration[p] * x[p, d, r, s] 
                               for p in patient_ids for s in surgeons) <= capacity, f"Room_Capacity_{d}_{r}"

    # (3) Capacidad del Cirujano / No Ubicuidad: Surgeon can be in at most one place at a time?
    # Or total time? The prompt implies "block assignment" or simply "not two places at once".
    # Since we don't have time slots, we can enforce:
    # - A surgeon works at most X minutes per day (Availability)?
    # - A surgeon cannot be in > 1 room per day? (This is too strict, they can do multiple ops).
    # Let's assume Surgeon Capacity in minutes (say 8 hours = 480 mins) AND availability.
    # The generator provides `availability[s_d]`. If 0, surgeon cannot work that day.
    
    for s in surgeons:
        for d in days:
            is_available = data['availability'].get(f"{s}_{d}", 0)
            if is_available == 0:
                 # Cannot work at all
                prob += pulp.lpSum(x[p, d, r, s] for p in patient_ids for r in rooms) == 0, f"Surgeon_Unavailable_{s}_{d}"
            else:
                # Can work, but total duration limit? Let's say max 600 mins per day to be safe,
                # OR, more importantly, can't be in multiple rooms *simultaneously*?
                # Without time slots, we can't strictly enforce "simultaneity" unless we sum durations.
                # Let's enforce total duration <= Day Length (same as room).
                prob += pulp.lpSum(duration[p] * x[p, d, r, s] 
                                   for p in patient_ids for r in rooms) <= 540, f"Surgeon_TimeLimit_{s}_{d}"

    # (4) Competencia Tecnica
    for p in patient_ids:
        for s in surgeons:
            is_competent = data['competence'].get(f"{s}_{p}", 0)
            if is_competent == 0:
                for d in days:
                    for r in rooms:
                        prob += x[p, d, r, s] == 0, f"Incompetent_{s}_{p}_{d}_{r}"
                        
    # (5) Factibilidad Infraestructura (Room Compatible)
    for p in patient_ids:
        for r in rooms:
            is_compatible = data['room_compatibility'].get(f"{r}_{p}", 0)
            if is_compatible == 0:
                for d in days:
                    for s in surgeons:
                        prob += x[p, d, r, s] == 0, f"IncompatibleRoom_{r}_{p}_{d}_{s}"

    # 6. Solve
    solver = pulp.getSolver(solver_name, timeLimit=time_limit, msg=False)
    
    # Fallback to CBC if CPLEX not available (but try CPLEX first as requested)
    if not solver.available():
        # print("Solver not available, trying default CBC")
        solver = pulp.PULP_CBC_CMD(timeLimit=time_limit, msg=False)

    start_time = time.time()
    status = prob.solve(solver)
    solve_time = time.time() - start_time

    # 7. Results
    status_str = pulp.LpStatus[status]
    obj_value = pulp.value(prob.objective)
    
    assigned_patients = []
    for p in patient_ids:
        for d in days:
            for r in rooms:
                for s in surgeons:
                    if pulp.value(x[p, d, r, s]) and pulp.value(x[p, d, r, s]) > 0.5:
                        assigned_patients.append({
                            "patient_id": p,
                            "day": d,
                            "room": r,
                            "surgeon": s
                        })
    
    result = {
        "instance": data['name'],
        "status": status_str,
        "objective_value": obj_value,
        "solve_time": solve_time,
        "assigned_count": len(assigned_patients),
        "assignments": assigned_patients
    }
    
    return result

if __name__ == "__main__":
    # Test with one instance if run directly. Look for instances next to this script first,
    # then fall back to a CWD 'instances/' directory.
    import glob
    script_dir = os.path.dirname(os.path.abspath(__file__))
    instances = sorted(glob.glob(os.path.join(script_dir, "instances", "*.json")))
    if not instances:
        instances = sorted(glob.glob(os.path.join(os.getcwd(), "instances", "*.json")))

    if instances:
        res = solve_instance(instances[0])
        print(json.dumps(res, indent=4))
    else:
        print(f"No instances found. Checked: {os.path.join(script_dir,'instances')} and {os.path.join(os.getcwd(),'instances')}")

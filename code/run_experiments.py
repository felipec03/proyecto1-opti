import glob
import json
import csv
import os
from solver import solve_instance

def run_all():
    instance_files = sorted(glob.glob("instances/*.json"))
    results = []
    
    print(f"Found {len(instance_files)} instances. Starting experiments...")
    
    for instance_path in instance_files:
        print(f"Solving {instance_path}...")
        try:
            res = solve_instance(instance_path, time_limit=300)
            results.append(res)
            print(f"  -> Solved in {res['solve_time']:.2f}s. Obj: {res['objective_value']}")
        except Exception as e:
            print(f"  -> Failed: {e}")
            results.append({
                "instance": os.path.basename(instance_path),
                "status": "Failed",
                "objective_value": 0,
                "solve_time": 0,
                "assigned_count": 0
            })
            
    # Save results to CSV
    keys = ['instance', 'status', 'objective_value', 'solve_time', 'assigned_count']
    with open("results.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in results:
            # Filter only keys we want to write
            row = {k: r.get(k, 0) for k in keys}
            writer.writerow(row)
    print("Results saved to results.csv")
    
    # Generate a brief report (Markdown table)
    with open("report.md", "w") as f:
        f.write("# Experiment Results\n\n")
        f.write("| Instance | Status | Objective | Time (s) | Assigned |\n")
        f.write("|---|---|---|---|---|\n")
        for r in results:
            f.write(f"| {r.get('instance')} | {r.get('status')} | {r.get('objective_value'):.2f} | {r.get('solve_time'):.2f} | {r.get('assigned_count')} |\n")
        
    print("Report saved to report.md")

if __name__ == "__main__":
    run_all()

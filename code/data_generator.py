import json
import random
import os
import math

def generate_instances(num_instances=10, output_dir="instances"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    instances = []
    
    for i in range(1, num_instances + 1):
        # Instance configuration parameters
        num_patients = random.randint(50, 100)
        num_days = 5  # Monday to Friday
        num_rooms = random.randint(2, 4)
        num_surgeons = random.randint(5, 10)
        
        # Room Capacity (Time in minutes, e.g., 8am - 5pm = 9 hours = 540 mins)
        room_capacities = {}
        for d in range(1, num_days + 1):
            for r in range(1, num_rooms + 1):
                room_capacities[f"{d}_{r}"] = 540 # Consistent capacity

        # Surgeons
        surgeons = []
        surgeon_specialties = {} # Surgeon -> List of specialties
        for s in range(1, num_surgeons + 1):
            surgeons.append(s)
            # Each surgeon has 1-2 specialties out of 5 possible types
            surgeon_specialties[s] = random.sample([1, 2, 3, 4, 5], k=random.randint(1, 2))
            
        # Patients
        patients = []
        for p in range(1, num_patients + 1):
            # waiting time 0-365 days
            waiting_time = random.randint(0, 365)
            # Clinical category 1-5 (5 is most urgent theoretically, or we strictly follow the table)
            # Table 2 in paper: A, B, C, D, E. Let's map A=1 (most urgent) to E=5.
            # Actually, paper DUMP says: "Prioridad_p is derived from biomedical category and waiting time"
            # Paper ILP1 uses NAWD = Pond_i * t_ei. Pond_i in {1,2,4,12,48} for categories.
            # Let's assign a biomedical category 1-5.
            category_weights = {1: 48, 2: 12, 3: 4, 4: 2, 5: 1}
            biomed_category = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.2, 0.3, 0.2, 0.2])[0]
            
            # Simple priority score directly proportional to need (or we can use the formula directly in the solver)
            # Here we pre-calculate a "Priority" score to be simple for the MILP input.
            # Score = Weight * (Waiting Time + 1)
            priority_score = category_weights[biomed_category] * (waiting_time + 1)
            
            # Duration (Log-Normal roughly centered on 90-120 mins)
            # mu=4.5, sigma=0.6 -> median exp(4.5) ~= 90 mins. Max could be 300+.
            duration = int(random.lognormvariate(4.5, 0.6))
            duration = max(30, min(duration, 300)) # Clamp between 30 mins and 5 hours
            
            # Required Specialty
            required_specialty = random.randint(1, 5)
            
            patients.append({
                "id": p,
                "duration": duration,
                "priority": priority_score,
                "category": biomed_category,
                "waiting_time": waiting_time,
                "required_specialty": required_specialty
            })
            
        # Competence Matrix (Surgeon s can operate Patient p)
        competence = {}
        for p_data in patients:
            p_id = p_data['id']
            p_spec = p_data['required_specialty']
            for s_id in surgeons:
                if p_spec in surgeon_specialties[s_id]:
                    competence[f"{s_id}_{p_id}"] = 1
                else:
                    competence[f"{s_id}_{p_id}"] = 0
                    
        # Surgeon Availability (assume 80% available on any given day)
        availability = {}
        for s_id in surgeons:
            for d in range(1, num_days + 1):
                availability[f"{s_id}_{d}"] = 1 if random.random() < 0.85 else 0
                
        # Equipment/Room Compatibility (assume 90% compatible)
        room_compatibility = {}
        for p_data in patients:
            p_id = p_data['id']
            for r in range(1, num_rooms + 1):
                room_compatibility[f"{r}_{p_id}"] = 1 if random.random() < 0.9 else 0

        instance_data = {
            "name": f"instance_{i}",
            "num_days": num_days,
            "num_rooms": num_rooms,
            "num_surgeons": num_surgeons,
            "patients": patients,
            "room_capacities": room_capacities,
            "competence": competence,
            "availability": availability,
            "room_compatibility": room_compatibility
        }
        
        filename = os.path.join(output_dir, f"instance_{i}.json")
        with open(filename, 'w') as f:
            json.dump(instance_data, f, indent=4)
        instances.append(filename)

    print(f"Generated {len(instances)} instances in {output_dir}")


# Use a relative 'instances' directory located next to this script when run directly.
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_output = os.path.join(script_dir, "instances")
    generate_instances(output_dir=default_output)

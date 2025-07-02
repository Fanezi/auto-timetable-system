# timetable/constraints_cp.py

from ortools.sat.python import cp_model
from timetable.utils import load_modules, load_lecturers, load_venues, load_enrollments
from timetable.slot_model import generate_time_slots, get_double_periods

def solve_timetable():
    # Load data
    modules_df = load_modules()
    lecturers_df = load_lecturers()
    venues_df = load_venues()
    enrollments_df = load_enrollments()

    # Create model
    model = cp_model.CpModel()

    # Time slots
    slots = generate_time_slots()
    double_periods = get_double_periods(slots)
    num_slots = len(slots)
    num_venues = len(venues_df)
    num_modules = len(modules_df)

    # Data mappings
    module_ids = modules_df["ModuleCode"].tolist()
    venue_ids = venues_df["Venue"].tolist()
    module_to_lecturer = dict(zip(modules_df["ModuleCode"], modules_df["Lecturer"]))
    venue_cap = dict(zip(venues_df["Venue"], venues_df["Capacity"]))
    module_enroll = dict(zip(enrollments_df["ModuleCode"], enrollments_df["Enrolled"]))
    module_cohort = dict(zip(enrollments_df["ModuleCode"], enrollments_df["Cohort"]))

    # Day mapping (based on slot index range)
    slot_id_to_day = {}
    for i, slot in enumerate(slots):
        hour = slot["start"].hour
        if hour < 10:
            day = "Mon"
        elif hour < 12:
            day = "Tue"
        elif hour < 14:
            day = "Wed"
        elif hour < 16:
            day = "Thu"
        else:
            day = "Fri"
        slot_id_to_day[i] = day

    def get_day(slot_index):
        return slot_id_to_day.get(slot_index, "Unknown")

    # Assignment variables: 3 double periods per module
    assignment = {}
    for m in module_ids:
        for i in range(3):
            slot_var = model.NewIntVar(0, len(double_periods) - 1, f"slot_{m}_{i}")
            venue_var = model.NewIntVar(0, num_venues - 1, f"venue_{m}_{i}")
            assignment[(m, i)] = (slot_var, venue_var)

    # Constraint 1: No module uses same slot twice
    for m in module_ids:
        slots_used = [assignment[(m, i)][0] for i in range(3)]
        model.AddAllDifferent(slots_used)

    # Constraint 2: No same slot+venue for different modules
    all_assignments = list(assignment.items())
    for i in range(len(all_assignments)):
        (m1, _), (s1, v1) = all_assignments[i]
        for j in range(i + 1, len(all_assignments)):
            (m2, _), (s2, v2) = all_assignments[j]
            model.Add(s1 != s2).OnlyEnforceIf(v1 == v2)

    # Constraint 3: No lecturer teaches 2 modules at same time
    for i, m1 in enumerate(module_ids):
        for j, m2 in enumerate(module_ids):
            if i >= j: continue
            if module_to_lecturer[m1] != module_to_lecturer[m2]: continue
            for a in range(3):
                for b in range(3):
                    s1, _ = assignment[(m1, a)]
                    s2, _ = assignment[(m2, b)]
                    model.Add(s1 != s2)

    # Constraint 4: No overlap of compulsory modules per cohort
    for i, m1 in enumerate(module_ids):
        for j, m2 in enumerate(module_ids):
            if i >= j: continue
            if module_cohort.get(m1) != module_cohort.get(m2): continue
            for a in range(3):
                for b in range(3):
                    s1, _ = assignment[(m1, a)]
                    s2, _ = assignment[(m2, b)]
                    model.Add(s1 != s2)

    # Constraint 5: Venue capacity must be sufficient
    for (m, i), (slot_var, venue_var) in assignment.items():
        for v_idx, v_name in enumerate(venue_ids):
            if module_enroll[m] > venue_cap[v_name]:
                model.Add(venue_var != v_idx)

    # Solve model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        print("\n🗓 Final Timetable:\n")
        for (m, i), (slot_var, venue_var) in assignment.items():
            slot_idx = solver.Value(slot_var)
            venue_name = venue_ids[solver.Value(venue_var)]
            slot_pair = double_periods[slot_idx]
            slot1 = slots[slot_pair[0]]
            slot2 = slots[slot_pair[1]]
            day = get_day(slot_pair[0])
            label = f"{slot1['label']} + {slot2['label']}"
            print(f"📘 Module {m:<10} | Period {i+1} | {day:<3} | {label:<25} | Venue: {venue_name}")
    else:
        print("❌ No feasible solution found.\n")
        print("📋 Modules, Cohorts, and Lecturers:")
        for mod in module_ids:
            print(f"Module {mod} | Cohort: {module_cohort.get(mod)} | Lecturer: {module_to_lecturer.get(mod)} | Enrolled: {module_enroll.get(mod)}")
        print("\n🛠 Tip: Check for too many modules in same cohort/lecturer, or limited venue/time availability.")

if __name__ == "__main__":
    solve_timetable()


from datetime import time, timedelta, datetime

# Define all valid time slots (each is 45 mins)
SLOT_DURATION = timedelta(minutes=45)
BREAK_DURATION = timedelta(minutes=5)

# Define the start and end of the academic day
DAY_START = datetime.strptime("08:00", "%H:%M")
LUNCH_START = datetime.strptime("13:00", "%H:%M")
DAY_END = datetime.strptime("17:05", "%H:%M")  # last slot ends here

# Define breaks (5 mins) AFTER most slots except slot 0–1 and 7–8 (double periods)
SKIP_BREAK_AFTER = [0, 7]  # Don't insert break after these for double periods

# Generate slots with optional breaks
def generate_time_slots():
    slots = []
    current_time = DAY_START
    slot_id = 0

    while current_time + SLOT_DURATION <= DAY_END:
        end_time = current_time + SLOT_DURATION
        label = f"{current_time.strftime('%H:%M')} – {end_time.strftime('%H:%M')}"
        slots.append({
            "slot_id": slot_id,
            "start": current_time.time(),
            "end": end_time.time(),
            "label": label
        })
        slot_id += 1

        # Add a 5-min break unless it's a double period transition
        if (slot_id - 1) not in SKIP_BREAK_AFTER:
            current_time = end_time + BREAK_DURATION
        else:
            current_time = end_time

        # Skip over lunch
        if current_time >= LUNCH_START and current_time < (LUNCH_START + timedelta(minutes=60)):
            current_time = LUNCH_START + timedelta(minutes=60)

    return slots

# Define valid double-period slot pairs
def get_double_periods(slots):
    double_periods = []

    for i in range(len(slots) - 1):
        # Get two consecutive slots
        s1 = slots[i]
        s2 = slots[i + 1]

        # Check if they are continuous (no break between them)
        s1_end = datetime.combine(datetime.today(), s1["end"])
        s2_start = datetime.combine(datetime.today(), s2["start"])

        if (s2_start - s1_end) <= timedelta(minutes=1):  # treat <=1 min as continuous
            double_periods.append((s1["slot_id"], s2["slot_id"]))

    return double_periods

# For testing
if __name__ == "__main__":
    slots = generate_time_slots()
    for slot in slots:
        print(f"Slot {slot['slot_id']}: {slot['label']}")

    print("\nValid Double Periods (90 mins):")
    for pair in get_double_periods(slots):
        print(f"Slot Pair: {pair}")

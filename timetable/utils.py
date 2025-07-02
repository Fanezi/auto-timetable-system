import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_lecturers():
    path = os.path.join(DATA_DIR, "lecturers.csv")
    return pd.read_csv(path)

def load_modules():
    path = os.path.join(DATA_DIR, "modules.csv")
    return pd.read_csv(path)

def load_venues():
    path = os.path.join(DATA_DIR, "venues.csv")
    return pd.read_csv(path)

def load_enrollments():
    path = os.path.join(DATA_DIR, "enrollments.csv")
    return pd.read_csv(path)

# Test all loaders
if __name__ == "__main__":
    print("Lecturers:")
    print(load_lecturers().head())

    print("\nModules:")
    print(load_modules().head())

    print("\nVenues:")
    print(load_venues().head())

    print("\nEnrollments:")
    print(load_enrollments().head())

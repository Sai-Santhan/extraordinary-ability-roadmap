#!/usr/bin/env python3
"""Export Pydantic models to JSON Schema files for frontend consumption."""
import json
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.models.schemas import (
    ImmigrationProfile,
    CriteriaAssessment,
    ImmigrationRoadmap,
    RawCareerData,
)

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")
os.makedirs(SCHEMA_DIR, exist_ok=True)

for model in [ImmigrationProfile, CriteriaAssessment, ImmigrationRoadmap, RawCareerData]:
    path = os.path.join(SCHEMA_DIR, f"{model.__name__}.json")
    with open(path, "w") as f:
        json.dump(model.model_json_schema(), f, indent=2)
    print(f"Wrote {path}")

print("\nAll schemas exported successfully!")

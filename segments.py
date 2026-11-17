from profiles import build
from records import fingerprint


def fixed_groups(data, as_of):
    profiles = build(data, as_of)
    assignments = []
    for row in profiles["rows"]:
        if row["deliveries"] < 3:
            group = "new"
        elif row["on_time_rate"] >= .5 and row["off_grade_rate"] <= .05:
            group = "stable"
        else:
            group = "followup"
        assignments.append({"supplier": row["supplier"], "group": group, "basis": "fixed-rules-1"})
    result = {"profile_id": profiles["profile_id"], "assignments": assignments}
    return {**result, "segment_version": fingerprint(result)}


def effective_members(data, as_of):
    current = fixed_groups(data, as_of)
    overrides = {row["supplier"]: row for row in data["overrides"]
                 if row["starts_on"] <= as_of and (row["ends_on"] is None or as_of < row["ends_on"])}
    result = []
    for row in current["assignments"]:
        override = overrides.get(row["supplier"])
        result.append({**row, "data_group": row["group"], "group": override["group"] if override else row["group"],
                       "override_reason": override["reason"] if override else None})
    return {**current, "assignments": result}

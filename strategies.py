from segments import effective_members
from records import fingerprint


def dispatch(data, as_of):
    members = effective_members(data, as_of)
    policies = {row["group"]: row for row in data["strategies"]}
    result = []
    for member in members["assignments"]:
        group = member["group"]
        if group not in policies:
            raise ValueError("分组没有对应经营策略")
        policy = policies[group]
        result.append({"supplier": member["supplier"], "group": group,
                       "inspection_fraction": policy["inspection_fraction"],
                       "followup_days": policy["followup_days"], "manual": member["override_reason"] is not None})
    return {"profile_id": members["profile_id"], "segment_version": members["segment_version"],
            "dispatch_id": fingerprint(result), "actions": result}


def summarize(data, as_of):
    groups = {}
    for row in dispatch(data, as_of)["actions"]:
        group = groups.setdefault(row["group"], {"suppliers": 0, "manual_assignments": 0})
        group["suppliers"] += 1
        group["manual_assignments"] += row["manual"]
    return groups

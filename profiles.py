from datetime import date, timedelta
from records import latest, quantity, fingerprint


def build(data, as_of, window_days=60):
    if window_days < 1:
        raise ValueError("画像窗口须大于零")
    first = (date.fromisoformat(as_of) - timedelta(days=window_days - 1)).isoformat()
    groups = {row["supplier"]: [] for row in data["suppliers"] if row["joined_on"] <= as_of}
    for row in latest(data["deliveries"], "delivery_id", as_of):
        if first <= row["day"] <= as_of and row["supplier"] in groups:
            groups[row["supplier"]].append(row)
    rows = []
    for supplier, deliveries in sorted(groups.items()):
        received = sum(quantity(row["received_kg"]) for row in deliveries)
        off_grade = sum(quantity(row["off_grade_kg"]) for row in deliveries)
        if off_grade > received:
            raise ValueError("规格偏差重量超过到货重量")
        rows.append({"supplier": supplier, "deliveries": len(deliveries), "received_kg": received,
                     "on_time_rate": sum(row["late_hours"] == 0 for row in deliveries) / len(deliveries) if deliveries else None,
                     "off_grade_rate": off_grade / received if received else None})
    result = {"as_of": as_of, "window_days": window_days, "rows": rows}
    return {**result, "profile_id": fingerprint(result)}


def mixed_exposure(data, as_of):
    rows = []
    for row in latest(data["mixed_loads"], "load_id", as_of):
        mass = sum(quantity(value) for value in row["supplier_kg"].values())
        if not mass or quantity(row["off_grade_kg"]) > quantity(row["checked_kg"]):
            raise ValueError("混合车次质量记录无效")
        rows.append({**row, "load_kg": mass, "suppliers": sorted(row["supplier_kg"])})
    return {"loads": rows, "independent_rechecks": latest(data["independent_rechecks"], "check_id", as_of)}

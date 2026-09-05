def recommendations(stockouts, overstocked, nonmoving):
    output = []
    for row in stockouts:
        output.append({"issue": "Stock-out risk", "evidence": f"{row['closing_stock']} units available", "calculation": f"{row['closing_stock']} / {row['ads']:.2f} = {row['doi']:.2f} days", "recommendation": "Place a replenishment order immediately.", "priority": "Critical" if row["status"] == "CRITICAL" else "Warning", "assumption": "Recent demand remains approximately stable."})
    for row in overstocked:
        output.append({"issue": "Overstock", "evidence": f"{row['closing_stock']} units vs target {row['target_stock']}", "calculation": f"{row['excess_units']} excess units x ₹{row['unit_price']:.2f} = ₹{row['excess_capital']:.2f}", "recommendation": "Consider a promotion or stock transfer.", "priority": "Medium", "assumption": "Target stock is an appropriate holding level."})
    for row in nonmoving:
        output.append({"issue": "Non-moving product", "evidence": "Zero positive sales in the last 30 days", "calculation": "30-day quantity sold = 0", "recommendation": "Promote or review purchasing before replenishing.", "priority": "Medium", "assumption": "The sales records cover the full analysis period."})
    return output

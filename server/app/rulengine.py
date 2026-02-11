class IMCIRuleEngine:

    def __init__(self, rules, patient):
        self.rules = rules
        self.patient = patient

    def evaluate(self):
        matched = []

        for rule in self.rules:
            score = self.evaluate_node(rule["criteria"])

            if score > 0:
                confidence = score * rule.get("base_confidence", 1.0)

                matched.append({
                    "module": rule["module"],
                    "condition": rule["classification"],
                    "severity": rule["severity"],
                    "priority": rule["priority"],
                    "confidence": round(confidence, 2)
                })

        return self.aggregate(matched)

    # ----------------------------------------
    # Recursive Evaluator
    # ----------------------------------------

    def evaluate_node(self, node):

        # If logical group
        if "logic" in node:
            scores = [self.evaluate_node(cond) for cond in node["conditions"]]

            if node["logic"] == "AND":
                return sum(scores) / len(scores) if all(s > 0 for s in scores) else 0

            elif node["logic"] == "OR":
                return max(scores)

        # If simple condition
        return self.evaluate_condition(node)

    # ----------------------------------------
    # Condition evaluator
    # ----------------------------------------

    def evaluate_condition(self, cond):

        field = cond.get("field")
        operator = cond.get("operator")
        weight = cond.get("weight", 1.0)

        value = self.patient.get(field)

        if value is None:
            return 0

        # Age-based threshold
        if "age_based" in cond:
            age = self.patient.get("age_months")

            for age_range, threshold in cond["age_based"].items():
                min_age, max_age = map(int, age_range.split("-"))
                if min_age <= age <= max_age:
                    if value >= threshold:
                        return weight
                    else:
                        return 0

        # Standard comparison
        target = cond.get("value")

        if operator == "==":
            return weight if value == target else 0
        elif operator == ">=":
            return weight if value >= target else 0
        elif operator == "<=":
            return weight if value <= target else 0
        elif operator == ">":
            return weight if value > target else 0
        elif operator == "<":
            return weight if value < target else 0

        return 0

    # ----------------------------------------
    # Aggregate Results
    # ----------------------------------------

    def aggregate(self, matched):

        if not matched:
            return {
                "overall_risk_level": "Low",
                "classifications": []
            }

        highest = min(matched, key=lambda x: x["priority"])

        return {
            "overall_risk_level": highest["severity"],
            "classifications": sorted(
                matched,
                key=lambda x: (x["priority"], -x["confidence"])
            )
        }

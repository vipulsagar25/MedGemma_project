class IMCIRuleEngine:

    def __init__(self, rules, patient):
        self.rules = rules
        self.patient = patient

    # ----------------------------------------
    # Main Evaluation Entry
    # ----------------------------------------

    def evaluate(self):
        matched = []

        for rule in self.rules:
            score = self.evaluate_node(rule.get("criteria", {}))

            if score > 0:
                confidence = score * rule.get("base_confidence", 1.0)

                matched.append({
                    "module": rule.get("module"),
                    "condition": rule.get("classification"),
                    "severity": rule.get("severity"),
                    "priority": rule.get("priority", 999),
                    "confidence": round(confidence, 2)
                })

        return self.aggregate(matched)

    # ----------------------------------------
    # Recursive Evaluator
    # ----------------------------------------

    def evaluate_node(self, node):

        if not node:
            return 0

        # Logical group (AND / OR)
        if "logic" in node and "conditions" in node:

            scores = [self.evaluate_node(cond) for cond in node["conditions"]]

            if not scores:
                return 0

            if node["logic"] == "AND":
                # All conditions must pass
                if all(s > 0 for s in scores):
                    return min(scores)  # weakest link defines strength
                return 0

            elif node["logic"] == "OR":
                return max(scores)

            return 0

        # Simple condition
        return self.evaluate_condition(node)

    # ----------------------------------------
    # Condition Evaluator
    # ----------------------------------------

    def evaluate_condition(self, cond):

        field = cond.get("field")
        operator = cond.get("operator")
        weight = cond.get("weight", 1.0)

        if not field or not operator:
            return 0

        value = self.patient.get(field)

        # Missing field → no match
        if value is None:
            return 0

        # ------------------------------------
        # Age-Based Threshold Handling
        # ------------------------------------

        if "age_based" in cond:
            age = self.patient.get("age_months")

            if age is None:
                return 0

            for age_range, threshold in cond["age_based"].items():
                try:
                    min_age, max_age = map(int, age_range.split("-"))
                except ValueError:
                    continue

                if min_age <= age <= max_age:
                    return weight if value >= threshold else 0

            return 0

        # ------------------------------------
        # Standard Comparisons
        # ------------------------------------

        target = cond.get("value")

        try:
            if operator == "==":
                return weight if value == target else 0

            elif operator == "!=":
                return weight if value != target else 0

            elif operator == ">=":
                return weight if value >= target else 0

            elif operator == "<=":
                return weight if value <= target else 0

            elif operator == ">":
                return weight if value > target else 0

            elif operator == "<":
                return weight if value < target else 0

            elif operator == "in":
                return weight if value in target else 0

            elif operator == "exists":
                return weight if value is not None else 0

        except Exception:
            # Defensive safety
            return 0

        return 0

    # ----------------------------------------
    # Aggregation Logic
    # ----------------------------------------

    def aggregate(self, matched):

        if not matched:
            return {
                "overall_risk_level": "Low",
                "classifications": []
            }

        # Sort by priority first, then highest confidence
        sorted_matches = sorted(
            matched,
            key=lambda x: (x["priority"], -x["confidence"])
        )

        highest = sorted_matches[0]

        return {
            "overall_risk_level": highest["severity"],
            "classifications": sorted_matches
        }

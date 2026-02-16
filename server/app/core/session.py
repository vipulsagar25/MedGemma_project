class TriageSession:

    def __init__(self):
        self.patient_data = {
            "age_months": None,
            "cough": None,
            "fever": None,
            "respiratory_rate": None,
            "chest_indrawing": None,
            "convulsions": None
        }

        self.status = "incomplete"

    def update_patient_data(self, extracted_data: dict):
        for key, value in extracted_data.items():
            if key in self.patient_data and value is not None:
                self.patient_data[key] = value

    def get_missing_fields(self):
        return [k for k, v in self.patient_data.items() if v is None]

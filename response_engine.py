import json
from collections import defaultdict

from nlp import contains_keyword, preprocess


class ResponseEngine:
    def __init__(self, kb_path="knowledge_base.json", symptom_path="symptom.json"):
        # Load knowledge base
        with open(kb_path, "r", encoding="utf-8") as f:
            self.kb = json.load(f)

        # Load symptom data
        with open(symptom_path, "r", encoding="utf-8") as f:
            self.symptom_data = json.load(f)

        # Normalize keywords (lowercase)
        for entry in self.kb.get("entries", []):
            entry["keywords"] = [kw.lower() for kw in entry.get("keywords", [])]

        # Process symptom data: group symptoms by disease
        self.disease_symptoms = defaultdict(set)
        for entry in self.symptom_data:
            disease = entry["disease"]
            symptoms = [s.lower().replace(" ", "_") for s in entry["symptoms"]]
            self.disease_symptoms[disease].update(symptoms)

    def _normalize_lang(self, lang: str) -> str:
        if not lang:
            return "en"
        lang = lang.lower().strip()
        if lang in {"or", "odia", "oriya"}:
            return "or"
        return "en"

    def _localize(self, key: str, lang: str) -> str:
        messages = {
            "fallback": {
                "en": "I'm sorry, I do not have enough information. Please consult a medical professional.",
                "or": "ମୁଁ ପର୍ଯ୍ୟାପ୍ତ ସୂଚନା ପାଇନି। ଦୟାକରି ଡାକ୍ତରଙ୍କ ସହ କଥା ହୁଅନ୍ତୁ।",
            },
            "odia_missing_translation": {
                "en": "This response is currently available in English only.",
                "or": "ଏହି ଉତ୍ତରର ଓଡ଼ିଆ ସଂସ୍କରଣ ବର୍ତ୍ତମାନ ଉପଲବ୍ଧ ନାହିଁ।",
            },
            "diagnosis_intro": {
                "en": "Based on your symptoms, the most likely conditions could be: {diseases}.",
                "or": "ଆପଣଙ୍କ ଲକ୍ଷଣ ଅନୁସାରେ ସମ୍ଭାବ୍ୟ ରୋଗଗୁଡ଼ିକ ହେଲା: {diseases}।",
            },
            "diagnosis_next_steps": {
                "en": "What you can do now:",
                "or": "ଏବେ କଣ କରିପାରିବେ:",
            },
            "diagnosis_step_1": {
                "en": "1. Rest and stay hydrated.",
                "or": "1. ବିଶ୍ରାମ କରନ୍ତୁ ଏବଂ ପର୍ଯ୍ୟାପ୍ତ ପାଣି ପିଉନ୍ତୁ।",
            },
            "diagnosis_step_2": {
                "en": "2. Avoid self-medication and over-the-counter drugs unless advised by a doctor.",
                "or": "2. ଡାକ୍ତରୀ ପରାମର୍ଶ ଛଡ଼ା ନିଜେ ଔଷଧ ନଖାନ୍ତୁ।",
            },
            "diagnosis_step_3": {
                "en": "3. Monitor any changes in symptoms (fever, breathing, pain, rash, etc.).",
                "or": "3. ଜ୍ୱର, ଶ୍ୱାସକଷ୍ଟ, ବେଦନା, ଚୁଲୁକାଣି ଭଳି ଲକ୍ଷଣର ପରିବର୍ତ୍ତନ ଧ୍ୟାନରେ ରଖନ୍ତୁ।",
            },
            "diagnosis_step_4": {
                "en": "4. Seek medical advice for a proper diagnosis and treatment plan.",
                "or": "4. ଠିକ୍ ଚିକିତ୍ସା ପାଇଁ ଡାକ୍ତରଙ୍କ ପରାମର୍ଶ ନିଅନ୍ତୁ।",
            },
            "diagnosis_urgent": {
                "en": "Seek immediate medical care if you experience: difficulty breathing, chest pain, severe bleeding, confusion, or loss of consciousness.",
                "or": "ଯଦି ଶ୍ୱାସ ନେବାରେ କଷ୍ଟ, ଛାତିରେ ବେଦନା, ଅଧିକ ରକ୍ତସ୍ରାବ, ଅସ୍ପଷ୍ଟ ଚେତନା ବା ଅସୁଚେତନତା ହୁଏ, ତୁରନ୍ତ ଚିକିତ୍ସା ନିଅନ୍ତୁ।",
            },
        }
        return messages.get(key, {}).get(lang, messages.get(key, {}).get("en", ""))

    def _get_entry_response(self, entry: dict, lang: str) -> str:
        if lang == "or":
            if entry.get("response_or"):
                return entry["response_or"]
            if entry.get("odia_response"):
                return entry["odia_response"]
            responses = entry.get("responses")
            if isinstance(responses, dict) and responses.get("or"):
                return responses["or"]

            # Return English response directly if Odia not available
            english = entry.get("response", "")
            if english:
                return english
            return self._localize("fallback", lang)

        return entry.get("response", self._localize("fallback", "en"))

    def diagnose_symptoms(self, user_text, top_n: int = 3):
        """Return a list of possible diseases based on symptoms mentioned in user_text.

        Returns a list of dicts, each containing:
            - disease
            - match_ratio (0-1)
            - match_count
            - total_symptoms
        """
        text = preprocess(user_text)
        all_symptoms = set()
        for symptoms in self.disease_symptoms.values():
            all_symptoms.update(symptoms)

        mentioned_symptoms = set()
        for symptom in all_symptoms:
            if contains_keyword(text, symptom.replace("_", " ")):
                mentioned_symptoms.add(symptom)

        possible_diseases = []
        for disease, symptoms in self.disease_symptoms.items():
            matched = mentioned_symptoms & symptoms
            if not matched:
                continue
            match_count = len(matched)
            total = len(symptoms)
            match_ratio = match_count / total if total else 0
            possible_diseases.append(
                {
                    "disease": disease,
                    "match_ratio": match_ratio,
                    "match_count": match_count,
                    "total_symptoms": total,
                }
            )

        # Sort by match ratio desc, then by match count desc
        possible_diseases.sort(key=lambda x: (x["match_ratio"], x["match_count"]), reverse=True)

        return possible_diseases[:top_n]

    def format_diagnosis(self, diagnoses, lang: str = "en"):
        if not diagnoses:
            return None

        diseases = [d["disease"] for d in diagnoses][:3]
        disease_list = ", ".join(diseases)

        msg = [
            self._localize("diagnosis_intro", lang).format(diseases=disease_list),
            "",
            self._localize("diagnosis_next_steps", lang),
            self._localize("diagnosis_step_1", lang),
            self._localize("diagnosis_step_2", lang),
            self._localize("diagnosis_step_3", lang),
            self._localize("diagnosis_step_4", lang),
            "",
            self._localize("diagnosis_urgent", lang),
        ]

        return "\n".join(msg)

    def get_response(self, user_text, lang: str = "en"):
        lang = self._normalize_lang(lang)

        # Preprocess user input
        text = preprocess(user_text)

        # 1. Emergency check FIRST (highest priority)
        for entry in self.kb.get("entries", []):
            if entry.get("priority") == "high":
                for kw in entry["keywords"]:
                    if contains_keyword(text, kw):
                        return self._get_entry_response(entry, lang)

        # 2. Normal matching (score-based)
        best_entry = None
        best_score = 0

        for entry in self.kb.get("entries", []):
            score = 0
            for kw in entry["keywords"]:
                if contains_keyword(text, kw):
                    # Phrase keywords get higher weight
                    score += 2 if " " in kw else 1

            if score > best_score:
                best_score = score
                best_entry = entry

        # 3. Return best match
        if best_entry:
            return self._get_entry_response(best_entry, lang)

        # 4. Try symptom diagnosis
        diagnoses = self.diagnose_symptoms(user_text)
        formatted = self.format_diagnosis(diagnoses, lang=lang)
        if formatted:
            return formatted

        # 5. Fallback response
        fallback = self.kb.get("fallback")
        if lang == "or":
            fallback_or = self.kb.get("fallback_or")
            if fallback_or:
                return fallback_or
            # Return English fallback if Odia not available
            if fallback:
                return fallback
            return self._localize("fallback", lang)
        return fallback or self._localize("fallback", "en")

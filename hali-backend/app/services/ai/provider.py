from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.services.pii_redaction.redactor import PIIRedactor


class BaseAIProvider(ABC):
    @abstractmethod
    def generate_case_brief(
        self,
        student_handle: str,
        risk_tier: str,
        scores_history: List[Dict[str, Any]],
        sanitized_notes: List[str]
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def generate_assistant_reply(self, user_message: str, lang: str = "en") -> Dict[str, Any]:
        pass


class MockAIProvider(BaseAIProvider):
    """
    Mock AI Provider adhering strictly to the privacy and safety rules.
    Does NOT diagnose. Provides 4-bullet pre-session summaries and safe coping prompts.
    """

    CRISIS_KEYWORDS = {
        "die", "dead", "hurt", "kill", "suicid", "kujiua", "kujidhuru",
        "end it all", "better off dead", "hopeless", "hakuna matumaini", "give up"
    }

    def generate_case_brief(
        self,
        student_handle: str,
        risk_tier: str,
        scores_history: List[Dict[str, Any]],
        sanitized_notes: List[str]
    ) -> Dict[str, Any]:
        # Pre-redact notes if any
        redacted_notes = [PIIRedactor.redact(note)["redacted_text"] for note in sanitized_notes]

        summary = (
            f"Screening trajectory for {student_handle} indicates {risk_tier.lower()} tier presentation. "
            f"Multiple check-in reflections highlight academic deadlines, sleep disruption, and social factors. "
            f"Assessment trend indicates need for supportive exploratory consultation."
        )

        observations = [
            f"Latest screening tier classified deterministically as {risk_tier.upper()}",
            "Score trajectory reflects cumulative academic and exam period pressure",
            "Self-reported sleep disruption and energy changes noted during check-ins",
            "No reported pharmacological medication interventions on record"
        ]

        topics = [
            "Current exam workload distribution and manageable pacing",
            "Sleep hygiene adjustments and digital wind-down routine",
            "Campus support network and available peer study groups",
            "Collaborative agreement on upcoming check-in frequency"
        ]

        return {
            "summary": summary,
            "observations": observations,
            "topics": topics,
            "disclaimer": "AI-generated draft for counsellor review. It does not diagnose and is not a clinical decision."
        }

    def generate_assistant_reply(self, user_message: str, lang: str = "en") -> Dict[str, Any]:
        # Step 1: PII Redaction
        redaction_res = PIIRedactor.redact(user_message)
        sanitized_msg = redaction_res["redacted_text"].lower()

        # Step 2: Safety Check for Crisis Keywords
        is_crisis = any(kw in sanitized_msg for kw in self.CRISIS_KEYWORDS)
        if is_crisis:
            if lang == "sw":
                reply = (
                    "Inaonekana unapitia wakati mgumu sana. Ninakuunganisha mara moja na mshauri wa chuo "
                    "au huduma za dharura za afya ya akili. Huko peke yako, tafadhali piga simu bila malipo: 1199 au 0900 620 800."
                )
            else:
                reply = (
                    "That sounds very heavy and you don't have to carry it alone. "
                    "I am connecting you directly with human support and campus crisis responders. "
                    "Please reach out right away to toll-free hotlines: 1199 or 0900 620 800."
                )
            return {
                "reply": reply,
                "human_escalation_triggered": True,
                "redaction_applied": redaction_res["redaction_applied"],
                "crisis": True
            }

        # Step 3: Coping Skill Guidance (Non-diagnostic)
        if any(w in sanitized_msg for w in ["sleep", "lala", "usingizi", "insomnia"]):
            reply = (
                "Kuweka ratiba thabiti ya kulala na kuzima skrini dakika 30 kabla ya kitanda husaidia mara nyingi."
                if lang == "sw"
                else "A steady wake time and putting screens away 30 minutes before bed often helps restore rhythm. Would you like to review relaxation techniques?"
            )
        elif any(w in sanitized_msg for w in ["stress", "exam", "mtihani", "pressure", "overwhelmed"]):
            reply = (
                "Jaribu pumzi ya sanduku (box breathing): vuta pumzi kwa 4, shikilia kwa 4, toa kwa 4, shikilia kwa 4. Je, ungependa kupanga muda mfupi wa mapumziko?"
                if lang == "sw"
                else "Try box breathing: breathe in for 4, hold for 4, breathe out for 4, hold for 4. Would you like a 15-minute study-break plan?"
            )
        else:
            reply = (
                "Ninaweza kushiriki mikakati mifupi ya kujituliza na kukusaidia kupata msaada unaofaa. Mimi ni AI, si mshauri."
                if lang == "sw"
                else "I can share short coping skills and help you find the right campus resources. I am an AI assistant, not a counsellor."
            )

        return {
            "reply": reply,
            "human_escalation_triggered": False,
            "redaction_applied": redaction_res["redaction_applied"],
            "crisis": False
        }


def get_ai_provider() -> BaseAIProvider:
    return MockAIProvider()


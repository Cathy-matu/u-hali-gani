import re
from typing import Dict, Any, Tuple, List


class PIIRedactor:
    """
    Privacy-first PII Redaction Layer for Sheng, Swahili, and English text.
    Replaces sensitive personal identifiers with privacy placeholders before AI processing.
    """

    # Email pattern
    EMAIL_PATTERN = re.compile(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        re.IGNORECASE
    )

    # Phone numbers (Kenyan +254..., 07..., 01... and international)
    PHONE_PATTERN = re.compile(
        r"(\+?254\s?|0)[17]\d{1}[0-9\s-]{6,10}\b",
        re.IGNORECASE
    )

    # University Registration / Admission Number Patterns (e.g. CIT/0012/2021, P15/1234/2022, SC211-0042/2020)
    REG_NO_PATTERN = re.compile(
        r"\b([A-Z]{1,4}[0-9]{0,3}[/-][0-9]{2,6}[/-][0-9]{2,4}|[A-Z]{2,5}[/-][0-9]{3,6}[/-][0-9]{2,4})\b",
        re.IGNORECASE
    )

    # Lecturer / Professor patterns (English, Swahili, Sheng)
    LECTURER_PATTERN = re.compile(
        r"\b(lecturer|prof(?:\.|essor)?|dr\.|mwalimu|lecturer\s+ya)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",
        re.IGNORECASE
    )

    # Hostel patterns (English, Swahili, Sheng)
    HOSTEL_PATTERN = re.compile(
        r"\b(hostel\s+(?:ya\s+)?([A-Za-z0-9_-]+)|qwetu(?:\s+[A-Za-z]+)?|hall\s+[0-9A-Z]+|olympia\s+hostel|parkview\s+hostel)\b",
        re.IGNORECASE
    )

    # Kenyan Campus Locations & neighborhoods
    LOCATION_PATTERN = re.compile(
        r"\b(juja|ruiru|madaraka|parklands|roasters|kahawa\s+sukari|kahawa\s+wendani|ngara|kileleshwa|campus\s+gate|main\s+campus)\b",
        re.IGNORECASE
    )

    # Common Kenyan and standard names
    COMMON_NAMES = {
        "wanjiku", "kamau", "otieno", "wekesa", "mutua", "omondi", "ochieng",
        "mwangi", "njeri", "kinyua", "chebet", "korir", "kiprono", "cheruiyot",
        "john", "peter", "brian", "kevin", "grace", "amina", "mary", "sarah",
        "dennis", "mercy", "faith", "victor", "esther", "paul", "david"
    }

    @classmethod
    def redact(cls, text: str) -> Dict[str, Any]:
        if not text:
            return {
                "redacted_text": "",
                "redaction_count": 0,
                "redaction_applied": False,
                "matches": []
            }

        redacted = text
        redaction_count = 0
        matches: List[str] = []

        # 1. Emails
        emails = cls.EMAIL_PATTERN.findall(redacted)
        if emails:
            for em in emails:
                redacted = redacted.replace(em, "[EMAIL]")
                redaction_count += 1
                matches.append("EMAIL")

        # 2. Registration Numbers
        regs = cls.REG_NO_PATTERN.findall(redacted)
        if regs:
            for reg in regs:
                redacted = redacted.replace(reg, "[REGISTRATION_NUMBER]")
                redaction_count += 1
                matches.append("REGISTRATION_NUMBER")

        # 3. Phone numbers
        def replace_phone(match):
            nonlocal redaction_count
            redaction_count += 1
            matches.append("PHONE")
            return "[PHONE]"

        redacted = cls.PHONE_PATTERN.sub(replace_phone, redacted)

        # 4. Lecturers
        def replace_lecturer(match):
            nonlocal redaction_count
            redaction_count += 1
            matches.append("LECTURER")
            return "[LECTURER]"

        redacted = cls.LECTURER_PATTERN.sub(replace_lecturer, redacted)

        # 5. Hostels
        def replace_hostel(match):
            nonlocal redaction_count
            redaction_count += 1
            matches.append("HOSTEL")
            return "[HOSTEL]"

        redacted = cls.HOSTEL_PATTERN.sub(replace_hostel, redacted)

        # 6. Specific Locations
        def replace_location(match):
            nonlocal redaction_count
            redaction_count += 1
            matches.append("LOCATION")
            return "[LOCATION]"

        redacted = cls.LOCATION_PATTERN.sub(replace_location, redacted)

        # 7. Common Personal Names
        words = redacted.split()
        sanitized_words = []
        for word in words:
            clean_word = re.sub(r"[^\w]", "", word).lower()
            if clean_word in cls.COMMON_NAMES:
                # Replace with [PERSON] keeping surrounding punctuation
                punct_prefix = word[:word.lower().find(clean_word)]
                punct_suffix = word[word.lower().find(clean_word) + len(clean_word):]
                sanitized_words.append(f"{punct_prefix}[PERSON]{punct_suffix}")
                redaction_count += 1
                matches.append("PERSON")
            else:
                sanitized_words.append(word)

        redacted = " ".join(sanitized_words)

        return {
            "redacted_text": redacted,
            "redaction_count": redaction_count,
            "redaction_applied": redaction_count > 0,
            "matches": matches
        }


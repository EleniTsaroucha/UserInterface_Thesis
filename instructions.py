from __future__ import annotations

from session_config import SensitiveContent

INSTRUCTION_TEMPLATES: dict[str, str] = {
    "read_email": (
        "Άνοιξε το email με τους αποθηκευμένους κωδικούς σου. Θα τους "
        "χρειαστείς στα επόμενα βήματα."
    ),
    "navigate_to_banking": (
        "Πήγαινε στην καρτέλα «SecureBank Demo»."
    ),
    "bank_login": (
        "Αντέγραψε το bank username/password από το email και συνδέσου."
    ),
    "bank_pay": (
        "Αντέγραψε το IBAN από το email, επικόλλησέ το, πάτησε «Πληρωμή "
        "Λογαριασμού» και συμπλήρωσε το ποσό στο παράθυρο που θα ανοίξει."
    ),
    "navigate_to_health": (
        "Πήγαινε στην καρτέλα «e-Ραντεβού Demo»."
    ),
    "health_login": (
        "Αντέγραψε το Taxisnet username/password από το email και συνδέσου."
    ),
    "health_booking": (
        "Γράψε σύντομα μια πάθηση, επίλεξε ειδικότητα και ημερομηνία/ώρα, "
        "μετά πάτησε «Κλείσιμο Ραντεβού»."
    ),
    "return_to_email": (
        "Επίστρεψε στην καρτέλα «Demo Mail»."
    ),
    "navigate_to_gov": (
        "Πήγαινε στην καρτέλα «GovAtHome Demo»."
    ),
    "gov_login": (
        "Αντέγραψε το Taxisnet username/password από το email και συνδέσου."
    ),
    "gov_menu": (
        "Στο μενού υπηρεσιών, πάτησε «Ηλεκτρονική Υπογραφή»."
    ),
    "gov_select_document": (
        "Επίλεξε ένα έγγραφο και πάτησε «Αίτημα Ηλεκτρονικής Υπογραφής»."
    ),
    "check_email_otp": (
        "Πήγαινε στην καρτέλα «Demo Mail» και βρες με τα βελάκια το νέο "
        "email με τον 4ψήφιο κωδικό επιβεβαίωσης."
    ),
    "gov_enter_otp": (
        "Επίστρεψε στην καρτέλα «GovAtHome Demo», πληκτρολόγησε τον "
        "κωδικό και πάτησε «Επιβεβαίωση Υπογραφής»."
    ),
}


def get_instruction(step_id: str, content: SensitiveContent) -> str:
    return INSTRUCTION_TEMPLATES.get(step_id, "")

from __future__ import annotations

import random
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QScrollArea, QSizePolicy,
)

ACCENT = "#5b5fc7"         
RAIL_BG = "#f0f0f5"
LIST_BG = "#f5f5f8"
BUBBLE_IN = "#f0f0f0"
TEXT_PRIMARY = "#242424"
TEXT_SECONDARY = "#616161"
BORDER = "#e1e1e1"
FONT_FAMILY = "Segoe UI"


@dataclass(frozen=True)
class Message:
    sender: str         
    text: str
    stamp: str


@dataclass
class Conversation:
    chat_id: str
    name: str
    initials: str
    color: str
    last_date: str
    messages: list[Message]

_BASE_CONVERSATIONS: list[Conversation] = [
    Conversation("team_general", "Ομάδα Υποστήριξης", "ΟΥ", "#6264a7", "Σήμερα", [
        Message("Αγγελική Μιχαήλ", "Καλημέρα σε όλους! Το standup μεταφέρεται στις 10:30.", "9:02 π.μ."),
        Message("Κώστας Παπαδόπουλος", "Ελήφθη 👍", "9:04 π.μ."),
        Message("", "Οκ, θα είμαι εκεί.", "9:06 π.μ."),
        Message("Αγγελική Μιχαήλ", "Όποιος έχει εκκρεμότητες από χθες ας τις γράψει στο κανάλι.",
                "9:11 π.μ."),
    ]),
    Conversation("maria", "Μαρία Νικολάου", "ΜΝ", "#c239b3", "Σήμερα", [
        Message("Μαρία Νικολάου", "Καλημέρα! Πρόλαβες να δεις το αρχείο που σου έστειλα;", "9:20 π.μ."),
        Message("", "Καλημέρα Μαρία, το κοιτάω μέσα στο πρωί.", "9:25 π.μ."),
        Message("Μαρία Νικολάου", "Τέλεια, ευχαριστώ! Δεν βιάζομαι ιδιαίτερα.", "9:26 π.μ."),
    ]),
    Conversation("panos", "Πάνος Δ.", "ΠΔ", "#038387", "Χθες", [
        Message("Πάνος Δ.", "Είχες πρόβλημα με το VPN χθες το απόγευμα;", "4:41 μ.μ."),
        Message("", "Ναι, έπεσε για κάνα δεκάλεπτο. Μετά ήταν μια χαρά.", "4:48 μ.μ."),
        Message("Πάνος Δ.", "Το ίδιο κι εγώ. Το ανέφερα στο helpdesk.", "4:50 μ.μ."),
    ]),
    Conversation("hr", "Τμήμα Προσωπικού", "ΤΠ", "#8764b8", "Δευτέρα", [
        Message("Τμήμα Προσωπικού",
                "Υπενθύμιση: οι δηλώσεις αδειών Σεπτεμβρίου κλείνουν την Παρασκευή.", "11:15 π.μ."),
    ]),
    Conversation("kostas", "Κώστας Παπαδόπουλος", "ΚΠ", "#ca5010", "Δευτέρα", [
        Message("Κώστας Παπαδόπουλος", "Μπορείς να ρίξεις μια ματιά στο τελευταίο review όταν προλάβεις;",
                "2:03 μ.μ."),
        Message("", "Ναι, αύριο το πρωί.", "2:20 μ.μ."),
    ]),
]

_PERSONA_THREADS: dict[str, tuple[str, str, str, list[tuple[str, str, str]]]] = {
    "A": ("Κατερίνα Ιωαννίδου", "ΚΙ", "#c239b3", [
        ("Κατερίνα Ιωαννίδου", "Καλημέρα! Σου έστειλα τον φάκελο με email, ρίξε μια ματιά όποτε μπορείς.",
         "10:22 π.μ."),
        ("Κατερίνα Ιωαννίδου", "Θα χρειαστώ και τον αριθμό μητρώου από το e-Ραντεβού, αν βολεύει.",
         "10:23 π.μ."),
    ]),
    "B": ("Νίκος Δημητρίου", "ΝΔ", "#0078d4", [
        ("Νίκος Δημητρίου", "Γεια σου! Έστειλα την ανασκόπηση στο mail σου.", "11:00 π.μ."),
        ("Νίκος Δημητρίου", "Αν μπορείς, τσέκαρε και το τρέχον υπόλοιπο στο e-banking πριν απαντήσεις.",
         "11:02 π.μ."),
    ]),
    "C": ("Νίκος Παπαδημητρόπουλος", "ΝΠ", "#498205", [
        ("Νίκος Παπαδημητρόπουλος", "Καλημέρα, σου έστειλα το memo. Είναι λίγο επείγον.", "9:10 π.μ."),
        ("Νίκος Παπαδημητρόπουλος", "Θα χρειαστώ και τον προσωπικό αριθμό από το GovAtHome για την καταχώρηση.",
         "9:11 π.μ."),
    ]),
}


class _ChatRow(QWidget):
    def __init__(self, conv: Conversation, unread: bool, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet("background:transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        avatar = QLabel(conv.initials)
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            f"background:{conv.color}; color:white; border-radius:20px; "
            f"font-size:14px; font-weight:600;"
        )
        layout.addWidget(avatar)

        text_box = QVBoxLayout()
        text_box.setSpacing(1)
        top = QHBoxLayout()
        name = QLabel(conv.name)
        name.setStyleSheet(
            f"color:{TEXT_PRIMARY}; font-size:13.5px; "
            f"font-weight:{'700' if unread else '600'}; background:transparent;"
        )
        top.addWidget(name, stretch=1)
        date = QLabel(conv.last_date)
        date.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11px; background:transparent;")
        top.addWidget(date)
        text_box.addLayout(top)

        if unread:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{ACCENT}; font-size:12px; background:transparent;")
            top.addWidget(dot)

        last = conv.messages[-1]
        prefix = "Εσείς: " if last.sender == "" else ""
        preview = QLabel()
        preview.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:12px; background:transparent; "
            f"font-weight:{'600' if unread else '400'};"
        )
        fm = preview.fontMetrics()
        preview.setText(fm.elidedText(prefix + last.text, Qt.TextElideMode.ElideRight, 240))
        text_box.addWidget(preview)
        layout.addLayout(text_box, stretch=1)


class _Bubble(QWidget):

    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        outgoing = message.sender == ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        if not outgoing:
            name = QLabel(message.sender)
            name.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:11.5px; background:transparent;")
            layout.addWidget(name)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self.bubble = QLabel(message.text)
        self.bubble.setWordWrap(True)
        self.bubble.setMaximumWidth(620)
        self.bubble.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        if outgoing:
            self.bubble.setStyleSheet(
                f"background:{ACCENT}; color:white; border-radius:10px; padding:9px 14px; "
                f"font-size:13.5px;"
            )
            row.addStretch()
            row.addWidget(self.bubble)
        else:
            self.bubble.setStyleSheet(
                f"background:{BUBBLE_IN}; color:{TEXT_PRIMARY}; border-radius:10px; "
                f"padding:9px 14px; font-size:13.5px;"
            )
            row.addWidget(self.bubble)
            row.addStretch()
        layout.addLayout(row)


@dataclass(frozen=True)
class Distractor:
    """Ένα εισερχόμενο μήνυμα απόσπασης προσοχής."""
    chat_id: str
    sender: str
    text: str
    kind: str          # "message" | "meeting" | "deadline"


# Χρονισμός παράδοσης μέσα σε κάθε μπλοκ. Το ΤΙ στέλνεται δεν ορίζεται εδώ:
# επιλέγεται τη στιγμή της παράδοσης από τις παρακάτω δεξαμενές, ώστε δύο
# μπλοκ να μη δίνουν ποτέ την ίδια ακολουθία.
DELIVERY_DELAYS_MS: tuple[int, ...] = (12_000, 35_000, 95_000, 160_000, 225_000)


# Δεξαμενή ανά συνομιλία. Κάθε επαφή έχει δικό της ύφος και θεματολογία: το
# Τμήμα Προσωπικού ανακοινώνει, ο Κώστας μιλά για κώδικα, ο Πάνος για υποδομές.
# Έτσι το μήνυμα παραμένει πιστευτό ανεξάρτητα από το ποια στιγμή θα πέσει.
DISTRACTOR_POOL: dict[str, list[Distractor]] = {
    "team_general": [
        Distractor("team_general", "Αγγελική Μιχαήλ",
                   "Υπενθύμιση: σύσκεψη ομάδας σε 15 λεπτά στην αίθουσα Β.", "meeting"),
        Distractor("team_general", "Αγγελική Μιχαήλ",
                   "Το standup μεταφέρεται στις 11:00, δεν είναι διαθέσιμη η αίθουσα.", "meeting"),
        Distractor("team_general", "Κώστας Παπαδόπουλος",
                   "Παιδιά, το build στο main περνάει ξανά. Ήταν το cache.", "message"),
        Distractor("team_general", "Πάνος Δ.",
                   "Όποιος έχει ανοιχτά tickets από την περασμένη εβδομάδα ας τα κλείσει.", "message"),
        Distractor("team_general", "Αγγελική Μιχαήλ",
                   "Ανεβάζω τα πρακτικά της σύσκεψης στο κανάλι μέχρι το απόγευμα.", "message"),
        Distractor("team_general", "Κώστας Παπαδόπουλος",
                   "Θα λείπω μετά τις 4. Αν χρειαστεί κάτι, στείλτε μου μήνυμα.", "message"),
    ],
    "maria": [
        Distractor("maria", "Μαρία Νικολάου",
                   "Πρόλαβες να δεις το αρχείο; Δεν βιάζομαι, απλώς να ξέρω.", "message"),
        Distractor("maria", "Μαρία Νικολάου",
                   "Σου έστειλα και δεύτερη έκδοση, αγνόησε την πρώτη.", "message"),
        Distractor("maria", "Μαρία Νικολάου",
                   "Η προθεσμία για τα σχόλια είναι αύριο το μεσημέρι.", "deadline"),
        Distractor("maria", "Μαρία Νικολάου",
                   "Μπορούμε να το δούμε μαζί σε ένα δεκάλεπτο κάποια στιγμή σήμερα;", "meeting"),
        Distractor("maria", "Μαρία Νικολάου",
                   "Ευχαριστώ για τη διόρθωση, την πέρασα στο τελικό.", "message"),
        Distractor("maria", "Μαρία Νικολάου",
                   "Ξέχασα να ρωτήσω — χρειάζεσαι κάτι από μένα για την αναφορά;", "message"),
    ],
    "panos": [
        Distractor("panos", "Πάνος Δ.",
                   "Το VPN ξανακολλάει; Εμένα με πέταξε έξω δύο φορές.", "message"),
        Distractor("panos", "Πάνος Δ.",
                   "Βρήκα τι έφταιγε με το certificate, είχε λήξει.", "message"),
        Distractor("panos", "Πάνος Δ.",
                   "Σου προώθησα το ticket του helpdesk, δες αν σε αφορά.", "message"),
        Distractor("panos", "Πάνος Δ.",
                   "Έκλεισα αίθουσα για την Πέμπτη στις 12. Σε βολεύει;", "meeting"),
        Distractor("panos", "Πάνος Δ.",
                   "Πάμε για καφέ σε καμιά ώρα;", "message"),
        Distractor("panos", "Πάνος Δ.",
                   "Το laptop μου πάει για αντικατάσταση, θα λείπω λίγο το πρωί.", "message"),
    ],
    "hr": [
        Distractor("hr", "Τμήμα Προσωπικού",
                   "Προθεσμία: οι δηλώσεις αδειών κλείνουν σε 2 ώρες.", "deadline"),
        Distractor("hr", "Τμήμα Προσωπικού",
                   "Υπενθύμιση: η ετήσια αξιολόγηση υποβάλλεται έως την Παρασκευή.", "deadline"),
        Distractor("hr", "Τμήμα Προσωπικού",
                   "Ενημέρωση: νέο έντυπο για τα έξοδα μετακίνησης στο intranet.", "message"),
        Distractor("hr", "Τμήμα Προσωπικού",
                   "Παρακαλούμε επιβεβαιώστε τη συμμετοχή σας στην εκπαίδευση ασφάλειας.", "deadline"),
        Distractor("hr", "Τμήμα Προσωπικού",
                   "Το γραφείο θα παραμείνει κλειστό τη Δευτέρα λόγω αργίας.", "message"),
        Distractor("hr", "Τμήμα Προσωπικού",
                   "Υπενθύμιση: εκκρεμεί υπογραφή εντύπου στον φάκελό σας.", "deadline"),
    ],
    "kostas": [
        Distractor("kostas", "Κώστας Παπαδόπουλος",
                   "Θύμισέ μου, η προθεσμία για την αναφορά είναι σήμερα ή αύριο;", "deadline"),
        Distractor("kostas", "Κώστας Παπαδόπουλος",
                   "Άφησα δύο σχόλια στο PR, τίποτα σοβαρό.", "message"),
        Distractor("kostas", "Κώστας Παπαδόπουλος",
                   "Μπορείς να κάνεις merge όποτε προλάβεις, εγώ το ενέκρινα.", "message"),
        Distractor("kostas", "Κώστας Παπαδόπουλος",
                   "Έχεις χρόνο για ένα γρήγορο call στις 3;", "meeting"),
        Distractor("kostas", "Κώστας Παπαδόπουλος",
                   "Το test suite βγάζει flaky αποτέλεσμα στο CI. Το είδες;", "message"),
        Distractor("kostas", "Κώστας Παπαδόπουλος",
                   "Ανέβασα το benchmark στο κανάλι, ρίξε μια ματιά.", "message"),
    ],
}


_NOTIFICATION_ICONS = {"meeting": "📅", "deadline": "⏰", "message": "💬"}


class TeamsScreen(QWidget):

    field_rendered = pyqtSignal(str, QRect, str)
    action_performed = pyqtSignal(str)
    notification_raised = pyqtSignal(str, str, str, str)
    unread_changed = pyqtSignal(int)

    def __init__(self, session_id: str | None = None, parent=None):
        super().__init__(parent)
        # Ντετερμινισμός ανά συνεδρία: ο ίδιος συμμετέχων δέχεται την ίδια
        # ακολουθία σε κάθε επανάληψη, ενώ διαφορετικοί συμμετέχοντες δέχονται
        # διαφορετική. Χωρίς σπόρο, η απόσπαση προσοχής γίνεται ανεξέλεγκτη
        # μεταβλητή που δεν μπορεί ούτε να αναπαραχθεί ούτε να αναφερθεί.
        self._rng = random.Random(session_id if session_id else "default")
        self._chat_bag: list[str] = []
        self._text_bags: dict[str, list[Distractor]] = {}
        self._last_chat_id: str | None = None
        self.conversations: list[Conversation] = [
            Conversation(c.chat_id, c.name, c.initials, c.color, c.last_date, list(c.messages))
            for c in _BASE_CONVERSATIONS
        ]
        self.unread: set[str] = set()
        self.current_chat_id: str | None = None
        self._aoi_timer = QTimer(self)
        self._aoi_timer.setSingleShot(True)
        self._aoi_timer.timeout.connect(self._emit_bubble_positions)
        self._incoming_timers: list[QTimer] = []
        self._build_ui()
        self._refresh_chat_list()
        self.open_chat(self.conversations[0].chat_id)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_topbar())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_rail())
        body.addWidget(self._build_chat_list())
        body.addWidget(self._build_conversation_pane(), stretch=1)
        outer.addLayout(body, stretch=1)

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(48)
        bar.setStyleSheet(f"background:{RAIL_BG}; border-bottom:1px solid {BORDER};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(12)
        for glyph in ("◫", "‹", "›"):
            lbl = QLabel(glyph)
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:15px; background:transparent;")
            layout.addWidget(lbl)

        search = QLineEdit()
        search.setPlaceholderText("Αναζήτηση")
        search.setFixedHeight(30)
        search.setMaximumWidth(720)
        search.setStyleSheet(
            f"QLineEdit {{ background:white; border:1px solid {BORDER}; border-radius:6px; "
            f"padding:0 12px; font-size:13px; color:{TEXT_PRIMARY}; }}"
        )
        layout.addWidget(search, stretch=1)
        layout.addStretch()
        avatar = QLabel("ΕΤ")
        avatar.setFixedSize(28, 28)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(
            f"background:{ACCENT}; color:white; border-radius:14px; font-size:11px; font-weight:600;")
        layout.addWidget(avatar)
        return bar

    def _build_rail(self) -> QWidget:
        rail = QWidget()
        rail.setFixedWidth(56)
        rail.setStyleSheet(f"background:{RAIL_BG}; border-right:1px solid {BORDER};")
        layout = QVBoxLayout(rail)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(6)
        for glyph, label, active in (("🔔", "Δραστηριότητα", False), ("💬", "Συνομιλία", True),
                                     ("👥", "Ομάδες", False), ("📅", "Ημερολόγιο", False),
                                     ("📞", "Κλήσεις", False)):
            item = QLabel(glyph)
            item.setFixedHeight(48)
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setToolTip(label)
            item.setStyleSheet(
                f"font-size:17px; background:transparent; "
                f"border-left:3px solid {ACCENT if active else 'transparent'};"
            )
            layout.addWidget(item)
        layout.addStretch()
        return rail

    def _build_chat_list(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(300)
        panel.setStyleSheet(f"background:{LIST_BG}; border-right:1px solid {BORDER};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(56)
        hb = QHBoxLayout(header)
        hb.setContentsMargins(16, 0, 12, 0)
        title = QLabel("Συνομιλία")
        title.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
        hb.addWidget(title)
        hb.addStretch()
        for glyph in ("🔍", "🎥", "✎"):
            lbl = QLabel(glyph)
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:14px; background:transparent;")
            hb.addWidget(lbl)
        layout.addWidget(header)

        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet(
            f"QListWidget {{ background:{LIST_BG}; border:none; outline:none; }}"
            f"QListWidget::item:selected {{ background:#e1dfdd; border-radius:6px; }}"
            f"QListWidget::item:hover:!selected {{ background:#ebebeb; border-radius:6px; }}"
        )
        self.chat_list.itemClicked.connect(self._on_chat_clicked)
        layout.addWidget(self.chat_list, stretch=1)
        return panel

    def _build_conversation_pane(self) -> QWidget:
        pane = QWidget()
        pane.setStyleSheet("background:white;")
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f"background:white; border-bottom:1px solid {BORDER};")
        hb = QHBoxLayout(header)
        hb.setContentsMargins(20, 0, 20, 0)
        hb.setSpacing(12)
        self.header_avatar = QLabel()
        self.header_avatar.setFixedSize(32, 32)
        self.header_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hb.addWidget(self.header_avatar)
        self.header_name = QLabel()
        self.header_name.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        self.header_name.setStyleSheet(f"color:{TEXT_PRIMARY}; background:transparent;")
        hb.addWidget(self.header_name)
        for tab in ("Συνομιλία", "Αρχεία", "Φωτογραφίες"):
            lbl = QLabel(tab)
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:13px; background:transparent;")
            hb.addSpacing(10)
            hb.addWidget(lbl)
        hb.addStretch()
        for glyph in ("🎥", "📞", "👤+", "⋯"):
            lbl = QLabel(glyph)
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:14px; background:transparent;")
            hb.addWidget(lbl)
        layout.addWidget(header)

        self.msg_scroll = QScrollArea()
        self.msg_scroll.setWidgetResizable(True)
        self.msg_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.msg_scroll.setStyleSheet("background:white;")
        self.msg_scroll.verticalScrollBar().valueChanged.connect(
            lambda _: self._aoi_timer.start(120))
        msg_container = QWidget()
        msg_container.setStyleSheet("background:white;")
        self.msg_layout = QVBoxLayout(msg_container)
        self.msg_layout.setContentsMargins(28, 18, 28, 18)
        self.msg_layout.setSpacing(12)
        self.msg_layout.addStretch()
        self.msg_scroll.setWidget(msg_container)
        layout.addWidget(self.msg_scroll, stretch=1)

        composer = QWidget()
        composer.setFixedHeight(78)
        composer.setStyleSheet("background:white;")
        cb = QHBoxLayout(composer)
        cb.setContentsMargins(28, 10, 28, 20)
        box = QWidget()
        box.setStyleSheet(f"background:white; border:1.5px solid {ACCENT}; border-radius:6px;")
        bb = QHBoxLayout(box)
        bb.setContentsMargins(14, 4, 10, 4)
        bb.setSpacing(8)
        self.compose_field = QLineEdit()
        self.compose_field.setPlaceholderText("Πληκτρολογήστε ένα μήνυμα")
        self.compose_field.setStyleSheet(
            f"QLineEdit {{ background:transparent; border:none; font-size:13.5px; "
            f"color:{TEXT_PRIMARY}; }}"
        )
        self.compose_field.returnPressed.connect(self._send_message)
        bb.addWidget(self.compose_field, stretch=1)
        for glyph in ("😊", "📎", "🖼"):
            lbl = QLabel(glyph)
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:14px; background:transparent;")
            bb.addWidget(lbl)
        send = QPushButton("➤")
        send.setFixedSize(30, 28)
        send.setCursor(Qt.CursorShape.PointingHandCursor)
        send.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{ACCENT}; border:none; font-size:15px; }}"
            f"QPushButton:hover {{ background:#eeedf9; border-radius:6px; }}"
        )
        send.clicked.connect(self._send_message)
        bb.addWidget(send)
        cb.addWidget(box)
        layout.addWidget(composer)
        return pane

    def _refresh_chat_list(self) -> None:
        self.chat_list.clear()
        for conv in self.conversations:
            item = QListWidgetItem()
            item.setSizeHint(QSize(280, 66))
            item.setData(Qt.ItemDataRole.UserRole, conv.chat_id)
            self.chat_list.addItem(item)
            self.chat_list.setItemWidget(item, _ChatRow(conv, conv.chat_id in self.unread))
            if conv.chat_id == self.current_chat_id:
                self.chat_list.setCurrentItem(item)

    def _conversation(self, chat_id: str) -> Conversation | None:
        return next((c for c in self.conversations if c.chat_id == chat_id), None)

    def _on_chat_clicked(self, item: QListWidgetItem) -> None:
        self.open_chat(item.data(Qt.ItemDataRole.UserRole))

    def open_chat(self, chat_id: str) -> None:
        conv = self._conversation(chat_id)
        if conv is None:
            return
        self.current_chat_id = chat_id
        self.unread.discard(chat_id)
        self.unread_changed.emit(len(self.unread))

        self.header_avatar.setText(conv.initials)
        self.header_avatar.setStyleSheet(
            f"background:{conv.color}; color:white; border-radius:16px; "
            f"font-size:12px; font-weight:600;"
        )
        self.header_name.setText(conv.name)

        while self.msg_layout.count():
            item = self.msg_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self._bubbles: list[tuple[str, _Bubble, Message]] = []
        last_stamp = None
        for i, message in enumerate(conv.messages):
            if message.stamp != last_stamp:
                sep = QLabel(f"{conv.last_date}, {message.stamp}")
                sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
                sep.setStyleSheet(
                    f"color:{TEXT_SECONDARY}; font-size:11px; background:transparent; padding:4px;")
                self.msg_layout.addWidget(sep)
                last_stamp = message.stamp
            bubble = _Bubble(message)
            self.msg_layout.addWidget(bubble)
            self._bubbles.append((f"teams_{chat_id}_{i}", bubble, message))
        self.msg_layout.addStretch()

        self._refresh_chat_list()
        self.action_performed.emit(f"teams_chat_opened_{chat_id}")
        QTimer.singleShot(0, lambda: self.msg_scroll.verticalScrollBar().setValue(
            self.msg_scroll.verticalScrollBar().maximum()))
        self._aoi_timer.start(150)

    def _send_message(self) -> None:
        text = self.compose_field.text().strip()
        if not text or self.current_chat_id is None:
            return
        conv = self._conversation(self.current_chat_id)
        if conv is None:
            return
        conv.messages.append(Message("", text, "Τώρα"))
        conv.last_date = "Σήμερα"
        self.compose_field.clear()
        self.open_chat(self.current_chat_id)
        self.action_performed.emit("teams_message_sent")


    def _next_chat_id(self) -> str:
        """Σακούλα χωρίς επανάληψη: κάθε επαφή μιλά μία φορά πριν μιλήσει
        ξανά οποιαδήποτε. Στο γέμισμα νέας σακούλας αποκλείεται η τελευταία
        επαφή από την πρώτη θέση, ώστε να μην εμφανίζεται δύο φορές στη σειρά
        στο όριο μεταξύ δύο σακουλών."""
        if not self._chat_bag:
            self._chat_bag = [c for c in DISTRACTOR_POOL if self._conversation(c) is not None]
            self._rng.shuffle(self._chat_bag)
            if (len(self._chat_bag) > 1
                    and self._chat_bag[-1] == self._last_chat_id):
                self._chat_bag[-1], self._chat_bag[-2] = (
                    self._chat_bag[-2], self._chat_bag[-1])
        return self._chat_bag.pop()

    def _next_distractor(self) -> Distractor | None:
        chat_id = self._next_chat_id()
        bag = self._text_bags.get(chat_id)
        if not bag:
            bag = list(DISTRACTOR_POOL[chat_id])
            self._rng.shuffle(bag)
            self._text_bags[chat_id] = bag
        self._last_chat_id = chat_id
        return bag.pop()

    def _deliver_next(self) -> None:
        item = self._next_distractor()
        if item is not None:
            self.deliver_message(item.chat_id, item.sender, item.text, item.kind)

    def start_incoming(self) -> None:
        """Οι χρονιστές ορίζουν μόνο ΠΟΤΕ θα φτάσει μήνυμα. Το περιεχόμενο
        επιλέγεται τη στιγμή της παράδοσης, οπότε οι σακούλες συνεχίζουν από
        εκεί που έμειναν και ένα νέο μπλοκ δεν ξαναπαίζει το προηγούμενο."""
        self.stop_incoming()
        for delay in DELIVERY_DELAYS_MS:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self._deliver_next)
            timer.start(delay)
            self._incoming_timers.append(timer)

    def stop_incoming(self) -> None:
        for timer in self._incoming_timers:
            timer.stop()
        self._incoming_timers.clear()

    def deliver_message(self, chat_id: str, sender: str, text: str, kind: str = "message") -> None:
        conv = self._conversation(chat_id)
        if conv is None:
            return
        conv.messages.append(Message(sender, text, "Τώρα"))
        conv.last_date = "Σήμερα"
        if chat_id != self.current_chat_id:
            self.unread.add(chat_id)
        self._refresh_chat_list()
        if chat_id == self.current_chat_id:
            self.open_chat(chat_id)
        self.unread_changed.emit(len(self.unread))
        self.notification_raised.emit(sender, text, chat_id, kind)
        self.action_performed.emit(f"teams_incoming_{kind}_{chat_id}")

    def load_persona_thread(self, persona: str) -> None:
        sender, initials, color, raw = _PERSONA_THREADS[persona]
        self.conversations = [c for c in self.conversations if c.chat_id != "persona"]
        conv = Conversation("persona", sender, initials, color, "Σήμερα",
                            [Message(s, t, st) for s, t, st in raw])
        self.conversations.insert(0, conv)
        self.unread.add("persona")
        self._refresh_chat_list()
        self.unread_changed.emit(len(self.unread))
        self.action_performed.emit(f"teams_thread_loaded_{persona}")

    def content_rect(self) -> QRect | None:
        vp = self.msg_scroll.viewport()
        return QRect(vp.mapTo(self, QPoint(0, 0)), vp.size())

    def on_tab_activated(self) -> None:
        self._aoi_timer.start(150)

    def reset_fields(self) -> None:
        self.compose_field.clear()

    def _emit_bubble_positions(self) -> None:
        viewport = self.msg_scroll.viewport()
        visible = QRect(viewport.mapTo(self, QPoint(0, 0)), viewport.size())
        for aoi_id, bubble, message in getattr(self, "_bubbles", []):
            if not bubble.isVisible():
                continue
            top_left = bubble.bubble.mapTo(self, QPoint(0, 0))
            bbox = QRect(top_left, bubble.bubble.size())
            if not visible.intersects(bbox):
                continue
            self.field_rendered.emit(aoi_id, bbox, message.text)

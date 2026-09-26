from __future__ import annotations

from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor
from PyQt6.QtWidgets import (
    QFileDialog,
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QPushButton,
    QApplication, QStackedWidget, QTextEdit, QTextBrowser, QListWidget,
    QListWidgetItem, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
)

from session_config import SensitiveContent
from mail_stimuli import STIMULI, Stimulus, CRED_SUBJECT_TOKEN


FONT_FAMILY = "Segoe UI"
BG_APP = "#f6f8fc"
BG_PANEL = "#ffffff"
TEXT_PRIMARY = "#131417"
TEXT_SECONDARY = "#3c4043"
TEXT_MUTED = "#5f6368"
ACCENT = "#0842a0"
ACCENT_SOFT = "#c6dafc"
SEARCH_BG = "#e4ecfa"
BORDER = "#b9bec4"
COMPOSE_BG = "#c2e7ff"
# Εικονίδια γραμμών εργαλείων: το ανοιχτό γκρι χανόταν εντελώς κάτω από το
# θόλωμα και στη βιντεοσκόπηση της συνεδρίας.
TOOLBAR_ICON = "#1c1f23"
TOOLBAR_HOVER = "#dbe1e8"
TOOLBAR_ACTIVE = "#0842a0"


_MINUTES_PDF = (
    "ΠΡΑΚΤΙΚΑ ΣΥΝΑΝΤΗΣΗΣ ΟΜΑΔΑΣ\n"
    "Ημερομηνία: 21 Αυγούστου 2026 — Αίθουσα Β\n\n"
    "Παρόντες: Αγγελική Μιχαήλ, Κώστας Παπαδόπουλος, Μαρία Νικολάου, "
    "Πάνος Δ.\n\n"
    "1. Ανασκόπηση εκκρεμοτήτων\n"
    "Παρουσιάστηκε η κατάσταση των τριών ανοιχτών παραδοτέων. Δύο από αυτά "
    "παραμένουν εντός χρονοδιαγράμματος, ενώ το τρίτο μετατίθεται κατά μία "
    "εβδομάδα λόγω καθυστέρησης στην παραλαβή στοιχείων από εξωτερικό "
    "συνεργάτη.\n\n"
    "2. Κατανομή εργασιών\n"
    "Συμφωνήθηκε ότι η επισκόπηση των εντύπων θα ολοκληρωθεί έως την "
    "Παρασκευή. Η τελική έκδοση θα σταλεί σε όλους για σχόλια πριν την "
    "υποβολή.\n\n"
    "3. Επόμενα βήματα\n"
    "Η επόμενη συνάντηση ορίστηκε για την Τρίτη στις 10:00. Όποιος έχει "
    "θέματα προς συζήτηση παρακαλείται να τα προσθέσει στην ατζέντα έως τη "
    "Δευτέρα το μεσημέρι.\n\n"
    "Τα πρακτικά συντάχθηκαν από τη Γραμματεία."
)

_SENDER_COLORS = [
    "#1a73e8", "#d93025", "#188038", "#e37400", "#9334e6",
    "#0b8043", "#c5221f", "#7c4dff", "#00838f",
]


def _format_iban_display(raw: str) -> str:
    if not raw:
        return raw
    digits = raw[2:] if raw.startswith("GR") else raw
    return "GR-" + "-".join(digits[i:i + 4] for i in range(0, len(digits), 4))


def apply_card_shadow_local(widget: QWidget) -> None:
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(30)
    shadow.setOffset(0, 6)
    shadow.setColor(QColor(0, 0, 0, 120))
    widget.setGraphicsEffect(shadow)


def _sender_color(name: str) -> str:
    return _SENDER_COLORS[sum(ord(c) for c in name) % len(_SENDER_COLORS)]


def _avatar(initial: str, color: str, size: int = 30) -> QLabel:
    lbl = QLabel(initial.upper())
    lbl.setFixedSize(size, size)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        f"background:{color}; color:white; border-radius:{size // 2}px; "
        f"font-weight:600; font-size:{int(size * 0.42)}px; font-family:'{FONT_FAMILY}';"
    )
    return lbl


def _icon_label(glyph: str, size: int = 17, color: str = TOOLBAR_ICON) -> QLabel:
    lbl = QLabel(glyph)
    lbl.setStyleSheet(f"color:{color}; font-size:{size}px; font-weight:600; "
                      f"background:transparent;")
    return lbl


def _flat_button(text: str, tooltip: str = "") -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFixedHeight(30)
    btn.setToolTip(tooltip)
    btn.setStyleSheet(
        f"QPushButton {{ background:transparent; color:{TOOLBAR_ICON}; border:none; "
        f"border-radius:15px; padding:0 8px; font-size:17px; font-weight:600; }}"
        f"QPushButton:hover {{ background:{TOOLBAR_HOVER}; color:{TOOLBAR_ACTIVE}; }}"
    )
    return btn


class _EmailRow(QWidget):

    star_toggled = pyqtSignal(str, bool)

    def __init__(self, email: dict, parent=None):
        super().__init__(parent)
        self.email = email
        unread = email.get("unread", False)
        self.setFixedHeight(40)
        self.setStyleSheet("background:transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 18, 0)
        layout.setSpacing(10)

        self.checkbox = QLabel("☐")
        self.checkbox.setStyleSheet(f"color:{TEXT_MUTED}; font-size:15px; background:transparent;")
        layout.addWidget(self.checkbox)

        self.star = QPushButton("★" if email.get("starred") else "☆")
        self.star.setFixedSize(22, 22)
        self.star.setCursor(Qt.CursorShape.PointingHandCursor)
        self._sync_star()
        self.star.clicked.connect(self._toggle_star)
        layout.addWidget(self.star)

        weight = "600" if unread else "400"
        color = TEXT_PRIMARY if unread else "#3c4043"

        self.sender_lbl = QLabel()
        self.sender_lbl.setFixedWidth(170)
        self.sender_lbl.setText(self.sender_lbl.fontMetrics().elidedText(
            email["sender_name"], Qt.TextElideMode.ElideRight, 166))
        self.sender_lbl.setStyleSheet(
            f"color:{color}; font-size:13px; font-weight:{weight}; background:transparent;"
        )
        layout.addWidget(self.sender_lbl)

        self.text_lbl = QLabel()
        self.text_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.text_lbl.setStyleSheet("background:transparent;")
        self._subject = email["subject"]
        self._preview = email.get("preview", "")
        self._unread = unread
        layout.addWidget(self.text_lbl, stretch=1)

        self.time_lbl = QLabel(email.get("time", ""))
        self.time_lbl.setStyleSheet(
            f"color:{color}; font-size:11.5px; font-weight:{weight}; background:transparent;"
        )
        self.time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.time_lbl.setFixedWidth(80)
        layout.addWidget(self.time_lbl)

        self._render_text(600)

    def _render_text(self, available_px: int) -> None:
        """Θέμα με έντονα γράμματα + γκρι απόσπασμα στην ΙΔΙΑ γραμμή, με
        αποκοπή στο διαθέσιμο πλάτος -- ακριβώς όπως η λίστα ενός webmail."""
        fm = self.text_lbl.fontMetrics()
        subject_weight = 600 if self._unread else 400
        subject = fm.elidedText(self._subject, Qt.TextElideMode.ElideRight,
                                max(120, int(available_px * 0.45)))
        preview = fm.elidedText(self._preview, Qt.TextElideMode.ElideRight,
                                max(80, int(available_px * 0.55)))
        self.text_lbl.setText(
            f"<span style='color:{TEXT_PRIMARY}; font-weight:{subject_weight}; font-size:13px;'>"
            f"{subject}</span>"
            f"<span style='color:{TEXT_MUTED}; font-size:13px;'> &nbsp;-&nbsp; {preview}</span>"
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._render_text(self.text_lbl.width())

    def _sync_star(self) -> None:
        starred = self.email.get("starred", False)
        self.star.setText("★" if starred else "☆")
        self.star.setStyleSheet(
            f"QPushButton {{ background:transparent; border:none; font-size:15px; "
            f"color:{'#f4b400' if starred else TEXT_MUTED}; }}"
        )

    def _toggle_star(self) -> None:
        self.email["starred"] = not self.email.get("starred", False)
        self._sync_star()
        self.star_toggled.emit(self.email["email_id"], self.email["starred"])


class GmailScreen(QWidget):

    field_rendered = pyqtSignal(str, QRect, str)
    action_performed = pyqtSignal(str)
    reply_submitted = pyqtSignal(str, str)          # email_id, πλήρες κείμενο απάντησης
    draft_saved = pyqtSignal(str, int)              # email_id, μήκος προχείρου σε χαρακτήρες

    _LIST_STYLE = f"""
        QListWidget {{ background:{BG_PANEL}; border:none; outline:none; }}
        QListWidget::item {{ border-bottom:1px solid #f1f3f4; }}
        QListWidget::item:hover {{ background:#f5f6f7; }}
        QListWidget::item:selected {{ background:#e8f0fe; }}
    """
    _COPY_STYLE = (
        f"QPushButton {{ background:{ACCENT_SOFT}; color:{ACCENT}; border:none; "
        f"border-radius:6px; padding:3px 8px; font-size:12px; font-weight:600; }}"
        f"QPushButton:hover {{ background:#bcd4f7; }}"
    )
    _COPIED_STYLE = (
        "QPushButton { background:#188038; color:white; border:none; "
        "border-radius:6px; padding:3px 8px; font-size:12px; font-weight:600; }"
    )

    CATEGORIES = (("primary", "Κύρια", "🗂"), ("promotions", "Προσφορές", "🏷"),
                  ("social", "Κοινωνικά", "👥"), ("updates", "Ενημερώσεις", "ⓘ"))

    def __init__(self, content: SensitiveContent, parent=None):
        super().__init__(parent)
        self.content = content
        self.current_stimulus: Stimulus | None = None
        self._all_stimuli_mode: bool = False

        self._active_category = "primary"
        self._active_folder = "inbox"
        self._copy_buttons: dict[str, tuple[QPushButton, str]] = {}
        self._reply_started = False
        self._drafts: dict[str, str] = {}
        self._reply_attachments: list[str] = []
        self._draft_timer = QTimer(self)
        self._draft_timer.setSingleShot(True)
        self._draft_timer.timeout.connect(self._save_draft)
        self._aoi_timer = QTimer(self)
        self._aoi_timer.setSingleShot(True)
        self._aoi_timer.timeout.connect(self._emit_aoi_positions)

        self.emails: list[dict] = self._build_initial_emails()
        self.current_email_id: str | None = None
        self._build_ui()
        self._refresh_list()


    def _build_initial_emails(self) -> list[dict]:
        """Το "θόρυβο" του inbox. Χρειάζεται: ένα inbox με τρία μηνύματα δεν
        μοιάζει με inbox εργαζομένου, και η οπτική πυκνότητα επηρεάζει
        άμεσα το πόση πληροφορία είναι εκτεθειμένη ανά πάσα στιγμή."""
        # (κατηγορία, όνομα, διεύθυνση, θέμα, απόσπασμα, ετικέτα ώρας,
        #  λεπτά πριν από «τώρα», προαιρετική σημαία)
        filler = [
            ("promotions", "Δοκιμαστική ΕΠΕ", "promo@dokimastiki.demo",
             "Τελευταίες μέρες προσφορών", "Οι εκπτώσεις ολοκληρώνονται την Κυριακή.", "5:39 μ.μ.", 6),
            ("promotions", "Demo Market", "news@demomarket.demo",
             "Εβδομαδιαίες προσφορές", "Καφές, φρέσκα προϊόντα και είδη σπιτιού σε νέες τιμές.", "1:51 μ.μ.", 234),
            ("updates", "Ημερολόγιο", "calendar@demo.test",
             "Υπενθύμιση: εβδομαδιαία συνάντηση ομάδας", "Αύριο 10:00, αίθουσα Β.", "11:31 π.μ.", 374),
            ("social", "Δίκτυο Demo", "no-reply@social.demo",
             "Έχετε 2 νέες συνδέσεις", "Δείτε ποιος επισκέφθηκε το προφίλ σας αυτή την εβδομάδα.", "10:00 π.μ.", 465),
            # Σημερινή αλληλογραφία ρουτίνας: χωρίς αυτήν τα μηνύματα-ερεθίσματα
            # σχηματίζουν συμπαγές μπλοκ στην κορυφή και γίνονται αναγνωρίσιμα.
            ("primary", "Θανάσης Ρ.", "t.roussos@demo.test",
             "Re: Ερώτηση για το staging", "Το κοίταξα, σου απαντάω αναλυτικά αύριο.", "5:20 μ.μ.", 25),
            ("primary", "Δανάη Β.", "d.vlachou@demo.test",
             "Μεσημεριανό;", "Πάμε κάτω στις 2 αν προλαβαίνεις.", "1:12 μ.μ.", 273),
            ("primary", "IT Helpdesk", "helpdesk@demo.test",
             "Το αίτημα #8812 ενημερώθηκε", "Ο τεχνικός πρόσθεσε σχόλιο στο αίτημά σας.", "3:47 μ.μ.", 118),
            ("primary", "Γραμματεία", "office@demo.test",
             "Ατζέντα για αύριο", "Στέλνω τα θέματα που συγκεντρώθηκαν μέχρι τώρα.", "11:05 π.μ.", 400),
            ("primary", "Χριστίνα Λ.", "c.lambrou@demo.test",
             "Fwd: Οδηγίες υποβολής εξόδων", "Σου προωθώ τις οδηγίες, μην ξεχάσεις την προθεσμία.", "4:32 μ.μ.", 78),
            ("primary", "Τμήμα Προσωπικού", "hr@demo.test",
             "Δήλωση αδειών Σεπτεμβρίου", "Παρακαλούμε συμπληρώστε τη δήλωση έως την Παρασκευή.", "26 Αυγ", 13000),
            ("primary", "IT Helpdesk", "helpdesk@demo.test",
             "Προγραμματισμένη συντήρηση", "Το VPN θα είναι εκτός λειτουργίας το Σάββατο 02:00-04:00.", "26 Αυγ", 13100),
            ("updates", "Σύστημα Αναφορών", "reports@demo.test",
             "Η μηνιαία αναφορά είναι διαθέσιμη", "Η αναφορά Ιουλίου δημιουργήθηκε αυτόματα.", "25 Αυγ", 14500),
            ("promotions", "Pilot Systems ΑΕ", "offers@pilotsystems.demo",
             "Νέα σειρά προϊόντων", "Δείτε πρώτοι τα νέα μοντέλα της σεζόν.", "25 Αυγ", 14600),
            ("primary", "Τμήμα Προσωπικού", "hr@demo.test",
             "Αποστολή υπογεγραμμένου εντύπου",
             "Παρακαλούμε επισυνάψτε το υπογεγραμμένο έντυπο σε PDF και απαντήστε.",
             "26 Αυγ", 12900, "needs_attachment"),
            ("primary", "Λογιστήριο", "accounting@demo.test",
             "Παραστατικά Αυγούστου", "Υπενθύμιση για την υποβολή των παραστατικών.", "24 Αυγ", 16000),
            ("primary", "Μαρία Κ.", "m.k@demo.test",
             "Re: Πρόγραμμα εβδομάδας", "Σου στέλνω το αναθεωρημένο πρόγραμμα, δες το πριν τη Δευτέρα.", "24 Αυγ", 16100),
            ("primary", "Γραμματεία", "office@demo.test",
             "Πρακτικά συνάντησης 21/08",
             "Επισυνάπτονται τα πρακτικά της τελευταίας συνάντησης.", "22 Αυγ", 19000,
             "has_attachment"),
            ("primary", "Δοκιμαστική ΕΠΕ", "billing@dokimastiki.demo",
             "Η απόδειξή σας", "Η συνδρομή σας ανανεώθηκε αυτόματα για έναν μήνα.", "21 Αυγ", 20500),
            ("primary", "Αρχείο Έργων", "projects@demo.test",
             "Ενημέρωση κατάστασης έργου", "Τρία παραδοτέα παραμένουν σε εκκρεμότητα.", "20 Αυγ", 22000),
            ("primary", "Ομάδα Ποιότητας", "qa@demo.test",
             "Έλεγχος διαδικασιών", "Ο περιοδικός έλεγχος ξεκινά την επόμενη εβδομάδα.", "19 Αυγ", 23500),
            ("primary", "Νίκος Π.", "n.p@demo.test",
             "Ερώτηση για το αρχείο", "Μπορείς να μου στείλεις την τελευταία έκδοση;", "18 Αυγ", 25000),
            ("primary", "Υποστήριξη Demo", "support@demo.test",
             "Το αίτημά σας #4471 έκλεισε", "Το αίτημα ολοκληρώθηκε. Βαθμολογήστε την εξυπηρέτηση.", "18 Αυγ", 25100),
        ]
        emails = []
        for i, row in enumerate(filler):
            cat, name, mail, subj, prev, when, minutes = row[:7]
            flag = row[7] if len(row) > 7 else ""
            emails.append({
                "email_id": f"filler_{i}", "kind": "generic", "category": cat,
                "sender_name": name, "sender_email": mail, "subject": subj,
                "preview": prev, "body": prev, "time": when, "unread": False,
                "starred": False, "folder": "inbox", "received": minutes,
                # Σε αυτό το μήνυμα η απάντηση απαιτεί συνημμένο ΤΟΥ ΧΡΗΣΤΗ.
                "requires_attachment": flag == "needs_attachment",
            })
            if flag == "has_attachment":
                emails[-1]["attachment"] = "Πρακτικά_21-08-2026.pdf"
                emails[-1]["attachment_body"] = _MINUTES_PDF
                emails[-1]["attachment_is_html"] = False

        emails.append({
            "email_id": "credentials", "kind": "credentials", "category": "primary",
            "sender_name": "εγώ", "sender_email": "me@demo.test",
            "subject": self.content.email_subject,
            "preview": "Bank username, password, IBAN, ΑΦΜ, ΑΜΚΑ, Taxisnet…",
            "time": "Χθες", "unread": False, "starred": True, "folder": "inbox",
            "received": 1600,
        })
        return emails

    def _visible_emails(self) -> list[dict]:
        folder = self._active_folder
        if folder == "drafts":
            drafts = []
            for email_id, text in self._drafts.items():
                source = self._email_by_id(email_id)
                if source is None:
                    continue
                first_line = next((ln for ln in text.splitlines() if ln.strip()), "(κενό)")
                drafts.append({
                    "email_id": f"draft::{email_id}", "kind": "draft_ref",
                    "category": self._active_category, "sender_name": "Πρόχειρο",
                    "sender_email": source["sender_email"],
                    "subject": f"Απ: {source['subject']}",
                    "preview": first_line[:110], "time": "Αποθηκεύτηκε",
                    "unread": False, "starred": False, "folder": "drafts",
                })
            return drafts
        if folder == "starred":
            found = [e for e in self.emails
                     if e.get("starred") and e.get("folder", "inbox") != "trash"]
        elif folder in ("snoozed", "trash", "sent"):
            found = [e for e in self.emails if e.get("folder") == folder]
        else:
            found = [e for e in self.emails
                     if e.get("folder", "inbox") == folder
                     and e.get("category", "primary") == self._active_category]
        # Χρονολογική σειρά, νεότερο πρώτα -- τα μηνύματα-ερεθίσματα
        # παρεμβάλλονται στον «θόρυβο» αντί να στοιβάζονται στην κορυφή.
        return sorted(found, key=lambda e: e.get("received", 10 ** 9))

    def _email_by_id(self, email_id: str) -> dict | None:
        return next((e for e in self.emails if e["email_id"] == email_id), None)

   
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.setStyleSheet(f"background:{BG_APP};")

        outer.addWidget(self._build_topbar())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_sidebar())

        panel = QWidget()
        panel.setStyleSheet(f"background:{BG_PANEL}; border-top-left-radius:16px;")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_inbox_page())
        self.stack.addWidget(self._build_message_page())
        panel_layout.addWidget(self.stack)

     
        self._build_viewer()

        body.addWidget(panel, stretch=1)
        outer.addLayout(body, stretch=1)

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(64)
        bar.setStyleSheet(f"background:{BG_APP};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 8, 18, 8)
        layout.setSpacing(14)

        layout.addWidget(_icon_label("☰", 18))
        logo = QLabel("✉")
        logo.setStyleSheet(f"color:{ACCENT}; font-size:22px; background:transparent;")
        layout.addWidget(logo)
        name = QLabel("Demo Mail")
        name.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:19px; background:transparent;")
        layout.addWidget(name)
        layout.addSpacing(20)

        search_box = QWidget()
        search_box.setFixedHeight(44)
        search_box.setMaximumWidth(720)
        search_box.setStyleSheet(f"background:{SEARCH_BG}; border-radius:8px;")
        search_layout = QHBoxLayout(search_box)
        search_layout.setContentsMargins(16, 0, 16, 0)
        search_layout.setSpacing(10)
        search_layout.addWidget(_icon_label("🔍", 15))
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Αναζήτηση μηνυμάτων")
        self.search_field.setStyleSheet(
            f"QLineEdit {{ background:transparent; border:none; font-size:14px; "
            f"color:{TEXT_PRIMARY}; }}"
        )
        self.search_field.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_field, stretch=1)
        search_layout.addWidget(_icon_label("⚙", 15))
        layout.addWidget(search_box, stretch=1)

        layout.addStretch()
        for glyph in ("?", "⚙", "⠿"):
            layout.addWidget(_icon_label(glyph, 16))
        layout.addWidget(_avatar("E", ACCENT, 34))
        return bar

    def _build_sidebar(self) -> QWidget:
        side = QWidget()
        side.setFixedWidth(232)
        side.setStyleSheet(f"background:{BG_APP};")
        layout = QVBoxLayout(side)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(2)

        compose = QPushButton("✏   Σύνταξη")
        compose.setFixedHeight(48)
        compose.setCursor(Qt.CursorShape.PointingHandCursor)
        compose.setStyleSheet(
            f"QPushButton {{ background:{COMPOSE_BG}; color:#001d35; border:none; "
            f"border-radius:16px; font-size:14px; font-weight:500; text-align:left; "
            f"padding-left:20px; }}"
            f"QPushButton:hover {{ background:#b0dcf8; }}"
        )
        compose.clicked.connect(lambda: self.action_performed.emit("compose_clicked"))
        layout.addWidget(compose)
        layout.addSpacing(14)

        self._folder_buttons: dict[str, QPushButton] = {}
        for folder, glyph, key in (("Εισερχόμενα", "📥", "inbox"), ("Με αστέρι", "☆", "starred"),
                                   ("Σε αναβολή", "🕐", "snoozed"), ("Απεσταλμένα", "➤", "sent"),
                                   ("Πρόχειρα", "📄", "drafts"), ("Κάδος", "🗑", "trash")):
            btn = QPushButton(f"   {glyph}    {folder}")
            btn.setFixedHeight(34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self.set_folder(k))
            self._folder_buttons[key] = btn
            layout.addWidget(btn)
        self._folder_titles = {"inbox": "Εισερχόμενα", "starred": "Με αστέρι",
                               "snoozed": "Σε αναβολή", "sent": "Απεσταλμένα",
                               "drafts": "Πρόχειρα", "trash": "Κάδος"}
        self._highlight_folder("inbox")

        layout.addSpacing(12)
        tags = QLabel("   Ετικέτες")
        tags.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:13px; background:transparent;")
        layout.addWidget(tags)
        layout.addStretch()
        return side

    def _highlight_folder(self, active_key: str) -> None:
        for key, btn in self._folder_buttons.items():
            label = self._folder_titles[key]
            count = len(self._drafts) if key == "drafts" else 0
            btn.setText(f"   {btn.text().strip().split(' ')[0]}    {label}"
                        + (f"  ({count})" if count else ""))
            if key == active_key:
                btn.setStyleSheet(
                    f"QPushButton {{ background:{ACCENT_SOFT}; color:#041e49; font-size:13px; "
                    f"font-weight:600; border:none; border-radius:17px; text-align:left; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background:transparent; color:{TEXT_SECONDARY}; "
                    f"font-size:13px; border:none; border-radius:17px; text-align:left; }}"
                    f"QPushButton:hover {{ background:#e8eaed; }}"
                )

    def set_folder(self, key: str) -> None:
        self._active_folder = key
        self._highlight_folder(key)
        self.stack.setCurrentIndex(0)
        self._refresh_list()
        self.action_performed.emit(f"mail_folder_{key}")

    def _build_inbox_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QWidget()
        toolbar.setFixedHeight(46)
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(14, 0, 18, 0)
        tb.setSpacing(8)
        tb.addWidget(_icon_label("☐ ▾", 14))
        tb.addWidget(_flat_button("⟳", "Ανανέωση"))
        tb.addWidget(_flat_button("⋮"))
        tb.addStretch()
        self.pagination_label = QLabel()
        self.pagination_label.setStyleSheet(
            f"color:{TOOLBAR_ICON}; font-size:12.5px; font-weight:600; "
            f"background:transparent;")
        tb.addWidget(self.pagination_label)
        tb.addWidget(_flat_button("‹"))
        tb.addWidget(_flat_button("›"))
        layout.addWidget(toolbar)

        tabs = QWidget()
        tabs.setFixedHeight(46)
        tabs.setStyleSheet("border-bottom:1px solid #f1f3f4;")
        tabs_layout = QHBoxLayout(tabs)
        tabs_layout.setContentsMargins(14, 0, 14, 0)
        tabs_layout.setSpacing(0)
        self._category_buttons: dict[str, QPushButton] = {}
        for key, label, glyph in self.CATEGORIES:
            btn = QPushButton(f"{glyph}   {label}")
            btn.setFixedHeight(45)
            btn.setMinimumWidth(190)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._set_category(k))
            self._category_buttons[key] = btn
            tabs_layout.addWidget(btn)
        tabs_layout.addStretch()
        layout.addWidget(tabs)
        self._sync_category_styles()

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(self._LIST_STYLE)
        self.list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget, stretch=1)
        return page

    def _build_message_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        actions = QWidget()
        actions.setFixedHeight(46)
        ab = QHBoxLayout(actions)
        ab.setContentsMargins(14, 0, 18, 0)
        ab.setSpacing(6)
        back = _flat_button("←", "Επιστροφή στα εισερχόμενα")
        back.clicked.connect(self._back_to_inbox)
        ab.addWidget(back)
        for glyph in ("🗄", "🗑", "✉", "🕐"):
            ab.addWidget(_flat_button(glyph))
        ab.addStretch()
        layout.addWidget(actions)

        self.msg_scroll = QScrollArea()
        self.msg_scroll.setWidgetResizable(True)
        self.msg_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.msg_scroll.setStyleSheet(f"background:{BG_PANEL};")
        self.msg_scroll.verticalScrollBar().valueChanged.connect(self._schedule_aoi_emit)

        container = QWidget()
        container.setStyleSheet(f"background:{BG_PANEL};")
        self.msg_layout = QVBoxLayout(container)
        self.msg_layout.setContentsMargins(56, 10, 56, 40)
        self.msg_layout.setSpacing(0)

        self.subject_label = QLabel()
        self.subject_label.setWordWrap(True)
        self.subject_label.setStyleSheet(
            f"color:{TEXT_PRIMARY}; font-size:22px; font-weight:400; background:transparent;")
        self.msg_layout.addWidget(self.subject_label)
        self.msg_layout.addSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)
        self.header_avatar = _avatar("?", TEXT_SECONDARY, 38)
        header.addWidget(self.header_avatar, alignment=Qt.AlignmentFlag.AlignTop)
        sender_box = QVBoxLayout()
        sender_box.setSpacing(1)
        self.sender_label = QLabel()
        self.sender_label.setStyleSheet(
            f"color:{TEXT_PRIMARY}; font-size:13.5px; font-weight:600; background:transparent;")
        self.recipient_label = QLabel("προς εμένα ▾")
        self.recipient_label.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:12px; background:transparent;")
        sender_box.addWidget(self.sender_label)
        sender_box.addWidget(self.recipient_label)
        header.addLayout(sender_box)
        header.addStretch()
        self.time_label = QLabel()
        self.time_label.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:12px; background:transparent;")
        header.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignTop)
        self.msg_layout.addLayout(header)
        self.msg_layout.addSpacing(20)

     
        self.body_view = QTextBrowser()
        self.body_view.setReadOnly(True)
        self.body_view.setFrameShape(QFrame.Shape.NoFrame)
        self.body_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.body_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.body_view.setStyleSheet(
            f"QTextBrowser {{ background:transparent; border:none; color:{TEXT_PRIMARY}; "
            f"font-family:'{FONT_FAMILY}'; font-size:14px; }}"
        )
        self.body_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.msg_layout.addWidget(self.body_view)

        self.attachment_layout = QVBoxLayout()   # chip συνημμένου + προεπισκόπηση
        self.attachment_layout.setSpacing(8)
        self.msg_layout.addLayout(self.attachment_layout)

        self.extra_layout = QVBoxLayout()   # κωδικοί / OTP -- structured περιεχόμενο
        self.extra_layout.setSpacing(6)
        self.msg_layout.addLayout(self.extra_layout)

        self.msg_layout.addSpacing(24)
        self.reply_button_row = QHBoxLayout()
        self.reply_btn = QPushButton("↩   Απάντηση")
        self.forward_btn = QPushButton("↪   Προώθηση")
        for btn in (self.reply_btn, self.forward_btn):
            btn.setFixedHeight(42)
            btn.setMinimumWidth(160)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
       
        self.reply_btn.setStyleSheet(
            f"QPushButton {{ background:{ACCENT}; color:white; border:none; "
            f"border-radius:21px; font-size:14px; font-weight:600; }}"
            f"QPushButton:hover {{ background:#0a52c7; }}"
            f"QPushButton:pressed {{ background:#063178; }}"
            f"QPushButton:disabled {{ background:#c9ced6; color:#6b7079; }}"
        )
        self.forward_btn.setStyleSheet(
            f"QPushButton {{ background:white; color:{ACCENT}; "
            f"border:1.5px solid {ACCENT}; border-radius:21px; font-size:14px; "
            f"font-weight:600; }}"
            f"QPushButton:hover {{ background:{ACCENT_SOFT}; }}"
        )
        self.reply_btn.clicked.connect(self._open_reply)
        self.forward_btn.clicked.connect(lambda: self.action_performed.emit("email_forward_clicked"))
        self.reply_button_row.addWidget(self.reply_btn)
        self.reply_button_row.addWidget(self.forward_btn)
        self.reply_button_row.addStretch()
        self.msg_layout.addLayout(self.reply_button_row)

        self.msg_layout.addWidget(self._build_reply_card())
        self.msg_layout.addStretch()

        self.msg_scroll.setWidget(container)
        layout.addWidget(self.msg_scroll, stretch=1)
        return page

    def _build_reply_card(self) -> QWidget:
        self.reply_card = QWidget()
        self.reply_card.setStyleSheet(
            f"background:{BG_PANEL}; border:1px solid {BORDER}; border-radius:12px;")
        layout = QVBoxLayout(self.reply_card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(_icon_label("↩", 14, ACCENT))
        self.reply_to_label = QLabel()
        self.reply_to_label.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:12.5px; background:transparent; border:none;")
        head.addWidget(self.reply_to_label)
        head.addStretch()
        self.draft_status = QLabel("")
        self.draft_status.setStyleSheet(
            f"color:{TEXT_MUTED}; font-size:11.5px; background:transparent; border:none;")
        head.addWidget(self.draft_status)
        layout.addLayout(head)

        self.reply_edit = QTextEdit()
        self.reply_edit.setMinimumHeight(230)
        self.reply_edit.setStyleSheet(
            f"QTextEdit {{ background:transparent; border:none; color:{TEXT_PRIMARY}; "
            f"font-family:'{FONT_FAMILY}'; font-size:13.5px; }}"
        )
        self.reply_edit.textChanged.connect(self._on_reply_typing)
        layout.addWidget(self.reply_edit)

       
        self.reply_attach_row = QHBoxLayout()
        self.reply_attach_row.setSpacing(8)
        layout.addLayout(self.reply_attach_row)

        footer = QHBoxLayout()
        self.send_btn = QPushButton("Αποστολή")
        self.send_btn.setFixedSize(110, 36)
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setStyleSheet(
            f"QPushButton {{ background:{ACCENT}; color:white; border:none; "
            f"border-radius:18px; font-size:13.5px; font-weight:600; }}"
            f"QPushButton:hover {{ background:#0a4fb8; }}"
        )
        self.send_btn.clicked.connect(self._send_reply)
        footer.addWidget(self.send_btn)
        footer.addSpacing(6)
        attach_btn = QPushButton("📎")
        attach_btn.setFixedSize(36, 36)
        attach_btn.setToolTip("Επισύναψη αρχείου")
        attach_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        attach_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{TEXT_SECONDARY}; border:none; "
            f"border-radius:18px; font-size:16px; }}"
            f"QPushButton:hover {{ background:#e8eaed; }}"
        )
        attach_btn.clicked.connect(self._choose_attachment)
        footer.addWidget(attach_btn)
        footer.addStretch()
        discard = _flat_button("🗑", "Απόρριψη")
        discard.clicked.connect(self._discard_reply)
        footer.addWidget(discard)
        layout.addLayout(footer)

        self.reply_card.hide()
        return self.reply_card

    def _build_viewer(self) -> None:
        self.viewer = QWidget(self)
        self.viewer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.viewer.setStyleSheet("background:#3c4043;")
        layout = QVBoxLayout(self.viewer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet("background:#202124;")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(16, 0, 16, 0)
        bl.setSpacing(12)
        badge = QLabel("PDF")
        badge.setStyleSheet("background:#c5221f; color:white; border-radius:3px; "
                             "padding:3px 7px; font-size:10px; font-weight:bold;")
        bl.addWidget(badge)
        self.viewer_title = QLabel()
        self.viewer_title.setStyleSheet("color:white; font-size:13.5px; font-weight:600; "
                                         "background:transparent;")
        bl.addWidget(self.viewer_title)
        bl.addStretch()
        for glyph in ("🖨", "⭳"):
            lbl = QLabel(glyph)
            lbl.setStyleSheet("color:#e8eaed; font-size:15px; background:transparent;")
            bl.addWidget(lbl)
        close = QPushButton("✕")
        close.setFixedSize(32, 32)
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setStyleSheet(
            "QPushButton { background:transparent; color:white; border:none; font-size:16px; }"
            "QPushButton:hover { background:#5f6368; border-radius:16px; }"
        )
        close.clicked.connect(self.close_attachment)
        bl.addWidget(close)
        layout.addWidget(bar)

        self.viewer_scroll = QScrollArea()
        self.viewer_scroll.setWidgetResizable(True)
        self.viewer_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.viewer_scroll.setStyleSheet("background:#3c4043;")
        self.viewer_scroll.verticalScrollBar().valueChanged.connect(
            lambda _: self._schedule_aoi_emit())

        holder = QWidget()
        holder.setStyleSheet("background:#3c4043;")
        hl = QVBoxLayout(holder)
        hl.setContentsMargins(0, 28, 0, 28)

        # «Σελίδα» A4: λευκό φύλλο με σκιά, κεντραρισμένο σε σκούρο φόντο --
        # η οπτική σύμβαση κάθε προβολέα PDF.
        page = QWidget()
        page.setFixedWidth(820)
        page.setStyleSheet("background:white;")
        apply_card_shadow_local(page)
        pl = QVBoxLayout(page)
        pl.setContentsMargins(72, 64, 72, 64)
        self.viewer_body = QTextBrowser()
        self.viewer_body.setReadOnly(True)
        self.viewer_body.setFrameShape(QFrame.Shape.NoFrame)
        self.viewer_body.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.viewer_body.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.viewer_body.setStyleSheet(
            f"QTextBrowser {{ background:transparent; border:none; color:#101114; "
            f"font-family:'{FONT_FAMILY}'; font-size:14.5px; }}"
        )
        self.viewer_body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        pl.addWidget(self.viewer_body)
        page_row = QHBoxLayout()
        page_row.addStretch()
        page_row.addWidget(page)
        page_row.addStretch()
        hl.addLayout(page_row)
        hl.addStretch()
        self.viewer_scroll.setWidget(holder)
        layout.addWidget(self.viewer_scroll, stretch=1)

        self._viewer_email_id: str | None = None
        self.viewer.hide()

   
    def _set_category(self, key: str) -> None:
        self._active_category = key
        self._sync_category_styles()
        self._refresh_list()
        self.action_performed.emit(f"mail_category_{key}")

    def _sync_category_styles(self) -> None:
        for key, btn in self._category_buttons.items():
            active = key == self._active_category
            btn.setStyleSheet(
                f"QPushButton {{ background:transparent; text-align:left; padding-left:14px; "
                f"color:{ACCENT if active else '#2b3138'}; font-size:13.5px; "
                f"font-weight:{'600' if active else '400'}; border:none; "
                f"border-bottom:{'3px solid ' + ACCENT if active else '3px solid transparent'}; }}"
                f"QPushButton:hover {{ background:#f5f6f7; }}"
            )

    def _on_search(self, text: str) -> None:
        self._refresh_list(filter_text=text.strip())
        if text.strip():
            self.action_performed.emit("mail_search_used")

    def _refresh_list(self, filter_text: str = "") -> None:
        self.list_widget.clear()
        needle = filter_text.casefold()
        shown = 0
        for email in self._visible_emails():
            if needle and needle not in (
                    email["sender_name"] + email["subject"] + email.get("preview", "")).casefold():
                continue
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 40))
            item.setData(Qt.ItemDataRole.UserRole, email["email_id"])
            self.list_widget.addItem(item)
            row = _EmailRow(email)
            row.star_toggled.connect(lambda eid, on: self.action_performed.emit(
                f"email_star_{'on' if on else 'off'}"))
            self.list_widget.setItemWidget(item, row)
            shown += 1
        total = 9_655 + shown       # πλήθος τύπου "1-50 από 9.655", για αληθοφάνεια
        self.pagination_label.setText(f"1–{shown} από {total:,}".replace(",", "."))

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        email_id = item.data(Qt.ItemDataRole.UserRole)
        if email_id.startswith("draft::"):
            source_id = email_id.split("::", 1)[1]
            self.action_performed.emit("draft_reopened")
            self.set_folder("inbox")
            self.open_email(source_id)
            self._open_reply()
            return
        email = self._email_by_id(email_id)
        if email is None:
            return
        email["unread"] = False
        self.open_email(email_id)

    def _back_to_inbox(self) -> None:
        self._flush_draft()
        self.stack.setCurrentIndex(0)
        self._refresh_list()
        self.action_performed.emit("mail_back_to_inbox")

  
    def open_email(self, email_id: str) -> None:
        email = self._email_by_id(email_id)
        if email is None:
            return
        self._flush_draft()      # το πρόχειρο του ΠΡΟΗΓΟΥΜΕΝΟΥ μηνύματος
        self.current_email_id = email_id
        self._clear_layout(self.extra_layout)
        self._copy_buttons = {}
        self._reply_started = False
        self.reply_card.hide()
        self.reply_btn.setEnabled(True)

        self.subject_label.setText(email["subject"])
        initial = email["sender_name"][:1] or "?"
        self.header_avatar.setText(initial.upper())
        self.header_avatar.setStyleSheet(
            f"background:{_sender_color(email['sender_name'])}; color:white; "
            f"border-radius:19px; font-weight:600; font-size:16px;"
        )
        self.sender_label.setText(f"{email['sender_name']}  <{email['sender_email']}>")
        self.time_label.setText(email.get("time", ""))

        self._clear_layout(self.attachment_layout)
        if email.get("attachment"):
            self._render_attachment(email)

        if email["kind"] == "credentials":
            self.body_view.hide()
            self._render_credentials()
        elif email["kind"] == "otp":
            self.body_view.hide()
            self._render_otp(email)
            self.action_performed.emit("otp_email_opened")
        else:
            self.body_view.show()
            self.body_view.setPlainText(email.get("body", ""))
            self._fit_body_height()

        self.stack.setCurrentIndex(1)
        self.msg_scroll.verticalScrollBar().setValue(0)
        self.action_performed.emit(f"email_opened_{email_id}")
        self._schedule_aoi_emit()

    def _render_attachment(self, email: dict) -> None:
        label = QLabel("1 συνημμένο")
        label.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:12.5px; font-weight:600;")
        self.attachment_layout.addWidget(label)

        card = QPushButton()
        card.setFixedSize(280, 170)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(
            f"QPushButton {{ background:white; border:1.5px solid {BORDER}; "
            f"border-radius:10px; text-align:left; }}"
            f"QPushButton:hover {{ border-color:{ACCENT}; background:#f4f8ff; }}"
        )
        card.clicked.connect(lambda: self.open_attachment(email["email_id"]))

        inner = QVBoxLayout(card)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)

        thumb = QLabel()
        thumb.setFixedHeight(122)
        thumb.setStyleSheet(
            "background:white; border-top-left-radius:10px; "
            "border-top-right-radius:10px; border-bottom:1px solid #d7dbe0; "
            "color:#3c4043; font-size:7px; padding:8px 10px;"
        )
        thumb.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        thumb.setWordWrap(True)
        if email.get("attachment_is_html"):
            # Το raw markup δεν είναι μικρογραφία· δείχνουμε τη σύνοψη.
            preview_source = email.get("attachment_preview", "")
        else:
            preview_source = email.get("attachment_body", "")
        thumb.setText(" ".join(preview_source.split())[:340])
        inner.addWidget(thumb)

        foot = QWidget()
        foot.setStyleSheet("background:#f5f6f8; border-bottom-left-radius:10px; "
                            "border-bottom-right-radius:10px;")
        fl = QHBoxLayout(foot)
        fl.setContentsMargins(10, 0, 10, 0)
        fl.setSpacing(8)
        icon = QLabel("PDF")
        icon.setStyleSheet(
            "background:#c5221f; color:white; border-radius:3px; padding:2px 5px; "
            "font-size:9px; font-weight:bold;"
        )
        fl.addWidget(icon)
        name = QLabel()
        name.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:11.5px; font-weight:600;")
        fm = name.fontMetrics()
        name.setText(fm.elidedText(email["attachment"], Qt.TextElideMode.ElideMiddle, 200))
        fl.addWidget(name, stretch=1)
        inner.addWidget(foot)

        self.attachment_layout.addWidget(card)

    def open_attachment(self, email_id: str) -> None:
        email = self._email_by_id(email_id)
        if email is None or not email.get("attachment"):
            return
        self.viewer_title.setText(email["attachment"])
        if email.get("attachment_is_html"):
            self.viewer_body.setHtml(email.get("attachment_body", ""))
        else:
            self.viewer_body.setPlainText(email.get("attachment_body", ""))
        self._fit_viewer_height()
        self.viewer.setGeometry(0, 0, self.width(), self.height())
        self.viewer.show()
        self.viewer.raise_()
        self.viewer_scroll.verticalScrollBar().setValue(0)
        self._viewer_email_id = email_id
        self.action_performed.emit(f"attachment_opened_{email_id}")
        self._schedule_aoi_emit()

    def close_attachment(self) -> None:
        self.viewer.hide()
        self._viewer_email_id = None
        self.action_performed.emit("attachment_closed")
        self._schedule_aoi_emit()

    def _fit_viewer_height(self) -> None:
        doc = self.viewer_body.document()
        width = max(400, self.viewer_body.viewport().width())
        doc.setTextWidth(width)
        self.viewer_body.setFixedHeight(int(doc.size().height()) + 20)

    def _fit_body_height(self) -> None:
       
        doc = self.body_view.document()
        width = max(400, self.body_view.viewport().width())
        doc.setTextWidth(width)
        self.body_view.setFixedHeight(int(doc.size().height()) + 12)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.body_view.isVisible():
            self._fit_body_height()
        if self.viewer.isVisible():
            self.viewer.setGeometry(0, 0, self.width(), self.height())
            self._fit_viewer_height()
        self._schedule_aoi_emit()

    def _render_credentials(self) -> None:
        rows = [
            ("email_bank_username", "Bank username", self.content.bank_username),
            ("email_bank_password", "Bank password", self.content.bank_password),
            ("email_iban", "IBAN", _format_iban_display(self.content.iban)),
            ("email_afm", "ΑΦΜ", self.content.afm),
            ("email_amka", "ΑΜΚΑ", self.content.amka),
            ("email_taxis_username", "Taxisnet username", self.content.taxis_username),
            ("email_taxis_password", "Taxisnet password", self.content.taxis_password),
        ]
        for field_id, label_text, value in rows:
            row = QHBoxLayout()
            lbl = QLabel(f"{label_text}:")
            lbl.setFixedWidth(170)
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY}; font-size:13.5px;")
            val = QLabel(value)
            val.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
            val.setStyleSheet(f"color:{TEXT_PRIMARY};")
            # Χωρίς κουμπί αντιγραφής: η τιμή επιλέγεται με το ποντίκι και
            # αντιγράφεται με Ctrl+C, όπως σε κάθε webmail. Ο συμμετέχων
            # αποφασίζει μόνος του αν θα αντιγράψει ή θα πληκτρολογήσει, και
            # αυτή η επιλογή είναι η ίδια συμπεριφορά που μετράμε.
            val.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
                | Qt.TextInteractionFlag.TextSelectableByKeyboard)
            val.setCursor(Qt.CursorShape.IBeamCursor)
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            self.extra_layout.addLayout(row)
            self._emit_widget_bbox(field_id, val, value)

    def _render_otp(self, email: dict) -> None:
        info = QLabel(f"Κωδικός επιβεβαίωσης για την υπογραφή του εγγράφου "
                      f"«{email['document']}»:")
        info.setWordWrap(True)
        info.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:14px;")
        self.extra_layout.addWidget(info)

        row = QHBoxLayout()
        code = QLabel(email["code"])
        code.setFont(QFont("Consolas", 22, QFont.Weight.Bold))
        code.setStyleSheet(f"color:{ACCENT};")
        btn = QPushButton("Αντιγραφή")
        btn.setFixedWidth(120)
        btn.setStyleSheet(self._COPY_STYLE)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(
            lambda: self._on_copy("email_otp_code", email["code"], btn, "Αντιγραφή"))
        self._copy_buttons["email_otp_code"] = (btn, "Αντιγραφή")
        row.addWidget(code)
        row.addWidget(btn)
        row.addStretch()
        self.extra_layout.addLayout(row)
        self._emit_widget_bbox("email_otp_code", code, email["code"])

    def _on_copy(self, field_id: str, value: str, button: QPushButton, original: str) -> None:
        QApplication.clipboard().setText(value)
        self.action_performed.emit(f"{field_id}_copied")
        button.setText("✓ Αντιγράφηκε")
        button.setStyleSheet(self._COPIED_STYLE)

    def reset_copy_indicators(self) -> None:
        for button, original in self._copy_buttons.values():
            button.setText(original)
            button.setStyleSheet(self._COPY_STYLE)

   
    def _open_reply(self) -> None:
        email = self._email_by_id(self.current_email_id or "")
        if email is None:
            return
        self.reply_to_label.setText(f"Προς: {email['sender_name']} <{email['sender_email']}>")
        existing = self._drafts.get(email["email_id"])
        self.reply_edit.blockSignals(True)
        self.reply_edit.setPlainText(existing if existing is not None else "")
        self.reply_edit.blockSignals(False)
        if existing is not None:
            self.action_performed.emit("draft_restored")
        self._reply_attachments = []
        self._render_reply_attachments()
        if email.get("requires_attachment"):
            self.draft_status.setText("Το μήνυμα ζητά συνημμένο — χρησιμοποίησε το 📎")
        self.reply_card.show()
        self.reply_btn.setEnabled(False)
        self.reply_edit.setFocus()
        cursor = self.reply_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.reply_edit.setTextCursor(cursor)
        self.action_performed.emit("reply_opened")
        QTimer.singleShot(0, lambda: self.msg_scroll.verticalScrollBar().setValue(
            self.msg_scroll.verticalScrollBar().maximum()))

    def _stimulus_for(self, email: dict) -> Stimulus | None:
        sid = email.get("stimulus_id")
        return STIMULI.get(sid) if sid else None

    def _save_draft(self) -> None:
        if self.current_email_id is None or not self.reply_card.isVisible():
            return
        text = self.reply_edit.toPlainText()
        if not text.strip():
            self._drafts.pop(self.current_email_id, None)
        else:
            self._drafts[self.current_email_id] = text
        self._highlight_folder(self._active_folder)
        self.draft_status.setText("Το πρόχειρο αποθηκεύτηκε" if text.strip() else "")
        QTimer.singleShot(2500, lambda: self.draft_status.setText(""))
        self.draft_saved.emit(self.current_email_id, len(text))

    def _flush_draft(self) -> None:
        self._draft_timer.stop()
        self._save_draft()

    def _choose_attachment(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Επιλογή αρχείου", "", "Αρχεία PDF (*.pdf);;Όλα τα αρχεία (*)")
        if path:
            self.attach_file(path)

    def attach_file(self, path: str) -> None:
        from pathlib import Path as _Path
        name = _Path(path).name
        if name in self._reply_attachments:
            return
        self._reply_attachments.append(name)
        self._render_reply_attachments()
        self.action_performed.emit("reply_attachment_added")

    def _render_reply_attachments(self) -> None:
        self._clear_layout(self.reply_attach_row)
        for name in self._reply_attachments:
            chip = QWidget()
            chip.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
            chip.setFixedHeight(34)
            chip.setStyleSheet(
                f"background:#eef2f8; border:1px solid {BORDER}; border-radius:6px;")
            cl = QHBoxLayout(chip)
            cl.setContentsMargins(9, 0, 6, 0)
            cl.setSpacing(8)
            badge = QLabel("PDF")
            badge.setStyleSheet("background:#c5221f; color:white; border-radius:3px; "
                                 "padding:2px 5px; font-size:9px; font-weight:bold;")
            cl.addWidget(badge)
            label = QLabel(name)
            label.setStyleSheet(f"color:{TEXT_PRIMARY}; font-size:12px; background:transparent; "
                                 f"border:none;")
            cl.addWidget(label)
            remove = QPushButton("✕")
            remove.setFixedSize(20, 20)
            remove.setCursor(Qt.CursorShape.PointingHandCursor)
            remove.setStyleSheet(
                f"QPushButton {{ background:transparent; color:{TEXT_MUTED}; border:none; "
                f"font-size:11px; }} QPushButton:hover {{ color:#c5221f; }}"
            )
            remove.clicked.connect(lambda _, n=name: self._remove_attachment(n))
            cl.addWidget(remove)
            self.reply_attach_row.addWidget(chip)
        self.reply_attach_row.addStretch()

    def _remove_attachment(self, name: str) -> None:
        if name in self._reply_attachments:
            self._reply_attachments.remove(name)
            self._render_reply_attachments()
            self.action_performed.emit("reply_attachment_removed")

    def _on_reply_typing(self) -> None:
        self._draft_timer.start(700)     # debounce: αποθήκευση μετά από παύση
        if not self._reply_started:
            self._reply_started = True
            self.action_performed.emit("reply_typing_started")

    def _send_reply(self) -> None:
        email = self._email_by_id(self.current_email_id or "")
        if email is None:
            return
        text = self.reply_edit.toPlainText()
        self._draft_timer.stop()
        self._drafts.pop(email["email_id"], None)
        if self._reply_attachments:
            text = text + "\n\n[συνημμένα: " + ", ".join(self._reply_attachments) + "]"
        self.reply_submitted.emit(email["email_id"], text)
        self.action_performed.emit(f"email_reply_sent_{email['email_id']}")

        self.emails.append({
            "email_id": f"sent_{email['email_id']}", "kind": "generic", "category": "primary",
            "sender_name": "εγώ", "sender_email": "me@demo.test",
            "subject": f"Απ: {email['subject']}", "preview": text.strip().split("\n")[0][:90],
            "body": text, "time": "Τώρα", "unread": False, "starred": False,
            "folder": "sent", "received": 0,
        })
        self.reply_card.hide()
        self.reply_btn.setEnabled(True)
        self._back_to_inbox()

    def _discard_reply(self) -> None:
        self._draft_timer.stop()
        self._drafts.pop(self.current_email_id or "", None)
        self._highlight_folder(self._active_folder)
        self.reply_card.hide()
        self.reply_btn.setEnabled(True)
        self.action_performed.emit("reply_discarded")

    
    def _schedule_aoi_emit(self) -> None:
        self._aoi_timer.start(120)      # throttle: το scroll παράγει δεκάδες events

    def _emit_widget_bbox(self, field_id: str, widget: QWidget, value: str) -> None:
        def _do() -> None:
            top_left = widget.mapTo(self, QPoint(0, 0))
            self.field_rendered.emit(field_id, QRect(top_left, widget.size()), value)
        QTimer.singleShot(0, _do)

    def _emit_aoi_positions(self) -> None:
        email = self._email_by_id(self.current_email_id or "")
        if email is None or self.stack.currentIndex() != 1:
            return
        stim = self._stimulus_for(email)
        if stim is None:
            return
        if self.viewer.isVisible():
            surface, scroll = self.viewer_body, self.viewer_scroll
        elif self.body_view.isVisible():
            surface, scroll = self.body_view, self.msg_scroll
        else:
            return

        viewport = scroll.viewport()
        visible = QRect(viewport.mapTo(self, QPoint(0, 0)), viewport.size())
        doc = surface.document()

        for aoi_id, needle in stim.aoi_items:
            cursor = doc.find(needle)
            if cursor.isNull():
                continue
            start = QTextCursor(doc)
            start.setPosition(cursor.selectionStart())
            end = QTextCursor(doc)
            end.setPosition(cursor.selectionEnd())
            rect = surface.cursorRect(start).united(surface.cursorRect(end))
            top_left = surface.viewport().mapTo(self, rect.topLeft())
            bbox = QRect(top_left, rect.size())
            if not visible.intersects(bbox):
                continue      
            self.field_rendered.emit(f"email_{aoi_id}", bbox, needle)

   
    def _stimulus_email(self, stim: Stimulus) -> dict:
        """Μετατρέπει ένα Stimulus σε εγγραφή inbox. Το σύμβολο του θέματος
        των διαπιστευτηρίων αντικαθίσταται με το πραγματικό θέμα της
        συνεδρίας, ώστε η παραπομπή μέσα στο κείμενο να είναι συνεπής."""
        body = stim.body.replace(CRED_SUBJECT_TOKEN, self.content.email_subject)
        preview = stim.preview.replace(CRED_SUBJECT_TOKEN, self.content.email_subject)
        entry = {
            "email_id": f"stimulus_{stim.stimulus_id}", "kind": "stimulus",
            "category": "primary", "stimulus_id": stim.stimulus_id,
            "sender_name": stim.sender_name, "sender_email": stim.sender_email,
            "subject": stim.subject, "preview": preview, "body": body,
            "time": stim.time_label, "received": stim.received_minutes,
            "unread": True, "starred": False, "folder": "inbox",
        }
        if stim.attachment:
            entry["attachment"] = stim.attachment
            entry["attachment_body"] = stim.attachment_html or ""
            entry["attachment_is_html"] = bool(stim.attachment_html)
            entry["attachment_preview"] = stim.attachment_preview
        return entry

    def load_stimulus(self, stimulus_id: str) -> None:
        """Φορτώνει ΕΝΑ μήνυμα-ερέθισμα (καθοδηγούμενη ροή βημάτων)."""
        stim = STIMULI[stimulus_id]
        self._all_stimuli_mode = False
        self.emails = [e for e in self.emails if e.get("kind") != "stimulus"]
        self.emails.append(self._stimulus_email(stim))
        self.current_stimulus = stim
        self._active_category = "primary"
        self._sync_category_styles()
        self._refresh_list()
        self.action_performed.emit(f"stimulus_loaded_{stimulus_id}")

    def load_all_stimuli(self) -> None:
        """Φορτώνει και τα δέκα μηνύματα του ενεργού προφίλ ταυτόχρονα. Ο
        συμμετέχων επιλέγει ελεύθερα ποιο θα ανοίξει και με ποια σειρά."""
        self._all_stimuli_mode = True
        self.emails = [e for e in self.emails if e.get("kind") != "stimulus"]
        for stim in STIMULI.values():
            self.emails.append(self._stimulus_email(stim))
        self.current_stimulus = None
        self._active_category = "primary"
        self._sync_category_styles()
        self._refresh_list()
        self.action_performed.emit(f"all_stimuli_loaded_{len(STIMULI)}")

    def add_otp_email(self, code: str, document_name: str) -> None:
        self.emails.insert(0, {
            "email_id": "otp", "kind": "otp", "category": "primary",
            "sender_name": "GovAtHome", "sender_email": "govathome@demo.test",
            "subject": "Κωδικός επιβεβαίωσης υπογραφής",
            "preview": f"Ο κωδικός για το έγγραφο «{document_name}» είναι έτοιμος.",
            "time": "Τώρα", "code": code, "document": document_name,
            "unread": True, "starred": False, "folder": "inbox", "received": 0,
        })
        self._refresh_list()
        self.action_performed.emit("otp_email_received")

    def reset_emails(self) -> None:
        keep_all = self._all_stimuli_mode
        keep = self.current_stimulus
        self._drafts.clear()
        self._active_folder = "inbox"
        self._highlight_folder("inbox")
        self.emails = self._build_initial_emails()
        self.current_email_id = None
        self.reply_card.hide()
        self.stack.setCurrentIndex(0)
        if keep_all:
            self.load_all_stimuli()
        elif keep is not None:
            self.load_stimulus(keep.stimulus_id)
        else:
            self._refresh_list()

    def content_rect(self) -> QRect | None:
        if self.viewer.isVisible():
            vp = self.viewer_scroll.viewport()
            return QRect(vp.mapTo(self, QPoint(0, 0)), vp.size())
        if self.stack.currentIndex() == 1:
            vp = self.msg_scroll.viewport()
            return QRect(vp.mapTo(self, QPoint(0, 0)), vp.size())
        return QRect(self.list_widget.mapTo(self, QPoint(0, 0)), self.list_widget.size())

    def on_tab_deactivated(self) -> None:
        self._flush_draft()

    def on_tab_activated(self) -> None:
        if self.stack.currentIndex() == 1 and self.current_email_id:
            email = self._email_by_id(self.current_email_id)
            if email and email["kind"] in ("credentials", "otp"):
                self._clear_layout(self.extra_layout)
                self._copy_buttons = {}
                if email["kind"] == "credentials":
                    self._render_credentials()
                else:
                    self._render_otp(email)
        self._schedule_aoi_emit()

    def _clear_layout(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                continue
            child = item.layout()
            if child is not None:
                self._clear_layout(child)

MockEmailScreen = GmailScreen

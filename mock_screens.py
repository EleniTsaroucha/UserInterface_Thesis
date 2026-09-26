from __future__ import annotations

import random
from pathlib import Path

from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QPen
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QLineEdit, QPushButton,
    QApplication, QStackedWidget, QComboBox, QTextEdit, QDialog, QListWidget,
    QListWidgetItem, QGridLayout, QGraphicsDropShadowEffect, QScrollArea,
)

from session_config import SensitiveContent

FONT_FAMILY = "Segoe UI"


BANK_DARK = "#0d3b2e"       
BANK_ACCENT = "#15594a"     
BANK_YELLOW = "#ffd200"    
BANK_CREAM = "#faf9f6"
HEALTH_ACCENT = "#1967d2"
GOV_ACCENT = "#1a3c6e"
EMAIL_ACCENT = "#f9ab00"

_INPUT_STYLE = """
QLineEdit, QTextEdit, QComboBox {
    border: 1px solid #dadce0;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 13px;
    font-family: 'Segoe UI';
    background: white;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1.5px solid #1a73e8;
}
"""


def _darken(hex_color: str, factor: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r, g, b = int(r * factor), int(g * factor), int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def _accent_button_style(accent_hex: str) -> str:
    hover = _darken(accent_hex, 0.88)
    pressed = _darken(accent_hex, 0.74)
    return (
        f"QPushButton {{ background:{accent_hex}; color:white; border:none; "
        f"border-radius:8px; font-size:14px; font-weight:600; font-family:'Segoe UI'; }} "
        f"QPushButton:hover {{ background:{hover}; }} "
        f"QPushButton:pressed {{ background:{pressed}; padding-top:2px; }} "
        f"QPushButton:disabled {{ background:#dadce0; color:#9aa0a6; }}"
    )


def apply_card_shadow(widget: QWidget, blur: int = 24, y_offset: int = 6, alpha: int = 45) -> None:
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y_offset)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)


def make_light_navbar(logo_text: str, title: str, accent_hex: str) -> QWidget:
    bar = QWidget()
    bar.setFixedHeight(54)
    bar.setStyleSheet(f"background:white; border-bottom:3px solid {accent_hex};")
    layout = QHBoxLayout(bar)
    layout.setContentsMargins(18, 8, 18, 8)
    layout.setSpacing(10)

    logo = QLabel(logo_text)
    logo.setFixedSize(34, 34)
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    logo.setStyleSheet(
        f"background:{accent_hex}; color:white; border-radius:9px; "
        f"font-weight:bold; font-size:12px; font-family:'Segoe UI';"
    )
    layout.addWidget(logo)

    title_lbl = QLabel(title)
    title_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.DemiBold))
    title_lbl.setStyleSheet("color:#202124;")
    layout.addWidget(title_lbl)
    layout.addStretch()

    badge = QLabel("DEMO / TEST")
    badge.setStyleSheet(
        "background:#fef7e0; color:#a15c00; border:1px solid #f2d68a; "
        "border-radius:10px; padding:3px 12px; font-size:10px; font-weight:bold;"
    )
    layout.addWidget(badge)
    return bar


def make_solid_navbar(logo_text: str, title: str, accent_hex: str, subtitle: str = "") -> QWidget:
    bar = QWidget()
    bar.setFixedHeight(58)
    bar.setStyleSheet(f"background:{accent_hex};")
    layout = QHBoxLayout(bar)
    layout.setContentsMargins(20, 8, 20, 8)
    layout.setSpacing(12)

    logo = QLabel(logo_text)
    logo.setFixedSize(36, 36)
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    logo.setStyleSheet(
        "background:rgba(255,255,255,0.22); color:white; border-radius:9px; "
        "font-weight:bold; font-size:13px; font-family:'Segoe UI';"
    )
    layout.addWidget(logo)

    title_box = QVBoxLayout()
    title_box.setSpacing(0)
    title_lbl = QLabel(title)
    title_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
    title_lbl.setStyleSheet("color:white;")
    title_box.addWidget(title_lbl)
    if subtitle:
        sub_lbl = QLabel(subtitle)
        sub_lbl.setFont(QFont(FONT_FAMILY, 9))
        sub_lbl.setStyleSheet("color:rgba(255,255,255,0.75);")
        title_box.addWidget(sub_lbl)
    layout.addLayout(title_box)
    layout.addStretch()

    badge = QLabel("DEMO / TEST")
    badge.setStyleSheet(
        "background:rgba(255,255,255,0.92); color:#3c2f00; border-radius:10px; "
        "padding:3px 12px; font-size:10px; font-weight:bold;"
    )
    layout.addWidget(badge)
    return bar


def make_bank_header(subtitle: str = "") -> QWidget:
    bar = QWidget()
    bar.setFixedHeight(66)
    bar.setStyleSheet(f"background:{BANK_CREAM}; border-bottom:3px solid {BANK_YELLOW};")
    layout = QHBoxLayout(bar)
    layout.setContentsMargins(34, 0, 34, 0)
    layout.setSpacing(16)

    logo = QLabel("////  SecureBank")
    logo.setFont(QFont(FONT_FAMILY, 17, QFont.Weight.Bold))
    logo.setStyleSheet(f"color:{BANK_DARK}; background:transparent;")
    layout.addWidget(logo)

    if subtitle:
        sep = QLabel("|")
        sep.setStyleSheet("color:#b9bec4; background:transparent;")
        layout.addWidget(sep)
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet(f"color:{BANK_DARK}; font-size:14px; background:transparent;")
        layout.addWidget(sub_lbl)

    layout.addStretch()
    for label in ("Επικοινωνία", "Χρήσιμα Εργαλεία"):
        item = QLabel(label)
        item.setStyleSheet(f"color:{BANK_DARK}; font-size:13px; background:transparent;")
        layout.addWidget(item)
    logout = QLabel("Αποσύνδεση")
    logout.setStyleSheet(
        f"color:{BANK_DARK}; font-size:13px; font-weight:600; background:transparent; "
        f"border:1.5px solid {BANK_DARK}; border-radius:15px; padding:5px 14px;"
    )
    layout.addWidget(logout)
    badge = QLabel("DEMO / TEST")
    badge.setStyleSheet(
        "background:#fff3c4; color:#4a3a00; border:1px solid #e0c65a; "
        "border-radius:10px; padding:3px 12px; font-size:10px; font-weight:bold;"
    )
    layout.addWidget(badge)
    return bar


def breadcrumb(path: list[str]) -> QLabel:
    lbl = QLabel("  ›  ".join(path))
    lbl.setStyleSheet("color:#5f6368; font-size:11px; padding:10px 0 0 0;")
    return lbl


def sso_banner(service_name: str, service_icon: str, accent_hex: str, light_bg: str) -> QWidget:
    box = QWidget()
    box.setFixedWidth(340)
    box.setStyleSheet(f"background:{light_bg}; border:1px solid {accent_hex}; border-radius:8px;")
    layout = QHBoxLayout(box)
    layout.setContentsMargins(12, 8, 12, 8)
    layout.setSpacing(8)
    icon = QLabel(service_icon)
    icon.setFont(QFont("Sans Serif", 16))
    layout.addWidget(icon)
    text = QLabel(f"Θα συνδεθείτε στην υπηρεσία «{service_name}» μέσω Taxisnet")
    text.setWordWrap(True)
    text.setStyleSheet(f"color:{accent_hex}; font-size:11px; font-weight:600;")
    layout.addWidget(text, stretch=1)
    return box


def _apply_avatar_style(lbl: QLabel, initial: str, accent_hex: str, size: int) -> None:
    lbl.setFixedSize(size, size)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setText(initial.upper())
    lbl.setStyleSheet(
        f"background:{accent_hex}; color:white; border-radius:{size // 2}px; "
        f"font-weight:bold; font-size:{int(size * 0.42)}px; font-family:'Segoe UI';"
    )


def circular_avatar(initial: str, accent_hex: str, size: int = 40) -> QLabel:
    lbl = QLabel()
    _apply_avatar_style(lbl, initial, accent_hex, size)
    return lbl


_SENDER_COLORS = {
    "εγώ": "#f9ab00",
    "Ενημερωτικά Demo": "#7c4dff",
    "Ημερολόγιο": "#34a853",
    "GovAtHome": GOV_ACCENT,
}


def _sender_color(sender_name: str) -> str:
    return _SENDER_COLORS.get(sender_name, "#5f6368")


def sidebar_field(label_text: str, value_text: str, color: str = "#202124") -> tuple[QWidget, QLabel]:
    box = QWidget()
    v = QVBoxLayout(box)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(2)
    lbl = QLabel(label_text)
    lbl.setStyleSheet("color:#5f6368; font-size:11px;")
    val = QLabel(value_text)
    val.setStyleSheet(f"color:{color}; font-weight:600; font-size:13px;")
    val.setWordWrap(True)
    v.addWidget(lbl)
    v.addWidget(val)
    return box, val


def _format_iban_display(raw: str) -> str:
    if not raw:
        return raw
    digits = raw[2:] if raw.startswith("GR") else raw
    groups = [digits[i:i + 4] for i in range(0, len(digits), 4)]
    return "GR-" + "-".join(groups)


def emit_measured(screen: QWidget, signal: pyqtSignal, field_id: str,
                   field_widget: QWidget, value: str) -> None:
    def _do_emit() -> None:
        if not field_widget.isVisible():
            return
        top_left = field_widget.mapTo(screen, QPoint(0, 0))
        bbox = QRect(top_left, field_widget.size())
        signal.emit(field_id, bbox, value)
    QTimer.singleShot(0, _do_emit)


_INPUT_ERROR_SUFFIX = "QLineEdit { border: 1.5px solid #d93025; }"


def show_field_error(fields: list[QLineEdit], error_label: QLabel,
                     base_style: str | None = None) -> None:
    """base_style: το κανονικό stylesheet των πεδίων, ώστε η επαναφορά μετά το
    σφάλμα να μην τα γυρίζει σε ξένη εμφάνιση. Χωρίς αυτό, οθόνες με δικό τους
    στυλ (π.χ. η σελίδα ΓΓΠΣ) θα άλλαζαν όψη μετά από αποτυχημένη σύνδεση."""
    style = _INPUT_STYLE if base_style is None else base_style
    error_label.setVisible(True)
    for f in fields:
        f.setStyleSheet(style + _INPUT_ERROR_SUFFIX)
    QTimer.singleShot(1600, lambda: _clear_field_error(fields, error_label, style))


def _clear_field_error(fields: list[QLineEdit], error_label: QLabel,
                       base_style: str | None = None) -> None:
    error_label.setVisible(False)
    for f in fields:
        f.setStyleSheet(_INPUT_STYLE if base_style is None else base_style)


def error_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("color:#d93025; font-size:11.5px; font-weight:600;")
    lbl.setVisible(False)
    return lbl


def wrap_scrollable(navbar: QWidget, content: QWidget, bg_hex: str) -> QWidget:
    page = QWidget()
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)
    outer.addWidget(navbar)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.Shape.NoFrame)
    scroll.setStyleSheet(f"QScrollArea {{ background:{bg_hex}; border:none; }}")
    content.setStyleSheet(f"background:{bg_hex};")
    scroll.setWidget(content)
    outer.addWidget(scroll, stretch=1)
    return page


# ============================================================================
# gov.gr / ΓΓΠΣ — κοινόχρηστα δομικά στοιχεία
# ============================================================================

GOVGR_NAVY      = "#0b2a63"      # μπάρα κεφαλίδας υπηρεσίας gov.gr
GOVGR_CTA       = "#1387e8"      # κουμπί «Είσοδος με TaxisNet»
GOVGR_CTA_HOVER = "#0f76cf"
GGPS_BAR        = "#5a7fa6"      # μπάρα «Αυθεντικοποίηση Χρήστη»
GGPS_BTN        = "#4a86b8"
GGPS_BTN_HOVER  = "#3d75a3"
GGPS_LINK       = "#1c5fa8"
GGPS_TEXT       = "#20477e"
GOV_PAGE_BG     = "#e9eaec"
GOV_CARD_BORDER = "#c8ccd2"

_ASSETS_DIR = Path(__file__).with_name("assets")
_LOGO_FILES = {
    "govgr": "govgr.png",
    "idika": "idika.png",
    "ggps": "ggps.png",
    "hellenic": "hellenic_republic.png",
}

_GGPS_INPUT_STYLE = """
QLineEdit {
    background: white;
    border: 1px solid #b4b9c0;
    border-radius: 3px;
    padding: 0 9px;
    font-size: 14px;
    font-family: 'Segoe UI';
    color: #1a1a1a;
}
QLineEdit:focus { border: 1px solid #5a9bd8; }
"""


def _logo_placeholder(text: str, height: int, fg: str) -> QPixmap:
    """Υποκατάστατο όταν δεν υπάρχει αρχείο λογοτύπου, ώστε η οθόνη να μη
    σπάει. Αντικαθίσταται αυτόματα μόλις προστεθεί το assets/."""
    font = QFont(FONT_FAMILY, max(8, int(height * 0.40)), QFont.Weight.Bold)
    probe = QLabel()
    probe.setFont(font)
    pm = QPixmap(probe.fontMetrics().horizontalAdvance(text) + 16, height)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setFont(font)
    painter.setPen(QPen(QColor(fg)))
    painter.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, text)
    painter.end()
    return pm


def gov_logo(key: str, height: int, fallback_text: str, fallback_fg: str) -> QLabel:
    lbl = QLabel()
    lbl.setStyleSheet("background:transparent; border:none;")
    path = _ASSETS_DIR / _LOGO_FILES[key]
    if path.exists():
        pm = QPixmap(str(path))
        if not pm.isNull():
            lbl.setPixmap(pm.scaledToHeight(
                height, Qt.TransformationMode.SmoothTransformation))
            return lbl
    lbl.setPixmap(_logo_placeholder(fallback_text, height, fallback_fg))
    return lbl


def _gov_centered(card: QWidget) -> QWidget:
    page = QWidget()
    page.setStyleSheet(f"background:{GOV_PAGE_BG};")
    outer = QVBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.addStretch(2)
    row = QHBoxLayout()
    row.addStretch()
    row.addWidget(card)
    row.addStretch()
    outer.addLayout(row)
    outer.addStretch(3)
    return page


def build_govgr_portal_page(service_title: str, heading: str, intro: str,
                            authority: str, on_login,
                            logo_key: str = "idika", logo_text: str = "ΗΔΙΚΑ",
                            logo_color: str = "#4db8e8") -> QWidget:
    """Η αρχική σελίδα μιας υπηρεσίας gov.gr: κεφαλίδα σε μία σειρά
    (gov.gr | τίτλος | φορέας), σώμα με περιγραφή και το κουμπί TaxisNet."""
    card = QFrame()
    card.setFixedWidth(680)
    card.setStyleSheet(
        f"QFrame {{ background:white; border:1px solid {GOV_CARD_BORDER}; }}")
    apply_card_shadow(card, blur=22, y_offset=2, alpha=38)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    header = QWidget()
    header.setFixedHeight(96)
    header.setStyleSheet(f"background:{GOVGR_NAVY}; border:none;")
    hl = QHBoxLayout(header)
    hl.setContentsMargins(26, 0, 26, 0)
    hl.setSpacing(20)
    hl.addWidget(gov_logo("govgr", 30, "govgr", "#ffffff"),
                 alignment=Qt.AlignmentFlag.AlignVCenter)
    divider = QFrame()
    divider.setFixedSize(1, 44)
    divider.setStyleSheet("background:#3a5a92; border:none;")
    hl.addWidget(divider, alignment=Qt.AlignmentFlag.AlignVCenter)
    title = QLabel(service_title)
    title.setStyleSheet(
        f"color:white; font-family:'{FONT_FAMILY}'; font-size:17px; "
        f"font-weight:600; background:transparent; border:none;")
    hl.addWidget(title, alignment=Qt.AlignmentFlag.AlignVCenter)
    hl.addStretch()
    hl.addWidget(gov_logo(logo_key, 34, logo_text, logo_color),
                 alignment=Qt.AlignmentFlag.AlignVCenter)
    layout.addWidget(header)

    body = QWidget()
    body.setStyleSheet("background:white; border:none;")
    bl = QVBoxLayout(body)
    bl.setContentsMargins(56, 34, 56, 30)
    bl.setSpacing(0)

    head_lbl = QLabel(heading)
    head_lbl.setStyleSheet(
        f"color:#1a1a1a; font-family:'{FONT_FAMILY}'; font-size:19px; "
        f"font-weight:600; background:transparent; border:none;")
    bl.addWidget(head_lbl)
    bl.addSpacing(10)

    intro_lbl = QLabel(intro)
    intro_lbl.setWordWrap(True)
    intro_lbl.setStyleSheet(
        f"color:#444a52; font-family:'{FONT_FAMILY}'; font-size:13.5px; "
        f"background:transparent; border:none;")
    bl.addWidget(intro_lbl)
    bl.addSpacing(24)

    btn = QPushButton("Είσοδος με TaxisNet")
    btn.setFixedHeight(48)
    btn.setMinimumWidth(260)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(
        f"QPushButton {{ background:{GOVGR_CTA}; color:white; border:none; "
        f"border-radius:6px; font-family:'{FONT_FAMILY}'; font-size:15px; "
        f"font-weight:600; padding:0 30px; }}"
        f"QPushButton:hover {{ background:{GOVGR_CTA_HOVER}; }}"
        f"QPushButton:pressed {{ background:#0c67b4; }}"
    )
    btn.clicked.connect(on_login)
    btn_row = QHBoxLayout()
    btn_row.setContentsMargins(0, 0, 0, 0)
    btn_row.addWidget(btn)
    btn_row.addStretch()
    bl.addLayout(btn_row)
    bl.addSpacing(26)

    rule = QFrame()
    rule.setFixedHeight(1)
    rule.setStyleSheet("background:#e2e5e9; border:none;")
    bl.addWidget(rule)
    bl.addSpacing(12)

    footer = QLabel(f"Αρμόδιος φορέας: {authority}   ·   DEMO / TEST")
    footer.setStyleSheet(
        f"color:#6b7178; font-family:'{FONT_FAMILY}'; font-size:11.5px; "
        f"background:transparent; border:none;")
    bl.addWidget(footer)
    layout.addWidget(body)

    return _gov_centered(card)


def build_taxisnet_auth_page(user_field: QLineEdit, pass_field: QLineEdit,
                             login_error: QLabel, on_submit, on_language) -> QWidget:
    """Η σελίδα «Αυθεντικοποίηση Χρήστη» της ΓΓΠΣ. Τα πεδία δημιουργούνται από
    τον καλούντα, ώστε να διατηρούνται τα ονόματα ιδιοτήτων και η καταγραφή."""
    for field in (user_field, pass_field):
        field.setFixedHeight(36)
        field.setPlaceholderText("")
        field.setStyleSheet(_GGPS_INPUT_STYLE)
        field.returnPressed.connect(on_submit)

    card = QFrame()
    card.setFixedWidth(700)
    card.setStyleSheet(
        f"QFrame {{ background:white; border:1px solid {GOV_CARD_BORDER}; }}")
    apply_card_shadow(card, blur=22, y_offset=2, alpha=38)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # --- λωρίδα λογοτύπων
    strip = QWidget()
    strip.setFixedHeight(86)
    strip.setStyleSheet("background:white; border:none;")
    sl = QHBoxLayout(strip)
    sl.setContentsMargins(24, 0, 24, 0)
    left = QHBoxLayout()
    left.setSpacing(12)
    left.addWidget(gov_logo("ggps", 52, "ΓΓΠΣ", "#d1642a"),
                   alignment=Qt.AlignmentFlag.AlignVCenter)
    ggps_text = QLabel("Γενική Γραμματεία\nΠληροφοριακών Συστημάτων &\n"
                        "Ψηφιακής Διακυβέρνησης")
    ggps_text.setStyleSheet(
        f"color:{GGPS_TEXT}; font-family:'{FONT_FAMILY}'; font-size:11.5px; "
        f"font-weight:600; background:transparent; border:none;")
    left.addWidget(ggps_text, alignment=Qt.AlignmentFlag.AlignVCenter)
    sl.addLayout(left)
    sl.addStretch()
    right = QHBoxLayout()
    right.setSpacing(12)
    right.addWidget(gov_logo("hellenic", 52, "◉", GGPS_TEXT),
                    alignment=Qt.AlignmentFlag.AlignVCenter)
    hel_text = QLabel("ΕΛΛΗΝΙΚΗ ΔΗΜΟΚΡΑΤΙΑ\nΥπουργείο Ψηφιακής\nΔιακυβέρνησης")
    hel_text.setStyleSheet(
        f"color:{GGPS_TEXT}; font-family:'{FONT_FAMILY}'; font-size:11.5px; "
        f"font-weight:600; background:transparent; border:none;")
    right.addWidget(hel_text, alignment=Qt.AlignmentFlag.AlignVCenter)
    sl.addLayout(right)
    layout.addWidget(strip)

    # --- μπάρα τίτλου
    bar = QWidget()
    bar.setFixedHeight(60)
    bar.setStyleSheet(f"background:{GGPS_BAR}; border:none;")
    bl = QHBoxLayout(bar)
    bl.setContentsMargins(18, 0, 18, 0)
    bl.addStretch()
    bar_title = QLabel("Αυθεντικοποίηση Χρήστη")
    bar_title.setStyleSheet(
        f"color:white; font-family:'{FONT_FAMILY}'; font-size:21px; "
        f"background:transparent; border:none;")
    bl.addWidget(bar_title)
    bl.addStretch()
    english = QPushButton("English")
    english.setFixedSize(88, 34)
    english.setCursor(Qt.CursorShape.PointingHandCursor)
    english.setStyleSheet(
        f"QPushButton {{ background:#5b93c4; color:white; border:none; "
        f"border-radius:4px; font-family:'{FONT_FAMILY}'; font-size:13px; }}"
        f"QPushButton:hover {{ background:#4d84b5; }}"
    )
    english.clicked.connect(on_language)
    bl.addWidget(english, alignment=Qt.AlignmentFlag.AlignVCenter)
    layout.addWidget(bar)

    # --- φόρμα
    body = QWidget()
    body.setStyleSheet("background:white; border:none;")
    fl = QVBoxLayout(body)
    fl.setContentsMargins(40, 26, 40, 26)
    fl.setSpacing(0)

    heading = QLabel("Σύνδεση")
    heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
    heading.setStyleSheet(
        f"color:#1a1a1a; font-family:'{FONT_FAMILY}'; font-size:29px; "
        f"font-weight:400; background:transparent; border:none;")
    fl.addWidget(heading)
    fl.addSpacing(8)

    subtitle = QLabel("Παρακαλώ εισάγετε τους κωδικούς σας στο <b>TaxisNet</b> "
                       "για να συνδεθείτε.")
    subtitle.setTextFormat(Qt.TextFormat.RichText)
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    subtitle.setStyleSheet(
        f"color:#444a52; font-family:'{FONT_FAMILY}'; font-size:13.5px; "
        f"background:transparent; border:none;")
    fl.addWidget(subtitle)
    fl.addSpacing(18)

    rule = QFrame()
    rule.setFixedHeight(1)
    rule.setStyleSheet("background:#dfe2e6; border:none;")
    fl.addWidget(rule)
    fl.addSpacing(20)

    inner = QVBoxLayout()
    inner.setContentsMargins(120, 0, 120, 0)
    inner.setSpacing(0)
    for label_text, field in (("Χρήστης:", user_field), ("Κωδικός:", pass_field)):
        lbl = QLabel(label_text)
        lbl.setStyleSheet(
            f"color:#1a1a1a; font-family:'{FONT_FAMILY}'; font-size:13.5px; "
            f"font-weight:600; background:transparent; border:none;")
        inner.addWidget(lbl)
        inner.addSpacing(6)
        inner.addWidget(field)
        inner.addSpacing(14)

    inner.addWidget(login_error)
    inner.addSpacing(8)

    submit = QPushButton("Σύνδεση")
    submit.setFixedHeight(40)
    submit.setCursor(Qt.CursorShape.PointingHandCursor)
    submit.setStyleSheet(
        f"QPushButton {{ background:{GGPS_BTN}; color:white; border:none; "
        f"border-radius:4px; font-family:'{FONT_FAMILY}'; font-size:15px; }}"
        f"QPushButton:hover {{ background:{GGPS_BTN_HOVER}; }}"
        f"QPushButton:pressed {{ background:#356690; }}"
    )
    submit.clicked.connect(on_submit)
    inner.addWidget(submit)
    fl.addLayout(inner)

    fl.addSpacing(24)
    link = QLabel("Κέντρο Διαλειτουργικότητας (ΚΕ.Δ.) Υπουργείου "
                   "Ψηφιακής Διακυβέρνησης")
    link.setAlignment(Qt.AlignmentFlag.AlignCenter)
    link.setStyleSheet(
        f"color:{GGPS_LINK}; font-family:'{FONT_FAMILY}'; font-size:13px; "
        f"background:transparent; border:none;")
    fl.addWidget(link)
    layout.addWidget(body)

    return _gov_centered(card)


class MockEmailScreen(QWidget):

    field_rendered = pyqtSignal(str, QRect, str)
    action_performed = pyqtSignal(str)

    _LIST_STYLE = """
        QListWidget {
            background: #f8f9fa;
            border: none;
            border-right: 1px solid #dadce0;
            outline: none;
        }
        QListWidget::item {
            border-bottom: 1px solid #e8eaed;
        }
        QListWidget::item:selected {
            background: #e8f0fe;
            border-left: 3px solid #1a73e8;
        }
        QListWidget::item:hover:!selected {
            background: #f1f3f4;
        }
    """

    def __init__(self, content: SensitiveContent, parent=None):
        super().__init__(parent)
        self.content = content
        self.emails: list[dict] = self._build_initial_emails()
        self.current_index = 1  # ξεκινά επιλεγμένο το email με τους κωδικούς
        self._build_ui()
        self._refresh_list()
        self._render_current_email()

    def _build_initial_emails(self) -> list[dict]:
        return [
            {"kind": "generic", "sender_name": "Ενημερωτικά Demo", "sender_email": "newsletter@demo.test",
             "subject": "Ενημερωτικό δελτίο", "unread": False,
             "body": "Γενικό ενημερωτικό περιεχόμενο, καμία ευαίσθητη πληροφορία.",
             "preview": "Γενικό ενημερωτικό περιεχόμενο, καμία ευαίσθητη πληροφορία.",
             "time": "9:02"},
            {"kind": "credentials", "sender_name": "εγώ", "sender_email": "me@demo.test",
             "subject": "Οι κωδικοί μου", "unread": False,
             "preview": "Bank username, password, IBAN, ΑΦΜ, ΑΜΚΑ, Taxisnet…",
             "time": "Χθες"},
            {"kind": "generic", "sender_name": "Ημερολόγιο", "sender_email": "calendar@demo.test",
             "subject": "Υπενθύμιση συνάντησης", "unread": False,
             "body": "Η εβδομαδιαία συνάντηση ομάδας είναι αύριο στις 10:00.",
             "preview": "Η εβδομαδιαία συνάντηση ομάδας είναι αύριο στις 10:00.",
             "time": "2 μέρες πριν"},
        ]

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        navbar = make_light_navbar("DM", "Demo Mail", EMAIL_ACCENT)
        outer.addWidget(navbar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Αριστερή λίστα ("Εισερχόμενα")
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 12, 0, 0)
        left_layout.setSpacing(4)
        left_panel.setFixedWidth(230)
        left_panel.setStyleSheet("background:#f8f9fa; border-right:1px solid #dadce0;")

        compose_btn = QPushButton("✎  Σύνταξη")
        compose_btn.setFixedHeight(38)
        compose_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        compose_btn.setStyleSheet(
            "QPushButton { background:white; color:#3c4043; border:1px solid #dadce0; "
            "border-radius:18px; font-size:12px; font-weight:600; text-align:left; padding-left:16px; } "
            "QPushButton:hover { background:#f1f3f4; border-color:#c6c9cc; } "
            "QPushButton:pressed { background:#e8eaed; }"
        )
        compose_row = QHBoxLayout()
        compose_row.setContentsMargins(14, 0, 14, 0)
        compose_row.addWidget(compose_btn)
        left_layout.addLayout(compose_row)
        left_layout.addSpacing(10)

        self.inbox_label = QLabel()
        self.inbox_label.setStyleSheet(
            "background:#e8f0fe; color:#1a73e8; font-weight:600; font-size:12px; "
            "padding:9px 18px; border-left:3px solid #1a73e8;"
        )
        left_layout.addWidget(self.inbox_label)

        for folder_name in ("Απεσταλμένα", "Πρόχειρα", "Κάδος"):
            folder_lbl = QLabel(f"    {folder_name}")
            folder_lbl.setStyleSheet("color:#5f6368; font-size:12px; padding:9px 18px;")
            left_layout.addWidget(folder_lbl)

        left_layout.addSpacing(6)
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color:#dadce0; margin:0 14px;")
        left_layout.addWidget(divider)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(self._LIST_STYLE)
        self.list_widget.currentRowChanged.connect(self._on_list_selection)
        left_layout.addWidget(self.list_widget, stretch=1)

        body.addWidget(left_panel)

        # Δεξιά: περιεχόμενο επιλεγμένου email
        right_panel = QWidget()
        right_panel.setStyleSheet("background:#fffdf5;")
        right_outer = QVBoxLayout(right_panel)
        right_outer.setContentsMargins(30, 20, 30, 20)

        header_row = QHBoxLayout()
        self.header_avatar = QLabel()
        header_row.addWidget(self.header_avatar)
        header_text_box = QVBoxLayout()
        header_text_box.setSpacing(2)
        self.subject_label = QLabel("")
        self.subject_label.setFont(QFont("Sans Serif", 15, QFont.Weight.Bold))
        self.sender_label = QLabel("")
        self.sender_label.setStyleSheet("color:#5f6368; font-size:12px;")
        header_text_box.addWidget(self.subject_label)
        header_text_box.addWidget(self.sender_label)
        header_row.addLayout(header_text_box)
        header_row.addStretch()
        right_outer.addLayout(header_row)

        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 16, 0, 0)
        right_outer.addWidget(self.content_area)
        right_outer.addStretch()

        body.addWidget(right_panel, stretch=1)
        outer.addLayout(body)

    def _update_inbox_label(self) -> None:
        unread_count = sum(1 for e in self.emails if e.get("unread"))
        text = f"📥  Εισερχόμενα  ({unread_count})" if unread_count else "📥  Εισερχόμενα"
        self.inbox_label.setText(text)

    def _build_email_row_widget(self, email: dict) -> QWidget:
        unread = email.get("unread", False)
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 9, 12, 9)
        layout.setSpacing(9)

        initial = email["sender_name"][0] if email["sender_name"] else "?"
        avatar = circular_avatar(initial, _sender_color(email["sender_name"]), size=32)
        layout.addWidget(avatar)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)

        top_row = QHBoxLayout()
        top_row.setSpacing(4)
        sender_lbl = QLabel(email["sender_name"])
        sender_lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold if unread else QFont.Weight.DemiBold))
        sender_lbl.setStyleSheet("color:#202124;" if unread else "color:#3c4043;")
        top_row.addWidget(sender_lbl, stretch=1)
        time_lbl = QLabel(email.get("time", ""))
        time_lbl.setStyleSheet("color:#9aa0a6; font-size:10px;")
        top_row.addWidget(time_lbl)
        if unread:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{EMAIL_ACCENT}; font-size:9px;")
            top_row.addWidget(dot)
        text_box.addLayout(top_row)

        subject_lbl = QLabel(email["subject"])
        subject_lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold if unread else QFont.Weight.Normal))
        subject_lbl.setStyleSheet("color:#202124;" if unread else "color:#5f6368;")
        fm_subject = subject_lbl.fontMetrics()
        subject_lbl.setText(fm_subject.elidedText(email["subject"], Qt.TextElideMode.ElideRight, 168))
        text_box.addWidget(subject_lbl)

        preview_lbl = QLabel()
        preview_lbl.setStyleSheet("color:#9aa0a6; font-size:10px;")
        fm_preview = preview_lbl.fontMetrics()
        preview_lbl.setText(fm_preview.elidedText(email.get("preview", ""), Qt.TextElideMode.ElideRight, 168))
        text_box.addWidget(preview_lbl)

        layout.addLayout(text_box, stretch=1)
        return row

    def _refresh_list(self) -> None:
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for email in self.emails:
            item = QListWidgetItem()
            item.setSizeHint(QSize(200, 72))
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, self._build_email_row_widget(email))
        self.list_widget.setCurrentRow(self.current_index)
        self.list_widget.blockSignals(False)
        self._update_inbox_label()

    def _on_list_selection(self, row: int) -> None:
        if row < 0:
            return
        self.current_index = row
        email = self.emails[row]
        email["unread"] = False
        self._refresh_list()
        self._render_current_email()
        if email["kind"] == "otp":
            self.action_performed.emit("otp_email_opened")

    def _clear_content_area(self) -> None:
        self._clear_layout_recursive(self.content_layout)

    def _clear_layout_recursive(self, layout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
                continue
            child_layout = item.layout()
            if child_layout is not None:
                self._clear_layout_recursive(child_layout)

    _COPY_STYLE = (
        "QPushButton { background:#e8f0fe; color:#1a73e8; border:1px solid #aecbfa; "
        "border-radius:6px; padding:4px 6px; font-size:13px; font-weight:600; } "
        "QPushButton:hover { background:#d2e3fc; } "
        "QPushButton:pressed { background:#aecbfa; }"
    )
    _COPIED_STYLE = (
        "QPushButton { background:#34a853; color:white; border:1px solid #1e7e34; "
        "border-radius:6px; padding:4px 6px; font-size:14px; font-weight:bold; }"
    )

    def _render_current_email(self) -> None:
        self._clear_content_area()
        self._copy_buttons: dict[str, tuple[QPushButton, str]] = {}
        email = self.emails[self.current_index]

        self.subject_label.setText(email["subject"])
        _apply_avatar_style(self.header_avatar, email["sender_name"][0] if email["sender_name"] else "?",
                             _sender_color(email["sender_name"]), 38)
        self.sender_label.setText(
            f"{email['sender_name']} <{email['sender_email']}>   ·   Προς: εγώ   ·   {email.get('time', '')}"
        )

        if email["kind"] == "generic":
            body_lbl = QLabel(email["body"])
            body_lbl.setWordWrap(True)
            self.content_layout.addWidget(body_lbl)

        elif email["kind"] == "credentials":
            rows = [
                ("email_bank_username", "Bank username:", self.content.bank_username),
                ("email_bank_password", "Bank password:", self.content.bank_password),
                ("email_iban",           "IBAN:", _format_iban_display(self.content.iban)),
                ("email_afm",             "ΑΦΜ:", self.content.afm),
                ("email_amka",            "ΑΜΚΑ:", self.content.amka),
                ("email_taxis_username",  "Taxisnet username:", self.content.taxis_username),
                ("email_taxis_password",  "Taxisnet password:", self.content.taxis_password),
            ]
            for field_id, label_text, display_value in rows:
                row = QHBoxLayout()
                lbl = QLabel(label_text)
                lbl.setFixedWidth(150)
                lbl.setStyleSheet("color:#5f6368;")
                val = QLabel(display_value)
                val.setFont(QFont("Monospace", 12, QFont.Weight.Bold))
                val.setStyleSheet("color:#202124;")
                copy_btn = QPushButton("📋")
                copy_btn.setFixedWidth(44)  # αρκετό για το "✓" checkmark μετά την αντιγραφή
                copy_btn.setStyleSheet(self._COPY_STYLE)
                copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                copy_btn.clicked.connect(
                    lambda _, fid=field_id, v=display_value, btn=copy_btn: self._on_copy(fid, v, btn, "📋", "✓")
                )
                self._copy_buttons[field_id] = (copy_btn, "📋")
                row.addWidget(lbl)
                row.addWidget(val)
                row.addWidget(copy_btn)
                row.addStretch()
                self.content_layout.addLayout(row)
                emit_measured(self, self.field_rendered, field_id, val, display_value)

        elif email["kind"] == "otp":
            info = QLabel(f"Κωδικός επιβεβαίωσης για την υπογραφή του εγγράφου «{email['document']}»:")
            info.setWordWrap(True)
            self.content_layout.addWidget(info)

            row = QHBoxLayout()
            code_label = QLabel(email["code"])
            code_label.setFont(QFont("Monospace", 22, QFont.Weight.Bold))
            code_label.setStyleSheet("color:#1a73e8;")
            copy_btn = QPushButton("📋 Αντιγραφή")
            copy_btn.setMinimumWidth(140)  # αρκετό για το πλήρες "✓ Αντιγράφηκε"
            copy_btn.setStyleSheet(self._COPY_STYLE)
            copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            copy_btn.clicked.connect(
                lambda: self._on_copy("email_otp_code", email["code"], copy_btn, "📋 Αντιγραφή", "✓ Αντιγράφηκε")
            )
            self._copy_buttons["email_otp_code"] = (copy_btn, "📋 Αντιγραφή")
            row.addWidget(code_label)
            row.addWidget(copy_btn)
            row.addStretch()
            self.content_layout.addLayout(row)
            emit_measured(self, self.field_rendered, "email_otp_code", code_label, email["code"])

    def _on_copy(self, field_id: str, value: str, button: QPushButton,
                 original_text: str, copied_text: str = "✓") -> None:
        QApplication.clipboard().setText(value)
        self.action_performed.emit(f"{field_id}_copied")
        button.setText(copied_text)
        button.setStyleSheet(self._COPIED_STYLE)

    def reset_copy_indicators(self) -> None:
        for button, original_text in getattr(self, "_copy_buttons", {}).values():
            button.setText(original_text)
            button.setStyleSheet(self._COPY_STYLE)

    def add_otp_email(self, code: str, document_name: str) -> None:
        self.emails.insert(0, {
            "kind": "otp", "sender_name": "GovAtHome", "sender_email": "govathome@demo.test",
            "subject": "Κωδικός επιβεβαίωσης υπογραφής",
            "preview": f"Ο κωδικός επιβεβαίωσης για το έγγραφο «{document_name}» είναι έτοιμος.",
            "time": "Τώρα", "code": code, "document": document_name, "unread": True,
        })
        # το τρέχον επιλεγμένο email μετατοπίστηκε +1 θέση λόγω insert
        self.current_index += 1
        self._refresh_list()
        self.action_performed.emit("otp_email_received")

    def reset_emails(self) -> None:
        self.emails = self._build_initial_emails()
        self.current_index = 1
        self._refresh_list()
        self._render_current_email()

    def on_tab_activated(self) -> None:
        """Καλείται από το main.py όποτε η καρτέλα Demo Mail γίνεται ενεργή --
        ξαναδηλώνει (με πραγματική γεωμετρία) τα πεδία του τρέχοντος email."""
        self._render_current_email()


class PaymentAmountDialog(QDialog):

    def __init__(self, iban_display: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ποσό Πληρωμής")
        self.setModal(True)
        self.setFixedWidth(340)
        self._captured_bbox: QRect | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(8)
        layout.addWidget(QLabel(f"Πληρωμή προς:\n{iban_display}"))
        layout.addWidget(QLabel("Ποσό (EUR):"))
        self.amount_field = QLineEdit()
        self.amount_field.setPlaceholderText("π.χ. 45.00")
        self.amount_field.setFixedHeight(36)
        self.amount_field.setStyleSheet(_INPUT_STYLE)
        layout.addWidget(self.amount_field)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("Επιβεβαίωση")
        ok_btn.setFixedHeight(36)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setStyleSheet(_accent_button_style(BANK_ACCENT))
        cancel_btn = QPushButton("Άκυρο")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(
            "QPushButton { background:#f1f3f4; color:#3c4043; border:1px solid #dadce0; "
            "border-radius:8px; font-size:14px; } QPushButton:hover { background:#e8eaed; }"
        )
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        QTimer.singleShot(0, self._capture_bbox)

    def _capture_bbox(self) -> None:
        pos = self.amount_field.mapToGlobal(QPoint(0, 0))
        self._captured_bbox = QRect(pos, self.amount_field.size())

    def get_amount(self) -> str:
        return self.amount_field.text().strip()

    def get_amount_bbox_global(self) -> QRect | None:
        return self._captured_bbox


class ConfirmationDialog(QDialog):

    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Επιβεβαίωση")
        self.setModal(True)
        self.setFixedWidth(360)
        self._captured_bbox: QRect | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)
        self.message_label = QLabel("✅ " + message)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color:#137333; font-weight:500;")
        layout.addWidget(self.message_label)

        ok_btn = QPushButton("OK")
        ok_btn.setFixedHeight(36)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setStyleSheet(_accent_button_style("#137333"))
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

        QTimer.singleShot(0, self._capture_bbox)

    def _capture_bbox(self) -> None:
        pos = self.message_label.mapToGlobal(QPoint(0, 0))
        self._captured_bbox = QRect(pos, self.message_label.size())

    def get_bbox_global(self) -> QRect | None:
        return self._captured_bbox


class MockBankingScreen(QWidget):
    field_rendered = pyqtSignal(str, QRect, str)
    action_performed = pyqtSignal(str)

    _FAKE_TRANSACTIONS = [
        ("Καφετέρια Κέντρο", "-4,30 €", "Χθες", False),
        ("Μισθοδοσία", "+1.250,00 €", "3 ημέρες πριν", True),
        ("ΔΕΗ", "-62,40 €", "5 ημέρες πριν", False),
    ]

    def __init__(self, content: SensitiveContent, parent=None):
        super().__init__(parent)
        self.content = content
        self._build_ui()
        self._emit_current_fields()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_login_page())     # index 0
        self.stack.addWidget(self._build_dashboard_page())  # index 1
        outer.addWidget(self.stack)

    def _build_login_page(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        #  (1) λωρίδα προειδοποίησης ασφαλείας 
        self.security_banner = QWidget()
        self.security_banner.setStyleSheet(f"background:{BANK_YELLOW};")
        banner_layout = QHBoxLayout(self.security_banner)
        banner_layout.setContentsMargins(40, 12, 24, 12)
        banner_layout.setSpacing(20)
        warn_icon = QLabel("!")
        warn_icon.setFixedSize(44, 44)
        warn_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warn_icon.setStyleSheet(
            "border:2px solid #1a1a1a; border-radius:22px; color:#1a1a1a; "
            "font-size:20px; font-weight:bold; background:transparent;"
        )
        banner_layout.addWidget(warn_icon)
        warn_text = QLabel(
            "«ΠΡΟΣΟΧΗ. ΣΗΜΑΝΤΙΚΗ ΕΝΗΜΕΡΩΣΗ!! — Η τράπεζα δεν θα σας ζητήσει ποτέ και "
            "με κανέναν τρόπο τους κωδικούς σας και τα προσωπικά σας δεδομένα, μέσω "
            "email ή μέσω sms. Για περισσότερες πληροφορίες πατήστε εδώ.»"
        )
        warn_text.setWordWrap(True)
        warn_text.setStyleSheet(
            "color:#1a1a1a; font-size:14px; font-weight:600; background:transparent;")
        banner_layout.addWidget(warn_text, stretch=1)
        close_banner = QPushButton("✕")
        close_banner.setFixedSize(38, 38)
        close_banner.setCursor(Qt.CursorShape.PointingHandCursor)
        close_banner.setStyleSheet(
            "QPushButton { border:1px solid #1a1a1a; background:transparent; "
            "color:#1a1a1a; font-size:16px; } QPushButton:hover { background:#f0c400; }"
        )
        close_banner.clicked.connect(self._dismiss_security_banner)
        banner_layout.addWidget(close_banner)
        outer.addWidget(self.security_banner)

        #  (2) header 
        header = QWidget()
        header.setFixedHeight(72)
        header.setStyleSheet(f"background:{BANK_CREAM}; border-bottom:3px solid {BANK_YELLOW};")
        head_layout = QHBoxLayout(header)
        head_layout.setContentsMargins(40, 0, 40, 0)
        head_layout.setSpacing(30)
        logo = QLabel("////  SecureBank")
        logo.setFont(QFont(FONT_FAMILY, 19, QFont.Weight.Bold))
        logo.setStyleSheet(f"color:{BANK_DARK}; background:transparent;")
        head_layout.addWidget(logo)
        head_layout.addStretch()
        for icon, label in (("🏢", "Σύνδεση ως Επιχείρηση"), ("📞", "Επικοινωνία"),
                            ("🛠", "Χρήσιμα Εργαλεία"), ("🌐", "Ελληνικά")):
            item = QLabel(f"{icon}   {label}")
            item.setStyleSheet(
                f"color:{BANK_DARK}; font-size:13.5px; background:transparent;")
            head_layout.addWidget(item)
        outer.addWidget(header)

        #  (3)+(4) hero: προωθητικό πάνελ + κάρτα σύνδεσης 
        hero = QWidget()
        hero.setStyleSheet("background:qlineargradient(x1:0,y1:0,x2:1,y2:1, "
                            "stop:0 #eef3ee, stop:1 #dfe9e2);")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(70, 40, 60, 30)
        hero_layout.setSpacing(40)

        promo_col = QVBoxLayout()
        promo_col.addStretch()
        promo = QWidget()
        promo.setStyleSheet("background:white;")
        promo.setFixedWidth(430)
        promo_layout = QVBoxLayout(promo)
        promo_layout.setContentsMargins(44, 44, 44, 44)
        promo_layout.setSpacing(16)
        promo_title = QLabel("Το ανανεωμένο\nSecureBank app\nείναι εδώ")
        promo_title.setFont(QFont(FONT_FAMILY, 21))
        promo_title.setStyleSheet(f"color:{BANK_DARK}; background:transparent;")
        promo_layout.addWidget(promo_title)
        promo_sub = QLabel("Οι καθημερινές σου συναλλαγές\nακόμα πιο εύκολες")
        promo_sub.setStyleSheet("color:#3c4043; font-size:14px; background:transparent;")
        promo_layout.addWidget(promo_sub)
        promo_btn = QPushButton("Μάθετε Περισσότερα")
        promo_btn.setFixedSize(230, 46)
        promo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        promo_btn.setStyleSheet(
            f"QPushButton {{ background:{BANK_DARK}; color:white; border:none; "
            f"font-size:14px; font-weight:600; }} "
            f"QPushButton:hover {{ background:{_darken(BANK_DARK, 0.85)}; }}"
        )
        promo_layout.addWidget(promo_btn)
        promo_col.addWidget(promo)
        promo_col.addSpacing(22)

        dots = QHBoxLayout()
        dots.addStretch()
        for i in range(8):
            dot = QLabel("●")
            dot.setStyleSheet(
                f"color:{'#5f6368' if i == 5 else '#c4ccc6'}; font-size:11px; "
                f"background:transparent;"
            )
            dots.addWidget(dot)
        dots.addStretch()
        promo_col.addLayout(dots)
        promo_col.addStretch()
        hero_layout.addLayout(promo_col, stretch=1)

        login_col = QVBoxLayout()
        login_col.addStretch()

        tabs_row = QHBoxLayout()
        tabs_row.setSpacing(0)
        self.bank_tab_codes = QPushButton("Κωδικοί Εισόδου")
        self.bank_tab_qr = QPushButton("Είσοδος QR code")
        for btn in (self.bank_tab_codes, self.bank_tab_qr):
            btn.setFixedHeight(52)
            btn.setMinimumWidth(210)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bank_tab_codes.setStyleSheet(
            f"QPushButton {{ background:{BANK_DARK}; color:white; border:none; "
            f"font-size:14px; font-weight:600; }}"
        )
        self.bank_tab_qr.setStyleSheet(
            "QPushButton { background:#3f5f52; color:#dfe9e2; border:none; font-size:14px; } "
            "QPushButton:hover { background:#4a6b5d; }"
        )
        self.bank_tab_qr.clicked.connect(
            lambda: self.action_performed.emit("bank_qr_tab_clicked"))
        tabs_row.addWidget(self.bank_tab_codes)
        tabs_row.addWidget(self.bank_tab_qr)
        tabs_row.addStretch()
        login_col.addLayout(tabs_row)

        card = QWidget()
        card.setFixedWidth(480)
        card.setStyleSheet(f"background:{BANK_DARK};")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 26, 30, 30)
        card_layout.setSpacing(10)

        card_title = QLabel("Σύνδεση στο SecureBank e-banking")
        card_title.setStyleSheet("color:white; font-size:16px; background:transparent;")
        card_layout.addWidget(card_title)
        card_layout.addSpacing(8)

        self.bank_user_field = QLineEdit()
        self.bank_user_field.setPlaceholderText("Username")
        self.bank_pass_field = QLineEdit()
        self.bank_pass_field.setPlaceholderText("Password")
        # Ορατός κωδικός: σκόπιμο -- το αντικείμενο της μέτρησης είναι ακριβώς
        # η έκθεση του περιεχομένου της οθόνης σε τρίτο παρατηρητή. Ένα πεδίο
        # με τελίτσες δεν εκθέτει τίποτα και δεν θα είχε νόημα να μετρηθεί.
        self.bank_pass_field.setEchoMode(QLineEdit.EchoMode.Normal)
        for field, icon in ((self.bank_user_field, "👤"), (self.bank_pass_field, "🔒")):
            wrapper = QWidget()
            wrapper.setFixedHeight(52)
            wrapper.setStyleSheet("background:#e8e8e4;")
            wrap_layout = QHBoxLayout(wrapper)
            wrap_layout.setContentsMargins(14, 0, 14, 0)
            wrap_layout.setSpacing(10)
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size:15px; background:transparent;")
            wrap_layout.addWidget(icon_lbl)
            field.setStyleSheet(
                "QLineEdit { background:transparent; border:none; font-size:15px; "
                "color:#202124; }"
            )
            field.returnPressed.connect(self._attempt_login)
            wrap_layout.addWidget(field, stretch=1)
            info = QLabel("ⓘ")
            info.setStyleSheet("color:#5f6368; font-size:14px; background:transparent;")
            wrap_layout.addWidget(info)
            card_layout.addWidget(wrapper)

            hint = QLabel("Ξεχάσατε το Username;" if icon == "👤"
                          else "Ξεχάσατε/Απενεργοποιήσατε το Password;")
            hint.setStyleSheet("color:#dfe9e2; font-size:12.5px; background:transparent;")
            card_layout.addWidget(hint)

        self.bank_login_error = error_label("Λάθος όνομα χρήστη ή κωδικός.")
        card_layout.addWidget(self.bank_login_error)
        card_layout.addSpacing(6)

        login_btn = QPushButton("ΣΥΝΔΕΣΗ")
        login_btn.setFixedHeight(52)
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.setStyleSheet(
            f"QPushButton {{ background:{BANK_YELLOW}; color:#1a1a1a; border:none; "
            f"font-size:15px; font-weight:bold; letter-spacing:1px; }} "
            f"QPushButton:hover {{ background:#f0c400; }}"
        )
        login_btn.clicked.connect(self._attempt_login)
        card_layout.addWidget(login_btn)
        card_layout.addSpacing(10)

        signup = QLabel("Δεν έχετε SecureBank e-banking;     Online εγγραφή")
        signup.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signup.setStyleSheet("color:#dfe9e2; font-size:12.5px; background:transparent;")
        card_layout.addWidget(signup)
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color:#3f5f52;")
        card_layout.addWidget(divider)
        deactivate = QLabel("Απενεργοποίηση πρόσβασης SecureBank e-banking")
        deactivate.setStyleSheet("color:#dfe9e2; font-size:12.5px; background:transparent;")
        card_layout.addWidget(deactivate)

        login_col.addWidget(card)
        login_col.addStretch()
        hero_layout.addLayout(login_col)

        outer.addWidget(hero, stretch=1)

        #  (5) cookies + chat -- επιπλέουν πάνω από το hero 
        self.cookie_chip = QLabel("🍪", hero)
        self.cookie_chip.setFixedSize(56, 56)
        self.cookie_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cookie_chip.setStyleSheet(
            "background:#f1efe7; border:1px solid #d8d4c4; border-radius:28px; font-size:22px;")
        self.chat_bubble = QLabel("💬", hero)
        self.chat_bubble.setFixedSize(58, 58)
        self.chat_bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chat_bubble.setStyleSheet(
            f"background:{BANK_YELLOW}; border-radius:29px; font-size:22px;")
        hero.resizeEvent = self._reposition_floaters(hero)
        return page

    def _reposition_floaters(self, hero: QWidget):
        def handler(event):
            QWidget.resizeEvent(hero, event)
            size = hero.size()
            self.cookie_chip.move(26, size.height() - self.cookie_chip.height() - 26)
            self.chat_bubble.move(size.width() - self.chat_bubble.width() - 26,
                                   size.height() - self.chat_bubble.height() - 26)
        return handler

    def _dismiss_security_banner(self) -> None:
        self.security_banner.setVisible(False)
        self.action_performed.emit("bank_security_banner_dismissed")

    def _build_dashboard_page(self) -> QWidget:
        navbar = make_bank_header("Ο λογαριασμός μου")

        content = QWidget()
        body = QHBoxLayout(content)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Αριστερά: κάρτα στοιχείων λογαριασμού
        sidebar = QWidget()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"background:{BANK_CREAM}; border-right:1px solid #d8d4c4;")
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(18, 20, 18, 20)
        side_layout.setSpacing(10)

        avatar = circular_avatar(self.content.bank_username[0], BANK_ACCENT)
        side_layout.addWidget(avatar)

        self.bank_user_lbl = QLabel(self.content.bank_username)
        self.bank_user_lbl.setFont(QFont("Sans Serif", 12, QFont.Weight.Bold))
        self.bank_user_lbl.setWordWrap(True)
        side_layout.addWidget(self.bank_user_lbl)

        side_layout.addSpacing(8)
        balance_box, self.bank_balance_value = sidebar_field(
            "Υπόλοιπο", f"€ {self.content.bank_balance_eur}", BANK_DARK
        )
        side_layout.addWidget(balance_box)
        iban_box, _ = sidebar_field("IBAN", _format_iban_display(self.content.iban))
        side_layout.addWidget(iban_box)
        charges_box, _ = sidebar_field("Χρεώσεις", "€ 0,00")
        side_layout.addWidget(charges_box)
        side_layout.addStretch()

        body.addWidget(sidebar)

        # Δεξιά: μενού ενεργειών + πρόσφατες συναλλαγές (διακοσμητικό, ρεαλισμού χάριν)
        main_area = QWidget()
        main_area.setStyleSheet("background:white;")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(30, 24, 30, 24)
        main_layout.setSpacing(12)

        greeting = QLabel(f"Καλωσήρθες, {self.content.bank_username}")
        greeting.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        greeting.setStyleSheet(f"color:{BANK_DARK};")
        main_layout.addWidget(greeting)

        pay_menu_btn = self._menu_card("💳  Πληρωμή Λογαριασμού", enabled=True)
        pay_menu_btn.clicked.connect(self._toggle_payment_panel)
        main_layout.addWidget(pay_menu_btn)

        send_menu_btn = self._menu_card("📤  Αποστολή με IBAN", enabled=False)
        main_layout.addWidget(send_menu_btn)

        loan_menu_btn = self._menu_card("💰  Δανειολήψεις", enabled=False)
        main_layout.addWidget(loan_menu_btn)

        # Κρυφό panel πληρωμής
        self.payment_panel = QWidget()
        panel_layout = QVBoxLayout(self.payment_panel)
        panel_layout.setContentsMargins(0, 10, 0, 0)
        panel_layout.addWidget(QLabel("Νέα πληρωμή λογαριασμού:"))

        self.pay_iban_field = QLineEdit()
        self.pay_iban_field.setPlaceholderText("Επικόλλησε εδώ το IBAN (Ctrl+V)")
        self.pay_iban_field.setFixedHeight(36)
        self.pay_iban_field.setFont(QFont("Monospace", 12))
        self.pay_iban_field.setStyleSheet(_INPUT_STYLE)
        panel_layout.addWidget(self.pay_iban_field)

        confirm_pay_btn = QPushButton("Πληρωμή Λογαριασμού")
        confirm_pay_btn.setFixedHeight(38)
        confirm_pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_pay_btn.setStyleSheet(
            f"QPushButton {{ background:{BANK_YELLOW}; color:#1a1a1a; border:none; "
            f"border-radius:8px; font-size:14px; font-weight:bold; }} "
            f"QPushButton:hover {{ background:#f0c400; }} "
            f"QPushButton:pressed {{ background:#dcb400; padding-top:2px; }}"
        )
        confirm_pay_btn.clicked.connect(self._on_pay_clicked)
        panel_layout.addWidget(confirm_pay_btn)

        self.payment_panel.setVisible(False)
        self._payment_panel_open = False
        main_layout.addWidget(self.payment_panel)

        main_layout.addSpacing(6)
        tx_label = QLabel("Πρόσφατες συναλλαγές")
        tx_label.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        tx_label.setStyleSheet("color:#3c4043;")
        main_layout.addWidget(tx_label)
        for merchant, amount, when, positive in self._FAKE_TRANSACTIONS:
            main_layout.addWidget(self._transaction_row(merchant, amount, when, positive))

        main_layout.addStretch()

        body.addWidget(main_area, stretch=1)
        return wrap_scrollable(navbar, content, "white")

    @staticmethod
    def _transaction_row(merchant: str, amount: str, when: str, positive: bool) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(4, 6, 4, 6)
        text_box = QVBoxLayout()
        text_box.setSpacing(0)
        merchant_lbl = QLabel(merchant)
        merchant_lbl.setStyleSheet("color:#202124; font-size:12px;")
        when_lbl = QLabel(when)
        when_lbl.setStyleSheet("color:#9aa0a6; font-size:10px;")
        text_box.addWidget(merchant_lbl)
        text_box.addWidget(when_lbl)
        layout.addLayout(text_box)
        layout.addStretch()
        amount_lbl = QLabel(amount)
        amount_lbl.setStyleSheet(
            f"color:{'#137333' if positive else '#3c4043'}; font-weight:600; font-size:12px;"
        )
        layout.addWidget(amount_lbl)
        row.setStyleSheet("QWidget { border-bottom: 1px solid #f1f3f4; }")
        return row

    @staticmethod
    @staticmethod
    def _menu_card(text: str, enabled: bool) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(52)
        btn.setEnabled(enabled)
        btn.setCursor(Qt.CursorShape.PointingHandCursor if enabled
                      else Qt.CursorShape.ForbiddenCursor)
        if enabled:
            btn.setStyleSheet(
                f"QPushButton {{ background:white; border:1.5px solid {BANK_ACCENT}; "
                f"border-left:6px solid {BANK_ACCENT}; border-radius:8px; text-align:left; "
                f"padding-left:18px; font-size:14px; font-weight:600; color:{BANK_DARK}; }} "
                f"QPushButton:hover {{ background:#eaf3ef; }}"
            )
        else:
            btn.setStyleSheet(
                "QPushButton { background:#f4f4f2; border:1px solid #d8d4c4; "
                "border-radius:8px; text-align:left; padding-left:18px; font-size:14px; "
                "color:#8a8f96; }"
            )
        return btn

    def _toggle_payment_panel(self) -> None:
        self._payment_panel_open = not self._payment_panel_open
        self.payment_panel.setVisible(self._payment_panel_open)

    def _attempt_login(self) -> None:
        if (self.bank_user_field.text() == self.content.bank_username
                and self.bank_pass_field.text() == self.content.bank_password):
            self.action_performed.emit("bank_login_success")
            self.stack.setCurrentIndex(1)
            self._emit_current_fields()
        else:
            self.action_performed.emit("bank_login_failed")
            show_field_error([self.bank_user_field, self.bank_pass_field], self.bank_login_error)

    def _on_pay_clicked(self) -> None:
        QApplication.processEvents()
        iban_display = _format_iban_display(self.pay_iban_field.text().strip() or self.content.iban)
        amount_dialog = PaymentAmountDialog(iban_display, self)
        if amount_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        amount = amount_dialog.get_amount()
        if not amount:
            return

        self.action_performed.emit("bank_amount_entered")
        global_bbox = amount_dialog.get_amount_bbox_global()
        if global_bbox is not None:
            local_bbox = QRect(self.mapFromGlobal(global_bbox.topLeft()), global_bbox.size())
            self.field_rendered.emit("bank_payment_amount", local_bbox, amount)

        confirm_msg = f"Η πληρωμή {amount}€ προς {iban_display} ολοκληρώθηκε επιτυχώς."
        confirm_dialog = ConfirmationDialog(confirm_msg, self)
        confirm_dialog.exec()
        confirm_bbox = confirm_dialog.get_bbox_global()
        if confirm_bbox is not None:
            local_bbox = QRect(self.mapFromGlobal(confirm_bbox.topLeft()), confirm_bbox.size())
            self.field_rendered.emit("bank_payment_confirmation_text", local_bbox, confirm_msg)

        self.action_performed.emit("bank_payment_confirmed")

    def _emit_current_fields(self) -> None:
        """Εκπέμπει field_rendered για ό,τι είναι αυτή τη στιγμή ορατό στη
        στοίβα (login ή dashboard), με πραγματικά μετρημένη γεωμετρία."""
        if self.stack.currentIndex() == 0:
            emit_measured(self, self.field_rendered, "bank_login_username",
                          self.bank_user_field, self.content.bank_username)
            emit_measured(self, self.field_rendered, "bank_login_password",
                          self.bank_pass_field, self.content.bank_password)
        else:
            emit_measured(self, self.field_rendered, "bank_username_display",
                          self.bank_user_lbl, self.content.bank_username)
            emit_measured(self, self.field_rendered, "bank_balance_display",
                          self.bank_balance_value, self.content.bank_balance_eur)

    def on_tab_activated(self) -> None:
        self._emit_current_fields()

    def reset_fields(self) -> None:
        self.bank_user_field.clear()
        self.bank_pass_field.clear()
        self.pay_iban_field.clear()
        self.payment_panel.setVisible(False)
        self._payment_panel_open = False
        self.stack.setCurrentIndex(0)


class MockHealthScreen(QWidget):

    field_rendered = pyqtSignal(str, QRect, str)
    action_performed = pyqtSignal(str)

    SPECIALTIES = ["Παθολόγος", "Καρδιολόγος", "Ορθοπεδικός", "Δερματολόγος", "Οφθαλμίατρος"]
    SLOTS = ["Δευτέρα 10:00", "Τρίτη 12:30", "Τετάρτη 09:00", "Πέμπτη 17:00", "Παρασκευή 11:15"]
    _SPECIALTY_ICONS = ["🩺", "🦴", "👁️", "🫀", "🧠"]

    def __init__(self, content: SensitiveContent, parent=None):
        super().__init__(parent)
        self.content = content
        self._build_ui()
        self._emit_current_fields()

    # Δείκτες σελίδων -- ονόματα αντί για αριθμούς, ώστε μια μελλοντική
    # παρεμβολή σελίδας να μη σπάει σιωπηλά τη ροή.
    PAGE_PORTAL = 0
    PAGE_AUTH = 1
    PAGE_BOOKING = 2

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_portal_page())     # 0
        self.stack.addWidget(self._build_login_page())      # 1
        self.stack.addWidget(self._build_booking_page())    # 2
        outer.addWidget(self.stack)

    def _build_portal_page(self) -> QWidget:
        """Πύλη gov.gr: η σελίδα που βλέπει ο χρήστης πριν ανακατευθυνθεί
        στην κεντρική υπηρεσία αυθεντικοποίησης."""
        return build_govgr_portal_page(
            service_title="Ηλεκτρονικά ιατρικά ραντεβού\neΡαντεβού",
            heading="Κλείστε το ραντεβού σας ηλεκτρονικά",
            intro=("Μέσω της υπηρεσίας μπορείτε να προγραμματίσετε ραντεβού σε "
                   "δημόσιες δομές υγείας, να δείτε τα ενεργά σας ραντεβού και "
                   "να τα ακυρώσετε. Η είσοδος γίνεται με τους προσωπικούς σας "
                   "κωδικούς TaxisNet."),
            authority="ΗΔΙΚΑ Α.Ε. — Υπουργείο Υγείας",
            on_login=self._goto_taxisnet,
        )

    def _build_login_page(self) -> QWidget:
        """Σελίδα αυθεντικοποίησης ΓΓΠΣ. Ο κωδικός παραμένει σε EchoMode.Normal
        -- σκόπιμη απόκλιση από την πραγματική σελίδα, ώστε να είναι οπτικά
        υποκλέψιμος· βλ. health_login_password στην καταγραφή."""
        self.health_user_field = QLineEdit()
        self.health_pass_field = QLineEdit()
        self.health_pass_field.setEchoMode(QLineEdit.EchoMode.Normal)
        self.health_login_error = error_label("Λάθος όνομα χρήστη ή κωδικός.")

        return build_taxisnet_auth_page(
            self.health_user_field, self.health_pass_field,
            self.health_login_error,
            on_submit=self._attempt_login,
            on_language=lambda: self.action_performed.emit("health_language_toggle"),
        )

    def _goto_taxisnet(self) -> None:
        self.stack.setCurrentIndex(self.PAGE_AUTH)
        self.action_performed.emit("health_taxisnet_redirect")
        self.health_user_field.setFocus()
        self._emit_current_fields()

    def _build_booking_page(self) -> QWidget:
        navbar = make_solid_navbar("eΡ", "e-Ραντεβού", HEALTH_ACCENT, "Κράτηση ραντεβού")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)

        card = QWidget()
        card.setStyleSheet("background:white; border-radius:12px;")
        apply_card_shadow(card)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(26, 22, 26, 22)
        card_layout.setSpacing(10)

        avatar_row = QHBoxLayout()
        avatar_row.addWidget(circular_avatar(self.content.taxis_username[0], HEALTH_ACCENT, size=34))
        info_box = QVBoxLayout()
        info_box.setSpacing(0)
        self.health_user_display = QLabel(self.content.taxis_username)
        self.health_user_display.setStyleSheet("color:#202124; font-weight:600; font-size:12px;")
        self.health_amka_display = QLabel(f"ΑΜΚΑ: {self.content.amka}")
        self.health_amka_display.setStyleSheet("color:#5f6368; font-size:11px;")
        self.health_registry_display = QLabel(f"Αρ. Μητρώου: ΑΜ-{self.content.amka[:6]}")
        self.health_registry_display.setStyleSheet(
            "color:#1967d2; font-size:11px; font-weight:600;")
        info_box.addWidget(self.health_user_display)
        info_box.addWidget(self.health_amka_display)
        info_box.addWidget(self.health_registry_display)
        avatar_row.addLayout(info_box)
        avatar_row.addStretch()
        card_layout.addLayout(avatar_row)
        card_layout.addSpacing(4)

        card_layout.addWidget(QLabel("Περιγραφή πάθησης / λόγος επίσκεψης:"))
        self.condition_field = QTextEdit()
        self.condition_field.setPlaceholderText("Γράψε σύντομα την πάθηση/το σύμπτωμα...")
        self.condition_field.setFixedHeight(130)
        self.condition_field.setStyleSheet(_INPUT_STYLE)
        card_layout.addWidget(self.condition_field)

        specialty_row = QHBoxLayout()
        specialty_row.addWidget(QLabel("Ειδικότητα:"))
        self.specialty_combo = QComboBox()
        self.specialty_combo.addItems(self.SPECIALTIES)
        self.specialty_combo.setStyleSheet(_INPUT_STYLE)
        specialty_row.addWidget(self.specialty_combo)
        card_layout.addLayout(specialty_row)

        slot_row = QHBoxLayout()
        slot_row.addWidget(QLabel("Ημερομηνία/Ώρα:"))
        self.slot_combo = QComboBox()
        self.slot_combo.addItems(self.SLOTS)
        self.slot_combo.setStyleSheet(_INPUT_STYLE)
        slot_row.addWidget(self.slot_combo)
        card_layout.addLayout(slot_row)
        card_layout.addSpacing(4)

        confirm_btn = QPushButton("Κλείσιμο Ραντεβού")
        confirm_btn.setFixedHeight(40)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(_accent_button_style(HEALTH_ACCENT))
        confirm_btn.clicked.connect(self._on_confirm)
        card_layout.addWidget(confirm_btn)

        content_layout.addWidget(card)
        content_layout.addStretch()

        return wrap_scrollable(navbar, content, "#eef4fc")

    def _attempt_login(self) -> None:
        if (self.health_user_field.text() == self.content.taxis_username
                and self.health_pass_field.text() == self.content.taxis_password):
            self.action_performed.emit("health_login_success")
            self.stack.setCurrentIndex(self.PAGE_BOOKING)
            self._emit_current_fields()
        else:
            self.action_performed.emit("health_login_failed")
            show_field_error([self.health_user_field, self.health_pass_field],
                             self.health_login_error, _GGPS_INPUT_STYLE)

    def _on_confirm(self) -> None:
        QApplication.processEvents()  # βλ. σχόλιο στο MockBankingScreen._on_pay_clicked
        emit_measured(self, self.field_rendered, "health_condition_text",
                      self.condition_field, self.condition_field.toPlainText())

        specialty = self.specialty_combo.currentText()
        slot = self.slot_combo.currentText()
        confirm_msg = f"Το ραντεβού σας με {specialty} στις {slot} επιβεβαιώθηκε."
        confirm_dialog = ConfirmationDialog(confirm_msg, self)
        confirm_dialog.exec()
        confirm_bbox = confirm_dialog.get_bbox_global()
        if confirm_bbox is not None:
            local_bbox = QRect(self.mapFromGlobal(confirm_bbox.topLeft()), confirm_bbox.size())
            self.field_rendered.emit("health_appointment_confirmation_text", local_bbox, confirm_msg)

        self.action_performed.emit("appointment_confirmed")

    def _emit_current_fields(self) -> None:
        page = self.stack.currentIndex()
        if page == self.PAGE_PORTAL:
            return          # η πύλη δεν εμφανίζει ευαίσθητα πεδία
        if page == self.PAGE_AUTH:
            emit_measured(self, self.field_rendered, "health_login_username",
                          self.health_user_field, self.content.taxis_username)
            emit_measured(self, self.field_rendered, "health_login_password",
                          self.health_pass_field, self.content.taxis_password)
        else:
            emit_measured(self, self.field_rendered, "health_username_display",
                          self.health_user_display, self.content.taxis_username)
            emit_measured(self, self.field_rendered, "health_amka_display",
                          self.health_amka_display, self.content.amka)
            emit_measured(self, self.field_rendered, "health_registry_display",
                          self.health_registry_display, f"ΑΜ-{self.content.amka[:6]}")

    def on_tab_activated(self) -> None:
        self._emit_current_fields()

    def reset_fields(self) -> None:
        self.health_user_field.clear()
        self.health_pass_field.clear()
        self.condition_field.clear()
        self.specialty_combo.setCurrentIndex(0)
        self.slot_combo.setCurrentIndex(0)
        self.stack.setCurrentIndex(self.PAGE_PORTAL)


class GovAtHomeScreen(QWidget):

    field_rendered = pyqtSignal(str, QRect, str)
    action_performed = pyqtSignal(str)
    otp_requested = pyqtSignal(str, str)  # code, document_name

    DOCUMENTS = ["Υπεύθυνη Δήλωση Στοιχείων", "Ενοικιαστήριο Συμβόλαιο", "Εξουσιοδότηση Τρίτου"]

    def __init__(self, content: SensitiveContent, parent=None):
        super().__init__(parent)
        self.content = content
        self._generated_otp: str | None = None
        self._generated_protocol: str | None = None
        self._build_ui()
        self._emit_current_fields()

    # Ονομασμένοι δείκτες σελίδων -- η παρεμβολή της πύλης μετατοπίζει όλους
    # τους επόμενους, οπότε οι γυμνοί αριθμοί δεν είναι πια ασφαλείς.
    PAGE_PORTAL = 0
    PAGE_AUTH = 1
    PAGE_MENU = 2
    PAGE_DOCUMENT = 3
    PAGE_OTP = 4
    PAGE_SIGNED = 5

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_portal_page())          # 0
        self.stack.addWidget(self._build_login_page())            # 1
        self.stack.addWidget(self._build_landing_menu_page())     # 2
        self.stack.addWidget(self._build_document_page())         # 3
        self.stack.addWidget(self._build_otp_page())              # 4
        self.stack.addWidget(self._build_signed_page())           # 5
        outer.addWidget(self.stack)

    def _build_portal_page(self) -> QWidget:
        return build_govgr_portal_page(
            service_title="Ψηφιακή υπογραφή εγγράφων\nGovAtHome",
            heading="Υπογράψτε τα έγγραφά σας ηλεκτρονικά",
            intro=("Μέσω της υπηρεσίας μπορείτε να εκδώσετε και να υπογράψετε "
                   "ψηφιακά υπεύθυνες δηλώσεις και εξουσιοδοτήσεις, με ισχύ "
                   "ισοδύναμη του γνησίου της υπογραφής. Η είσοδος γίνεται με "
                   "τους προσωπικούς σας κωδικούς TaxisNet."),
            authority="Υπουργείο Ψηφιακής Διακυβέρνησης",
            on_login=self._goto_taxisnet,
            logo_key="hellenic", logo_text="ΥΠ. ΨΗ.Δ.", logo_color="#ffffff",
        )

    def _goto_taxisnet(self) -> None:
        self.stack.setCurrentIndex(self.PAGE_AUTH)
        self.action_performed.emit("gov_taxisnet_redirect")
        self.gov_user_field.setFocus()
        self._emit_current_fields()

    def _build_login_page(self) -> QWidget:
        """Σελίδα αυθεντικοποίησης ΓΓΠΣ -- η ίδια που χρησιμοποιεί και το
        e-Ραντεβού, όπως συμβαίνει και στην πραγματικότητα."""
        self.gov_user_field = QLineEdit()
        self.gov_pass_field = QLineEdit()
        self.gov_pass_field.setEchoMode(QLineEdit.EchoMode.Normal)
        self.gov_login_error = error_label("Λάθος όνομα χρήστη ή κωδικός.")

        return build_taxisnet_auth_page(
            self.gov_user_field, self.gov_pass_field, self.gov_login_error,
            on_submit=self._attempt_login,
            on_language=lambda: self.action_performed.emit("gov_language_toggle"),
        )

    def _build_landing_menu_page(self) -> QWidget:
        navbar = make_solid_navbar("GH", "GovAtHome", GOV_ACCENT, "Αρχική")

        content = QWidget()
        body = QHBoxLayout(content)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Αριστερά: κάρτα στοιχείων χρήστη
        sidebar = QWidget()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet("background:#f2f4f7; border-right:1px solid #dbe0e8;")
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(18, 20, 18, 20)
        side_layout.setSpacing(10)

        avatar = circular_avatar(self.content.taxis_username[0], GOV_ACCENT)
        side_layout.addWidget(avatar)

        user_lbl = QLabel(self.content.taxis_username)
        user_lbl.setFont(QFont("Sans Serif", 12, QFont.Weight.Bold))
        user_lbl.setWordWrap(True)
        side_layout.addWidget(user_lbl)

        side_layout.addSpacing(8)
        afm_box, self.gov_afm_value = sidebar_field("ΑΦΜ", self.content.afm)
        side_layout.addWidget(afm_box)
        amka_box, self.gov_amka_value = sidebar_field("ΑΜΚΑ", self.content.amka)
        side_layout.addWidget(amka_box)
        code_box, _ = sidebar_field("Προσ. Αριθμός", f"GOV-{self.content.afm[:5]}")
        side_layout.addWidget(code_box)
        side_layout.addStretch()
        body.addWidget(sidebar)

    
        main_area = QWidget()
        main_area.setStyleSheet("background:white;")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(30, 24, 30, 24)
        main_layout.setSpacing(14)

        greeting = QLabel("Υπηρεσίες")
        greeting.setFont(QFont("Sans Serif", 14, QFont.Weight.Bold))
        main_layout.addWidget(greeting)

        grid = QGridLayout()
        grid.setSpacing(14)
        tiles = [
            ("🖋️", "Ηλεκτρονική\nΥπογραφή", True),
            ("🧾", "eΠαράβολο", False),
            ("🏠", "Ε9", False),
            ("📋", "Φορολογική\nΔήλωση", False),
        ]
        for i, (icon, label, enabled) in enumerate(tiles):
            tile = self._service_tile(icon, label, enabled)
            if enabled:
                tile.clicked.connect(self._go_to_document_page)
            grid.addWidget(tile, i // 2, i % 2)
        grid_wrap = QHBoxLayout()
        grid_wrap.addLayout(grid)
        grid_wrap.addStretch()
        main_layout.addLayout(grid_wrap)
        main_layout.addStretch()

        body.addWidget(main_area, stretch=1)
        return wrap_scrollable(navbar, content, "#eef1f6")

    @staticmethod
    def _service_tile(icon: str, label: str, enabled: bool) -> QPushButton:
        btn = QPushButton(f"{icon}\n{label}")
        btn.setFixedSize(150, 100)
        btn.setEnabled(enabled)
        btn.setCursor(Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ForbiddenCursor)
        if enabled:
            btn.setStyleSheet(
                f"QPushButton {{ background:white; border:1.5px solid #cfd8e3; border-radius:12px; "
                f"font-size:12px; font-weight:600; color:#202124; }} "
                f"QPushButton:hover {{ border-color:{GOV_ACCENT}; background:#f2f6fb; }} "
                f"QPushButton:pressed {{ background:#e4ecf5; }}"
            )
        else:
            btn.setToolTip("Μη διαθέσιμο σε αυτό το demo")
            btn.setStyleSheet(
                "QPushButton { background:#f8f9fa; border:1.5px dashed #dadce0; border-radius:12px; "
                "font-size:12px; color:#9aa0a6; }"
            )
        return btn

    def _go_to_document_page(self) -> None:
        self.action_performed.emit("gov_menu_signature_selected")
        self.stack.setCurrentIndex(self.PAGE_DOCUMENT)

    def _build_document_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background:#eef1f6;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(make_solid_navbar("GH", "GovAtHome", GOV_ACCENT, "Ηλεκτρονική Υπογραφή"))
        crumb_row = QHBoxLayout()
        crumb_row.setContentsMargins(24, 0, 24, 0)
        crumb_row.addWidget(breadcrumb(["Αρχική", "Ηλεκτρονική Υπογραφή"]))
        crumb_row.addStretch()
        outer.addLayout(crumb_row)
        outer.addStretch()

        card = QWidget()
        card.setFixedWidth(340)
        card.setStyleSheet("background:white; border-radius:14px;")
        apply_card_shadow(card)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 26, 28, 26)
        card_layout.setSpacing(10)

        icon = QLabel("📄")
        icon.setFont(QFont("Sans Serif", 26))
        icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(icon)

        card_layout.addWidget(QLabel("Επίλεξε έγγραφο προς υπογραφή:"))
        self.doc_combo = QComboBox()
        self.doc_combo.addItems(self.DOCUMENTS)
        self.doc_combo.setStyleSheet(_INPUT_STYLE)
        card_layout.addWidget(self.doc_combo)
        card_layout.addSpacing(6)

        request_btn = QPushButton("Αίτημα Ηλεκτρονικής Υπογραφής")
        request_btn.setFixedHeight(40)
        request_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        request_btn.setStyleSheet(_accent_button_style(GOV_ACCENT))
        request_btn.clicked.connect(self._on_request_signature)
        card_layout.addWidget(request_btn)

        center_row = QHBoxLayout()
        center_row.addStretch()
        center_row.addWidget(card)
        center_row.addStretch()
        outer.addLayout(center_row)
        outer.addStretch()
        return page

    def _build_otp_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background:#eef1f6;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(make_solid_navbar("GH", "GovAtHome", GOV_ACCENT, "Επιβεβαίωση Υπογραφής"))
        crumb_row = QHBoxLayout()
        crumb_row.setContentsMargins(24, 0, 24, 0)
        crumb_row.addWidget(breadcrumb(["Αρχική", "Ηλεκτρονική Υπογραφή", "Επιβεβαίωση"]))
        crumb_row.addStretch()
        outer.addLayout(crumb_row)
        outer.addStretch()

        card = QWidget()
        card.setFixedWidth(340)
        card.setStyleSheet("background:white; border-radius:14px;")
        apply_card_shadow(card)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 26, 28, 26)
        card_layout.setSpacing(10)

        icon = QLabel("🔐")
        icon.setFont(QFont("Sans Serif", 26))
        icon.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(icon)

        self.doc_display_label = QLabel("")
        self.doc_display_label.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        self.doc_display_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.doc_display_label.setWordWrap(True)
        card_layout.addWidget(self.doc_display_label)

        info = QLabel(
            "Στάλθηκε 4ψήφιος κωδικός επιβεβαίωσης στο email σας. "
            "Μετάβα στην καρτέλα «Demo Mail» για να τον βρεις."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color:#5f6368;")
        card_layout.addWidget(info)

        self.otp_field = QLineEdit()
        self.otp_field.setPlaceholderText("Κωδικός OTP (4 ψηφία)")
        self.otp_field.setMaxLength(4)
        self.otp_field.setFixedHeight(40)
        self.otp_field.setFont(QFont("Monospace", 16))
        self.otp_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.otp_field.setStyleSheet(_INPUT_STYLE)
        card_layout.addWidget(self.otp_field)

        self.otp_error = error_label("Λάθος κωδικός. Έλεγξε το email και ξαναδοκίμασε.")
        card_layout.addWidget(self.otp_error)
        card_layout.addSpacing(6)

        confirm_btn = QPushButton("Επιβεβαίωση Υπογραφής")
        confirm_btn.setFixedHeight(40)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.setStyleSheet(_accent_button_style(GOV_ACCENT))
        confirm_btn.clicked.connect(self._on_confirm_otp)
        card_layout.addWidget(confirm_btn)

        center_row = QHBoxLayout()
        center_row.addStretch()
        center_row.addWidget(card)
        center_row.addStretch()
        outer.addLayout(center_row)
        outer.addStretch()
        return page

    def _build_signed_page(self) -> QWidget:
        """Σελίδα ολοκλήρωσης. Ο αριθμός πρωτοκόλλου πρέπει να παραμένει
        ορατός: ο συμμετέχων τον χρειάζεται για να τον στείλει ως απάντηση,
        και ένας modal διάλογος που κλείνει θα τον υποχρέωνε να τον
        απομνημονεύσει."""
        page = QWidget()
        page.setStyleSheet("background:#eef1f6;")
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(make_solid_navbar(
            "GH", "GovAtHome", GOV_ACCENT,
            "gov.gr-style demo — πειραματικό περιβάλλον"))
        outer.addStretch()

        card = QWidget()
        card.setFixedWidth(460)
        card.setStyleSheet("background:white; border-radius:14px;")
        apply_card_shadow(card)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(30, 26, 30, 28)
        cl.setSpacing(10)

        tick = QLabel("\u2705  Η υπογραφή ολοκληρώθηκε")
        tick.setStyleSheet(
            f"color:#137333; font-family:'{FONT_FAMILY}'; font-size:16px; "
            f"font-weight:bold; background:transparent;")
        cl.addWidget(tick)

        self.signed_doc_label = QLabel()
        self.signed_doc_label.setWordWrap(True)
        self.signed_doc_label.setStyleSheet(
            f"color:#3c4043; font-family:'{FONT_FAMILY}'; font-size:13px; "
            f"background:transparent;")
        cl.addWidget(self.signed_doc_label)
        cl.addSpacing(8)

        proto_box = QWidget()
        proto_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        proto_box.setStyleSheet(
            "background:#e7f4ea; border:1px solid #a8d5b5; border-radius:8px;")
        pb = QVBoxLayout(proto_box)
        pb.setContentsMargins(16, 12, 16, 13)
        pb.setSpacing(3)
        caption = QLabel("Αριθμός πρωτοκόλλου")
        caption.setStyleSheet(
            f"color:#3c4043; font-family:'{FONT_FAMILY}'; font-size:11.5px; "
            f"letter-spacing:0.5px; background:transparent; border:none;")
        pb.addWidget(caption)
        self.protocol_value_label = QLabel("\u2014")
        self.protocol_value_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        self.protocol_value_label.setStyleSheet(
            "color:#0d652d; font-family:'Consolas','Monospace'; font-size:19px; "
            "font-weight:bold; background:transparent; border:none;")
        pb.addWidget(self.protocol_value_label)
        cl.addWidget(proto_box)
        cl.addSpacing(6)

        hint = QLabel("Στείλτε τον αριθμό πρωτοκόλλου ως απάντηση στο μήνυμα "
                       "που σας ζήτησε την υπογραφή.")
        hint.setWordWrap(True)
        hint.setStyleSheet(
            f"color:#5f6368; font-family:'{FONT_FAMILY}'; font-size:12px; "
            f"background:transparent;")
        cl.addWidget(hint)
        cl.addSpacing(8)

        back_btn = QPushButton("Επιστροφή στην αρχική")
        back_btn.setFixedHeight(38)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(_accent_button_style(GOV_ACCENT))
        back_btn.clicked.connect(self._back_to_menu)
        cl.addWidget(back_btn)

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(card)
        row.addStretch()
        outer.addLayout(row)
        outer.addStretch()
        return page

    def _back_to_menu(self) -> None:
        self.stack.setCurrentIndex(self.PAGE_MENU)
        self.action_performed.emit("gov_returned_to_menu")
        self._emit_current_fields()

    def _attempt_login(self) -> None:
        if (self.gov_user_field.text() == self.content.taxis_username
                and self.gov_pass_field.text() == self.content.taxis_password):
            self.action_performed.emit("gov_login_success")
            self.stack.setCurrentIndex(self.PAGE_MENU)
            self._emit_current_fields()
        else:
            self.action_performed.emit("gov_login_failed")
            show_field_error([self.gov_user_field, self.gov_pass_field],
                             self.gov_login_error, _GGPS_INPUT_STYLE)

    def _on_request_signature(self) -> None:
        document_name = self.doc_combo.currentText()
        code = f"{random.randint(0, 9999):04d}"
        self._generated_otp = code

        self.action_performed.emit("gov_signature_requested")
        self.otp_requested.emit(code, document_name)

        self.doc_display_label.setText(f"Έγγραφο: {document_name}")
        self.stack.setCurrentIndex(self.PAGE_OTP)
        self._emit_current_fields()

    def _on_confirm_otp(self) -> None:
        entered = self.otp_field.text().strip()
        if not entered:
            return
        if entered == self._generated_otp:
            self.action_performed.emit("otp_correct")
            QApplication.processEvents()  # βλ. σχόλιο στο MockBankingScreen._on_pay_clicked
            document_name = self.doc_combo.currentText()
            protocol = f"ΑΠ-2026-{random.randint(10000, 99999)}"
            self._generated_protocol = protocol
            confirm_msg = (f"Το έγγραφο «{document_name}» υπογράφηκε επιτυχώς.\n"
                           f"Αριθμός πρωτοκόλλου: {protocol}")
            confirm_dialog = ConfirmationDialog(confirm_msg, self)
            confirm_dialog.exec()
            confirm_bbox = confirm_dialog.get_bbox_global()
            if confirm_bbox is not None:
                local_bbox = QRect(self.mapFromGlobal(confirm_bbox.topLeft()), confirm_bbox.size())
                self.field_rendered.emit("gov_signature_confirmation_text", local_bbox, confirm_msg)
            self.signed_doc_label.setText(f"Έγγραφο: {document_name}")
            self.protocol_value_label.setText(protocol)
            self.stack.setCurrentIndex(self.PAGE_SIGNED)
            self.action_performed.emit("document_signed")
            self._emit_current_fields()
        else:
            self.action_performed.emit("otp_incorrect")
            show_field_error([self.otp_field], self.otp_error)

    def _emit_current_fields(self) -> None:
        idx = self.stack.currentIndex()
        if idx == self.PAGE_PORTAL:
            return          # η πύλη δεν εμφανίζει ευαίσθητα πεδία
        if idx == self.PAGE_AUTH:
            emit_measured(self, self.field_rendered, "gov_login_username",
                          self.gov_user_field, self.content.taxis_username)
            emit_measured(self, self.field_rendered, "gov_login_password",
                          self.gov_pass_field, self.content.taxis_password)
        elif idx == self.PAGE_MENU:
            emit_measured(self, self.field_rendered, "gov_afm_display",
                          self.gov_afm_value, self.content.afm)
            emit_measured(self, self.field_rendered, "gov_amka_display",
                          self.gov_amka_value, self.content.amka)
        elif idx == self.PAGE_SIGNED and self._generated_protocol is not None:
            emit_measured(self, self.field_rendered, "gov_protocol_number",
                          self.protocol_value_label, self._generated_protocol)
        elif idx == self.PAGE_OTP and self._generated_otp is not None:
            emit_measured(self, self.field_rendered, "gov_selected_document",
                          self.doc_display_label, self.doc_combo.currentText())

    def on_tab_activated(self) -> None:
        self._emit_current_fields()

    def reset_fields(self) -> None:
        self.gov_user_field.clear()
        self.gov_pass_field.clear()
        self.doc_combo.setCurrentIndex(0)
        self.otp_field.clear()
        self._generated_otp = None
        self._generated_protocol = None
        self.protocol_value_label.setText("\u2014")
        self.signed_doc_label.setText("")
        self.stack.setCurrentIndex(self.PAGE_PORTAL)

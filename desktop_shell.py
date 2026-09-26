from __future__ import annotations

import random
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QDate, QPoint, QRectF, QTime, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QRadialGradient
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget,
    QGraphicsDropShadowEffect, QGridLayout, QLineEdit, QFrame,
)

FONT_FAMILY = "Segoe UI"
TASKBAR_H = 52
TASKBAR_BG = "#d3d9e0"
TASKBAR_BORDER = "#94a0ab"
TASKBAR_TEXT = "#101418"          # ώρα, θερμοκρασία, δίσκος συστήματος
TASKBAR_TEXT_SOFT = "#2d353d"     # δευτερεύον κείμενο
TASKBAR_HOVER = "#bcc5ce"
TASKBAR_ACTIVE = "#aab4bf"
BADGE_RED = "#d1332e"
ACCENT_BLUE = "#005ab0"


@dataclass
class AppSpec:
    app_id: str
    title: str
    icon: str          
    accent: str       
    pinned: bool = True


DECORATIVE_SHORTCUTS: list[tuple[str, str, str]] = [
    ("Αυτός ο\nυπολογιστής", "🖥", "#3a7bd5"),
    ("Κάδος\nΑνακύκλωσης", "🗑", "#4a8fd6"),
    ("Έγγραφα", "📁", "#e8b923"),
    ("Λήψεις", "📁", "#e8b923"),
    ("Διπλωματική", "📁", "#e8b923"),
    ("Εικόνες", "📁", "#e8b923"),
    ("Δίκτυο", "🌐", "#3a7bd5"),
    ("Ρυθμίσεις", "⚙", "#5f6368"),
]


class _Wallpaper(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        rng = random.Random(7)   # σταθερό seed: ίδια ταπετσαρία σε κάθε συνεδρία
        self._blobs = [
            (rng.uniform(0.15, 0.85), rng.uniform(0.15, 0.85),
             rng.uniform(0.25, 0.55), rng.uniform(0.10, 0.30))
            for _ in range(7)
        ]

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = max(1, self.width()), max(1, self.height())

        base = QLinearGradient(0, 0, float(w), float(h))
        base.setColorAt(0.0, QColor("#f6bfe0"))
        base.setColorAt(0.5, QColor("#ef9ed2"))
        base.setColorAt(1.0, QColor("#e97fc4"))
        painter.fillRect(self.rect(), base)

        for cx, cy, radius, alpha in self._blobs:
            px, py = cx * w, cy * h
            r = radius * max(w, h) * 0.5
            grad = QRadialGradient(px, py, r)
            grad.setColorAt(0.0, QColor(214, 51, 132, int(alpha * 255)))
            grad.setColorAt(0.6, QColor(190, 40, 140, int(alpha * 120)))
            grad.setColorAt(1.0, QColor(190, 40, 140, 0))
            path = QPainterPath()
            path.addEllipse(QRectF(px - r, py - r * 0.55, r * 2, r * 1.1))
            painter.fillPath(path, grad)

        sheen = QLinearGradient(0.0, h * 0.35, float(w), h * 0.75)
        sheen.setColorAt(0.0, QColor(255, 255, 255, 0))
        sheen.setColorAt(0.5, QColor(255, 235, 250, 70))
        sheen.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(self.rect(), sheen)
        painter.end()


class _DesktopIcon(QWidget):

    activated = pyqtSignal(str)
    selected = pyqtSignal(object)

    def __init__(self, key: str, title: str, glyph: str, colour: str, parent=None):
        super().__init__(parent)
        self.key = key
        self._selected = False
        self.setFixedSize(96, 98)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 4)
        layout.setSpacing(4)

        tile = QLabel(glyph)
        tile.setFixedSize(46, 46)
        tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tile.setStyleSheet(
            f"background:{colour}; border-radius:9px; font-size:22px; color:white;")
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(tile)
        row.addStretch()
        layout.addLayout(row)

        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        label.setWordWrap(True)
        label.setStyleSheet("color:white; font-size:11px; background:transparent;")
        # Σκιά κειμένου: χωρίς αυτήν, λευκές ετικέτες πάνω σε ανοιχτόχρωμη
        # ταπετσαρία γίνονται δυσανάγνωστες -- και η αναγνωσιμότητα κάθε
        # στοιχείου της οθόνης είναι εδώ μετρούμενη μεταβλητή, όχι λεπτομέρεια.
        shadow = QGraphicsDropShadowEffect(label)
        shadow.setBlurRadius(6)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(0, 0, 0, 200))
        label.setGraphicsEffect(shadow)
        layout.addWidget(label)
        self._apply_style()

    def _apply_style(self) -> None:
        if self._selected:
            self.setStyleSheet(
                "background:rgba(255,255,255,0.30); "
                "border:1px solid rgba(255,255,255,0.55); border-radius:6px;")
        else:
            self.setStyleSheet("background:transparent; border:1px solid transparent;")

    def set_selected(self, value: bool) -> None:
        self._selected = value
        self._apply_style()

    def mousePressEvent(self, event) -> None:
        self.selected.emit(self)

    def mouseDoubleClickEvent(self, event) -> None:
        self.activated.emit(self.key)

    def enterEvent(self, event) -> None:
        if not self._selected:
            self.setStyleSheet(
                "background:rgba(255,255,255,0.16); "
                "border:1px solid rgba(255,255,255,0.30); border-radius:6px;")

    def leaveEvent(self, event) -> None:
        self._apply_style()


class _Toast(QWidget):

    clicked = pyqtSignal(str)

    def __init__(self, title: str, body: str, chat_id: str, icon: str,
                 app_name: str, parent=None):
        super().__init__(parent)
        self.chat_id = chat_id
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(372)
        self.setStyleSheet(
            "background:#f3f3f3; border:1px solid #d0d0d0; border-radius:8px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(6)

        head = QHBoxLayout()
        head.setSpacing(8)
        app_lbl = QLabel(f"{icon}  {app_name}")
        app_lbl.setStyleSheet(
            "color:#5f6368; font-size:11px; background:transparent; border:none;")
        head.addWidget(app_lbl)
        head.addStretch()
        close = QLabel("✕")
        close.setStyleSheet(
            "color:#5f6368; font-size:11px; background:transparent; border:none;")
        head.addWidget(close)
        layout.addLayout(head)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "color:#131417; font-size:13.5px; font-weight:600; "
            "background:transparent; border:none;")
        layout.addWidget(title_lbl)

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setStyleSheet(
            "color:#3c4043; font-size:12.5px; background:transparent; border:none;")
        layout.addWidget(body_lbl)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self.chat_id)


class _StartMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedSize(560, 400)
        self.setStyleSheet(
            "background:#f3f3f3; border:1px solid #d5d5d5; border-radius:10px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 18)
        layout.setSpacing(12)

        search = QLineEdit()
        search.setPlaceholderText("Αναζήτηση εφαρμογών και αρχείων")
        search.setFixedHeight(36)
        search.setStyleSheet(
            "QLineEdit { background:white; border:1px solid #d0d0d0; border-radius:6px; "
            "padding:0 12px; font-size:13px; color:#131417; }"
        )
        layout.addWidget(search)

        title = QLabel("Καρφιτσωμένα")
        title.setStyleSheet(
            "color:#131417; font-size:13px; font-weight:600; "
            "background:transparent; border:none;")
        layout.addWidget(title)

        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(self.grid)
        layout.addStretch()

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color:#dcdcdc;")
        layout.addWidget(divider)

        foot = QHBoxLayout()
        user = QLabel("👤   Eleni")
        user.setStyleSheet(
            "color:#131417; font-size:12.5px; background:transparent; border:none;")
        foot.addWidget(user)
        foot.addStretch()
        power = QLabel("⏻")
        power.setStyleSheet(
            "color:#131417; font-size:14px; background:transparent; border:none;")
        foot.addWidget(power)
        layout.addLayout(foot)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 110))
        self.setGraphicsEffect(shadow)
        self.hide()

    def populate(self, apps: list[AppSpec], on_click) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for i, spec in enumerate(apps):
            btn = QPushButton(f"{spec.icon}\n{spec.title}")
            btn.setFixedSize(96, 86)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(
                "QPushButton { background:transparent; border:none; border-radius:6px; "
                "color:#131417; font-size:11.5px; } "
                "QPushButton:hover { background:#e6e6e6; }"
            )
            btn.clicked.connect(lambda _, a=spec.app_id: on_click(a))
            self.grid.addWidget(btn, i // 5, i % 5)


class DesktopShell(QWidget):

    app_opened = pyqtSignal(str)
    app_focused = pyqtSignal(str)
    notification_clicked = pyqtSignal(str, str)   # app_id, chat_id
    shortcut_activated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.apps: dict[str, AppSpec] = {}
        self.widgets: dict[str, QWidget] = {}
        self.open_apps: list[str] = []
        self.current_app: str | None = None
        self._toasts: list[_Toast] = []
        self._badges: dict[str, int] = {}
        self._icons: list[_DesktopIcon] = []
        self._icon_slot = 0
        self._build_ui()

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._tick_clock)
        self._clock_timer.start(1000)
        self._tick_clock()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_desktop_page())   # index 0
        outer.addWidget(self.stack, stretch=1)
        outer.addWidget(self._build_taskbar())

        self.start_menu = _StartMenu(self)

    def _build_desktop_page(self) -> QWidget:
        page = _Wallpaper()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 14, 16, 14)

        self.icon_grid = QGridLayout()
        self.icon_grid.setSpacing(2)
        self.icon_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(self.icon_grid)
        layout.addStretch()
        return page

    def _build_taskbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(TASKBAR_H)
        bar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Επιλογέας με objectName: χωρίς αυτόν το border-top κληρονομείται από
        # κάθε θυγατρικό widget και εμφανίζονται γραμμές πάνω από τον καιρό και
        # τον δίσκο συστήματος.
        bar.setObjectName("taskbar")
        bar.setStyleSheet(
            f"QWidget#taskbar {{ background:{TASKBAR_BG}; "
            f"border-top:2px solid {TASKBAR_BORDER}; }}")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 4, 12, 4)
        layout.setSpacing(8)

        #  αριστερά: widget καιρού 
        weather = QWidget()
        weather.setFixedWidth(150)
        wl = QHBoxLayout(weather)
        wl.setContentsMargins(6, 0, 6, 0)
        wl.setSpacing(8)
        sun = QLabel("☀")
        sun.setFixedSize(30, 30)
        sun.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sun.setStyleSheet(
            "background:#e08600; color:white; border-radius:15px; font-size:15px; "
            "font-weight:bold;")
        wl.addWidget(sun)
        wt = QVBoxLayout()
        wt.setSpacing(0)
        temp = QLabel("32°C")
        temp.setStyleSheet(f"color:{TASKBAR_TEXT}; font-size:12.5px; font-weight:700; "
                            f"background:transparent;")
        cond = QLabel("Ηλιοφάνεια")
        cond.setStyleSheet(f"color:{TASKBAR_TEXT_SOFT}; font-size:11px; font-weight:600; "
                            f"background:transparent;")
        wt.addWidget(temp)
        wt.addWidget(cond)
        wl.addLayout(wt)
        layout.addWidget(weather)
        layout.addStretch()

        #  κέντρο: Έναρξη + αναζήτηση + καρφιτσωμένα 
        centre = QHBoxLayout()
        centre.setSpacing(6)
        self.start_btn = QPushButton("⊞")
        self.start_btn.setFixedSize(42, 40)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; border:none; border-radius:6px; "
            f"color:{ACCENT_BLUE}; font-size:21px; font-weight:bold; }} "
            f"QPushButton:hover {{ background:{TASKBAR_HOVER}; }}"
        )
        self.start_btn.clicked.connect(self.toggle_start_menu)
        centre.addWidget(self.start_btn)

        search_box = QWidget()
        search_box.setFixedSize(230, 38)
        search_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        search_box.setStyleSheet(
            f"background:#ffffff; border:1.5px solid {TASKBAR_BORDER}; "
            f"border-radius:19px;")
        sl = QHBoxLayout(search_box)
        sl.setContentsMargins(14, 0, 12, 0)
        sl.setSpacing(8)
        glass = QLabel("🔍")
        glass.setStyleSheet("font-size:12px; background:transparent; border:none;")
        sl.addWidget(glass)
        self.desktop_search = QLineEdit()
        self.desktop_search.setPlaceholderText("Αναζήτηση")
        self.desktop_search.setStyleSheet(
            f"QLineEdit {{ background:transparent; border:none; font-size:12.5px; "
            f"font-weight:600; color:{TASKBAR_TEXT}; }}"
            f"QLineEdit::placeholder {{ color:{TASKBAR_TEXT_SOFT}; }}")
        sl.addWidget(self.desktop_search, stretch=1)
        centre.addWidget(search_box)

        self.task_buttons_layout = QHBoxLayout()
        self.task_buttons_layout.setSpacing(4)
        centre.addLayout(self.task_buttons_layout)
        layout.addLayout(centre)
        layout.addStretch()

        #  δεξιά: δίσκος συστήματος + ρολόι δύο γραμμών 
        tray = QLabel("^\u2003ΕΛ\u2003📶\u2003🔊\u2003🔋")
        tray.setStyleSheet(f"color:{TASKBAR_TEXT}; font-size:13px; font-weight:700; "
                            f"background:transparent;")
        layout.addWidget(tray)
        battery = QLabel("83%")
        battery.setStyleSheet(
            "color:#0b6b34; font-size:11.5px; font-weight:700; background:transparent; "
            "padding:0 8px 0 2px;")
        layout.addWidget(battery)

        clock_box = QVBoxLayout()
        clock_box.setSpacing(0)
        self.clock_time = QLabel()
        self.clock_time.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock_time.setStyleSheet(
            f"color:{TASKBAR_TEXT}; font-size:12.5px; font-weight:700; "
            f"background:transparent;")
        self.clock_date = QLabel()
        self.clock_date.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock_date.setStyleSheet(
            f"color:{TASKBAR_TEXT_SOFT}; font-size:11.5px; font-weight:600; "
            f"background:transparent;")
        clock_box.addWidget(self.clock_time)
        clock_box.addWidget(self.clock_date)
        layout.addLayout(clock_box)
        return bar

    def _tick_clock(self) -> None:
        self.clock_time.setText(QTime.currentTime().toString("HH:mm"))
        self.clock_date.setText(QDate.currentDate().toString("d/M/yyyy"))

    def register_app(self, spec: AppSpec, widget: QWidget) -> None:
        self.apps[spec.app_id] = spec
        self.widgets[spec.app_id] = widget
        self.stack.addWidget(widget)
        self._add_icon(spec.app_id, spec.title, spec.icon, spec.accent)
        self.start_menu.populate(list(self.apps.values()), self.open_app)
        self._rebuild_taskbar()

    def add_decorative_shortcuts(self) -> None:
        for title, glyph, colour in DECORATIVE_SHORTCUTS:
            self._add_icon(f"shortcut::{title}", title, glyph, colour)

    def _add_icon(self, key: str, title: str, glyph: str, colour: str) -> None:
        icon = _DesktopIcon(key, title, glyph, colour)
        icon.activated.connect(self._on_icon_activated)
        icon.selected.connect(self._on_icon_selected)
        self._icons.append(icon)
        rows_per_column = 7
        self.icon_grid.addWidget(icon, self._icon_slot % rows_per_column,
                                  self._icon_slot // rows_per_column)
        self._icon_slot += 1

    def _on_icon_selected(self, icon: _DesktopIcon) -> None:
        for other in self._icons:
            other.set_selected(other is icon)

    def _on_icon_activated(self, key: str) -> None:
        if key.startswith("shortcut::"):
            self.shortcut_activated.emit(key.split("::", 1)[1])
            return
        self.open_app(key)

    def open_app(self, app_id: str) -> None:
        if app_id not in self.widgets:
            return
        self.start_menu.hide()
        if app_id not in self.open_apps:
            self.open_apps.append(app_id)
            self.app_opened.emit(app_id)
        self.focus_app(app_id)

    def focus_app(self, app_id: str) -> None:
        widget = self.widgets.get(app_id)
        if widget is None:
            return
        self.start_menu.hide()
        self.stack.setCurrentWidget(widget)
        self.current_app = app_id
        self._badges[app_id] = 0
        self._rebuild_taskbar()
        self.app_focused.emit(app_id)

    def show_desktop(self) -> None:
        self.start_menu.hide()
        self.stack.setCurrentIndex(0)
        self.current_app = None
        self._rebuild_taskbar()
        self.app_focused.emit("desktop")

    def toggle_start_menu(self) -> None:
        if self.start_menu.isVisible():
            self.start_menu.hide()
            return
        self.start_menu.populate(list(self.apps.values()), self.open_app)
        self._position_start_menu()
        self.start_menu.show()
        self.start_menu.raise_()

    def _position_start_menu(self) -> None:
        x = (self.width() - self.start_menu.width()) // 2
        y = self.height() - TASKBAR_H - self.start_menu.height() - 10
        self.start_menu.move(max(10, x), max(10, y))

    def set_badge(self, app_id: str, count: int) -> None:
        if app_id != self.current_app:
            self._badges[app_id] = count
            self._rebuild_taskbar()

    def _rebuild_taskbar(self) -> None:
        while self.task_buttons_layout.count():
            item = self.task_buttons_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # Μόνο το deleteLater() δεν αρκεί: η διαγραφή είναι
                # χρονοπρογραμματισμένη, ενώ το takeAt() έχει ήδη βγάλει το
                # widget από το layout -- οπότε μέχρι να καταστραφεί μένει
                # ορατό στη θέση (0, 0) της μπάρας, πάνω από το widget του
                # καιρού. Με κάθε ειδοποίηση Teams στοιβάζεται ένα ακόμη.
                widget.setParent(None)
                widget.deleteLater()
        for app_id, spec in self.apps.items():
            if not spec.pinned and app_id not in self.open_apps:
                continue
            running = app_id in self.open_apps
            active = app_id == self.current_app
            badge = self._badges.get(app_id, 0)
            btn = QPushButton(spec.icon)
            btn.setFixedSize(46, 40)
            btn.setToolTip(spec.title)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            # Ένδειξη εκτέλεσης: γραμμή κάτω από το εικονίδιο, στο χρώμα της
            # ίδιας της εφαρμογής -- η σύμβαση των Windows 11. Το χρώμα είναι
            # ό,τι απομένει ως διακριτικό όταν πέσει το θόλωμα, γιατί το σχήμα
            # του εικονιδίου χάνεται πρώτο.
            underline = "transparent"
            if running:
                underline = spec.accent if active else "#6c7680"
            btn.setStyleSheet(
                f"QPushButton {{ background:{TASKBAR_ACTIVE if active else 'transparent'}; "
                f"border:none; border-bottom:4px solid {underline}; border-radius:6px; "
                f"font-size:18px; color:{TASKBAR_TEXT}; }} "
                f"QPushButton:hover {{ background:{TASKBAR_HOVER}; }}"
            )
            btn.clicked.connect(lambda _, a=app_id: self.open_app(a))

            if badge:
                # Κόκκινο δισκίο πάνω δεξιά αντί για αριθμό δίπλα στο εικονίδιο:
                # διακρίνεται ως χρωματική κηλίδα ακόμη κι όταν ο αριθμός δεν
                # διαβάζεται.
                chip = QLabel(str(badge) if badge < 10 else "9+", btn)
                chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
                chip.setFixedSize(17, 17)
                chip.move(26, 3)
                chip.setStyleSheet(
                    f"background:{BADGE_RED}; color:white; border:1.5px solid white; "
                    f"border-radius:8px; font-size:9.5px; font-weight:bold;"
                )
                chip.raise_()

            self.task_buttons_layout.addWidget(btn)

    def show_notification(self, app_id: str, title: str, body: str,
                          chat_id: str, icon: str = "💬") -> None:
        app_name = self.apps[app_id].title if app_id in self.apps else "Σύστημα"
        toast = _Toast(title, body, chat_id, icon, app_name, self)
        toast.clicked.connect(lambda cid, a=app_id: self._on_toast_clicked(a, cid))
        self._toasts.append(toast)
        toast.show()
        self._reposition_toasts()
        QTimer.singleShot(7000, lambda t=toast: self._dismiss_toast(t))

    def _on_toast_clicked(self, app_id: str, chat_id: str) -> None:
        self.open_app(app_id)
        self.notification_clicked.emit(app_id, chat_id)
        for toast in list(self._toasts):
            self._dismiss_toast(toast)

    def _dismiss_toast(self, toast: _Toast) -> None:
        if toast in self._toasts:
            self._toasts.remove(toast)
            toast.hide()
            toast.deleteLater()
            self._reposition_toasts()

    def _reposition_toasts(self) -> None:
        margin = 16
        y = self.height() - TASKBAR_H - margin
        for toast in reversed(self._toasts):
            toast.adjustSize()
            y -= toast.height()
            toast.move(self.width() - toast.width() - margin, y)
            toast.raise_()
            y -= 10

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._reposition_toasts()
        if self.start_menu.isVisible():
            self._position_start_menu()

from __future__ import annotations

from PyQt6.QtCore import Qt, QRect, QTimer, QDateTime, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter
from PyQt6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from profiles import PROFILE_IDS, Profile, build_profiles

PASSWORD_ECHO_CLEARTEXT = False

HINT_AFTER_ATTEMPTS = 3


class ProfileTile(QFrame):

    selected = pyqtSignal(str)

    def __init__(self, profile: Profile, enabled: bool = True,
                 reveal_password: bool = False, parent=None):
        super().__init__(parent)
        self.profile_id = profile.profile_id
        self._enabled = enabled
        self._is_selected = False

        self.setFixedSize(200, 236 if reveal_password else 210)
        self.setCursor(
            Qt.CursorShape.PointingHandCursor if enabled else Qt.CursorShape.ForbiddenCursor
        )
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 22, 0, 18)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.avatar = QLabel(profile.profile_id)
        self.avatar.setFixedSize(96, 96)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar.setStyleSheet(
            "background: rgba(255,255,255,0.16); border-radius: 48px; "
            "color: #ffffff; font-size: 40px; font-weight: 300;"
        )
        layout.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.name = QLabel(profile.display_name)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name.setStyleSheet(
            "color: #ffffff; font-size: 17px; font-weight: 500; background: transparent;"
        )
        layout.addWidget(self.name)

        self.account = QLabel(profile.account_name)
        self.account.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.account.setStyleSheet(
            "color: rgba(255,255,255,0.55); font-size: 12px; background: transparent;"
        )
        layout.addWidget(self.account)

        if reveal_password:
            self.hint = QLabel(profile.os_password)
            self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.hint.setStyleSheet(
                "color: #ffd479; font-family: 'Consolas', monospace; font-size: 13px; "
                "letter-spacing: 1px; background: transparent;"
            )
            layout.addWidget(self.hint)

        self._apply_style()

    def set_selected(self, value: bool) -> None:
        self._is_selected = value
        self._apply_style()

    def _apply_style(self) -> None:
        if not self._enabled:
            border = "1px solid rgba(255,255,255,0.06)"
            background = "rgba(255,255,255,0.02)"
            self.setGraphicsEffect(None)
        elif self._is_selected:
            border = "1px solid rgba(255,255,255,0.55)"
            background = "rgba(255,255,255,0.14)"
        else:
            border = "1px solid rgba(255,255,255,0.14)"
            background = "rgba(255,255,255,0.05)"
        self.setStyleSheet(
            f"ProfileTile {{ background: {background}; border: {border}; border-radius: 14px; }}"
        )
        opacity = "1.0" if self._enabled else "0.35"
        self.avatar.setStyleSheet(
            f"background: rgba(255,255,255,{0.16 if self._enabled else 0.05}); "
            f"border-radius: 48px; color: rgba(255,255,255,{opacity}); "
            "font-size: 40px; font-weight: 300;"
        )

    def mousePressEvent(self, event) -> None:
        if self._enabled:
            self.selected.emit(self.profile_id)
        super().mousePressEvent(event)


class LoginScreen(QWidget):


    login_succeeded = pyqtSignal(str)
    action_performed = pyqtSignal(str)
    field_shown = pyqtSignal(str, str, QRect)
    exit_requested = pyqtSignal()

    def __init__(self, session_id: str, required_profile: str | None = None,
                 reveal_passwords: bool = False, parent=None):
        super().__init__(parent)
        self.session_id = session_id
        self.profiles: dict[str, Profile] = build_profiles(session_id)
        self.required_profile = required_profile
        self.reveal_passwords = reveal_passwords
        self._active_profile: str | None = None
        self._attempts: dict[str, int] = {pid: 0 for pid in PROFILE_IDS}

        self._build_ui()
        self.reset()

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(2)

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_label.setStyleSheet(
            "color: #ffffff; font-size: 64px; font-weight: 200; background: transparent;"
        )
        outer.addWidget(self.clock_label)

        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet(
            "color: rgba(255,255,255,0.75); font-size: 18px; background: transparent;"
        )
        outer.addWidget(self.date_label)

        outer.addSpacing(46)

        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(28)
        tiles_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.tiles: dict[str, ProfileTile] = {}
        for pid in PROFILE_IDS:
            enabled = self.required_profile is None or self.required_profile == pid
            tile = ProfileTile(self.profiles[pid], enabled=enabled,
                               reveal_password=self.reveal_passwords)
            tile.selected.connect(self._on_tile_selected)
            self.tiles[pid] = tile
            tiles_row.addWidget(tile)
        outer.addLayout(tiles_row)

        self.prompt_label = QLabel(
            "Επίλεξε λογαριασμό για να συνεχίσεις"
            if self.required_profile is None
            else f"Συνδέσου με τον λογαριασμό {self.required_profile}"
        )
        self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt_label.setStyleSheet(
            "color: rgba(255,255,255,0.65); font-size: 13px; background: transparent;"
        )
        outer.addSpacing(16)
        outer.addWidget(self.prompt_label)

        outer.addSpacing(26)

        entry_row = QHBoxLayout()
        entry_row.setSpacing(8)
        entry_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.password_edit = QLineEdit()
        self.password_edit.setFixedSize(280, 38)
        self.password_edit.setPlaceholderText("Κωδικός πρόσβασης")
        self.password_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if PASSWORD_ECHO_CLEARTEXT
            else QLineEdit.EchoMode.Password
        )
        self.password_edit.setStyleSheet(
            "QLineEdit { background: rgba(255,255,255,0.92); border: none; "
            "border-radius: 4px; padding: 0 12px; font-size: 14px; color: #202124; } "
            "QLineEdit:focus { background: #ffffff; }"
        )
        self.password_edit.returnPressed.connect(self._attempt_login)
        entry_row.addWidget(self.password_edit)

        self.submit_button = QPushButton("→")
        self.submit_button.setFixedSize(38, 38)
        self.submit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_button.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.18); color: #ffffff; "
            "border: 1px solid rgba(255,255,255,0.35); border-radius: 4px; font-size: 17px; } "
            "QPushButton:hover { background: rgba(255,255,255,0.30); }"
        )
        self.submit_button.clicked.connect(self._attempt_login)
        entry_row.addWidget(self.submit_button)

        outer.addLayout(entry_row)

        self.message_label = QLabel(" ")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet(
            "color: #ffb4a9; font-size: 13px; background: transparent;"
        )
        outer.addSpacing(12)
        outer.addWidget(self.message_label)

        outer.addStretch(3)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.clock_label.setGraphicsEffect(shadow)
        self.exit_button = QPushButton("✕", self)
        self.exit_button.setFixedSize(34, 34)
        self.exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_button.setToolTip("Τερματισμός προγράμματος")
        self.exit_button.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,0.10); color: rgba(255,255,255,0.75); "
            "border: 1px solid rgba(255,255,255,0.22); border-radius: 8px; "
            "font-size: 14px; font-weight: bold; } "
            "QPushButton:hover { background: rgba(197,34,31,0.85); color: #ffffff; "
            "border: 1px solid rgba(255,255,255,0.35); }"
        )
        self.exit_button.clicked.connect(self._on_exit_clicked)
        self.exit_button.raise_()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.exit_button.move(self.width() - self.exit_button.width() - 22, 22)

    def _on_exit_clicked(self) -> None:
        answer = QMessageBox.question(
            self,
            "Τερματισμός προγράμματος",
            "Να κλείσει το πρόγραμμα;",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.action_performed.emit("os_login_aborted")
        self.exit_requested.emit()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#0f2027"))
        gradient.setColorAt(0.55, QColor("#203a43"))
        gradient.setColorAt(1.0, QColor("#2c5364"))
        painter.fillRect(self.rect(), QBrush(gradient))
        super().paintEvent(event)

    def reset(self) -> None:
        self.password_edit.clear()
        self.message_label.setText(" ")
        preselect = self.required_profile
        self._active_profile = None
        for pid, tile in self.tiles.items():
            tile.set_selected(False)
        if preselect is not None:
            self._on_tile_selected(preselect)

    def _on_tile_selected(self, profile_id: str) -> None:
        if self.required_profile is not None and profile_id != self.required_profile:
            return
        self._active_profile = profile_id
        for pid, tile in self.tiles.items():
            tile.set_selected(pid == profile_id)
        self.password_edit.clear()
        self.message_label.setText(" ")
        self.password_edit.setFocus()
        self.action_performed.emit(f"os_profile_selected_{profile_id}")

    def _attempt_login(self) -> None:
        if self._active_profile is None:
            self.message_label.setText("Επίλεξε πρώτα λογαριασμό.")
            return

        pid = self._active_profile
        typed = self.password_edit.text()
        if typed == self.profiles[pid].os_password:
            self.action_performed.emit(f"os_login_success_{pid}")
            self._maybe_emit_field(pid)
            self.login_succeeded.emit(pid)
            return

        self._attempts[pid] += 1
        self.action_performed.emit(f"os_login_failed_{pid}")
        self.password_edit.clear()
        if self._attempts[pid] >= HINT_AFTER_ATTEMPTS:
            self.message_label.setText(
                f"Λανθασμένος κωδικός. Υπενθύμιση: {self.profiles[pid].os_password}"
            )
        else:
            self.message_label.setText("Ο κωδικός δεν είναι σωστός. Δοκίμασε ξανά.")

    def _maybe_emit_field(self, profile_id: str) -> None:
        
        if not PASSWORD_ECHO_CLEARTEXT:
            return
        top_left = self.password_edit.mapToGlobal(self.password_edit.rect().topLeft())
        rect = QRect(top_left, self.password_edit.size())
        self.field_shown.emit(
            f"os_password_{profile_id}", self.profiles[profile_id].os_password, rect
        )

    def _update_clock(self) -> None:
        now = QDateTime.currentDateTime()
        self.clock_label.setText(now.toString("HH:mm"))
        self.date_label.setText(now.toString("dddd, d MMMM"))

    def keyPressEvent(self, event) -> None:
        if (event.key() == Qt.Key.Key_Q
                and event.modifiers() == (Qt.KeyboardModifier.ControlModifier
                                          | Qt.KeyboardModifier.AltModifier)):
            print("Έξοδος πειραματιστή από την οθόνη σύνδεσης.")
            self.action_performed.emit("os_login_aborted")
            self.exit_requested.emit()
            return
        super().keyPressEvent(event)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    session = sys.argv[1] if len(sys.argv) > 1 else "P07"
    screen = LoginScreen(session, reveal_passwords="--reveal" in sys.argv)
    screen.login_succeeded.connect(lambda pid: print(f"Είσοδος με προφίλ {pid}"))
    screen.action_performed.connect(lambda a: print(f"action: {a}"))
    screen.exit_requested.connect(app.quit)
    screen.resize(1280, 800)
    screen.show()

    from profiles import credentials_sheet
    print(credentials_sheet(session))

    sys.exit(app.exec())

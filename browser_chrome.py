from __future__ import annotations

from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLineEdit, QLabel, QPushButton,
    QGraphicsDropShadowEffect,
)

_TAB_STYLE = """
QTabWidget::pane {
    border: none;
    background: white;
}
QTabBar::tab {
    background: #b9c0c9;
    color: #14181d;
    padding: 9px 22px;
    margin-right: 2px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    min-width: 140px;
}
QTabBar::tab:hover { background: #cbd2da; }
QTabBar::tab:selected {
    background: white;
    font-weight: 700;
}
"""

_TAB_COLORS = ["#a2540b", "#0f5244", "#134a9c", "#12305c", "#42469e"]

_ADDRESS_BAR_STYLE = """
QLineEdit {
    background: #ffffff;
    border: 1px solid #9aa2ab;
    border-radius: 16px;
    padding: 6px 14px;
    color: #14181d;
    font-size: 13px;
    font-weight: 500;
}
"""

_TOOLBAR_STYLE = "background:#d5dae0; border-bottom: 1px solid #9aa2ab;"
_NAV_ICON_STYLE = "color:#14181d; font-size:18px; font-weight:bold; padding:0 7px;"


class InstructionOverlay(QWidget):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(340)
        self._collapsed = False
        self._full_text = ""
        self._avoid_rect: QRect | None = None
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background:rgba(32,33,36,0.96); border-radius:14px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 16)
        layout.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(6)
        icon = QLabel("💡")
        icon.setStyleSheet("font-size:14px; background:transparent;")
        header.addWidget(icon)
        tag = QLabel("ΟΔΗΓΙΑ ΣΥΣΤΗΜΑΤΟΣ")
        tag.setStyleSheet(
            "color:#e8eaed; font-size:10.5px; font-weight:bold; "
            "letter-spacing:1px; background:transparent;"
        )
        header.addWidget(tag)
        header.addStretch()

    
        self.toggle_btn = QPushButton("▾")
        self.toggle_btn.setFixedSize(22, 22)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setStyleSheet(
            "QPushButton { background:transparent; color:#e8eaed; border:none; "
            "font-size:12px; } QPushButton:hover { background:#3c4043; border-radius:11px; }"
        )
        self.toggle_btn.clicked.connect(self.toggle_collapsed)
        header.addWidget(self.toggle_btn)
        layout.addLayout(header)

        self.text_label = QLabel("")
        self.text_label.setWordWrap(True)
        self.text_label.setTextFormat(Qt.TextFormat.RichText)
        self.text_label.setStyleSheet("color:white; font-size:15px; font-weight:500; background:transparent;")
        layout.addWidget(self.text_label)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 130))
        self.setGraphicsEffect(shadow)

        self.hide()

    def toggle_collapsed(self) -> None:
        self._collapsed = not self._collapsed
        self.toggle_btn.setText("▸" if self._collapsed else "▾")
        self.text_label.setVisible(not self._collapsed)
        self.setFixedWidth(200 if self._collapsed else 340)
        self.adjustSize()
        if self.parent() is not None:
            self.reposition(self.parent().size())

    def enterEvent(self, event) -> None:
        self.setStyleSheet("background:rgba(32,33,36,0.35); border-radius:14px;")
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.setStyleSheet("background:rgba(32,33,36,0.96); border-radius:14px;")
        super().leaveEvent(event)

    def set_avoid_rect(self, rect: QRect | None) -> None:
        self._avoid_rect = rect
        if self.parent() is not None:
            self.reposition(self.parent().size())

    def set_text(self, text: str) -> None:
        if text:
            self.text_label.setText(f"<div style='line-height:150%;'>{text}</div>")
            self.adjustSize()
            self.show()
            self.raise_()
        else:
            self.hide()

    def reposition(self, parent_size) -> None:
        margin = 28
        w, h = self.width(), self.height()
        candidates = [
            (max(margin, parent_size.width() - w - margin),
             max(margin, parent_size.height() - h - margin)),          # κάτω δεξιά
            (margin, max(margin, parent_size.height() - h - margin)),  # κάτω αριστερά
            (max(margin, parent_size.width() - w - margin), margin),   # πάνω δεξιά
            (margin, margin),                                           # πάνω αριστερά
        ]
        if self._avoid_rect is None or not self._avoid_rect.isValid():
            self.move(*candidates[0])
            return

        def overlap(pos) -> int:
            box = QRect(QPoint(*pos), self.size())
            inter = box.intersected(self._avoid_rect)
            return inter.width() * inter.height() if inter.isValid() else 0

        best = min(candidates, key=overlap)
        self.move(*best)


class BrowserChromeWindow(QWidget):

    TAB_URLS = {
        0: "https://mail.demo.test/inbox",
        1: "https://bank.demo.test/dashboard",
        2: "https://rantevou.demo.test/login",
        3: "https://governmentathome.demo.test/login",
        4: "https://teams.demo.test/chat",
    }

    exit_requested = pyqtSignal()
    tab_changed = pyqtSignal()

    def __init__(self, email_widget: QWidget, banking_widget: QWidget, health_widget: QWidget,
                 gov_widget: QWidget, teams_widget: QWidget | None = None, parent=None):
        super().__init__(parent)
        self._build_ui(email_widget, banking_widget, health_widget, gov_widget, teams_widget)

    def _build_ui(self, email_widget: QWidget, banking_widget: QWidget, health_widget: QWidget,
                  gov_widget: QWidget, teams_widget: QWidget | None = None) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(_TAB_STYLE)
        self.tabs.addTab(email_widget, "📧  Demo Mail")
        self.tabs.addTab(banking_widget, "🏦  SecureBank Demo")
        self.tabs.addTab(health_widget, "🏥  e-Ραντεβού Demo")
        self.tabs.addTab(gov_widget, "🖋️  GovAtHome Demo")
        if teams_widget is not None:
            self.tabs.addTab(teams_widget, "💬  Ομάδες")
        bar = self.tabs.tabBar()
        for i in range(self.tabs.count()):
            bar.setTabTextColor(i, QColor(_TAB_COLORS[i % len(_TAB_COLORS)]))
        self.tabs.currentChanged.connect(self._sync_address_bar)

        self.exit_button = QPushButton("✕")
        self.exit_button.setFixedSize(28, 28)
        self.exit_button.setStyleSheet(
            "QPushButton { background:#eceff2; color:#14181d; border:1px solid #9aa2ab; "
            "border-radius:6px; font-size:13px; font-weight:bold; } "
            "QPushButton:hover { background:#fce8e6; color:#c5221f; }"
        )
        self.exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_button.clicked.connect(self.exit_requested.emit)

        exit_container = QWidget()
        exit_layout = QHBoxLayout(exit_container)
        exit_layout.setContentsMargins(4, 4, 14, 4)  # 14px δεξί margin -- fix για clipping
        exit_layout.addWidget(self.exit_button)
        self.tabs.setCornerWidget(exit_container, Qt.Corner.TopRightCorner)

        # fake toolbar: address bar πάνω από το tab content 
        toolbar = QWidget()
        toolbar.setStyleSheet(_TOOLBAR_STYLE)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 6, 12, 6)

        nav_back = QLabel("←")
        nav_fwd = QLabel("→")
        nav_reload = QLabel("⟳")
        for nav in (nav_back, nav_fwd, nav_reload):
            nav.setStyleSheet(_NAV_ICON_STYLE)

        lock = QLabel("🔒")
        lock.setStyleSheet("color:#0f7b3f; font-size:14px; padding:0 2px 0 8px;")

        self.address_bar = QLineEdit()
        self.address_bar.setReadOnly(True)
        self.address_bar.setStyleSheet(_ADDRESS_BAR_STYLE)

        toolbar_layout.addWidget(nav_back)
        toolbar_layout.addWidget(nav_fwd)
        toolbar_layout.addWidget(nav_reload)
        toolbar_layout.addWidget(lock)
        toolbar_layout.addWidget(self.address_bar, stretch=1)

        outer.addWidget(toolbar)
        outer.addWidget(self.tabs, stretch=1)

        self.instruction_overlay = InstructionOverlay(self)

        self._sync_address_bar(self.tabs.currentIndex())

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.instruction_overlay.reposition(self.size())

    def set_instruction(self, text: str) -> None:
        self.instruction_overlay.set_text(text)
        self.instruction_overlay.reposition(self.size())

    def set_instruction_avoid_rect(self, rect: QRect | None) -> None:
        self.instruction_overlay.set_avoid_rect(rect)

    def _sync_address_bar(self, index: int) -> None:
        self.address_bar.setText(self.TAB_URLS.get(index, ""))
        self.tab_changed.emit()

    def set_active_tab(self, screen: str) -> None:
        """screen: 'email' | 'banking' | 'health' | 'gov'."""
        index = {"email": 0, "banking": 1, "health": 2, "gov": 3, "teams": 4}.get(screen, 0)
        self.tabs.setCurrentIndex(index)

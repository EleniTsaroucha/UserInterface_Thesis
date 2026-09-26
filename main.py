from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QRect, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QApplication, QMainWindow

from block_sequencer import BlockSequencer
from browser_chrome import BrowserChromeWindow
from desktop_shell import DesktopShell, AppSpec
from gmail_screen import GmailScreen
from instructions import get_instruction
from login_screen import LoginScreen
from mail_stimuli import setup_stimuli_for_profile
from mock_screens import MockBankingScreen, MockHealthScreen, GovAtHomeScreen
from profiles import PROFILE_IDS, assign_profile, credentials_sheet
from protocol_runner import ProtocolRunner
from session_config import generate_sensitive_content
from session_logger import SessionLogger, SensitiveFieldEvent
from teams_screen import TeamsScreen
import time


EXPERIMENTER_EXIT_KEYS = {Qt.Key.Key_Q}
EXPERIMENTER_TEST_NOTIFICATION_KEY = Qt.Key.Key_T
EXPERIMENTER_EXIT_MODIFIERS = Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier

_TAB_SCREEN_NAMES = ["email", "banking", "health", "gov"]


def resolve_screen(app: QApplication, index: int | None = None):
    """Η οθόνη στην οποία τρέχει το πείραμα. Χωρίς ρητό index επιστρέφει την
    κύρια οθόνη του συστήματος -- ώστε σε διάταξη δύο οθονών το περιβάλλον να
    ανοίγει πάντα στην ίδια, ανεξάρτητα από το πού βρίσκεται ο δείκτης."""
    screens = app.screens()
    if index is not None and 0 <= index < len(screens):
        return screens[index]
    return app.primaryScreen()


def show_fullscreen_on(widget, screen) -> None:
    """Πλήρης οθόνη σε ΣΥΓΚΕΚΡΙΜΕΝΗ οθόνη. Σκέτο showFullScreen() ανοίγει σε
    όποια οθόνη τύχει να θεωρεί ενεργή το παράθυρο, που σε διάταξη δύο οθονών
    δεν είναι ντετερμινιστικό."""
    widget.winId()          # δημιουργεί το native handle
    handle = widget.windowHandle()
    if handle is not None and screen is not None:
        handle.setScreen(screen)
    if screen is not None:
        widget.setGeometry(screen.geometry())
    widget.showFullScreen()


class MockExperimentWindow(QMainWindow):

    # Εκπέμπεται όταν η συνεδρία τελειώνει ή διακόπτεται. Το main() αποφασίζει
    # τι ακολουθεί -- το παράθυρο δεν τερματίζει πια μόνο του την εφαρμογή.
    session_ended = pyqtSignal(str)
    def __init__(self, session_id: str, counterbalance_offset: int, log_dir: Path,
                 protocol_mode: bool = False, profile_id: str = "A",
                 logger: SessionLogger | None = None):
        super().__init__()
        self.setWindowTitle(f"Demo Mail — Πειραματικό Περιβάλλον (προφίλ {profile_id})")

        
        self.session_id = session_id
        self.profile_id = profile_id
        self.protocol_mode = protocol_mode
        self.content = generate_sensitive_content(session_id, profile_id=profile_id)
        self.sequencer = None if protocol_mode else BlockSequencer(
            session_id, counterbalance_offset, profile_id=profile_id)
        self.runner = ProtocolRunner(session_id) if protocol_mode else None
        self.logger = logger if logger is not None else SessionLogger(log_dir, session_id)
        self.logger.set_profile(profile_id)

        self.email_screen = GmailScreen(self.content)
        self.banking_screen = MockBankingScreen(self.content)
        self.health_screen = MockHealthScreen(self.content)
        self.gov_screen = GovAtHomeScreen(self.content)
        self.teams_screen = TeamsScreen(session_id=session_id)

        # Όλα τα 10 emails φορτώνονται ταυτόχρονα στα εισερχόμενα -- ο
        # συμμετέχων μπορεί να ανοίξει/απαντήσει σε όποιο θέλει, με όποια
        # σειρά θέλει, αντί να του παρουσιάζεται ένα τη φορά.
        self.email_screen.load_all_stimuli()

        self.browser = BrowserChromeWindow(
            self.email_screen, self.banking_screen, self.health_screen, self.gov_screen,
        )
        self.browser.exit_requested.connect(self._on_exit_requested)

        
        self.desktop = DesktopShell()
        self.desktop.register_app(
            AppSpec("browser", "Chrome", "🌐", "#1a73e8"), self.browser)
        self.desktop.register_app(
            AppSpec("teams", "Teams", "💬", "#5b5fc7"), self.teams_screen)
        self.desktop.add_decorative_shortcuts()
        self.desktop.shortcut_activated.connect(self._on_shortcut_activated)
        self.desktop.app_focused.connect(self._on_app_focused)
        self.desktop.notification_clicked.connect(self._on_notification_clicked)
        self.teams_screen.notification_raised.connect(self._on_teams_notification)
        self.teams_screen.unread_changed.connect(
            lambda n: self.desktop.set_badge("teams", n))
        self.setCentralWidget(self.desktop)

        self.email_screen.field_rendered.connect(self._on_field_rendered)
        self.banking_screen.field_rendered.connect(self._on_field_rendered)
        self.health_screen.field_rendered.connect(self._on_field_rendered)
        self.gov_screen.field_rendered.connect(self._on_field_rendered)
        self.teams_screen.field_rendered.connect(self._on_field_rendered)

        self.email_screen.action_performed.connect(self._on_user_action)
        self.banking_screen.action_performed.connect(self._on_user_action)
        self.health_screen.action_performed.connect(self._on_user_action)
        self.gov_screen.action_performed.connect(self._on_user_action)
        self.teams_screen.action_performed.connect(self._on_user_action)

        self.gov_screen.otp_requested.connect(self.email_screen.add_otp_email)

        self.browser.tab_changed.connect(self.email_screen.reset_copy_indicators)

        
        self.browser.tab_changed.connect(self._on_tab_changed)

        self.email_screen.reply_submitted.connect(self._on_reply_submitted)
        self.email_screen.draft_saved.connect(self._on_draft_saved)

        if self.sequencer is not None:
            self.sequencer.block_started.connect(self._on_block_started)
            self.sequencer.step_started.connect(self._on_step_started)
            self.sequencer.block_finished.connect(self._on_block_finished)
            self.sequencer.session_finished.connect(self._on_session_finished)
            self.sequencer.step_completed.connect(self._on_step_completed)
        if self.runner is not None:
            self.runner.trial_started.connect(self._on_trial_started)
            self.runner.trial_finished.connect(self._on_trial_finished)
            self.runner.attacker_window_opened.connect(self._on_attacker_window)
            self.runner.block_break.connect(self._on_block_break)
            self.runner.session_finished.connect(self._on_session_finished)

        self._current_block_index = 0
        self._current_condition_id = "baseline"
        self._current_step_id = ""

    # Qt slots 
    def _on_field_rendered(self, field_id: str, bbox: QRect, value: str) -> None:
        if field_id.startswith("email_"):
            origin_widget = self.email_screen
        elif field_id.startswith("teams_"):
            origin_widget = self.teams_screen
        elif field_id.startswith("bank_"):
            origin_widget = self.banking_screen
        elif field_id.startswith("health_"):
            origin_widget = self.health_screen
        else:
            origin_widget = self.gov_screen
        global_top_left = origin_widget.mapToGlobal(bbox.topLeft())

        event = SensitiveFieldEvent(
            timestamp=time.time(),
            session_id=self.session_id,
            block_index=self._current_block_index,
            condition_id=self._current_condition_id,
            step_id=self._current_step_id,
            sensitive_field_id=field_id,
            sensitive_value=value,
            bbox_x=global_top_left.x(),
            bbox_y=global_top_left.y(),
            bbox_w=bbox.width(),
            bbox_h=bbox.height(),
        )
        self.logger.log_field_shown(event)

    def _on_user_action(self, action_id: str) -> None:
        self.logger.log_user_action(
            self.session_id, self._current_block_index,
            self._current_condition_id, self._current_step_id, action_id,
        )
        print(f"  ↳ ενέργεια χρήστη: {action_id}")
        if self.sequencer is not None:
            self.sequencer.notify_action(action_id)
        if self.runner is not None:
            self.runner.notify_action(action_id)

    def _on_block_started(self, block_index: int, condition_id: str, is_baseline: bool) -> None:
        self._current_block_index = block_index
        self._current_condition_id = condition_id
        self.logger.log_block_boundary(self.session_id, block_index, condition_id, "block_started")

        self.browser.set_active_tab("email")
        self.banking_screen.reset_fields()
        self.health_screen.reset_fields()
        self.gov_screen.reset_fields()
        self.email_screen.reset_emails()
        self.teams_screen.reset_fields()
        self.browser.set_active_tab("email")

        QApplication.beep()

        label = "BASELINE (χωρίς παρατηρητή)" if is_baseline else f"Συνθήκη: {condition_id}"
        print(f"[block {block_index}] {label}")

    def _on_step_started(self, step_id: str, screen: str) -> None:
        self._current_step_id = step_id
        self.logger.log_step_boundary(
            self.session_id, self._current_block_index,
            self._current_condition_id, step_id,
        )
        self.browser.set_instruction(get_instruction(step_id, self.content))

    def _on_step_completed(self, step_id: str, completed_naturally: bool) -> None:
        self.logger.log_step_completion(
            self.session_id, self._current_block_index,
            self._current_condition_id, step_id, completed_naturally,
        )
        if not completed_naturally:
            print(f"  ⏱ TIMEOUT στο βήμα '{step_id}' -- ο συμμετέχων δεν ολοκλήρωσε την ενέργεια εγκαίρως.")

    def _on_tab_changed(self) -> None:
        index = self.browser.tabs.currentIndex()
        screens = [self.email_screen, self.banking_screen, self.health_screen,
                   self.gov_screen, self.teams_screen]
        previous = getattr(self, "_active_screen_index", None)
        if previous is not None and previous != index and 0 <= previous < len(screens):
            leaving = screens[previous]
            if hasattr(leaving, "on_tab_deactivated"):
                leaving.on_tab_deactivated()
        self._active_screen_index = index
        if 0 <= index < len(screens):
            screens[index].on_tab_activated()
            if self.sequencer is not None:
                self.sequencer.notify_tab_changed(_TAB_SCREEN_NAMES[index])
        # Το κουτί οδηγιών ξαναϋπολογίζει θέση ΜΕΤΑ το layout pass της νέας
        # καρτέλας -- αλλιώς θα μετρούσε τη γεωμετρία της προηγούμενης.
        QTimer.singleShot(60, self._sync_instruction_avoid_rect)

    def _on_trial_started(self, trial) -> None:
        self._current_block_index = trial.block_index
        self._current_condition_id = f"{trial.backend}_{trial.scenario}"
        self._current_step_id = "reading_task"
        self.logger.set_trial_context(trial.trial_index, trial.backend,
                                       trial.scenario, trial.stimulus_id)
        self.logger.log_trial_boundary(self.session_id, "trial_started")

        # Τα emails είναι ήδη όλα φορτωμένα στα εισερχόμενα (βλ.
        # load_all_stimuli στο __init__) -- δεν φορτώνουμε ένα τη φορά.
        # Η εναλλαγή backend/συνθήκης γίνεται αυτόματα από το ξεχωριστό
        # παράθυρο ελέγχου -- δεν χρειάζεται συγχρονισμός εδώ.
        self.teams_screen.start_incoming()
        self.desktop.open_app("browser")
        self.banking_screen.reset_fields()
        self.health_screen.reset_fields()
        self.gov_screen.reset_fields()
        self.browser.set_active_tab("email")
        total_trials = len(self.runner.trials) if self.runner is not None else trial.trial_index + 1
        self.browser.set_instruction(
            f"<b>Δοκιμή {trial.trial_index + 1}/{total_trials}</b><br>"
            "Διάβασε ένα email της επιλογής σου από τα εισερχόμενα και "
            "<b>απάντησε</b> στα ερωτήματά του.<br>"
            "<span style='color:#bdc1c6;'>Η απάντηση αποθηκεύεται αυτόματα στα "
            "Πρόχειρα, μπορείς να φύγεις και να επιστρέψεις.</span>"
        )
        QApplication.beep()
        print(f"[trial {trial.trial_index}] backend={trial.backend} "
              f"σενάριο={trial.scenario} κείμενο={trial.stimulus_id} "
              f"(attacker ~{self.runner.attacker_offsets_ms[trial.trial_index] // 1000}s)")

    def _on_attacker_window(self, trial, offset_ms: int) -> None:
        print(f"  ▶ ΕΙΣΟΔΟΣ ATTACKER τώρα (σενάριο {trial.scenario}, "
              f"{offset_ms // 1000}s από την έναρξη του trial)")

    def _on_trial_finished(self, trial, completed_naturally: bool) -> None:
        self.teams_screen.stop_incoming()
        self.logger.log_trial_boundary(self.session_id, "trial_finished")
        if not completed_naturally:
            print(f"  ⏱ TIMEOUT/παράκαμψη στο trial {trial.trial_index}")
        self.logger.clear_trial_context()

    def _on_block_break(self, block_index: int) -> None:
        self.browser.set_instruction(
            "<b>Διάλειμμα</b><br>Ολοκληρώθηκε ένα σύνολο δοκιμών. "
            "Ο πειραματιστής θα ρυθμίσει το επόμενο σύστημα καταγραφής."
        )
        print(f"[διάλειμμα] τέλος block {block_index}")

    def _on_reply_submitted(self, email_id: str, text: str) -> None:
        self.logger.log_reply(self.session_id, email_id, text)

    def _on_draft_saved(self, email_id: str, length: int) -> None:
        self.logger.log_user_action(
            self.session_id, self._current_block_index, self._current_condition_id,
            f"draft_len_{length}", "draft_saved",
        )

    def _on_app_focused(self, app_id: str) -> None:
        self.logger.log_user_action(
            self.session_id, self._current_block_index, self._current_condition_id,
            self._current_step_id, f"app_focus_{app_id}",
        )
        if app_id == "browser":
            self._on_tab_changed()
        elif app_id == "teams":
            self.teams_screen.on_tab_activated()
            self.email_screen.on_tab_deactivated()

    def _on_shortcut_activated(self, name: str) -> None:
        self.logger.log_user_action(
            self.session_id, self._current_block_index, self._current_condition_id,
            self._current_step_id, f"desktop_shortcut_{name.replace(chr(10), ' ')}",
        )

    def _on_teams_notification(self, title: str, body: str, chat_id: str, kind: str) -> None:
        icon = {"meeting": "📅", "deadline": "⏰"}.get(kind, "💬")
        self.desktop.show_notification("teams", title, body, chat_id, icon)
        self.logger.log_user_action(
            self.session_id, self._current_block_index, self._current_condition_id,
            self._current_step_id, f"notification_shown_{kind}",
        )

    def _on_notification_clicked(self, app_id: str, chat_id: str) -> None:
        if app_id == "teams":
            self.teams_screen.open_chat(chat_id)
        self.logger.log_user_action(
            self.session_id, self._current_block_index, self._current_condition_id,
            self._current_step_id, "notification_clicked",
        )

    def _sync_instruction_avoid_rect(self) -> None:
        index = self.browser.tabs.currentIndex()
        screens = [self.email_screen, self.banking_screen, self.health_screen, self.gov_screen]
        rect = None
        if 0 <= index < len(screens):
            screen = screens[index]
            if hasattr(screen, "content_rect"):
                local = screen.content_rect()
                if local is not None:
                    top_left = screen.mapTo(self.browser, local.topLeft())
                    rect = QRect(top_left, local.size())
        self.browser.set_instruction_avoid_rect(rect)

    def _on_block_finished(self, block_index: int) -> None:
        self.logger.log_block_boundary(
            self.session_id, block_index, self._current_condition_id, "block_finished"
        )

    def shutdown(self) -> None:
        """Σταματά ό,τι τρέχει με χρονιστή. Ο logger ΔΕΝ κλείνει εδώ: ζει όσο
        η εφαρμογή, ώστε διαδοχικές συνεδρίες να γράφουν στο ίδιο αρχείο αντί
        να το ξαναδημιουργούν από την αρχή."""
        self.teams_screen.stop_incoming()
        if self.sequencer is not None:
            self.sequencer.stop()
        if self.runner is not None:
            self.runner.stop()

    def _on_session_finished(self) -> None:
        self.shutdown()
        print("Η συνεδρία ολοκληρώθηκε.")
        self.session_ended.emit("completed")

    def _on_exit_requested(self) -> None:
        self.shutdown()
        print("Έξοδος μέσω κουμπιού -- επιστροφή στην επιλογή προφίλ.")
        self.session_ended.emit("aborted")

    def start(self, screen=None) -> None:
        show_fullscreen_on(self, screen)
        self.desktop.show_desktop()
        self.teams_screen.start_incoming()
        starter = self.runner.start if self.runner is not None else self.sequencer.start
        QTimer.singleShot(0, starter)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (event.key() == EXPERIMENTER_TEST_NOTIFICATION_KEY
                and event.modifiers() == EXPERIMENTER_EXIT_MODIFIERS):
            self.teams_screen.deliver_message(
                "maria", "Μαρία Νικολάου",
                "Δοκιμαστικό μήνυμα ελέγχου ειδοποιήσεων.", "message")
            print("Στάλθηκε δοκιμαστική ειδοποίηση.")
            return
        if (event.key() in EXPERIMENTER_EXIT_KEYS
                and event.modifiers() == EXPERIMENTER_EXIT_MODIFIERS):
            self.shutdown()
            print("Έξοδος πειραματιστή -- επιστροφή στην επιλογή προφίλ.")
            self.session_ended.emit("aborted")
            return
        super().keyPressEvent(event)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mock privacy-shield experiment environment")
    parser.add_argument("--session-id", required=True, help="Μοναδικό ID συμμετέχοντα/συνεδρίας, π.χ. P03")
    parser.add_argument("--counterbalance-offset", type=int, default=0,
                         help="Offset για rotation της σειράς των 8 συνθηκών (π.χ. index συμμετέχοντα mod 8)")
    parser.add_argument("--log-dir", type=Path, default=Path("./mock_experiment_logs"))
    parser.add_argument("--protocol", action="store_true",
                        help="Εκτέλεση των 9 trials ανάγνωσης/απάντησης του πειραματικού "
                             "πρωτοκόλλου, αντί της καθοδηγούμενης ροής 14 βημάτων")
    parser.add_argument("--profile", choices=list(PROFILE_IDS), default=None,
                        help="Κλείδωμα της οθόνης σύνδεσης σε συγκεκριμένο προφίλ. "
                             "Χωρίς αυτό, ο συμμετέχων επιλέγει ελεύθερα Α ή Β.")
    parser.add_argument("--reveal-passwords", action="store_true",
                        help="Εμφάνιση του κωδικού κάτω από κάθε πλακίδιο. ΜΟΝΟ για "
                             "πιλοτικές δοκιμές -- δεν χρησιμοποιείται σε πραγματική συνεδρία.")
    parser.add_argument("--screen", type=int, default=None,
                        help="Δείκτης οθόνης (0 = πρώτη). Χωρίς αυτό χρησιμοποιείται "
                             "η κύρια οθόνη του συστήματος.")
    parser.add_argument("--skip-login", action="store_true",
                        help="Παράκαμψη της οθόνης σύνδεσης (απαιτεί --profile ή "
                             "χρησιμοποιεί την αυτόματη ανάθεση).")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setStyleSheet("* { font-family: 'Segoe UI'; }")
    # Η οθόνη σύνδεσης παραμένει ζωντανή αλλά κρυμμένη όσο τρέχει η συνεδρία.
    # Χωρίς αυτό, το κλείσιμο του παραθύρου του πειράματος θα τερμάτιζε την
    # εφαρμογή πριν προλάβει να ξαναεμφανιστεί η επιλογή προφίλ.
    app.setQuitOnLastWindowClosed(False)
    screen = resolve_screen(app, args.screen)
    print(f"Οθόνη εκτέλεσης: {screen.name()} {screen.geometry().width()}x"
          f"{screen.geometry().height()}")

    print(credentials_sheet(args.session_id))
    print()

    logger = SessionLogger(args.log_dir, args.session_id)

    live: dict[str, object] = {}

    def quit_app() -> None:
        print("\nΤερματισμός προγράμματος.")
        window = live.pop("window", None)
        if window is not None:
            window.shutdown()
            window.close()
        logger.close()
        widget = live.pop("login", None)
        if widget is not None:
            widget.close()
        app.quit()

    def return_to_login(reason: str) -> None:
        """Το X (ή Ctrl+Alt+Q) της συνεδρίας δεν κλείνει το πρόγραμμα: γυρίζει
        στην επιλογή προφίλ, ώστε να ξεκινήσει αμέσως η επόμενη εκτέλεση."""
        logger.log_trial_boundary(args.session_id, f"session_{reason}")
        window = live.pop("window", None)
        login = live.get("login")
        if login is None:
            # --skip-login: δεν υπάρχει οθόνη προφίλ να επιστρέψουμε.
            quit_app()
            return
        login.reset()
        show_fullscreen_on(login, screen)
        login.raise_()
        login.activateWindow()
        if window is not None:
            window.close()
            window.deleteLater()

    def launch(profile_id: str) -> None:
        print(f"\n=== Είσοδος με προφίλ {profile_id} -- έναρξη συνεδρίας ===\n")
        # Φόρτωση των emails για το επιλεγμένο profile
        setup_stimuli_for_profile(profile_id)
        window = MockExperimentWindow(
            args.session_id, args.counterbalance_offset, args.log_dir,
            protocol_mode=args.protocol, profile_id=profile_id, logger=logger,
        )
        live["window"] = window
        window.session_ended.connect(return_to_login)
        window.start(screen)
        login = live.get("login")
        if login is not None:
            login.hide()          # κρύβεται, δεν κλείνει -- θα ξαναχρειαστεί

    if args.skip_login:
        launch(args.profile or assign_profile(args.session_id))
    else:
        login = LoginScreen(args.session_id, required_profile=args.profile,
                            reveal_passwords=args.reveal_passwords)
        live["login"] = login
        login.action_performed.connect(
            lambda action_id: logger.log_login_event(
                args.session_id, action_id, action_id.rsplit("_", 1)[-1])
        )
        login.login_succeeded.connect(launch)

        def abort_from_login() -> None:
            print("\nΈξοδος από την οθόνη σύνδεσης.")
            quit_app()

        login.exit_requested.connect(abort_from_login)
        show_fullscreen_on(login, screen)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

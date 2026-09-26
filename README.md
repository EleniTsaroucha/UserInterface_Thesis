# Privacy Shield — Mock Experimental Environment

A simulated desktop environment used in the user study of the diploma thesis *Development of a visual privacy protection system through dynamic gaze tracking and shoulder surfing detection*, Department of Computer Engineering and Informatics, University of Patras.

The protection system itself is in a separate repository: [PrivacyShield_Thesis](https://github.com/EleniTsaroucha/PrivacyShield_Thesis).

---

## Purpose

To measure how much sensitive information a shoulder surfer can recover from a screen, the displayed information must be controlled and known in advance. This environment provides that control:

- **Realistic tasks.** It presents a simulated desktop with a web browser, a webmail client, three online services and a chat application, in which the participant performs realistic tasks (reading and answering emails, logging in, making a payment, booking an appointment, signing a document).
- **Known content.** All sensitive content (credentials, IBANs, tax and social security numbers) is fictitious and generated deterministically from the session ID.
- **Ground-truth logging.** Every time a sensitive field is rendered, its value and on-screen bounding box are logged, so that an observer's notes can be scored against what was actually visible, and so that the field positions can be related to gaze data.

In the experiments, this environment ran inside a virtual machine, while Dynamic Privacy Shield ran on the host.

> **Disclaimer.** All services, organizations, persons, credentials and identifiers in this environment are fictitious. The mock services are labelled *DEMO / TEST*, run entirely locally, perform no network communication, and are not affiliated with any real organization.

## Environment overview

| Component | Description |
|---|---|
| OS-style login | Two user profiles (A and B), each with its own fictitious content |
| Desktop | Wallpaper, desktop icons, taskbar, start menu, toast notifications |
| Browser | Four tabs: Demo Mail, SecureBank Demo, e-Ραντεβού Demo, GovAtHome Demo |
| Demo Mail | Webmail with 13 task emails per profile, mixed with routine "noise" emails; drafts, replies and PDF-style attachments |
| SecureBank Demo | Login and bill payment |
| e-Ραντεβού Demo | Portal and TaxisNet-style authentication, appointment booking |
| GovAtHome Demo | Portal and TaxisNet-style authentication, document signing with an email one-time code, protocol number |
| Teams-style chat | Background conversations and scheduled distractor messages |

The two profiles correspond to two work personas: **A**, a machine learning engineer, and **B**, a systems / DevOps engineer. Each profile has its own set of 13 task emails.

### Deterministic content

- Sensitive content is generated with a random generator seeded by the SHA-256 hash of the session ID (and profile). The same session ID always reproduces the same content.
- The sequence of distractor chat messages is also seeded by the session ID, so it can be reproduced and reported.

## Requirements

- Python 3 
- PyQt6

```powershell
pip install -r requirements.txt
```

## Usage

```powershell
python main.py --session-id P07 --protocol --log-dir .\logs
```

At start-up, a credentials sheet for both profiles of the session is printed to the console. It can also be printed separately, e.g. to prepare reference sheets for scoring:

```powershell
python profiles.py P07
```

The OS-style login passwords are `1234` (profile A) and `5678` (profile B).

### Command-line options

| Option | Description |
|---|---|
| `--session-id` | Session / participant ID (required); seeds all generated content |
| `--protocol` | Protocol mode: reading/reply trials with an attacker window (see below) |
| `--log-dir` | Directory for session logs (default: `./mock_experiment_logs`) |
| `--profile A\|B` | Restrict the login screen to one profile |
| `--skip-login` | Skip the login screen |
| `--screen N` | Index of the display to use (default: primary display) |
| `--counterbalance-offset` | Rotation offset for the block order of the guided mode |
| `--reveal-passwords` | Show login passwords under the profile tiles — pilot testing only |

### Modes

- **Protocol mode (`--protocol`)**. The session is organized into trials. All task emails are available in the inbox at once, and the participant chooses which to open and answer. Each trial has a maximum duration of 6 minutes, and a deterministic "attacker window" (60–150 s after the trial starts) is logged as the moment the observer should enter.
- **Guided mode (default).** A scripted sequence of 14 steps (read credentials, log in to the bank, pay, book an appointment, sign a document with a one-time code), with on-screen instructions and per-step time limits.

### Experimenter controls

| Key / control | Action |
|---|---|
| `Ctrl+Alt+Q` | End the current session and return to profile selection (on the login screen: exit) |
| `Ctrl+Alt+T` | Send a test chat notification |
| ✕ in the browser | End the session and return to profile selection |
| ✕ on the login screen | Exit the program (with confirmation) |

## Logged data

Each run writes one CSV file per session, `<session-id>_sensitive_events.csv`, in the log directory. Every row has a `row_type`:

| Row type | Content |
|---|---|
| `clock_sync` | Wall-clock time and `perf_counter` at start-up, for aligning with other recordings |
| `sensitive_field` | ID, value and screen-coordinate bounding box of a rendered sensitive field |
| `user_action` | Participant actions (tab changes, logins, replies, notifications, …) |
| `os_login` | Profile selection and login attempts |
| `trial_started` / `trial_finished` | Trial boundaries (protocol mode) |
| `step_started` / `step_completed` | Step boundaries and whether each step completed or timed out (guided mode) |
| `email_reply` | Full text of each sent reply |

Bounding boxes are in global screen coordinates, so they can be matched against gaze coordinates recorded on the same display.

## Data and privacy

Session logs are **not** included in this repository. Although the sensitive content is fictitious, the logs also contain free text typed by participants (email replies and other free-text fields), which may include personal data.

## Assets

The mock government pages can display logos from an `assets/` directory. These files are **not** included in this repository. When they are missing, the application renders neutral text placeholders instead.

## Citation

```bibtex
@mastersthesis{tsaroucha2026privacyshield,
  author = {Tsaroucha, Eleni},
  title  = {Development of a visual privacy protection system through dynamic gaze tracking and shoulder surfing detection},
  school = {Department of Computer Engineering and Informatics, University of Patras},
  type   = {Diploma thesis},
  year   = {2026}
}
```

## Author

Eleni Tsaroucha, Department of Computer Engineering and Informatics, University of Patras.


"""OBS Connection page."""

from __future__ import annotations

import customtkinter as ctk

PANEL = "#111111"
CARD = "#171717"
GOLD = "#E0AA36"
GOLD_DARK = "#9A6B16"


def _card(parent, title, row, column):
    frame = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14)
    frame.grid(row=row, column=column, padx=7, pady=7, sticky="nsew")
    ctk.CTkLabel(
        frame, text=title, text_color=GOLD,
        font=ctk.CTkFont(size=16, weight="bold"),
    ).pack(anchor="w", padx=16, pady=(14, 8))
    return frame


def _entry(parent, label, variable, hidden=False):
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=5)
    ctk.CTkLabel(row, text=label, width=155, anchor="w", text_color="#BCA870").pack(side="left")
    entry = ctk.CTkEntry(row, textvariable=variable, show="*" if hidden else "")
    entry.pack(side="left", fill="x", expand=True)
    return entry, row


def show_obs_connection_page(app, controller):
    app.set_active("OBS Connection")
    app.clear_main()
    app.page_title("OBS Connection")

    root = ctk.CTkFrame(app.main, fg_color=PANEL, corner_radius=18)
    root.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)

    status = ctk.CTkFrame(root, fg_color="#15130F", corner_radius=12)
    status.grid(row=0, column=0, columnspan=2, padx=14, pady=(14, 5), sticky="ew")
    app.obs_connection_status_label = ctk.CTkLabel(
        status, text="● Status wird geprüft …", text_color="#E0B86A",
        font=ctk.CTkFont(size=15, weight="bold"),
    )
    app.obs_connection_status_label.pack(side="left", padx=14, pady=11)
    app.obs_connection_detail_label = ctk.CTkLabel(
        status, text="", text_color="#9B927D", anchor="e",
    )
    app.obs_connection_detail_label.pack(side="right", padx=14, pady=11)

    connection = _card(root, "Verbindung", 1, 0)
    _entry(connection, "Host", app.host)
    _entry(connection, "Port", app.port)
    password_entry, password_row = _entry(connection, "Passwort", app.password, hidden=True)
    app.obs_password_entry = password_entry
    app.obs_password_toggle = ctk.CTkButton(
        password_row, text="ANZEIGEN", width=88, fg_color="#333333",
        command=controller.toggle_password,
    )
    app.obs_password_toggle.pack(side="left", padx=(8, 0))
    _entry(connection, "Szene (optional)", app.scene_name)
    ctk.CTkLabel(
        connection,
        text="Ohne Szenenname verwendet VADAFOK automatisch die aktive OBS-Programmszene.",
        text_color="#827A67", wraplength=650, justify="left",
    ).pack(anchor="w", padx=16, pady=(6, 10))

    buttons = ctk.CTkFrame(connection, fg_color="transparent")
    buttons.pack(fill="x", padx=16, pady=(0, 15))
    ctk.CTkButton(
        buttons, text="VERBINDEN / NEU VERBINDEN", fg_color=GOLD,
        text_color="#111111", hover_color=GOLD_DARK, command=controller.connect,
    ).pack(side="left", fill="x", expand=True, padx=(0, 5))
    ctk.CTkButton(
        buttons, text="TRENNEN", fg_color="#6B2929", command=controller.disconnect,
    ).pack(side="left", padx=5)
    ctk.CTkButton(
        buttons, text="STATUS PRÜFEN", fg_color="#333333", command=controller.test_connection,
    ).pack(side="left", padx=(5, 0))

    mappings = _card(root, "VADAFOK-Quellen", 2, 0)
    for label, variable in (
        ("Caption Group", app.caption_group),
        ("Text Source", app.caption_text),
        ("Banner Source", app.caption_banner_source),
        ("Render Source", app.caption_render_source),
        ("Scene Card Source", app.scene_card_source),
        ("Stream Effect Source", app.stream_effect_source),
    ):
        _entry(mappings, label, variable)
    ctk.CTkButton(
        mappings, text="EINSTELLUNGEN SPEICHERN", fg_color="#333333",
        command=app.save_config,
    ).pack(anchor="e", padx=16, pady=(8, 15))

    diagnostics = _card(root, "Diagnose", 1, 1)
    ctk.CTkLabel(
        diagnostics,
        text=("Prüft die aktive oder konfigurierte Szene und sucht die benötigten Quellen "
              "auch innerhalb von OBS-Gruppen."),
        text_color="#9B927D", wraplength=680, justify="left",
    ).pack(anchor="w", padx=16, pady=(0, 10))
    ctk.CTkButton(
        diagnostics, text="SZENE & QUELLEN PRÜFEN", fg_color=GOLD,
        text_color="#111111", hover_color=GOLD_DARK,
        command=controller.diagnose_sources,
    ).pack(fill="x", padx=16, pady=(0, 10))
    app.obs_diagnostics_list = ctk.CTkScrollableFrame(
        diagnostics, fg_color="#0D0D0D", corner_radius=10,
    )
    app.obs_diagnostics_list.pack(fill="both", expand=True, padx=16, pady=(0, 15))

    help_card = _card(root, "Wenn keine Verbindung möglich ist", 2, 1)
    ctk.CTkLabel(
        help_card,
        text=("1. OBS öffnen\n"
              "2. Werkzeuge → WebSocket-Servereinstellungen\n"
              "3. WebSocket-Server aktivieren\n"
              "4. Port und Passwort hier identisch eintragen\n\n"
              "Standard-Port von OBS WebSocket 5 ist 4455."),
        text_color="#D9C58C", justify="left", anchor="nw",
    ).pack(fill="both", expand=True, padx=16, pady=(0, 15))

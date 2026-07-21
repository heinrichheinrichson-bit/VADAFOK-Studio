"""Settings page construction for VADAFOK Studio.

The application object keeps the existing state variables and callbacks. This
module owns only the page layout, preserving the previous behavior exactly.
"""

import customtkinter as ctk

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
PANEL = "#111111"


def show_settings_page(app):
    """Build and display the existing Settings page for *app*."""
    app.set_active("Settings")
    app.clear_main()
    app.page_title("Settings")

    box = ctk.CTkScrollableFrame(app.main, fg_color=PANEL, corner_radius=18)
    box.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    box.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        box,
        text="VADAFOK Projektordner",
        text_color=GOLD,
        font=ctk.CTkFont(size=18, weight="bold"),
    ).grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")

    folder_row = ctk.CTkFrame(box, fg_color="transparent")
    folder_row.grid(row=1, column=0, sticky="ew", padx=24, pady=8)
    folder_row.grid_columnconfigure(0, weight=1)

    ctk.CTkEntry(folder_row, textvariable=app.project_folder).grid(
        row=0, column=0, sticky="ew"
    )
    ctk.CTkButton(
        folder_row,
        text="Durchsuchen...",
        fg_color=GOLD,
        text_color="#111111",
        hover_color=GOLD_DARK,
        command=app.browse_project_folder,
    ).grid(row=0, column=1, padx=(8, 0))

    card_output_box = ctk.CTkFrame(
        box, fg_color="#0B0B0B", corner_radius=12,
        border_color="#3A2A0D", border_width=1,
    )
    card_output_box.grid(row=2, column=0, sticky="ew", padx=24, pady=(18, 8))
    card_output_box.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        card_output_box, text="Card Creator Output", text_color=GOLD,
        font=ctk.CTkFont(size=17, weight="bold"),
    ).grid(row=0, column=0, columnspan=4, padx=16, pady=(14, 3), sticky="w")

    ctk.CTkLabel(card_output_box, text="Single card folder", text_color="#BCA870").grid(row=1, column=0, padx=16, pady=8, sticky="w")
    ctk.CTkEntry(card_output_box, textvariable=app.card_output_folder).grid(row=1, column=1, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(card_output_box, text="BROWSE...", width=105, fg_color="#333333", hover_color="#444444", command=app.browse_card_output_folder).grid(row=1, column=2, padx=4, pady=8)
    ctk.CTkButton(card_output_box, text="OPEN", width=80, fg_color="#333333", hover_color="#444444", command=app.open_card_output_folder).grid(row=1, column=3, padx=(4, 16), pady=8)

    ctk.CTkLabel(card_output_box, text="Batch output folder", text_color="#BCA870").grid(row=2, column=0, padx=16, pady=8, sticky="w")
    ctk.CTkEntry(card_output_box, textvariable=app.card_batch_output_folder).grid(row=2, column=1, padx=8, pady=8, sticky="ew")
    ctk.CTkButton(card_output_box, text="BROWSE...", width=105, fg_color="#333333", hover_color="#444444", command=app.browse_card_batch_output_folder).grid(row=2, column=2, padx=4, pady=8)
    ctk.CTkButton(card_output_box, text="OPEN", width=80, fg_color="#333333", hover_color="#444444", command=app.open_card_batch_output_folder).grid(row=2, column=3, padx=(4, 16), pady=8)

    ctk.CTkCheckBox(card_output_box, text="Ask for output location before rendering", variable=app.card_ask_output_location).grid(row=3, column=0, columnspan=4, padx=16, pady=(8, 14), sticky="w")

    stream_effect_box = ctk.CTkFrame(
        box,
        fg_color="#0B0B0B",
        corner_radius=12,
        border_color="#3A2A0D",
        border_width=1,
    )
    stream_effect_box.grid(row=3, column=0, sticky="ew", padx=24, pady=(18, 8))
    stream_effect_box.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        stream_effect_box,
        text="OBS Stream Effect",
        text_color=GOLD,
        font=ctk.CTkFont(size=17, weight="bold"),
    ).grid(row=0, column=0, columnspan=2, padx=16, pady=(14, 3), sticky="w")

    ctk.CTkLabel(
        stream_effect_box,
        text="Media Source name",
        text_color="#BCA870",
    ).grid(row=1, column=0, padx=16, pady=(6, 14), sticky="w")

    ctk.CTkEntry(
        stream_effect_box,
        textvariable=app.stream_effect_source,
        placeholder_text="VADAFOK Stream Effect",
    ).grid(row=1, column=1, padx=(8, 16), pady=(6, 14), sticky="ew")

    voice_box = ctk.CTkFrame(
        box,
        fg_color="#0B0B0B",
        corner_radius=12,
        border_color="#3A2A0D",
        border_width=1,
    )
    voice_box.grid(row=4, column=0, sticky="ew", padx=24, pady=(18, 8))
    voice_box.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        voice_box,
        text="Voice Trigger — Quick Caption",
        text_color=GOLD,
        font=ctk.CTkFont(size=17, weight="bold"),
    ).grid(row=0, column=0, columnspan=3, padx=16, pady=(14, 3), sticky="w")

    ctk.CTkLabel(
        voice_box,
        text=(
            "Lokale Windows-Spracherkennung. Der Befehl öffnet exakt "
            "dasselbe Quick-Caption-Fenster wie F8. Es wird kein Audio an OBS gesendet."
        ),
        text_color="#999999",
        wraplength=820,
        justify="left",
    ).grid(row=1, column=0, columnspan=3, padx=16, pady=(0, 10), sticky="w")

    ctk.CTkCheckBox(
        voice_box,
        text="Enable Voice Trigger",
        variable=app.voice_enabled,
        command=app.toggle_voice_trigger,
    ).grid(row=2, column=0, padx=16, pady=8, sticky="w")

    ctk.CTkLabel(voice_box, text="Command", text_color="#BCA870").grid(
        row=3, column=0, padx=16, pady=8, sticky="w"
    )
    command_entry = ctk.CTkEntry(voice_box, textvariable=app.voice_trigger_phrase)
    command_entry.grid(row=3, column=1, padx=8, pady=8, sticky="ew")

    ctk.CTkButton(
        voice_box,
        text="TEST F8 ACTION",
        width=140,
        fg_color="#333333",
        hover_color="#444444",
        command=app.test_voice_trigger,
    ).grid(row=3, column=2, padx=(8, 16), pady=8)

    ctk.CTkLabel(
        voice_box, text="Recognition culture", text_color="#BCA870"
    ).grid(row=4, column=0, padx=16, pady=8, sticky="w")
    culture_entry = ctk.CTkEntry(
        voice_box,
        textvariable=app.voice_culture,
        placeholder_text="de-DE",
    )
    culture_entry.grid(row=4, column=1, padx=8, pady=8, sticky="ew")

    ctk.CTkButton(
        voice_box,
        text="RESTART LISTENER",
        width=140,
        fg_color="#333333",
        hover_color="#444444",
        command=app.restart_voice_trigger,
    ).grid(row=4, column=2, padx=(8, 16), pady=8)

    ctk.CTkLabel(voice_box, text="Status:", text_color="#BCA870").grid(
        row=5, column=0, padx=16, pady=(8, 3), sticky="w"
    )
    ctk.CTkLabel(
        voice_box,
        textvariable=app.voice_status_var,
        text_color="#8FE6A0",
        wraplength=700,
        justify="left",
    ).grid(row=5, column=1, columnspan=2, padx=8, pady=(8, 3), sticky="w")

    ctk.CTkLabel(voice_box, text="Last heard:", text_color="#BCA870").grid(
        row=6, column=0, padx=16, pady=(3, 14), sticky="w"
    )
    ctk.CTkLabel(
        voice_box,
        textvariable=app.voice_last_heard_var,
        text_color="#CFCFCF",
        wraplength=700,
        justify="left",
    ).grid(row=6, column=1, columnspan=2, padx=8, pady=(3, 14), sticky="w")

    ctk.CTkButton(
        box,
        text="SAVE SETTINGS",
        height=42,
        fg_color=GOLD,
        text_color="#111111",
        hover_color=GOLD_DARK,
        command=app.save_config,
    ).grid(row=5, column=0, padx=24, pady=(10, 24), sticky="w")

    return box

# VADAFOK Studio 1.0 Phase A

## Ziel

Studio 1.0 beginnt mit dem neuen **Banner Profile System**.

Ab jetzt sollen Banner nicht mehr nur als Bilder behandelt werden, sondern als intelligente Objekte mit eigenen Profilen.

## Neu in Phase A

- Neue Datei:

```text
data/banner_profiles.json
```

- Neues Modul:

```text
vadafok_studio/core/banner_profiles.py
```

- Neuer Menüpunkt:

```text
Banner Profiles
```

- Banner können ein Standardprofil bekommen.
- Library zeigt bei Bannern mit Profil ein kleines ✓.

## Was Phase A noch nicht macht

Noch kein Mausrahmen.

Noch kein echter Banner Editor.

Noch keine automatische Nutzung der Profile im Renderer.

Das kommt in den nächsten Phasen:

- Phase B: Banner Editor Oberfläche
- Phase C: Mausrahmen ziehen
- Phase D: Live Card nutzt Profile automatisch

## Test

1. Studio starten.
2. Library laden.
3. Menüpunkt `Banner Profiles` öffnen.
4. Prüfen, ob Banner angezeigt werden.
5. Für 1–2 Banner `CREATE DEFAULT` klicken.
6. Zur Library zurückgehen.
7. Prüfen, ob bei diesen Bannern ein ✓ erscheint.

## Git

Erst committen, wenn Phase A funktioniert.

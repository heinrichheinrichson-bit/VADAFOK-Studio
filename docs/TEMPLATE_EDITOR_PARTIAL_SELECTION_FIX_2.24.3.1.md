# VADAFOK Studio 2.24.3.1 – Partial Selection Test & Apply Fix

## Ursache

Der Controller verwendet absichtlich eine sichere Abfrage:

- Refresh-Methode mit `getattr` ermitteln;
- nur aufrufen, wenn sie tatsächlich callable ist;
- bei teilweise aktualisierten Installationen auf den alten Seitenaufbau
  zurückfallen.

Der erste Test erwartete stattdessen fälschlich einen direkten Methodenaufruf
als exakten Quelltext.

## Korrektur

- Test prüft jetzt das tatsächliche sichere Controller-Verhalten.
- Apply-Patcher zeigt bei Fehlern vollständige Testausgabe und Traceback.
- Programmfunktion und geplanter Partial Refresh bleiben unverändert.

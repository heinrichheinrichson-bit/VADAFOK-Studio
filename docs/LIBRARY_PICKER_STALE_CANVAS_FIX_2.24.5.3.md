# VADAFOK Studio 2.24.5.3 – Library Picker – Stale Canvas Fix

## Laufzeitursache

Beim Öffnen der Library wird die Template-Editor-Seite zerstört. Das Attribut
`template_canvas` bleibt jedoch noch vorhanden und verweist auf ein nicht mehr
existierendes Widget.

Die bisherige Hintergrundübernahme versuchte zuerst, diesen alten Canvas neu zu
zeichnen. Der Callback brach dadurch ab, bevor die automatische Rückkehr zum
Template Editor erreicht wurde.

## Korrektur

- Rückkehrbedarf wird vor der Hintergrundübernahme ermittelt.
- Im Picker-Modus wird der zerstörte Canvas nicht aktualisiert.
- Picker-Zustand wird anschließend beendet.
- Template Editor wird neu aufgebaut.
- Der neue Canvas rendert den bereits gesetzten Hintergrund.

Normaler Hintergrundwechsel im geöffneten Template Editor aktualisiert den
bestehenden Canvas weiterhin direkt.

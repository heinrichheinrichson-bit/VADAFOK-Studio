
## 2.17 RC1 – Banner Workflow

### Ziel
Der häufige Bannerwechsel im Live-Card-Modul wird auf einen Klick reduziert.

### Umsetzung
- Das Live-Card-Modul zeigt bis zu vier vorhandene Banner-Favoriten als Miniaturen.
- Die Favoriten stammen aus der bereits vorhandenen Library-Favoritenverwaltung.
- Ein Klick auf eine Miniatur setzt das Banner als aktuelles Caption-Banner.
- Das aktive Banner wird hervorgehoben.
- Nicht belegte Plätze führen direkt zum bestehenden Banner-Picker.
- Die vollständige Banner Library und `CHANGE / MANAGE` bleiben erhalten.

### Datenhaltung
Es wird keine zweite Banner-Liste angelegt. Bannerdateien und bestehende
Library-Metadaten werden nur über die vorhandenen VADAFOK-Funktionen verwendet.

### Sicherheit
Das Feature ändert keine Bannerdateien und sendet nichts automatisch an OBS.

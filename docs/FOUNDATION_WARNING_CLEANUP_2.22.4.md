# VADAFOK Studio 2.22.4 – Foundation – Warning Cleanup

Entfernt den `return` aus dem `finally`-Block in `voice_control/foundation.py`, ohne das Verhalten zu ändern.

Ein Regressionstest verhindert, dass die Warnung zurückkehrt.

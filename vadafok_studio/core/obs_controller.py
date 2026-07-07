try:
    import obsws_python as obs
except ImportError:
    obs = None


class OBSController:
    def __init__(self):
        self.client = None
        self.connected = False

    def connect(self, host, port, password):
        self.disconnect()
        if obs is None:
            raise RuntimeError("obsws-python fehlt. Installiere: py -m pip install -r requirements.txt")
        self.client = obs.ReqClient(host=host, port=int(port), password=password)
        self.client.get_version()
        self.connected = True
        return True

    def disconnect(self):
        """Hard-disconnect OBS client and clear local connection state."""
        client = getattr(self, "client", None)
        if client is not None:
            # obsws-python ReqClient usually stores the websocket in private attributes.
            for obj in (
                client,
                getattr(client, "base_client", None),
                getattr(client, "_base_client", None),
                getattr(client, "ws", None),
                getattr(client, "_ws", None),
                getattr(getattr(client, "base_client", None), "ws", None),
                getattr(getattr(client, "base_client", None), "_ws", None),
                getattr(getattr(client, "_base_client", None), "ws", None),
                getattr(getattr(client, "_base_client", None), "_ws", None),
            ):
                if obj is None:
                    continue
                for method_name in ("disconnect", "close", "stop", "shutdown"):
                    method = getattr(obj, method_name, None)
                    if callable(method):
                        try:
                            method()
                        except Exception:
                            pass
                        break

        self.client = None
        self.connected = False
        return True

    def is_connected(self):
        return self.probe()


    def _require_connected(self):
        if not self.probe():
            raise RuntimeError("OBS ist nicht verbunden.")
        return self.client


    def probe(self):
        """Actively ask OBS if the websocket is still alive."""
        if not bool(getattr(self, "connected", False)) or getattr(self, "client", None) is None:
            self.connected = False
            return False
        try:
            self.client.get_version()
            self.connected = True
            return True
        except Exception:
            self.connected = False
            self.client = None
            return False


    def get_scene_list(self):
        """Return a list of OBS scene names."""
        client = self._require_connected()
        response = client.get_scene_list()
        raw_scenes = getattr(response, "scenes", [])
        scenes = []
        for item in raw_scenes:
            if isinstance(item, dict):
                name = item.get("sceneName") or item.get("scene_name") or item.get("name")
            else:
                name = getattr(item, "scene_name", None) or getattr(item, "sceneName", None) or getattr(item, "name", None) or str(item)
            if name:
                scenes.append(str(name))
        return scenes

    def get_current_scene_name(self):
        client = self._require_connected()
        response = client.get_current_program_scene()
        return getattr(response, "current_program_scene_name", None) or getattr(response, "scene_name", None) or ""


    def switch_scene(self, scene_name):
        """Switch OBS program scene."""
        client = self._require_connected()
        scene_name = str(scene_name or "").strip()
        if not scene_name:
            raise RuntimeError("Keine Szene ausgewählt.")
        client.set_current_program_scene(scene_name)
        return True

    def current_scene(self, scene_name=""):
        if scene_name:
            return scene_name
        client = self._require_connected()
        return client.get_current_program_scene().current_program_scene_name


    def get_scene_sources(self, scene_name=""):
        """Return sources/items for a scene with visibility state."""
        client = self._require_connected()
        scene = self.current_scene(scene_name)
        response = client.get_scene_item_list(scene)
        raw_items = getattr(response, "scene_items", [])
        sources = []
        for item in raw_items:
            if not isinstance(item, dict):
                item = {
                    "sourceName": getattr(item, "source_name", None) or getattr(item, "sourceName", None) or str(item),
                    "sceneItemId": getattr(item, "scene_item_id", None) or getattr(item, "sceneItemId", None),
                    "sceneItemEnabled": getattr(item, "scene_item_enabled", None) if hasattr(item, "scene_item_enabled") else getattr(item, "sceneItemEnabled", None),
                }
            name = item.get("sourceName") or item.get("source_name") or item.get("inputName") or item.get("name")
            item_id = item.get("sceneItemId") or item.get("scene_item_id")
            enabled = item.get("sceneItemEnabled")
            if enabled is None:
                enabled = item.get("scene_item_enabled")
            if enabled is None:
                enabled = True
            if name:
                sources.append({
                    "name": str(name),
                    "item_id": item_id,
                    "enabled": bool(enabled),
                })
        return sources

    def set_source_visibility(self, scene_name, source_name, enabled):
        scene = self.current_scene(scene_name)
        self.enable_source(scene, source_name, bool(enabled))
        return True

    def find_item_id(self, scene, source_name):
        client = self._require_connected()
        items = client.get_scene_item_list(scene).scene_items
        for item in items:
            if item.get("sourceName") == source_name:
                return item["sceneItemId"]
        raise RuntimeError(f"Quelle '{source_name}' wurde in Szene '{scene}' nicht gefunden.")

    def enable_source(self, scene, source_name, enabled):
        client = self._require_connected()
        item_id = self.find_item_id(scene, source_name)
        client.set_scene_item_enabled(scene, item_id, enabled)
        return True

    def set_text(self, source_name, text):
        client = self._require_connected()
        client.set_input_settings(name=source_name, settings={"text": text}, overlay=True)
        return True

    def set_image_file(self, source_name, file_path):
        client = self._require_connected()
        client.set_input_settings(name=source_name, settings={"file": str(file_path)}, overlay=True)
        return True

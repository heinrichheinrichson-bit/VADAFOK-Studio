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
        scene = str(scene_name or "").strip()
        if not scene:
            scene = self.current_scene("")

        response = client.get_scene_item_list(scene)
        raw_items = getattr(response, "scene_items", None)
        if raw_items is None:
            raw_items = getattr(response, "sceneItems", None)
        if raw_items is None and isinstance(response, dict):
            raw_items = response.get("sceneItems") or response.get("scene_items") or []
        raw_items = raw_items or []

        sources = []
        for item in raw_items:
            if not isinstance(item, dict):
                item = {
                    "sourceName": (
                        getattr(item, "source_name", None)
                        or getattr(item, "sourceName", None)
                        or getattr(item, "scene_item_source_name", None)
                        or getattr(item, "sceneItemSourceName", None)
                        or getattr(item, "input_name", None)
                        or getattr(item, "inputName", None)
                        or str(item)
                    ),
                    "sceneItemId": (
                        getattr(item, "scene_item_id", None)
                        or getattr(item, "sceneItemId", None)
                    ),
                    "sceneItemEnabled": (
                        getattr(item, "scene_item_enabled", None)
                        if hasattr(item, "scene_item_enabled")
                        else getattr(item, "sceneItemEnabled", None)
                    ),
                }

            name = (
                item.get("sourceName")
                or item.get("source_name")
                or item.get("sceneItemSourceName")
                or item.get("scene_item_source_name")
                or item.get("inputName")
                or item.get("input_name")
                or item.get("name")
            )
            item_id = item.get("sceneItemId") or item.get("scene_item_id")
            enabled = item.get("sceneItemEnabled")
            if enabled is None:
                enabled = item.get("scene_item_enabled")
            if enabled is None:
                enabled = True

            if name:
                sources.append({
                    "name": str(name).strip(),
                    "item_id": item_id,
                    "enabled": bool(enabled),
                    "raw": item,
                })

        return sources



    def get_group_sources(self, group_name):
        """Return sources/items inside an OBS group, best effort."""
        client = self._require_connected()
        try:
            response = client.get_group_scene_item_list(group_name)
            raw_items = getattr(response, "scene_items", None)
            if raw_items is None:
                raw_items = getattr(response, "sceneItems", None)
            if raw_items is None and isinstance(response, dict):
                raw_items = response.get("sceneItems") or response.get("scene_items") or []
            raw_items = raw_items or []
        except Exception:
            raw_items = []

        sources = []
        for item in raw_items:
            if not isinstance(item, dict):
                item = {
                    "sourceName": (
                        getattr(item, "source_name", None)
                        or getattr(item, "sourceName", None)
                        or getattr(item, "scene_item_source_name", None)
                        or getattr(item, "sceneItemSourceName", None)
                        or getattr(item, "input_name", None)
                        or getattr(item, "inputName", None)
                        or str(item)
                    ),
                    "sceneItemId": (
                        getattr(item, "scene_item_id", None)
                        or getattr(item, "sceneItemId", None)
                    ),
                    "sceneItemEnabled": (
                        getattr(item, "scene_item_enabled", None)
                        if hasattr(item, "scene_item_enabled")
                        else getattr(item, "sceneItemEnabled", None)
                    ),
                }
            name = (
                item.get("sourceName")
                or item.get("source_name")
                or item.get("sceneItemSourceName")
                or item.get("scene_item_source_name")
                or item.get("inputName")
                or item.get("input_name")
                or item.get("name")
            )
            item_id = item.get("sceneItemId") or item.get("scene_item_id")
            enabled = item.get("sceneItemEnabled")
            if enabled is None:
                enabled = item.get("scene_item_enabled")
            if enabled is None:
                enabled = True

            if name:
                sources.append({
                    "name": str(name).strip(),
                    "item_id": item_id,
                    "enabled": bool(enabled),
                    "raw": item,
                })
        return sources


    def scene_has_source(self, scene_name, source_name):
        """Check if a scene already contains a source by visible source name."""
        target = str(source_name or "").strip()
        if not target:
            return False
        try:
            for item in self.get_scene_sources_recursive(scene_name):
                if str(item.get("name", "")).strip() == target:
                    return True
        except Exception:
            try:
                for item in self.get_scene_sources(scene_name):
                    if str(item.get("name", "")).strip() == target:
                        return True
            except Exception:
                pass
        return False

    def add_existing_source_to_scene(self, scene_name, source_name, enabled=True):
        """Add an existing OBS source/input to a scene as a scene item, best effort."""
        client = self._require_connected()
        scene_name = str(scene_name or "").strip()
        source_name = str(source_name or "").strip()
        if not scene_name or not source_name:
            raise RuntimeError("Scene oder Source fehlt.")

        # obsws-python commonly exposes create_scene_item(sceneName, sourceName, sceneItemEnabled)
        attempts = [
            lambda: client.create_scene_item(scene_name, source_name, bool(enabled)),
            lambda: client.create_scene_item(scene_name=scene_name, source_name=source_name, scene_item_enabled=bool(enabled)),
            lambda: client.create_scene_item(sceneName=scene_name, sourceName=source_name, sceneItemEnabled=bool(enabled)),
            lambda: client.create_scene_item(scene_name, source_name),
        ]

        last_error = None
        for attempt in attempts:
            try:
                attempt()
                return True
            except Exception as e:
                last_error = e

        raise RuntimeError(f"Quelle '{source_name}' konnte nicht zu Szene '{scene_name}' hinzugefügt werden: {last_error}")

    def install_overlay_sources(self, source_scene, target_scene, required_sources):
        """Install missing existing VADAFOK sources into one target scene."""
        source_scene = str(source_scene or "").strip()
        target_scene = str(target_scene or "").strip()
        required_sources = [str(x).strip() for x in required_sources if str(x).strip()]

        if not source_scene:
            raise RuntimeError("Keine Source Scene gewählt.")
        if not target_scene:
            raise RuntimeError("Keine Ziel-Szene gewählt.")

        installed = []
        skipped = []
        errors = []

        # Verify source scene has the source somewhere before attempting install.
        source_names = []
        try:
            source_names = [item.get("name", "") for item in self.get_scene_sources_recursive(source_scene)]
        except Exception:
            source_names = [item.get("name", "") for item in self.get_scene_sources(source_scene)]

        for source_name in required_sources:
            if source_name not in source_names:
                skipped.append(f"{source_name} (not in source scene)")
                continue

            if self.scene_has_source(target_scene, source_name):
                skipped.append(f"{source_name} (already exists)")
                continue

            try:
                self.add_existing_source_to_scene(target_scene, source_name, enabled=True)
                installed.append(source_name)
            except Exception as e:
                errors.append(f"{source_name}: {e}")

        return {
            "target_scene": target_scene,
            "installed": installed,
            "skipped": skipped,
            "errors": errors,
        }

    def get_scene_sources_recursive(self, scene_name="", max_depth=3):
        """Return scene sources including best-effort group/nested scene contents."""
        scene = str(scene_name or "").strip()
        if not scene:
            scene = self.current_scene("")

        seen_containers = set()
        result = []

        def add_unique(source, parent=""):
            name = str(source.get("name", "")).strip()
            if not name:
                return
            copy = dict(source)
            copy["parent"] = parent
            result.append(copy)

        def walk_container(container_name, depth, parent=""):
            if depth > max_depth:
                return
            key = (container_name, depth)
            if key in seen_containers:
                return
            seen_containers.add(key)

            if parent:
                items = self.get_group_sources(container_name)
            else:
                items = self.get_scene_sources(container_name)

            for item in items:
                add_unique(item, parent=parent)
                name = item.get("name", "")

                # Try group contents.
                group_children = []
                try:
                    group_children = self.get_group_sources(name)
                except Exception:
                    group_children = []

                if group_children:
                    for child in group_children:
                        add_unique(child, parent=name)

                    # Recurse one level deeper into nested groups.
                    if depth + 1 <= max_depth:
                        for child in group_children:
                            child_name = child.get("name", "")
                            try:
                                if self.get_group_sources(child_name):
                                    walk_container(child_name, depth + 1, parent=child_name)
                            except Exception:
                                pass

        walk_container(scene, 0, parent="")
        return result

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

    def set_media_file(self, source_name, file_path):
        """Set the local file used by an OBS Media Source.

        Uses the raw OBS WebSocket v5 request payload so this remains stable
        across obsws-python wrapper signature changes.
        """
        client = self._require_connected()
        source_name = str(source_name or "").strip()
        file_path = str(file_path or "").strip()
        if not source_name:
            raise RuntimeError("Keine OBS Media Source angegeben.")
        if not file_path:
            raise RuntimeError("Keine Mediendatei angegeben.")

        client.send(
            "SetInputSettings",
            {
                "inputName": source_name,
                "inputSettings": {
                    "is_local_file": True,
                    "local_file": file_path,
                },
                "overlay": True,
            },
        )
        return True

    def restart_media_source(self, source_name):
        """Restart an OBS Media Source from the beginning.

        OBS WebSocket v5 expects the protocol string below. Sending the raw
        request avoids ambiguity in keyword names between obsws-python builds.
        """
        client = self._require_connected()
        source_name = str(source_name or "").strip()
        if not source_name:
            raise RuntimeError("Keine OBS Media Source angegeben.")

        client.send(
            "TriggerMediaInputAction",
            {
                "inputName": source_name,
                "mediaAction": "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART",
            },
        )
        return True

    def play_media_file(self, source_name, file_path):
        """Assign a local media file and restart it in OBS."""
        self.set_media_file(source_name, file_path)
        self.restart_media_source(source_name)
        return True

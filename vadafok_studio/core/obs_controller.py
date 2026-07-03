
try:
    import obsws_python as obs
except ImportError:
    obs = None

class OBSController:
    def __init__(self):
        self.client = None
        self.connected = False

    def connect(self, host, port, password):
        if obs is None:
            raise RuntimeError("obsws-python fehlt. Installiere: py -m pip install -r requirements.txt")
        self.client = obs.ReqClient(host=host, port=int(port), password=password)
        self.client.get_version()
        self.connected = True

    def current_scene(self, scene_name=""):
        if scene_name:
            return scene_name
        return self.client.get_current_program_scene().current_program_scene_name

    def find_item_id(self, scene, source_name):
        items = self.client.get_scene_item_list(scene).scene_items
        for item in items:
            if item.get("sourceName") == source_name:
                return item["sceneItemId"]
        raise RuntimeError(f"Quelle '{source_name}' wurde in Szene '{scene}' nicht gefunden.")

    def enable_source(self, scene, source_name, enabled):
        item_id = self.find_item_id(scene, source_name)
        self.client.set_scene_item_enabled(scene, item_id, enabled)

    def set_text(self, source_name, text):
        self.client.set_input_settings(name=source_name, settings={"text": text}, overlay=True)

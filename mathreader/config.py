import rhme
import json


class Configuration:
    package_path = rhme.__path__[0]
    config_path = package_path + '/docs/config/config.json'

    def get_configs(self):
        configs = {}
        try:
            with open(self.config_path) as json_file:
                config = json_file.read()
                if config:
                    configs = json.loads(config)
                else:
                    configs = {}
        except Exception as e:
            print("[config.py] Error while opening configurations: ", e)
        return configs

    def set_app_debug_mode(self, value):
        print("[config.py] set_app_debug_mode() ")
        if isinstance(value, str) and value != "":
            self.update_data('debug_mode', value)

    def set_app_debug_mode_image(self, value):
        print("[config.py] set_app_debug_mode_image() ")
        if isinstance(value, str) and value != "":
            self.update_data('debug_mode_image', value)

    def update_data(self, key, value):
        print("[config.py] update_data()")
        try:
            configs = self.get_configs()
            if 'application' in configs:
                configs['application'].update({key:  value})
            else:
                configs.update({'application': {
                    key: value
                }})
            with open(self.config_path, 'w') as f:
                f.write(json.dumps(configs))
            print('[config.py] update_data() | config updated: ', configs)
        except Exception as e:
            print("[config.py] Error while updating config json")
            raise e

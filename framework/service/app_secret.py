from framework.core import singleton


class SecretManager(object, metaclass=singleton):
      def disconnect_all(self):
        chassis_list = self.get_target_relatives_by_name(PARENT_CHILD_RELATION, 'HardwareChassis')
        for chassis in chassis_list:
            chassis.disconnect_chassis()
            self.on_chassis_disconnect(chassis)
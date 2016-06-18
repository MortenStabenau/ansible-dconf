#!/usr/bin/python

# Written by Morten Stabenau

DOCUMENTATION = '''

'''

EXAMPLES = '''
'''

import json

class Gsettings(object):
    """Wrapper class to interact with the dconf database"""
    def __init__(self, module):
        self.module = module
        self.__command = module.get_bin_path('gsettings')
        self.tools_ok = self.__command is not None

    def write(self, schema, key, value):
        rc, out, err = self._exec('set ' + schema + ' ' + key + ' ' + value)

    def read(self, schema, key):
        rc, out, err = self._exec('get ' + schema + ' ' + key)
        return out.strip('\n')

    def key_exists(self, schema, key):
        rc, out, err = self._exec('list-keys ' + schema)
        keys = filter(bool, out.split('\n'))
        return key in keys

    def _exec(self, command):
        return self.module.run_command(self.__command + ' ' + command,
            check_rc = True)

    def quote(self, string):
        return "'" + string.replace("'", "'\\''") + "'"

def get_arguments(module, gsettings):
    """Gets the module parameters and check them for errors. If an error is
    found, it calls module.fail with an appropriate message.
    Returns: schema, key, value
    """
    schema  = module.params.get('schema')
    key     = module.params.get('key')
    value   = module.params.get('value')

    if " " in value:
        value = gsettings.quote(value)

    if " " in schema:
        module.fail_json(msg='The schema "' + schema +
            '" does not seem like a valid schema name')

    if " " in key:
        module.fail_json(msg='The key "' + key +
            '" does not seem like a valid key name')

    return schema, key, value

def main():
    module = AnsibleModule(
        argument_spec = {
            'schema': {'required': True},
            'key': {'required': True},
            'value': {'required': True}
        }
    )

    gsettings = Gsettings(module)
    schema, key, value = get_arguments(module, gsettings)

    if not gsettings.tools_ok:
        module.fail_json(msg='The gsettings utility is not installed.')

    if not gsettings.key_exists(schema, key):
        module.fail_json(msg='Key ' + key +  ' does not exist in schema ' +
            schema + '.')

    old_value = gsettings.read(schema, key)

    if value == old_value:
        module.exit_json(changed=False)
    else:
        gsettings.write(schema, key,value)
        module.exit_json(changed=True, old_value=old_value, new_value=value)

from ansible.module_utils.basic import *
main()

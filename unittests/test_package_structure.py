import os
import re
import yaml

import base


class TestPackage(base.UnittetsBaseCiCd):
    def get_list_of_classes(self):
        class_names = []

        for path, dirs, files in os.walk(self.apps_dir):
            if path.endswith('Classes'):
                names = [os.path.join(path, f)
                         for f in files if f.endswith('.yaml')]
                class_names.extend(names)
        return class_names

    def check_name(self, namespace, cls_name, error_list):
        # read file
        data = ''
        with open(cls_name) as f:
            data = f.read()

        regexp_str = '%s:[A-Z]+' % namespace
        regexp = re.compile(regexp_str)
        if len(regexp.findall(data)) == 0:
            msg = ('Namespace "%s" is not used in the "%s" and should '
                   'be removed from list of Namespaces' % (namespace, cls_name))
            error_list.append(msg)

    def test_package_structure(self):
        error_list = []
        for cls_name in self.get_list_of_classes():
            for ns in self.get_namespaces(cls_name):
                self.check_name(ns, cls_name, error_list)

        error_string = "\n".join(error_list)
        msg = "Test detects follow list of errors: \n%s" % error_string

        self.assertEqual(0, len(error_list), msg)

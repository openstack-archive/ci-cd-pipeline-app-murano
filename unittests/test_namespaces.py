import os
import re
import yaml

import testtools


class TestNamespaces(testtools.TestCase):
    def get_list_of_classes(self):
        # TODO: should be fixed future with some common approach for all tests
        root_dir = os.path.dirname(os.path.abspath(__file__)).rsplit('/', 1)[0]
        apps_dir = os.path.join(root_dir, 'murano-apps')
        class_names = []

        for path, dirs, files in os.walk(apps_dir):
            if path.endswith('Classes'):
                names = [os.path.join(path, f)
                         for f in files if f.endswith('.yaml')]
                class_names.extend(names)
        return class_names

    def get_namespaces(self, cls_name):
        # workaround for PyYAML bug: http://pyyaml.org/ticket/221
        ###############################
        class YaqlYamlLoader(yaml.Loader):
                pass

        def yaql_constructor(loader, node):
            return

        YaqlYamlLoader.add_constructor(u'!yaql', yaql_constructor)
        ###############################

        # parse file
        parsed_data = ''
        with open(cls_name) as f:
            parsed_data = yaml.load(f, YaqlYamlLoader)

        n_spaces = parsed_data.get('Namespaces')
        if n_spaces is None:
            msg = 'File "%s" does not content "Namespaces" section' % cls_name
            raise ValueError(msg)
        # get only names of namespaces
        names = n_spaces.keys()
        # remove main namespace from the list
        names.remove('=')
        return names

    def check_name(self, namespace, cls_name, error_list):
        # read file
        data = ''
        with open(cls_name) as f:
            data = f.read()

        regexp_str = '[^a-zA-Z]%s:[a-zA-Z]+' % namespace
        regexp = re.compile(regexp_str)
        if len(regexp.findall(data)) == 0:
            msg = ('Namespace "%s" is not used in the "%s" and should '
                   'be removed from list of Namespaces' % (namespace, cls_name))
            error_list.append(msg)

    def test_namespaces(self):
        error_list = []
        for cls_name in self.get_list_of_classes():
            for ns in self.get_namespaces(cls_name):
                self.check_name(ns, cls_name, error_list)

        error_string = "\n".join(error_list)
        msg = "Test detects follow list of errors: \n%s" % error_string

        self.assertEqual(0, len(error_list), msg)

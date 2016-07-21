import os
import re
import yaml

import base


class TestNamespaces(base.UnittetsBaseCiCd):

    def get_list_of_classes(self):
        class_names = []

        for path, dirs, files in os.walk(self.apps_dir):
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


class TestPackageStructure(base.UnittetsBaseCiCd):
    '''
    Basic package can be described as example below,
    but for test purposes will be used structure similar on output
    for os.walk:

    class Content(object):
        def __init__(self, dirs=None, files=None):
            self.dirs = dirs
            self.files = files

    package_structure = Content(
        files=[], dirs={'package':
           Content(dirs={'Classes': Content(dirs=[],
                                            files=['*.yaml']),
                         'Resources': Content(dirs={'scripts': Content()},
                                              files=['*.template']),
                         'UI': Content(dirs=[],
                                       files=['ui.yaml'])
                        },
                   files=['manifest.yaml',
                          'logo.png',
                          'LICENSE'
                         ]
                    )
            }
    )
    '''
    package_structure = {
        '': {
            'files': [],
            'dirs': ['package']},
        'package': {
            'files': ['manifest.yaml', 'logo.png', 'LICENSE'],
            'dirs': ['Classes', 'Resources', 'UI']},
        'package/Classes': {
            'files': [re.compile('\w*.yaml')],
            'dirs': []},
        'package/Resources': {
            'files': [re.compile('\w*.template')],
            'dirs': ['scripts']},
        'package/Resources/scripts': {
            # None means, that there are no any requirements for this value
            'files': None,
            'dirs': None},
        'package/UI': {
            'files': ['ui.yaml'],
            'dirs': []},
    }

    def find_incorrect_items(self, expected, real, errors):
        if expected is None:
            return
        real_set = set(real)
        for val in expected:
            try:
                matches = filter(val.match, real_set)
            except AttributeError:
                # it's not a pattern and we just need to check,
                # that it's in list
                if val in real_set:
                    real_set.remove(val)
            else:
                # remove matches from real_set
                real_set -= set(matches)

        if real_set:
            return real_set

    def show_patterns_in_error(self, expected):
        output = []
        for val in expected:
            try:
                output.append(val.pattern)
            except AttributeError:
                output.append(val)
        return output

    def check_package_tree(self, package_name):
        errors = []
        base_path = os.path.join(self.apps_dir, package_name)
        for path, dirs, files in os.walk(base_path, topdown=True):
            # remove with backslash symbol '/'
            internal_path = path[len(base_path)+1:]
            if internal_path not in self.package_structure:
                continue
            p_files = self.package_structure[internal_path]['files']
            p_dirs = self.package_structure[internal_path]['dirs']
            wrong_files = self.find_incorrect_items(p_files, files, errors)
            if wrong_files:
                allowed_vals = self.show_patterns_in_error(p_files)
                msg = ('Path: "%s" contains wrong files: %s. Allowed values '
                       'are: %s ' % (path, str(wrong_files), allowed_vals))
                errors.append(msg)

            wrong_dirs = self.find_incorrect_items(p_dirs, dirs, errors)
            if wrong_dirs:
                allowed_vals = self.show_patterns_in_error(p_dirs)
                msg = ('Path: "%s" contains wrong dirs: %s. Allowed values '
                       'are: %s ' % (path, str(wrong_dirs), allowed_vals))
                errors.append(msg)

        return errors

    def test_packages(self):
        error_list = []
        packages = os.listdir(self.apps_dir)
        for package in packages:
            error_list.extend(self.check_package_tree(package))

        error_string = "\n".join(error_list)
        msg = "Test detects follow list of errors: \n%s" % error_string

        self.assertEqual(0, len(error_list), msg)

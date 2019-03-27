"""
author: deadc0de6 (https://github.com/deadc0de6)
Copyright (c) 2017, deadc0de6
basic unittest for the import function
"""


import unittest
import os
import yaml

from dotdrop.dotdrop import cmd_importer
from dotdrop.dotdrop import cmd_list_profiles
from dotdrop.dotdrop import cmd_list_files
from dotdrop.dotdrop import cmd_update
from dotdrop.linktypes import LinkTypes

from tests.helpers import get_path_strip_version, edit_content, \
                          load_options, create_random_file, \
                          clean, get_string, get_dotfile_from_yaml, \
                          get_tempdir, create_fake_config, create_dir


class TestImport(unittest.TestCase):

    CONFIG_BACKUP = False
    CONFIG_CREATE = True
    CONFIG_DOTPATH = 'dotfiles'
    CONFIG_NAME = 'config.yaml'

    def load_yaml(self, path):
        """Load yaml to dict"""
        self.assertTrue(os.path.exists(path))
        content = ''
        with open(path, 'r') as f:
            content = yaml.load(f)
        return content

    def assert_file(self, path, o, profile):
        """Make sure path has been inserted in conf for profile"""
        strip = get_path_strip_version(path)
        self.assertTrue(strip in [x.src for x in o.dotfiles])
        dsts = [os.path.expanduser(x.dst) for x in o.dotfiles]
        self.assertTrue(path in dsts)

    def assert_in_yaml(self, path, dic, link=False):
        """Make sure "path" is in the "dic" representing the yaml file"""
        strip = get_path_strip_version(path)
        self.assertTrue(strip in [x['src'] for x in dic['dotfiles'].values()])
        dsts = [os.path.expanduser(x['dst']) for x in dic['dotfiles'].values()]
        if link:
            self.assertTrue(get_dotfile_from_yaml(dic, path)['link'])
        self.assertTrue(path in dsts)

    def test_import(self):
        """Test the import function"""
        # on filesystem
        src = get_tempdir()
        self.assertTrue(os.path.exists(src))
        self.addCleanup(clean, src)

        # in dotdrop
        dotfilespath = get_tempdir()
        self.assertTrue(os.path.exists(dotfilespath))
        self.addCleanup(clean, dotfilespath)

        profile = get_string(10)
        confpath = create_fake_config(dotfilespath,
                                      configname=self.CONFIG_NAME,
                                      dotpath=self.CONFIG_DOTPATH,
                                      backup=self.CONFIG_BACKUP,
                                      create=self.CONFIG_CREATE)
        self.assertTrue(os.path.exists(confpath))
        o = load_options(confpath, profile)

        # create some random dotfiles
        dotfile1, content1 = create_random_file(src)
        self.addCleanup(clean, dotfile1)
        dotfile2, content2 = create_random_file(os.path.expanduser('~'))
        self.addCleanup(clean, dotfile2)
        homeconf = os.path.join(os.path.expanduser('~'), '.config')
        if not os.path.exists(homeconf):
            os.mkdir(homeconf)
            self.addCleanup(clean, homeconf)
        dotconfig = os.path.join(homeconf, get_string(5))
        create_dir(dotconfig)
        self.addCleanup(clean, dotconfig)
        dotfile3, content3 = create_random_file(dotconfig)
        dotfile4, content3 = create_random_file(homeconf)
        self.addCleanup(clean, dotfile4)

        # fake a directory containing dotfiles
        dotfile5 = get_tempdir()
        self.assertTrue(os.path.exists(dotfile5))
        self.addCleanup(clean, dotfile5)
        sub1, _ = create_random_file(dotfile5)
        sub2, _ = create_random_file(dotfile5)

        # fake a file for symlink
        dotfile6, content6 = create_random_file(dotconfig)
        self.addCleanup(clean, dotfile6)

        # fake a directory for symlink
        dotfile7 = get_tempdir()
        self.assertTrue(os.path.exists(dotfile7))
        self.addCleanup(clean, dotfile7)
        sub3, _ = create_random_file(dotfile7)
        sub4, _ = create_random_file(dotfile7)

        # import the dotfiles
        dfiles = [dotfile1, dotfile2, dotfile3, dotfile4, dotfile5]
        o.import_path = dfiles
        cmd_importer(o)
        # import symlink
        o.link = LinkTypes.PARENT
        sfiles = [dotfile6, dotfile7]
        o.import_path = sfiles
        cmd_importer(o)
        o.link = LinkTypes.NOLINK

        # reload the config
        o = load_options(confpath, profile)

        # test dotfiles in config class
        self.assertTrue(profile in o.profiles)
        self.assert_file(dotfile1, o, profile)
        self.assert_file(dotfile2, o, profile)
        self.assert_file(dotfile3, o, profile)
        self.assert_file(dotfile4, o, profile)
        self.assert_file(dotfile5, o, profile)
        self.assert_file(dotfile6, o, profile)
        self.assert_file(dotfile7, o, profile)

        # test dotfiles in yaml file
        y = self.load_yaml(confpath)
        self.assert_in_yaml(dotfile1, y)
        self.assert_in_yaml(dotfile2, y)
        self.assert_in_yaml(dotfile3, y)
        self.assert_in_yaml(dotfile4, y)
        self.assert_in_yaml(dotfile5, y)
        self.assert_in_yaml(dotfile6, y, link=True)
        self.assert_in_yaml(dotfile7, y, link=True)

        # test have been imported in dotdrop dotpath directory
        indt1 = os.path.join(dotfilespath,
                             self.CONFIG_DOTPATH,
                             get_path_strip_version(dotfile1))
        self.assertTrue(os.path.exists(indt1))
        indt2 = os.path.join(dotfilespath,
                             self.CONFIG_DOTPATH,
                             get_path_strip_version(dotfile2))
        self.assertTrue(os.path.exists(indt2))
        indt3 = os.path.join(dotfilespath,
                             self.CONFIG_DOTPATH,
                             get_path_strip_version(dotfile3))
        self.assertTrue(os.path.exists(indt3))
        indt4 = os.path.join(dotfilespath,
                             self.CONFIG_DOTPATH,
                             get_path_strip_version(dotfile4))
        self.assertTrue(os.path.exists(indt4))
        indt5 = os.path.join(dotfilespath,
                             self.CONFIG_DOTPATH,
                             get_path_strip_version(dotfile5))
        self.assertTrue(os.path.exists(indt5))
        s1 = os.path.join(dotfilespath,
                          self.CONFIG_DOTPATH,
                          get_path_strip_version(dotfile6),
                          sub1)
        self.assertTrue(os.path.exists(s1))
        s2 = os.path.join(dotfilespath,
                          self.CONFIG_DOTPATH,
                          get_path_strip_version(dotfile6),
                          sub2)
        self.assertTrue(os.path.exists(s2))
        indt6 = os.path.join(dotfilespath,
                             self.CONFIG_DOTPATH,
                             get_path_strip_version(dotfile6))
        self.assertTrue(os.path.exists(indt6))
        indt7 = os.path.join(dotfilespath,
                             self.CONFIG_DOTPATH,
                             get_path_strip_version(dotfile7))
        self.assertTrue(os.path.exists(indt7))
        s3 = os.path.join(dotfilespath,
                          self.CONFIG_DOTPATH,
                          get_path_strip_version(dotfile7),
                          sub3)
        self.assertTrue(os.path.exists(s3))
        s4 = os.path.join(dotfilespath,
                          self.CONFIG_DOTPATH,
                          get_path_strip_version(dotfile7),
                          sub4)
        self.assertTrue(os.path.exists(s4))

        # test symlink on filesystem
        self.assertTrue(os.path.islink(dotfile6))
        self.assertTrue(os.path.realpath(dotfile6) == indt6)
        self.assertTrue(os.path.islink(dotfile7))
        self.assertTrue(os.path.realpath(dotfile7) == indt7)

        cmd_list_profiles(o)
        cmd_list_files(o)

        # fake test update
        editcontent = 'edited'
        edit_content(dotfile1, editcontent)
        o.safe = False
        o.update_path = [dotfile1]
        cmd_update(o)
        c2 = open(indt1, 'r').read()
        self.assertTrue(editcontent == c2)


def main():
    unittest.main()


if __name__ == '__main__':
    main()

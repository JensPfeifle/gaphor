#!/usr/bin/env python
#
# setup.py for Gaphor
#
# vim:sw=4:et
"""Gaphor
"""

MAJOR_VERSION = 0
MINOR_VERSION = 8
MICRO_VERSION = 1

VERSION = '%d.%d.%d' % ( MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION )

LINGUAS = [ 'ca', 'es', 'nl', 'sv' ]

TESTS = [
    'gaphor.actions.tests.test_itemactions',
    'gaphor.actions.tests.test_placementactions',
    'gaphor.adapters.tests.test_connector',
    'gaphor.adapters.tests.test_editor',
    'gaphor.diagram.tests.test_diagramitem',
    'gaphor.diagram.tests.test_class',
    'gaphor.diagram.tests.test_action',
    'gaphor.diagram.tests.test_handletool',
    'gaphor.diagram.tests.test_interfaces',
    'gaphor.ui.tests.test_diagramtab',
    'gaphor.ui.tests.test_mainwindow',
    'gaphor.UML.tests.test_elementfactory',
    ]

#GCONF_DOMAIN='/apps/gaphor/' # don't forget trailing slash

import sys, os
from glob import glob
from commands import getoutput, getstatus, getstatusoutput

# Py2App should be imported before the utils classes are loaded
try:
    import py2app
except ImportError:
    print "No py2app, can't create application bundle"
else:
    from modulegraph.modulegraph import AddPackagePath
    AddPackagePath('gaphor', 'build/lib/gaphor')
    AddPackagePath('gaphor.UML', 'build/lib/gaphor/UML')

from distutils.core import setup, Command
from distutils.command.build_py import build_py
from distutils.command.install_lib import install_lib
from distutils.dep_util import newer
from utils.build_mo import build, build_mo
from utils.build_pot import build_pot
from utils.install_mo import install, install_mo

str_version = sys.version[:3]
version = map(int, str_version.split('.'))
if version < [2, 4]:
    raise SystemExit, \
        "Python 2.4 or higher is required, %s found" % str_version


class config_Gaphor(Command):
    description="Configure Gaphor"

    user_options = [
        #('pkg-config=', None, 'Path to pkg-config'),
    ]

    #pkg_config_checked=False
    config_failed=[]

    def initialize_options(self):
        #self.pkg_config = 'pkg-config'
        pass

    def finalize_options(self):
        # Check for existence of pkg-config
        #status, output = getstatusoutput('%s --version' % self.pkg_config)
        #if status != 0:
        #    print 'pkg-config not found.'
        #    raise SystemExit
        #print 'Found pkg-config version %s' % output
        pass

    def run(self):
        self.module_check('pygtk')
        import pygtk
        pygtk.require('2.0')

        self.module_check('xml.parsers.expat')
        self.module_check('gtk', ('gtk_version', (2, 8)),
                                 ('pygtk_version', (2, 8)))

        print ''
        if self.config_failed:
            print 'Config failed.'
            print 'The following modules can not be found or are to old:'
            print ' ', str(self.config_failed)[1:-1]
            print ''
            raise SystemExit
        else:
            print 'Config succeeded.'

    def pkg_config_check(self, package, version):
        """Check for availability of a package via pkg-config."""
        retval = os.system('%s --exists %s' % (self.pkg_config, package))
        if retval:
            print '!!! Required package %s not found.' % package
            self.config_failed.append(package)
            return
        pkg_version_str = getoutput('%s --modversion %s' % (self.pkg_config, package))
        pkg_version = map(int, pkg_version_str.split('.'))
        req_version = map(int, version.split('.'))
        if pkg_version >= req_version:
            print "Found '%s', version %s." % (package, pkg_version_str)
        else:
            print "!!! Package '%s' has version %s, should have at least version %s." % ( package, pkg_version_str, version )
            self.config_failed.append(package)

    def module_check(self, module, *version_checks):
        """Check for the availability of a module.

        version_checks is a set of ket/version pairs that should be true.
        """
        import string
        try:
            mod = __import__(module)
        except ImportError:
            print "!!! Required module '%s' not found." % module
            self.config_failed.append(module)
        else:
            print "Module '%s' found." % module
            for key, ver in version_checks:
                s_ver = string.join(map(str, ver), '.')
                print "  Checking key '%s.%s' >= %s..." % (module, key, s_ver),
                try:
                    modver = getattr(mod, key)
                except:
                    print "Not found." % key
                    self.config_failed.append(module)
                else:
                    s_modver = string.join(map(str, modver), '.')
                    if modver >= ver:
                        print "Okay (%s)." % s_modver
                    else:
                        print "Failed (%s)" % s_modver
                        self.config_failed.append(module)


class build_Gaphor(build):

    def run(self):
        self.run_command('config')
        build.run(self)


class version_py:

    def generate_version(self, dir, data_dir):
        """Create a file gaphor/version.py which contains the current version.
        """
        outfile = os.path.join(dir, 'gaphor', 'version.py')
        print 'generating %s' % outfile, dir, data_dir
        self.mkpath(os.path.dirname(outfile))
        f = open(outfile, 'w')
        f.write('"""\nVersion information generated by setup.py. DO NOT EDIT.\n"""\n\n')
        f.write('VERSION=\'%s\'\n' % VERSION)
        # expand backspaces
        f.write('DATA_DIR=\'%s\'\n' % data_dir.replace('\\', '\\\\'))
        if os.name == 'nt':
            home = 'USERPROFILE'
        else:
            home = 'HOME'
        f.write('import os\n')
        f.write('USER_DATA_DIR=os.path.join(os.getenv(\'%s\'), \'.gaphor\')\n' % home)
        f.write('del os\n')
        f.close()
        self.byte_compile([outfile])


class build_py_Gaphor(build_py, version_py):

    description = "build_py and generate gaphor/UML/uml2.py."

    def run(self):
        build_py.run(self)
        sys.path.insert(0, self.build_lib)
        # All data is stored in the local data directory
        data_dir = os.path.join(os.getcwd(), 'data')
        #data_dir = "os.path.join(os.getcwd(), 'data')"
        self.generate_version(self.build_lib, data_dir)
        self.generate_uml2()

    def generate_uml2(self):
        """Generate gaphor/UML/uml2.py in the build directory."""
        import utils.genUML2
        gen = os.path.join('utils', 'genUML2.py')
        overrides = os.path.join('gaphor', 'UML', 'uml2.override')
        model = os.path.join('gaphor', 'UML', 'uml2.gaphor')
        py_model = os.path.join('gaphor', 'UML', 'uml2.py')
        outfile = os.path.join(self.build_lib, py_model)
        self.mkpath(os.path.dirname(outfile))
        if self.force or newer(model, outfile) \
                      or newer(overrides, outfile) \
                      or newer(gen, outfile):
            print 'generating %s from %s...' % (py_model, model)
            print '  (warnings can be ignored)'
            utils.genUML2.generate(model, outfile, overrides)
        else:
            print 'not generating %s (up-to-date)' % py_model
        self.byte_compile([outfile])


class install_lib_Gaphor(install_lib, version_py):

    def initialize_options(self):
        install_lib.initialize_options(self)
        self.install_data= None

    def finalize_options(self):
        install_lib.finalize_options(self)
        self.set_undefined_options('install_data',
                                   ('install_dir', 'install_data'))

    def run(self):
        # install a new version.py with install_data as data_dir;
        # get rid of install root directory
        skip = len(self.get_finalized_command('install').root)

        self.generate_version(self.install_dir, self.install_data[skip:])
        install_lib.run(self)


class install_schemas(Command):
    """Do something like this:

        GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source` \
            gconftool --makefile-install-rule data/gaphor.schemas

    in a pythonic way.
    """

    description = "Install a configuration (using GConf)."

    user_options = [
        ('install-data=', None, 'installation directory for data files'),
        ('gconftool', None, 'The gconftool to use for installation'),
        ('gconf-config-source', None, 'Overrule the GConf config source'),
        ('force', 'f', 'force installation (overwrite existing keys)')
    ]

    boolean_options = ['force']

    def initialize_options(self):
        self.install_data = None
        self.gconftool = 'gconftool-2'
        self.gconf_config_source = ''
        self.force = None
        self.schemas_file = 'data/gaphor.schemas'

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('force', 'force'),
                                   ('install_data', 'install_data'))

    def run(self):
        getstatus('GCONF_CONFIG_SOURCE="%s" %s --makefile-install-rule %s' % (self.gconf_config_source, self.gconftool, self.schemas_file))

        self._set_value('/schemas/apps/gaphor/data_dir', self.install_data, 'string')

    def _set_value(self, key, value, type):
        print "setting gconf value '%s' to '%s'" % (key, value)
        #apply(getattr(self.gconf_client, 'set_' + type),
        #      (GCONF_DOMAIN + key, value))
        getstatus('%s --type=%s --set %s %s' % (self.gconftool, type, key, value))

#install.sub_commands.append(('install_schemas', None))


class run_Gaphor(Command):

    description = 'Launch Gaphor from the local directory'

    user_options = [
        ('build-dir=', None, ''),
        ('command=', 'c', 'execute command'),
        ('file=', 'f', 'execute file'),
        ('doctest=', 'd', 'execute doctests in module (e.g. gaphor.geometry)'),
        ('unittest=', 'u', 'execute unittest file (e.g. tests/test-ns.py)'),
        ('model=', 'm', 'load a model file'),
        ('coverage', None, 'Calculate coverage (utils/coverage.py)'),
    ]

    def initialize_options(self):
        self.build_lib = None
        self.command = None
        self.file = None
        self.doctest = None
        self.unittest = None
        self.model = None
        self.coverage = None
        self.verbosity = 2

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'))

    def run(self):
        print 'Starting Gaphor...'
        print 'Starting with model file', self.model
        self.run_command('build')

        import os.path
        import gaphor
        #os.environ['GAPHOR_DATADIR'] = os.path.abspath('data')
        if self.coverage:
            from utils import coverage
            coverage.start()

        if self.command:
            print 'Executing command: %s...' % self.command
            exec self.command

        elif self.doctest:
            print 'Running doctest cases in module: %s...' % self.doctest
            import imp
            # use zope's one since it handles coverage right
            from zope.testing import doctest

            # Figure out the file:
            f = os.path.join(*self.doctest.split('.')) + '.py'
            fp = open(f)
            # Prepend module's package path to sys.path
            pkg = os.path.join(self.build_lib, *self.doctest.split('.')[:-1])
            if pkg:
                sys.path.insert(0, pkg)
                print 'Added', pkg, 'to sys.path'
            # Load the module as local module (without package)
            test_module = imp.load_source(self.doctest.split('.')[-1], f, fp)
            failure, tests = doctest.testmod(test_module, name=self.doctest,
                 optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
            if self.coverage:
                print
                print 'Coverage report:'
                coverage.report(f)
            sys.exit(failure != 0)

        elif self.unittest:
            # Running a unit test is done by opening the unit test file
            # as a module and running the tests within that module.
            print 'Running test cases in unittest file: %s...' % self.unittest
            import imp, unittest
            fp = open(self.unittest)
            test_module = imp.load_source('gaphor_test', self.unittest, fp)
            test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
            #test_suite = unittest.TestLoader().loadTestsFromName(self.unittest)
            test_runner = unittest.TextTestRunner(verbosity=self.verbosity)
            result = test_runner.run(test_suite)
            if self.coverage:
                print
                print 'Coverage report:'
                coverage.report(self.unittest)
            sys.exit(not result.wasSuccessful())

        elif self.file:
            print 'Executing file: %s...' % self.file
            dir, f = os.path.split(self.file)
            print 'Extending PYTHONPATH with %s' % dir
            sys.path.append(dir)
            execfile(self.file, {})
        else:
            print 'Launching Gaphor...'
            gaphor.main(self.model)

class tests_Gaphor(Command):

    description = 'Run the Gaphor test suite.'

    user_options = [
    ]

    def initialize_options(self):
        self.verbosity = 9

    def finalize_options(self):
        pass

    def run(self):
        print 'Starting Gaphor test-suite...'

        self.run_command('build')

        import unittest

        test_suite = unittest.defaultTestLoader.loadTestsFromNames(TESTS)

        test_runner = unittest.TextTestRunner(verbosity=self.verbosity)
        result = test_runner.run(test_suite)
        sys.exit(not result.wasSuccessful())

def plugin_data(name):
    return 'plugins/%s' % name, glob('data/plugins/%s/*.*' % name)


setup(name='gaphor',
      version=VERSION,
      description="Gaphor is a UML modeling tool",
      url='http://gaphor.sourceforge.net',
      author='Arjan J. Molenaar',
      author_email='arjanmol@users.sourceforge.net',
      license="GNU General Public License (GPL, see COPYING)",
      long_description="Gaphor is a UML modeling tool written in Python. "
      "It uses the GNOME2 environment for user interaction.",
      platforms=['GNOME2'],
      packages=['gaphor',
                'gaphor.UML',
                'gaphor.UML.tests',
                'gaphor.diagram',
                'gaphor.diagram.tests',
                'gaphor.ui',
                'gaphor.ui.tests',
                'gaphor.misc',
                'gaphor.adapters',
                'gaphor.adapters.tests',
                'gaphor.actions',
                'gaphor.actions.tests',
                'zope',
                'zope.interface',
                'zope.component.bbb',
                'zope.component.bbb.tests',
                'zope.interface.common',
                'zope.component',
                'zope.exceptions',
                'zope.deprecation',
                'zope.testing',
                
      ],
#      ext_modules=ext_modules,
      # data files are relative to <prefix>/share/gaphor (see setup.cfg)
      data_files=[('', ['data/icons.xml']),
                  ('pixmaps', glob('data/pixmaps/*.png')),
                  plugin_data('plugineditor'),
                  plugin_data('alignment'),
                  plugin_data('checkmetamodel'),
                  plugin_data('diagramlayout'),
                  plugin_data('liveobjectbrowser'),
                  plugin_data('pngexport'),
                  plugin_data('pynsource'),
                  plugin_data('svgexport'),
                  plugin_data('pdfexport'),
                  plugin_data('xmiexport')
      ],
      scripts=['bin/gaphor', 'bin/gaphorconvert'],

#      distclass=Distribution,
      cmdclass={'config': config_Gaphor,
                'build_py': build_py_Gaphor,
                #'install_schemas': install_schemas,
                'build': build_Gaphor,
#                'build_ext': BuildExt,
                'build_mo': build_mo,
                'build_pot': build_pot,
                'install': install,
                'install_lib': install_lib_Gaphor,
                'install_mo': install_mo,
                'run': run_Gaphor,
                'tests': tests_Gaphor
      },
#      app=['gaphor-osx.py'],
      options = dict(
         py2app = dict(
             includes=['atk', 'pango', 'cairo', 'pangocairo'],
#             CFBundleDisplayName='Gaphor',
#             CFBundleIdentifier='net.sourceforge.gaphor'
         ),
         build_pot = dict(
             all_linguas = ','.join(LINGUAS),
         ),
         build_mo = dict(
             all_linguas = ','.join(LINGUAS),
         ),
     )
)

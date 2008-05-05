"Options"
import ConfigParser
import optparse
import os
import gettext
from version import VERSION
import logging
import sys

_ = gettext.gettext

def get_home_dir():
    """
    Return the closest possible equivalent to a 'home' directory.
    For Posix systems, this is $HOME, and on NT it's $HOMEDRIVE\$HOMEPATH.
    Currently only Posix and NT are implemented, a HomeDirError exception is
    raised for all other OSes.
    """

    if os.name == 'posix':
        return os.path.expanduser('~')
    elif os.name == 'nt':
        try:
            return os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
        except:
            try:
                import _winreg as wreg
                key = wreg.OpenKey(wreg.HKEY_CURRENT_USER,
                        "Software\Microsoft\Windows\Current" \
                                "Version\Explorer\Shell Folders")
                homedir = wreg.QueryValueEx(key, 'Personal')[0]
                key.Close()
                return homedir
            except:
                return 'C:\\'
    elif os.name == 'dos':
        return 'C:\\'
    else:
        return '.'

def find_path(progs, args):
    #TODO check for win32
    paths = [x for x in os.environ['PATH'].split(':')
            if os.path.isdir(x)]
    for dir in paths:
        content = os.listdir(dir)
        for prog in progs:
            if prog in content:
                return os.path.join(dir, prog) + ' ' + args
    return ''


class ConfigManager(object):
    "Config manager"

    def __init__(self):
        self.options = {
            'login.login': 'admin',
            'login.server': 'localhost',
            'login.port': '8070',
            'login.protocol': 'socket://',
            'login.db': False,
            'client.modepda': False,
            'client.toolbar': 'both',
            'tip.autostart': False,
            'tip.position': 0,
            'logging.logger': '',
            'logging.level': 'ERROR',
            'logging.verbose': False,
            'client.default_path': get_home_dir(),
            'form.toolbar': True,
            'client.form_tab': 'left',
            'client.form_tab_orientation': 90,
            'client.lang': 'en_US',
            'client.actions': {
                'odt': {0: find_path(['ooffice', 'ooffice2'], '%s'),
                    1: find_path(['ooffice', 'ooffice2'], '-p %s')},
                'txt': {0: find_path(['ooffice', 'ooffice2'], '%s'),
                    1: find_path(['ooffice', 'ooffice2'], '-p %s')},
                'pdf': {0: find_path(['evince', 'xpdf', 'gpdf',
                    'kpdf', 'epdfview', 'acroread'], '%s'), 1: ''},
                'png': {0: find_path(['display', 'qiv', 'eye', 'open'],
                    '%s'), 1: ''},
                },
        }
        parser = optparse.OptionParser(version=_("Tryton %s" % VERSION))
        parser.add_option("-c", "--config", dest="config",
                help=_("specify alternate config file"))
        parser.add_option("-v", "--verbose", action="store_true",
                default=False, dest="verbose",
                help=_("enable basic debugging"))
        parser.add_option("-d", "--log", dest="log_logger", default='',
                help=_("specify channels to log"))
        parser.add_option("-l", "--log-level", dest="log_level",
                default='ERROR', help=_("specify the log level: " \
                        "INFO, DEBUG, WARNING, ERROR, CRITICAL"))
        parser.add_option("-u", "--user", dest="login",
                help=_("specify the login user"))
        parser.add_option("-p", "--port", dest="port",
                help=_("specify the server port"))
        parser.add_option("-s", "--server", dest="server",
                help=_("specify the server hostname"))
        opt = parser.parse_args()[0]


        self.rcfile = opt.config or os.path.join(get_home_dir(), '.trytonrc')
        self.load()

        if opt.verbose:
            self.options['logging.verbose'] = True
        self.options['logging.logger'] = opt.log_logger
        self.options['logging.level'] = opt.log_level

        for arg in ('login', 'port', 'server'):
            if getattr(opt, arg):
                self.options['login.'+arg] = getattr(opt, arg)

    def save(self):
        try:
            configparser = ConfigParser.ConfigParser()
            for option in self.options.keys():
                if not len(option.split('.')) == 2:
                    continue
                section, name = option.split('.')
                if section in ('logging'):
                    continue
                if not configparser.has_section(section):
                    configparser.add_section(section)
                configparser.set(section, name, self.options[option])
            configparser.write(file(self.rcfile, 'wb'))
        except:
            logging.getLogger('common.options').warn(
                    _('Unable to write config file %s!') % \
                            (self.rcfile,))
            return False
        return True

    def load(self):
        try:
            if not os.path.isfile(self.rcfile):
                return False

            configparser = ConfigParser.ConfigParser()
            configparser.read([self.rcfile])
            for section in configparser.sections():
                for (name, value) in configparser.items(section):
                    if value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    if section == 'client' and name == 'actions':
                        value = eval(value)
                    self.options[section + '.' + name] = value
        except:
            logging.getLogger('options').warn(
                    _('Unable to read config file %s!') % \
                            (self.rcfile,))
            return False
        return True

    def __setitem__(self, key, value):
        self.options[key] = value

    def __getitem__(self, key):
        return self.options[key]

CONFIG = ConfigManager()
CURRENT_DIR = os.path.abspath(os.path.normpath(os.path.join(
    os.path.dirname(sys.argv[0]))))
PREFIX = os.path.abspath(os.path.normpath(os.path.join(
    os.path.dirname(sys.argv[0]), '..')))
PIXMAPS_DIR = os.path.join(CURRENT_DIR, 'share', 'pixmaps')
if not os.path.isdir(PIXMAPS_DIR):
    PIXMAPS_DIR = os.path.join(PREFIX, 'share', 'pixmaps')

if os.name == 'nt':
    sys.path.insert(0, os.path.join(CURRENT_DIR, 'GTK\\bin'))
    sys.path.insert(0, os.path.join(CURRENT_DIR, 'GTK\\lib'))
    sys.path.insert(0, os.path.join(CURRENT_DIR))
    os.environ['PATH'] = os.path.join(CURRENT_DIR, 'GTK\\lib') + ";" + \
            os.environ['PATH']
    os.environ['PATH'] = os.path.join(CURRENT_DIR, 'GTK\\bin') + ";" + \
            os.environ['PATH']
    os.environ['PATH'] = os.path.join(CURRENT_DIR) + ";" + os.environ['PATH']

import gtk

TRYTON_ICON = gtk.gdk.pixbuf_new_from_file(
        os.path.join(PIXMAPS_DIR, 'tryton-icon.png'))

def _data_dir():
    data_dir = os.path.join(CURRENT_DIR, 'share', 'tryton')
    if not os.path.isdir(data_dir):
        data_dir = os.path.join(PREFIX, 'share', 'tryton')
    return data_dir
DATA_DIR = _data_dir()
GLADE = os.path.join(DATA_DIR, 'tryton.glade')

# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.
import re
import string
import octoprint.plugin

class Nc2marlinPlugin(octoprint.plugin.SettingsPlugin,
                      octoprint.plugin.AssetPlugin,
                      octoprint.plugin.TemplatePlugin):

    def __init__(self):
        self._fan_gcode   = 'M106'
        self._wait_gcode  = 'G4'
        self._last_mcode  = ''
        self._last_gcode  = 'G0'
        self._mode        = ''
        self._wait        = 0

    # mode : none, marlin, laser, plotter
    def get_settings_defaults(self):
        return dict(mode = 'none', wait = '0')

    def get_settings_version(self):
        return 1

    def get_template_configs(self):
        return [
            dict(type = "settings", custom_bindings = False)
            #dict(type="settings", template="nc2marlin_settings.jinja2", custom_bindings=True)
        ]

    def get_assets(self):
        return dict(
            #js=['js/nc2marlin.js'],
            css=['css/nc2marlin.css'],
            less=['less/nc2marlin.less']
        )

    def get_template_vars(self):
        return dict(
            mode = self._settings.get(['mode']),
            wait = self._settings.get(['wait']),
        )

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            nc2marlin=dict(
                displayName='nc2marlin',
                displayVersion=self._plugin_version,

                # version check: github repository
                type='github_release',
                user='pinggusoft',
                repo='OctoPrint-nc2marlin',
                current=self._plugin_version,

                # update method: pip
                pip='https://github.com/pinggusoft/OctoPrint-nc2marlin/archive/{target_version}.zip'
            )
        )

    def get_settings(self):
        self._mode = self._settings.get(['mode'])
        self._wait = int(self._settings.get(['wait']))
        
    def on_after_startup(self):
        self.get_settings()

    # use below function only when custom_bindings is True
    #def on_settings_save(self, data):
    #    self._logger.info('SAVE data:' + data)
    #    octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
    #    self.get_settings()
        

    ###############################################################################################
    #  Codes
    ###############################################################################################
    def toFanCmd(self, out, strSpeed):
        speed = 0;
        isInv = True if self._mode == 'plotter' else False
        
        if strSpeed:
            speed = int(strSpeed)
        if isInv:
            speed = 255 - speed

        code = self._fan_gcode + ' S' + str(speed)
        if code != self._last_mcode:
            out.append(code)
            self._last_mcode = code
            if self._wait != 0:
                out.append(self._wait_gcode + ' P' + str(self._wait))

    def rewrite_gcode(self, comm_instance, phase, cmd, cmd_type, gcode, subcode, tags, *args, **kwargs):
        self.get_settings()
        #self._logger.info('Processing queuing: [' + cmd + ',' + str(cmd_type)+ ',' + str(tags) + ']')
        #self._logger.info('mode:' + self._mode + ', wait:' + str(self._wait))

        # return immediately if the mode is none
        if self._mode == 'none':
            return cmd
        
        line = cmd
        out  = []

        find = re.search('^[G|M|\(|;|T|\s].*', line)            # find valid commands G, M, (, ;, T, blank
        if find == None:                                        # if not, add last gcode to the begining
            line = self._last_gcode + ' ' + line
        
        # find available gcode
        find = re.search('^(G[0-3][^0-9]).*', line)             # find G0-G3
        if find:
            items = find.groups();
            self._last_gcode = items[0]

        # only add skipped gcode with marlin mode
        if self._mode == 'marlin':
            out.append(line)
            return out

        find = re.search('^(G[0-3][^0-9])(.*)S([0-9]*)', line)  # find G0-G3 with S parameter
        if find:
            items = find.groups();
            self.toFanCmd(out, items[2])
            if len(items[1]) > 1:
                out.append(items[0] + items[1])        
        else:
            find = re.search('(^M[3-4]$|^M[3-4][^0-9])\s*S*([0-9]*)', line)        # find M3, M4 w/wo S
            if find:
                items = find.groups();
                strSpeed = '255' if len(items[1]) == 0 else items[1]
                self.toFanCmd(out, strSpeed)
            else:
                find = re.search('^M5$', line)                      # find M5
                if find:
                    strSpeed = '0'
                    self.toFanCmd(out, strSpeed)
                else:
                    out.append(line)
                    
        #self._logger.info(out)
        return out

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ('OctoPrint-PluginSkeleton'), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = 'nc2marlin'

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = '>=2.7,<3' # only python 2
#__plugin_pythoncompat__ = '>=3,<4' # only python 3
__plugin_pythoncompat__ = '>=2.7,<4' # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Nc2marlinPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        'octoprint.plugin.softwareupdate.check_config': __plugin_implementation__.get_update_information,
        'octoprint.comm.protocol.gcode.queuing': __plugin_implementation__.rewrite_gcode,
    }


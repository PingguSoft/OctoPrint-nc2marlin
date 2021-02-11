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

    #;M3 (on) -> M107 (servo off : down)
    #;M5 (off) -> M106 (servo on : lift)
    #
    #;To use 3D Printer Laser Mode
    #;M3 (on) -> M106 S255 (laser on)
    #;M5 (off) -> M107 (laser off)

    def __init__(self):
        self.fan_gcode  = 'M106'
        self.last_mcode = ''
        self.last_gcode = 'G0'

    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return dict(mode="laser")

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    ##~~ AssetPlugin mixin
    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/nc2marlin.js"],
            css=["css/nc2marlin.css"],
            less=["less/nc2marlin.less"]
        )

    ##~~ Softwareupdate hook
    def get_template_vars(self):
        return dict(
            mode=self._settings.get(["mode"])
        )

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            nc2marlin=dict(
                displayName="nc2marlin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="pinggusoft",
                repo="OctoPrint-nc2marlin",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/pinggusoft/OctoPrint-nc2marlin/archive/{target_version}.zip"
            )
        )

#    def rewrite_m107(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
#        if gcode and gcode == "M107":
#            cmd = "M106 S0"
#        return cmd,

    def toFanCmd(self, isPlotter, strSpeed):
        speed = 0;
        if strSpeed:
            speed = int(strSpeed)
        if isPlotter:
            speed = 255 - speed
        return self.fan_gcode + ' S' + str(speed) + '\n'

    def rewrite_gcode(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        line = cmd
        find = re.search('^[G|M|\(|;|T|\s].*', line)            # find valid commands G, M, (, ;, T, blank
        if find == None:                                        # if not, add last gcode to the begining
            line = self.last_gcode + ' ' + line
        
        find = re.search('^(M[3-4])\s*S*([0-9]*)', line)        # find M3, M4 w/wo S
        if find:
            items = find.groups();
            speed = '255' if len(items[1]) == 0 else items[1]
            fan_cmd = self.toFanCmd(isPlotter, speed)
            if fan_cmd != self.last_mcode:
                self.last_mcode = fan_cmd
                return fan_cmd,
        else:
            find = re.search('^M5.*', line)                     # find M5
            if find:
                speed = '255' if isPlotter else '0'
                fan_cmd =  self.toFanCmd(isPlotter, speed)
                if fan_cmd != self.last_mcode:
                    self.last_mcode = fan_cmd
                    return fan_cmd,
            else:
                find = re.search('^(G[0-3]).*', line)           # find G0-G3
                if find:
                    items = find.groups();
                    self.last_gcode = items[0]
                
                find = re.search('^(G[0-3])(.*)S(.*)', line)    # find G0-G3 with S parameter
                if find:
                    items = find.groups();
                    fan_cmd =  self.toFanCmd(isPlotter, items[2])
                    
                    line = None
                    if len(items[1]) > 1:
                        line = items[0] + items[1] + '\n'

                    if fan_cmd != self.last_mcode:
                        self.last_mcode = fan_cmd
                    else:
                        fan_cmd = None
                    
                    if fan_cmd and line:
                        return [(fan_cmd,), (line,)]
                    elif fan_cmd:
                        return fan_cmd,
                    elif line:
                        return line,

        return line,
        


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "nc2marlin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Nc2marlinPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.rewrite_gcode,
    }


/*
 * View model for OctoPrint-nc2marlin
 *
 * Author: pinggusoft
 * License: AGPLv3
 */
$(function() {
    function Nc2marlinViewModel(parameters) {
        var self = this;
       
        self.settings   = parameters[0];
        self.sel_mode   = ko.observable();

        self.onBeforeBinding = function() {
            console.log('onBeforeBinding')

            self.mode = self.settings.settings.plugins.nc2marlin.mode()
            console.log('mode:' + self.mode)
            self.sel_mode(self.mode)
        }
        
        self.changeMode = function(obj, event) {
            if (event.originalEvent) {
                var mode = $("#id_mode").val()
                
                try {
                    console.log('mode :' + mode)
                    self.settings.settings.plugins.nc2marlin.mode(mode)
                } catch(ex) {
                    alert(ex);
                }
                
                self.settings.saveData();
            }
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: Nc2marlinViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ "settingsViewModel" ],
        // Elements to bind to, e.g. #settings_plugin_nc2marlin, #tab_plugin_nc2marlin, ...
        elements: [ "#tab_plugin_nc2marlin" ]
    });
});

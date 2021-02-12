/*
 * View model for OctoPrint-nc2marlin
 *
 * Author: pinggusoft
 * License: AGPLv3
 */
$(function() {
    function Nc2marlinViewModel(parameters) {
        var self = this;
       
        self.settings   = parameters[0]

        self.mode       = "disabled"
        self.sel_mode   = ko.observable()
        
        self.wait       = 0
        self.text_wait  = ko.observable()

        self.onBeforeBinding = function() {
            self.mode = self.settings.settings.plugins.nc2marlin.mode()
            self.sel_mode(self.mode)
            
            self.wait = self.settings.settings.plugins.nc2marlin.wait()
            self.text_wait(self.wait)
            
            console.log('onBeforeBinding : mode:' + self.mode + ', wait:' + self.wait)
        }
  
        self.changeMode = function(obj, event) {
            if (event.originalEvent) {
                self.save()
            }
        }
        
        self.save = function() {
            self.mode = $("#id_mode").val()
            self.wait = $("#id_wait").val()
            console.log('SAVE : mode:' + self.mode + ', wait:' + self.wait)
            self.settings.settings.plugins.nc2marlin.mode(self.mode)
            self.settings.settings.plugins.nc2marlin.wait(self.wait)
            self.settings.saveData()
        }        
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: Nc2marlinViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#tab_plugin_nc2marlin"] 
    });

});

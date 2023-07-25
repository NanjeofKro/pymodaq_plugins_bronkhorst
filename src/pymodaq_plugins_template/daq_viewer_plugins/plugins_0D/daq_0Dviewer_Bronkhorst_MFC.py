import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from hardwareimport propar as pr


class PythonWrapperOfYourInstrument:
    #  TODO Replace this fake class with the import of the real python wrapper of your instrument
    pass


class DAQ_0DViewer_Template(DAQ_Viewer_base):
    """
    """
    params = comon_parameters+[
        ## TODO for your custom plugin: elements to be added here as dicts in order to control your custom stage
        {"title": "Bronkhorst MFC",
         "name": "mfc_id",
         "type": "str",
         "value": "default",
         "readonly": False,
         },
        {"title":"COM inlet",
         "name":"COM_in",
         "type":"str",
         "value":"default",
         "readonly":False,
         },
        {"title":"Position on bus",
         "name":"bus_pos",
         "type":"int",
         "value":0,
         "readonly":False},
        {"title":"Setpoint",
         "name":"setpoint",
         "type":"float",
         "readonly":False,
         },
        {"title":"Flow",
         "name":"flow",
         "type":"float",
         "value":0,
         "min":0,
         "readonly":True,
         },
        {"title":"Flow unit",
         "name":"unit",
         "type":"str",
         "value":"nounit",
         "readonly":True},
        {"title": "User tag",
         "name":"user_tag",
         "type":"str",
         "value":"",
         "readonly":False,
         }
        ]

    def ini_attributes(self,params=params):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller=None
        for param in params:
            if param["name"]=="com_in":
                self.com_in=param["value"]
            if param["name"]=="bus_pos":
                self.bus_pos=param["value"]
            if param["name"]=="user_tag":
                self.user_tag==param["value"]
        self.master=None
        
        #TODO declare here attributes you want/need to init with a default value

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == "a_parameter_you've_added_in_self.params":
           self.controller.your_method_to_apply_this_param_change()  # when writing your own plugin replace this line
#        elif ...
        ##

    def ini_detector(self, COM_in,controller=None,):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        raise NotImplemented  # TODO when writing your own plugin remove this line and modify the one below
        self.ini_detector_init(old_controller=controller,
                               new_controller=pr.instrument(self.com_in, self.bus_pos))
        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data
        self.dte_signal_temp.emit(DataToExport(name='pymodaq_plugins_bronkhorst',
                                               data=DataFromPlugins(name=self.controller.readParameter(115),
                                                                    data=[np.array([0]), np.array([0])],
                                                                    dim='Data0D',
                                                                    labels=[self.controller.readParameters(115), 'label2'])))

        info = "Whatever info you want to log"
        initialized = self.controller.wink()
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        ## TODO for your custom plugin
        # when writing your own plugin remove this line
        #  self.controller.your_method_to_terminate_the_communication()  # when writing your own plugin replace this line
        self.controller.master.stop()
    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        ## TODO for your custom plugin

        # synchrone version (blocking function)
        raise NotImplemented  # when writing your own plugin remove this line
        data_tot = self.controller.your_method_to_start_a_grab_snap()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))
        #########################################################

        # asynchrone version (non-blocking function with callback)
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
        #########################################################


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name=self.controller.readParameter(115), data=data_tot,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        ## TODO for your custom plugin
        raise NotImplemented  # when writing your own plugin remove this line
        self.controller.your_method_to_stop_acquisition()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        ##############################
        return ''


if __name__ == '__main__':
    main(__file__)

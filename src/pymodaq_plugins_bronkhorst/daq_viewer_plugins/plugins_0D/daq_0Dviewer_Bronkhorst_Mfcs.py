import numpy as np
from pymodaq.utils.daq_utils import ThreadCommand
from pymodaq.utils.data import DataFromPlugins, DataToExport
from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.parameter import Parameter
from ...hardware import propar as pr


class DAQ_0DViewer_Bronkhorst_Mfcs(DAQ_Viewer_base):
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

    def ini_attributes(self):
        #  TODO declare the type of the wrapper (and assign it to self.controller) you're going to use for easy
        #  autocompletion
        self.controller=None
        self.com_in=None
        self.bus_pos=None
        self.user_tag=None
        self.unit=None
        self.data_offset=None
        self.data_span=None
        
        #TODO declare here attributes you want/need to init with a default value

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        ## TODO for your custom plugin
        if param.name() == "COM_in":
            self.com_in==param.value()
            self.ini_detector(self.controller)  # when writing your own plugin replace this line
        elif param.name() == "bus_pos":
            self.bus_pos=param.value()
            self.ini_detector(self.controller)
        elif param.name() == "user_tag":
            self.controller.writeParameter(115,param.value())
            self.user_tag=param.value()
            

        
    def ini_detector(self, controller=None):
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
        if self.com_in==None:
            raise ParameterError()
            print('self.com_in has no value; cannot initialise serial communication')
        if self.bus_pos==None:
            raise ParameterError()
            print('self.bus_pos has no value; cannot initialise serial communication')
          # TODO when writing your own plugin remove this line and modify the one below
        self.ini_detector_init(old_controller=controller,
                               new_controller=pr.instrument(self.com_in, self.bus_pos))
        self.user_tag=self.controller.readParameter(115)
        self.unit=self.controller.readParameter(129)
        self.data_offset=self.controller.readParameter(183)
        self.data_span=self.controller.readParameter(21)-self.data_offset
        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data
        self.dte_signal_temp.emit(DataToExport(name='pymodaq_plugins_bronkhorst',
                                               data=DataFromPlugins(name='Bronk_MFC_'+self.user_tag,
                                                                    data=[np.array([0]), np.array([0])],
                                                                    dim='Data0D',
                                                                    labels=['Flow ('+self.unit+')', 'label2'])))

        info = "Found MFC with user tag = "+self.user_tag
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
        data_tot = np.asarray(self.controller.get_data())
        self.dte_signal.emit(DataToExport(name='pymodaq_plugins_bronkhorst',
                                          data=[DataFromPlugins(name='Bronk_MFC_'+self.user_tag, data=data_tot,
                                                                dim='Data0D', labels=['Flow ('+self.unit+')', 'data1'])]))
        #########################################################

        # asynchrone version (non-blocking function with callback)
        #raise NotImplemented  # when writing your own plugin remove this line
        #self.controller.your_method_to_start_a_grab_snap(self.callback)  # when writing your own plugin replace this line
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
        #raise NotImplemented  # when writing your own plugin remove this line
        #self.controller.your_method_to_stop_acquisition()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['End of acquisition']))
        ##############################
        return ''
    def get_data(self):
        
        raw_data=self.controller.readParameter(8)
        #Magic numbers from Bronkhorst documentation:
        if raw_data<41943:
            data=raw_data/32000*self.data_span+self.data_offset
        else:
            data=(0.003125*raw_data-204.799)*self.data_span+self.data_offset 
        return data

if __name__ == '__main__':
    main(__file__)

class ParameterError(Exception):
    print('Parameter has no value')
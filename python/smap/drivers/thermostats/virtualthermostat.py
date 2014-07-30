from smap import driver, actuate
from smap.util import periodicSequentialCall

class VirtualThermostat(driver.SmapDriver):
    def setup(self, opts):
        self.state = {'temp': 70,
                      'humidity': 50,
                      'hvac_state': 1,
                      'temp_heat': 70,
                      'temp_cool': 75,
                      'hold': 0,
                      'override': 0,
                      'hvac_mode': 1,
                      'fan_mode': 1,
                      }

        self.readperiod = float(opts.get('ReadPeriod',.5))
        self.add_timeseries('/temp', 'F', data_type='long') 
        self.add_timeseries('/humidity', '%RH', data_type='long') 
        self.add_timeseries('/hvac_state', 'Mode', data_type='long') 
        self.add_timeseries('/temp_heat', 'F', data_type='long') 
        self.add_timeseries('/temp_cool', 'F', data_type='long') 
        self.add_timeseries('/hold', 'On/Off', data_type='long') 
        self.add_timeseries('/override', 'On/Off', data_type='long') 
        self.add_timeseries('/hvac_mode', 'Mode', data_type='long') 
        self.add_timeseries('/fan_mode', 'Mode', data_type='long') 

        self.add_actuator('/temp_heat_act', 'F', SetpointActuator(tstat=self, path='temp_heat', _range=(45, 95)))
        self.add_actuator('/temp_cool_act', 'F', SetpointActuator(tstat=self, path='temp_cool', _range=(45, 95)))
        self.add_actuator('/hold_act', 'On/Off', OnOffActuator(tstat=self, path='hold'))
        self.add_actuator('/override_act', 'On/Off', OnOffActuator(tstat=self, path='override'))
        self.add_actuator('/hvac_mode_act', 'Mode', ModeActuator(tstat=self, path='hvac_mode', states=[0,1,2,3]))
        self.add_actuator('/fan_mode_act', 'Mode', OnOffActuator(tstat=self, path='fan_mode'))

    def start(self):
        periodicSequentialCall(self.read).start(self.readperiod)

    def read(self):
        for k,v in self.state.iteritems():
            self.add('/'+k, v)

class VirtualThermostatActuator(actuate.SmapActuator):
    def __init__(self, **opts):
        self.tstat = opts.get('tstat')
        self.path = opts.get('path')

class SetpointActuator(VirtualThermostatActuator, actuate.ContinuousIntegerActuator):
    def __init__(self, **opts):
        actuate.ContinuousIntegerActuator.__init__(self, opts['_range'])
        VirtualThermostatActuator.__init__(self, **opts)

    def get_state(self, request):
        return self.tstat.state[self.path]
    
    def set_state(self, request, state):
        self.tstat.state[self.path] = int(state)
        return self.tstat.state[self.path]

class ModeActuator(VirtualThermostatActuator, actuate.NStateActuator):
    def __init__(self, **opts):
        actuate.NStateActuator.__init__(self, opts['states'])
        VirtualThermostatActuator.__init__(self, **opts)

    def get_state(self, request):
        return self.tstat.state[self.path]
    
    def set_state(self, request, state):
        self.tstat.state[self.path] = int(state)
        return self.tstat.state[self.path]

class OnOffActuator(VirtualThermostatActuator, actuate.BinaryActuator):
    def __init__(self, **opts):
        actuate.BinaryActuator.__init__(self)
        VirtualThermostatActuator.__init__(self, **opts)

    def get_state(self, request):
        return self.tstat.state[self.path]
    
    def set_state(self, request, state):
        self.tstat.state[self.path] = int(state)
        return self.tstat.state[self.path]
#!/usr/bin/env python

'''
first: Apr 11 2017
last : Apr 12 2017

Taejoon Byun <taejoon@umn.edu>
'''

import random, os


class RandomTestGenerator(object):
    TARGET_DIR = 'random_suites'

    def __init__(self, header, size, types, maxlen, filename):
        self.header = header
        self.size = size
        self.types = types
        self.maxlen = maxlen
        self.filename = filename

    def _get_bool(self):
        return 'true' if random.randint(0, 1) is 1 else 'false'

    def _get_int(self):
        return str(random.randint(-1000,1000))

    def _get_float(self):
        dividend = random.randint(-1000,1000)
        divisor = random.randint(1,100)
        return '%s/%s' % (str(dividend), str(divisor))

    def _get_rand_val(self, var_type):
        if var_type is bool:
            return self._get_bool()
        elif var_type is int:
            return self._get_int()
        elif var_type is float:
            return self._get_float()

    def _generate_test_case(self):
        testcase = ''
        for i in range(0, random.randint(1, self.maxlen)):
            # number of steps
            step = ''
            for t in self.types:
                step += self._get_rand_val(t) + ','
            testcase += step[:-1] + '\n'
        return testcase

    def generate_suite(self):
        suite = self.header + '\n'
        for i in range(0, self.size):
            suite += self._generate_test_case() + '\n'
        return suite[:-2]

    def write_to_file(self):
        if not os.path.exists(os.path.join(os.getcwd(), self.TARGET_DIR)):
            os.mkdir(os.path.join(os.getcwd(), self.TARGET_DIR))
        with open(os.path.join(self.TARGET_DIR, self.filename), 'w') as f:
            f.write(self.generate_suite())


def getMicrowaveGtor(size, maxlen):
    header = 'DOOR_CLOSED,KP_0,KP_1,KP_2,KP_3,KP_4,KP_5,KP_6,KP_7,KP_8,KP_9,'\
            'KP_CLEAR,KP_START'
    types = [bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,bool]
    return RandomTestGenerator(header, size, types, maxlen, 'obsnop.random_tests.csv')

def getCruiseGtor(size, maxlen):
    header = 'accelResume,brakePedal,cancel,carGear,carSpeed,decelSet,onOff,'\
            'validInputs'
    types = [bool, bool, bool, int, float, bool, bool, bool]
    return RandomTestGenerator(header, size, types, maxlen, 'cc.random_tests.csv')

def getDockingGtor(size, maxlen):
    header = 'GPS_receiverAvailability_status,GPS_satelliteVisibility_status,'\
            'GroundTrack_OrbitalPosition,GroundTrack_OrbitalVelocity,'\
            'GroundTrack_Time,InertialNavigation_time,RealTimeClock_time,'\
            'StageTransition,StarPlanetTracker_planetVisibility,'\
            'StarPlanetTracker_starVisibility,dockVisibility_status,'\
            'opticsAvailability_status,sunlight_status'
    types = [bool, int, int, int, int, bool, int, int, int, int, int, bool, bool]
    return RandomTestGenerator(header, size, types, maxlen, 'docking.random_tests.csv')

def getInfusionGtor(size, maxlen):
    header = 'ALARM_IN_Highest_Level_Alarm,CONFIG_IN_Configured,'\
            'CONFIG_IN_Duration_Total,CONFIG_IN_Flow_Rate_Basal,'\
            'CONFIG_IN_Flow_Rate_Intermittent_Bolus,CONFIG_IN_Flow_Rate_KVO,'\
            'CONFIG_IN_Flow_Rate_Patient_Bolus,'\
            'CONFIG_IN_Intermittent_Bolus_Duration,'\
            'CONFIG_IN_Interval_Intermittent_Bolus,'\
            'CONFIG_IN_Lock_Out_Duration,CONFIG_IN_Max_Patient_Bolus,'\
            'CONFIG_IN_Patient_Bolus_Duration,CONFIG_IN_VTBI_Total,'\
            'OP_CMD_IN_Infusion_Cancel,OP_CMD_IN_Infusion_Inhibit,'\
            'OP_CMD_IN_Infusion_Initiate,PATIENT_IN_Bolus_Request,'\
            'SYS_STAT_IN_Reservoir_Empty,SYS_STAT_Volume_Infused,'\
            'TLM_MODE_IN_On_Start'
    types = [int, int, int, int, int, int, int, int, int, int, int, int, int, bool, bool, bool, bool, bool, int, bool]
    return RandomTestGenerator(header, size, types, maxlen, 'infusion.random_tests.csv')


def main():
    random.seed()
    size, maxlen = 100, 30
    gtors = [getMicrowaveGtor(size, maxlen), getCruiseGtor(size, maxlen), 
            getDockingGtor(size, maxlen), getInfusionGtor(size, maxlen)]
    for gtor in gtors:
        gtor.write_to_file()

if __name__ == '__main__':
    main()


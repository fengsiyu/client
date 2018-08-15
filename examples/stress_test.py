#!/usr/bin/env python

__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import argparse
import json

from monodrive.configuration import SimulatorConfiguration, VehicleConfiguration
from monodrive import Simulator


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='monoDrive simulator stress test script')
    parser.add_argument('--sim-config', default='simulator.json')
    parser.add_argument('--vehicle-config', default='test.json')
    parser.add_argument('--clock-mode', default=None, help='override clock mode', choices=['Continuous','AutoStep','ClientStep'])
    parser.add_argument('--fps', help='override sensor fps', type=int)
    parser.add_argument('--exclude', help='comma separated list of sensors to exclude (sensors not in list will be included)')
    parser.add_argument('--include', help='comma separated list of sensors to include (sensors not in list will be excluded)')
    args = parser.parse_args()

    sim_config = SimulatorConfiguration(args.sim_config)
    vehicle_config = VehicleConfiguration(args.vehicle_config)

    sim_config.client_settings['logger']['sensor']='debug'
    sim_config.client_settings['logger']['network']='debug'

    if args.clock_mode:
        if args.clock_mode == 'Continuous':
            vehicle_config.configuration['clock_mode'] = 0
        elif args.clock_mode == 'AutoStep':
            vehicle_config.configuration['clock_mode'] = 1
        elif args.clock_mode == 'ClientStep':
            vehicle_config.configuration['clock_mode'] = 2

    if args.include:
        sensor_ids = args.include.split(',')
        sensors = vehicle_config.sensors

        list = []
        for sensor in sensors:
            if sensor['type'] in sensor_ids or sensor['type']+':'+sensor['id'] in sensor_ids:
                list.append(sensor)

        vehicle_config.sensors = list
        vehicle_config.configuration['sensors'] = list

    elif args.exclude:
        sensor_ids = args.exclude.split(',')
        sensors = vehicle_config.sensors

        list = []
        for sensor in sensors:
            if sensor['type'] in sensor_ids or sensor['type'] + ':' + sensor['id'] in sensor_ids:
                continue

            list.append(sensor)

        vehicle_config.sensors = list
        vehicle_config.configuration['sensors'] = list

    if args.fps:
        for sensor in vehicle_config.sensors:
            sensor['fps'] = args.fps

    print(json.dumps(vehicle_config.configuration))
    simulator = Simulator(sim_config)
    simulator.send_simulator_configuration()
    simulator.send_vehicle_configuration(vehicle_config)

    sensors = []
    for sensor in vehicle_config.sensors:
        sensor_class = vehicle_config.get_class(sensor['type'])
        sensors.append(sensor_class(sensor['type'], sensor, sim_config))

    for sensor in sensors:
        sensor.start()
        sensor.send_start_stream_command(simulator)

    for sensor in sensors:
        sensor.socket_ready_event.wait()

    for sensor in sensors:
        sensor.join()


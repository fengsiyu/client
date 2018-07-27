#!/usr/bin/env python

__author__ = "monoDrive"
__copyright__ = "Copyright (C) 2018 monoDrive"
__license__ = "MIT"
__version__ = "1.0"

import logging

from monodrive import SimulatorConfiguration, VehicleConfiguration
from monodrive.vehicles import SimpleVehicle
from monodrive import Simulator

if __name__ == "__main__":

    # Simulator configuration defines network addresses for connecting to the simulator and material properties
    simulator_config = SimulatorConfiguration('simulator.json')

    # Vehicle configuration defines ego vehicle configuration and the individual sensors configurations
    vehicle_configuration = VehicleConfiguration('demo.json')

    simulator = Simulator(simulator_config)

    logging.getLogger("simulator").info('Sending simulator configuration')
    simulator.send_simulator_configuration()

    while True:
        logging.getLogger("simulator").info('Sending vehicle configuration')
        simulator.send_vehicle_configuration(vehicle_configuration)

        # Start Vehicle
        vehicle_instance = simulator.start_vehicle(vehicle_configuration, SimpleVehicle)

        logging.getLogger("simulator").info('Starting vehicle')
        vehicle_instance.start()

        # Waits for the restart event to be set in the control process
        simulator.restart_event.wait()

        # Terminates vehicle and sensor processes
        simulator.stop()

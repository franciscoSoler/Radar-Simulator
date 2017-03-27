#!/usr/bin/python3
'''
This script adds an uniform error when the ideal distance is measured 
'''
import numpy as np
import json
import sys
sys.path.append("../")

import radar_model


if __name__ == "__main__":
    radar = radar_model.Radar()
    medium = radar_model.Medium(radar_model.Object(1, 0))
    tx_signal = radar.transmit()
    
    realizations = 100
    distance_errors = [0, 5, 10, 40]
    distances = [30760, 37760.1695479, 1000, 35000, 40000, 80000, 140000]
    
    results = {}
    for dist in distances:
        print(dist)
        dist_key = "Dist: {}".format(dist)
        results[dist_key] = {}
        for err in distance_errors:
            err_key = "Err: {}".format(err)
            res = []
            for _ in range(realizations):
                distance = dist + np.random.uniform(-err, err)
                radar.measure_distance_to_target(distance)

                rx_sign = medium.propagate_signal(tx_signal, dist_to_obj=dist)

                output = radar.receive(rx_sign)
                res.append(radar.process_reception(output))

            results[dist_key][err_key] = [np.mean(res), np.std(res)]

    with open("results_distance_errors.json", "w") as f:
        json.dump(results, f, sort_keys=True, indent=4)

    sys.exit(0)

#!/usr/bin/python3
'''
This script subtracts a distance from the ideal distance and takes the measurement
'''
import numpy as np
import json
import sys
import csv


sys.path.append("../")

import radar_model


if __name__ == "__main__":
    radar = radar_model.Radar()
    medium = radar_model.Medium(radar_model.Object(1, 0))
    tx_signal = radar.transmit()
    
    realizations = 1
    delta_distance = [0, 5, 10, 40, 100, 500, 1000, 6000]
    distances = [30760, 37760.1695479, 10000, 35000, 40000, 80000, 140000]
    
    csv_res = []
    results = {}
    for dist in distances:
        print(dist)
        dist_key = "Dist: {}".format(dist)
        results[dist_key] = {}
        for err in delta_distance:
            err_key = "DeltaDist: {}".format(err)
            res = []
            for _ in range(realizations):
                distance = dist - err
                radar.measure_distance_to_target(distance)

                rx_sign = medium.propagate_signal(tx_signal, dist_to_obj=dist)

                output = radar.receive(rx_sign)
                res.append(radar.process_reception(output))

            csv_res.append([dist_key, err_key, res[0]])
            results[dist_key][err_key] = res

    with open("results_delta_distance.json", "w") as f:
        json.dump(results, f, sort_keys=True, indent=4)

    with open("results_delta_distance.csv", "w") as f:
        spamwriter = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerows(csv_res)

    sys.exit(0)

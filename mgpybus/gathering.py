import mgpybus._common as _common
import urllib3
import json
import os
import time
import datetime

_realtime_bus_resource_id = "resource_id=f2e5503e-927d-4ad3-9500-4ab9e55deb59"


def _api_call(pool_manager: urllib3.PoolManager, url: str, fail_delay: int, fail_attempts: int, print_fails: bool, desired_type: type):
    attempts_remaining = fail_attempts

    while True:
        try:
            req = pool_manager.request('GET', url).data.decode("utf8")
        except:
            print("\u001b[33m", "Failed to connect to API", "\033[0m", sep="")

            attempts_remaining -= 1
            if attempts_remaining > 0:
                time.sleep(fail_delay)
                continue
            else:
                print("\u001b[31m", "ERROR: Too many consecutive fails to connect to API ", "\033[0m", sep="")

        call = json.loads(req)

        # z tego co zauwazylem to API nie ma bardzo ustandaryzowanych kodow bledow,
        # ale z doswiadczenia ponizsza linijka dziala dobrze w wykrywaniu czy dane sa poprawne czy nie
        if "result" not in call or type(call["result"]) != desired_type:
            if print_fails:
                print("\u001b[33m", "Failed to extract data from API:", "\033[0m", sep="")
                print("\u001b[33m", "Recieved: ", call, "\033[0m", sep="")

            attempts_remaining -= 1
            if attempts_remaining > 0:
                time.sleep(fail_delay)
                continue
            else:
                print("\u001b[31m", "ERROR: Too many consecutive fails to extract data from API: ", "\033[0m", sep="")
                print("\u001b[31m", "Last recieved: ", call, "\033[0m", sep="")
                exit()

        return call["result"]


def get_bus_positions(dest: str, apikey: str,
                      *, fail_delay: int = 5, fail_attempts: int = 5000, print_fails: bool = True) -> None:

    url = "https://api.um.warszawa.pl/api/action/busestrams_get/?" + _realtime_bus_resource_id + "&apikey=" + apikey + "&type=1"
    ulib_pool = urllib3.PoolManager()

    call = _api_call(ulib_pool, url, fail_delay, fail_attempts, print_fails, list)

    with open(dest, "w") as file:
        json.dump(call, file)


def gather_bus_positions(dest: str, apikey: str, count: int = 1, delay: int = 15,
                         *, fail_delay: int = 5, fail_attempts: int = 5000, print_fails: bool = True, print_progress: bool = True) -> None:

    if not os.path.isdir(dest):
        print("\u001b[31m", "ERROR: No such directory to save at: ", dest, "\033[0m", sep="")
        exit()

    url = "https://api.um.warszawa.pl/api/action/busestrams_get/?" + _realtime_bus_resource_id + "&apikey=" + apikey + "&type=1"
    ulib_pool = urllib3.PoolManager()

    for i in range(count):
        if print_progress:
            print("\u001b[34m", "Gathering progress: ", i, " of ", count, "\033[0m", sep="")

        if i != 0:
            time.sleep(delay)

        call = _api_call(ulib_pool, url, fail_delay, fail_attempts, print_fails, list)

        file_path = dest + "/" + _common.time_file_name(datetime.datetime.now())
        with open(file_path, "w") as file:
            json.dump(call, file)
        if print_progress:
            print("\u001b[32m", "Saving to ", file_path, " succesful", "\033[0m", sep="")

    if print_progress:
        print("\u001b[36m", "Gathering complete: ", count, " of ", count, "\033[0m", sep="")


def get_line_lengths(dest: str, apikey: str,
                     *, fail_delay: int = 5, fail_attempts: int = 5000, print_fails: bool = True) -> None:

    url = "https://api.um.warszawa.pl/api/action/public_transport_routes/?apikey=482d1b58-3cc7-46e1-b936-e9c47b96cabb"
    ulib_pool = urllib3.PoolManager()

    call = _api_call(ulib_pool, url, fail_delay, fail_attempts, print_fails, dict)

    result = {}

    for i in call:
        max_dst = 0
        for j in call[i].values():
            for k in j.values():
                max_dst = max(max_dst, k["odleglosc"])

        result.update({i: max_dst})

    with open(dest, "w") as file:
        json.dump(result, file)

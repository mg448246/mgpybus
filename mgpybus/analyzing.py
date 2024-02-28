import mgpybus._common as _common
import pandas
import json
import os
import datetime
import regex
import geopy.distance as dst
import plotly.express as px

def _lat_lon_wrong(lats_or_lons: list[float]) -> bool:
    for i in lats_or_lons:
        if i >= 90.0 or i <= -90.0:
            return True
    return False


class _BusLineHolder:
    def __init__(self, df):
        self.df = df

    def filter_by_lines(self, lines: list):
        for i in range(len(lines)):
            lines[i] = str(lines[i])

        return _BusLineHolder(self.df.loc[self.df["Lines"].isin(lines)].reset_index(drop=True))

    def filter_by_vehicle_number(self, v_numbers: list):
        for i in range(len(v_numbers)):
            v_numbers[i] = int(v_numbers[i])

        return _BusLineHolder(self.df.loc[self.df["VehicleNumber"].isin(v_numbers)].reset_index(drop=True))

    def calculate_speed(self):
        result_dic = {"Lines": [],
                      "Lon": [],
                      "VehicleNumber": [],
                      "Time": [],
                      "Lat": [],
                      "Speed": []}

        for i in range(len(self.df) - 1):
            if self.df.loc[i]["VehicleNumber"] == self.df.loc[i + 1]["VehicleNumber"]:
                time0 = _common.str_to_datetime(self.df.loc[i]["Time"])
                time1 = _common.str_to_datetime(self.df.loc[i + 1]["Time"])
                time_diff_h = (time1 - time0).total_seconds() / 3600.0

                lat0 = float(self.df.loc[i]["Lat"])
                lat1 = float(self.df.loc[i + 1]["Lat"])

                lon0 = float(self.df.loc[i]["Lon"])
                lon1 = float(self.df.loc[i + 1]["Lon"])

                if _lat_lon_wrong([lat0, lat1, lon0, lon1]):
                    continue

                distance = dst.great_circle((lat0, lon0), (lat1, lon1))
                speed = (distance / time_diff_h).km

                result_dic["Lines"].append(self.df.loc[i]["Lines"])
                result_dic["Lon"].append(lon1)
                result_dic["VehicleNumber"].append(self.df.loc[i]["VehicleNumber"])
                result_dic["Time"].append(time1)
                result_dic["Lat"].append(lat1)
                result_dic["Speed"].append(speed)

        return _BusSpeedHolder(pandas.DataFrame(result_dic))

    def show_positions_on_map(self):
        px.scatter_mapbox(self.df, lat="Lat", lon="Lon", mapbox_style="open-street-map").show()

    def count_buses_per_line(self):
        minimal_df = self.df[["Lines", "VehicleNumber"]].drop_duplicates()
        result = {}
        for index, row in minimal_df.iterrows():
            line = row["Lines"]
            if line not in result:
                result[line] = 1
            else:
                result[line] += 1
        return result


class _BusSpeedHolder(_BusLineHolder):
    def __init__(self, df):
        super().__init__(df)

    def filter_by_speed(self, minimum: float = 0.0, maximum: float = 90.0):
        with_min = self.df.loc[self.df["Speed"] >= minimum].reset_index(drop=True)
        return _BusSpeedHolder(with_min[with_min["Speed"] <= maximum].reset_index(drop=True))

    def show_speed_on_map(self):
        px.density_mapbox(self.df, lat="Lat", lon="Lon", z="Speed", mapbox_style="open-street-map").show()


def load_bus_positions(source: str, *, earliest: datetime.datetime = None, latest: datetime.datetime = None):

    with open(source, "r") as file:
        df = pandas.read_json(file)
        df = df.drop(["Brigade"], axis=1)
        blh = _BusLineHolder(df)

        if earliest is not None:
            blh.df = blh.df.loc[blh.df["Time"] >= _common.datetime_to_str(earliest)]

        if latest is not None:
            blh.df = blh.df.loc[blh.df["Time"] < _common.datetime_to_str(latest)]

        return blh


def load_many_bus_positions(source: str, *, earliest: datetime.datetime = None, latest: datetime.datetime = None,
                            buspos_only=True):

    if not os.path.isdir(source):
        print("\u001b[31m", "ERROR: No such directory to load from: ", source, "\033[0m", sep="")
        exit()

    result = None

    for file_name in os.listdir(source):
        if not buspos_only or regex.match(".*\\.buspos", file_name):
            if result is None:
                result = load_bus_positions(source + "/" + file_name, earliest=earliest, latest=latest).df
            else:
                result = pandas.concat([result,
                                        load_bus_positions(source + "/" + file_name, earliest=earliest, latest=latest).df]).drop_duplicates()

    result = result.sort_values(["VehicleNumber", "Time"], axis=0).reset_index(drop=True)
    return _BusLineHolder(result)

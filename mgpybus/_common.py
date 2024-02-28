import datetime


def time_file_name(time: datetime.datetime) -> str:
    file_name = str(time.year) + "-"
    file_name += str(time.month).rjust(2, "0") + "-"
    file_name += str(time.day).rjust(2, "0") + "-"
    file_name += str(time.hour).rjust(2, "0") + "-"
    file_name += str(time.minute).rjust(2, "0") + "-"
    file_name += str(time.second).rjust(2, "0") + ".buspos"
    return file_name


def datetime_to_str(dt: datetime.datetime):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def str_to_datetime(string: str):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

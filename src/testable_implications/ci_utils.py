import datetime
import time


class ConditionalIndependenceUtils():

    @staticmethod
    def durationStringToSeconds(runtime):
        # convert durating string '00:00:00' to seconds
        # if runtime == '0':
        #     return 0
        # elif runtime == '0:00:00':
        #     return 0
        
        x = time.strptime(runtime, '%H:%M:%S')
        seconds = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()

        # round up to avoid undefined value in log-log plot
        # if seconds == 0.0:
        #     seconds = seconds + 1

        return seconds
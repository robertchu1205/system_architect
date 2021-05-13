from datetime import datetime, timedelta
from pytz import timezone
from prometheus import PromMetrics
from config import Config
from connection import Connection
import logging, time, math

prom = PromMetrics()

def mean(data):
    summ = 0
    for d in data:
        summ += d 
    return summ / len(data)  

def variance(data, ddof=0):
    n = len(data)
    mean = sum(data) / n
    return sum((x - mean) ** 2 for x in data) / (n - ddof)

def stdev(data, ddof=0):
    return math.sqrt(variance(data, ddof))

### time_start, time_end to "%Y-%m-%d %H:%M:%S"
def backtohours(datetime_now="", hours=1):
    if datetime_now == "":
        dt = datetime.now()
    else:
        dt = datetime_now
    beijing = timezone('Asia/Shanghai')
    hoursago = dt - timedelta(hours = hours)
    ahourago = dt - timedelta(hours = 1)
    if datetime_now == "":
        lasthours_start = hoursago.astimezone(beijing).strftime("%Y-%m-%d %H:00:00")
        lastanhour_end = ahourago.astimezone(beijing).strftime("%Y-%m-%d %H:59:59")
    else:
        lasthours_start = hoursago.strftime("%Y-%m-%d %H:00:00")
        lastanhour_end = ahourago.strftime("%Y-%m-%d %H:59:59")
    return lasthours_start, lastanhour_end

### save scores to prometheus metrics
def hour_update(ssim, aiscore, model, line):
    if ssim != 0 and aiscore != 0:
        toupdate = ["ssim_avg_gauge", "ai_score_avg_gauge"]
    elif ssim != 0 and aiscore == 0:
        toupdate = ["ssim_hour_dot"]
    elif ssim == 0 and aiscore != 0:
        toupdate = ["ai_score_hour_dot"]
    while toupdate != []: 
        for tu in toupdate:
            try:
                if tu == "ssim_avg_gauge":
                    prom.ssim_avg_gauge.labels(line, model).set(ssim)
                elif tu == "ai_score_avg_gauge":
                    prom.ai_score_avg_gauge.labels(line, model).set(aiscore)
                toupdate.remove(tu)
            except Exception as e:
                logging.error(f"when update prometheus metrics, error: {e}")
                time.sleep(int(except_sleep)) # try again after 10 mins    

### in init, the latest last an hour record in real time
def hour_record(
        host, port, username, password, database, 
        cal_hours=1, cal_amount=5, except_sleep=600,
    ):
    connect = Connection(host, port, username, password, database)
    connect.time_start, connect.time_end = backtohours(hours=int(cal_hours))
    models_lines = connect.select_models_lines()
    for ml in models_lines:
        while 1:
            try:
                ssim = connect.cal_score("score", ml[0], ml[1], int(cal_amount))
                aiscore = connect.cal_score("AI_NNmodel_score", ml[0], ml[1], int(cal_amount))
                break
            except Exception as e:
                logging.error(f"when calculating scores in hour_record, error: {e}")
                time.sleep(int(except_sleep)) # try again after 10 mins
        hour_update(ssim, aiscore, ml[0], ml[1])
    del connect
    logging.info("hour_record Finished!")

### divide time range to list of {time_start, time_end} which is all interval of 1 hour
def divide_time(time_start, time_end, cal_hours=1):
    divided_periods = []
    time_start_compare = datetime.strptime(time_start, "%Y-%m-%d %H:%M:%S")
    while True:
        new_start, new_end = backtohours(
            datetime_now=datetime.strptime(time_end, "%Y-%m-%d %H:%M:%S"))
        new_start_compare = datetime.strptime(new_start, "%Y-%m-%d %H:%M:%S")
        new_end_compare = datetime.strptime(new_end, "%Y-%m-%d %H:%M:%S")
        if new_start_compare >= time_start_compare and new_end_compare >= time_start_compare:
            divided_periods.append({"time_start":new_start, "time_end":new_end})
            time_end = new_start
        else:
            break
    return divided_periods

### which_score defined either ai score or ssim score
def standard_lines(
        host, port, username, password, database, which_score,
        time_start="", time_end="", cal_amount=5, except_sleep=600,
    ):
    config = Config()
    divided_periods = divide_time(config.time_start[which_score], config.time_end[which_score])
    count_by_model_line = {} # model:line [average]
    for dp in divided_periods:
        connect = Connection(host, port, username, password, database)
        connect.time_start, connect.time_end = dp["time_start"], dp["time_end"]
        models_lines = connect.select_models_lines()
        for ml in models_lines:
            while 1:
                try:
                    score = connect.cal_score(which_score, ml[0], ml[1], int(cal_amount))
                    if score != 0:
                        try:
                            count_by_model_line[f"{ml[0]}:{ml[1]}"].append(score)
                        except:
                            count_by_model_line[f"{ml[0]}:{ml[1]}"] = [score]
                    break
                except Exception as e:
                    logging.error(f"when calculating scores in standard_lines, error: {e}")
                    time.sleep(int(except_sleep)) # try again after 10 mins
        del connect
    for key, value in count_by_model_line.items():
        if which_score == "score":
            prom.ssim_average_line.labels(key.split(":")[1], key.split(":")[0]).set(mean(value))
            prom.ssim_pos_one_sigma.labels(key.split(":")[1], key.split(":")[0]).set(stdev(value))
        elif which_score == "AI_NNmodel_score":
            prom.ai_score_average_line.labels(key.split(":")[1], key.split(":")[0]).set(mean(value))
            prom.ai_score_pos_one_sigma.labels(key.split(":")[1], key.split(":")[0]).set(stdev(value))
    logging.info(f"{which_score} Updated!")
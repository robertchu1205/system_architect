import time, schedule, logging, functions

logging.basicConfig(
    format="%(levelname)s %(message)s",
    level=logging.INFO
)

def average_sigma(which_score):
    functions.standard_lines(
        host="10.41.241.230", port="30123", 
        username="OneAI_App", password="yoyoeat2020", 
        database="OPS_WIH", which_score=which_score,
    )
    
if __name__ == '__main__':
    # init average, sigma
    average_sigma("score")
    average_sigma("AI_NNmodel_score")
    # init dots
    functions.hour_record(
        host="10.41.241.230", port="30123", 
        username="OneAI_App", password="yoyoeat2020", 
        database="OPS_WIH", cal_hours=1, cal_amount=5,
    )
    # schedule dots
    schedule.every().hours.at(":00").do(functions.hour_record, 
        host="10.41.241.230", port="30123", 
        username="OneAI_App", password="yoyoeat2020", 
        database="OPS_WIH", cal_hours=1, cal_amount=5,
    )
    # start the cronjob
    while 1:
        n = schedule.idle_seconds()
        logging.info(f"minutes to wait: {str(n)}")
        if n is None:
            # no more jobs
            break
        elif n > 0:
            # sleep exactly the right amount of time
            time.sleep(n)
        schedule.run_pending()
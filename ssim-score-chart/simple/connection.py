import mysql.connector
import logging

class Connection:
    ### db spec
    def __init__(self, host, port, user, password, database):
        self.connect = mysql.connector.connect(
            host="10.41.241.230",
            port="30123",
            user="OneAI_App",
            password="yoyoeat2020",
            database="OPS_WIH"
        )

        self.cur = self.connect.cursor()
        self.time_start = ""
        self.time_end = ""

    ### mean values of score_list
    def average(self, score_list):
        # try:
        if len(score_list) != 0:
            score = 0
            for s in score_list:
                score+=s[0]
            return score / len(score_list)
        else:
            return 0
        # except Exception as e:
        #     logging.error(f"when averaging scores, error: {e}")
        #     return 0

    ### distinct models, lines within time range
    def select_models_lines(self):
        if self.time_start == "" or self.time_end == "":
            return []
        logging.info(f"lines & models collected from {str(self.time_start)} to {str(self.time_end)}")
        self.cur.execute(f"""
            SELECT distinct model, line from report_multi_model_result 
            where import_time between '{self.time_start}' and '{self.time_end}'
            and line is not NULL and line > '' and line != 'nan' 
        """)
        models_lines = self.cur.fetchall()
        # models = [m[0] for m in models]
        return models_lines

    ### selecting models, lines by join took too long
    def select_models_lines_by_join(self):
        if self.time_start == "" or self.time_end == "":
            return []
        logging.info(f"lines & models collected from {str(self.time_start)} to {str(self.time_end)}")
        self.cur.execute(f"""
            SELECT distinct A.model, B.line FROM
            (
                SELECT model, image_name FROM report_multi_model_result
                WHERE import_time between '{self.time_start}' and '{self.time_end}'
            ) A INNER JOIN
            (
                SELECT line, image_name FROM report_daily_online_report 
                WHERE import_datetime between '{self.time_start}' and '{self.time_end}'
                and line is not NULL and line > '' and line != 'nan'
            ) B ON BINARY A.image_name = BINARY B.image_name
        """)
        models_lines = self.cur.fetchall()
        return models_lines

    ### select amount of scores with specific model and line and calculate mean of it
    def cal_score(self, which_score, model, line, amount=5):
        if self.time_start == "" or self.time_end == "":
            return 0
        self.cur.execute(f"""
            SELECT {str(which_score)}
            FROM report_multi_model_result
            WHERE model='{model}' and line='{line}'
            and import_time between '{self.time_start}' and '{self.time_end}' 
            and {str(which_score)} is not NULL 
            and label='OK'
            ORDER BY RAND() LIMIT {str(amount)}
        """)
        return self.average(self.cur.fetchall())
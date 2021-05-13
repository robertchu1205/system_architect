# Logics
- calculate data from db 
- expose metrics thru **"prometheus"** with method **"spc control chart"**
# Phase 1
- all standard time ranges from [config.py](./simple/config.py)
- query **join** took too long
- monitor both ai confidence and ssim score
    - Gauge **ssim_avg_gauge, ai_score_avg_gauge** saved random 5 scores in last an hour
    - Gauge **ssim_average_line; ai_score_average_line** the average of every 5 scores in an hour within defined time range
    - Gauge **ssim_pos_one_sigma; ai_score_pos_one_sigma** a sigma of every 5 scores in an hour within defined time range
- score chart started from executing **"python [main.py](./simple/main.py)"**
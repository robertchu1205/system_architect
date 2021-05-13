rsync -rtuv -e "ssh -i /home/robert/.ssh/id_rsa" wzsdat@172.30.52.10:/home/wzsdat/AIpredict /data/ftp/aoi-wzs-p3-dip-prewave-saiap
chown -R ftp:ftp /data/ftp/aoi-wzs-p3-dip-prewave-saiap/AIpredict/
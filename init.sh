#!/bin/bash
sudo apt install python3-pip
sudo -H pip3 install BASC-py4chan
#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "*/5 * * * * sh -x /home/ubuntu/ylyl-basc/script.sh > /home/ubuntu/ylyl-basc/ylyl.log 2>&1 >/dev/null 2>&1" >> mycron
#install new cron file
crontab mycron
rm mycron
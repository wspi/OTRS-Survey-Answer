#!/bin/bash

# author: Wagner Spirigoni
# email: wagner@wspi.com.br
# 11/2011

# creating queue
/opt/otrs/bin/otrs.AddQueue.pl -n "Waiting Approval" -g "approval"

# creating database
echo "Please enter root mysql password"
/usr/bin/mysql -u root -p otrs < db.sql

# copying script to default location
cp ./survey_answer.py /opt/otrs/Custom/
chmod +x /opt/otrs/Custom/survey_answer.py
chown otrs:otrs /opt/otrs/Custom/survey_answer.py

#cron
cp survey /opt/otrs/var/cron/
/opt/otrs/bin/Cron.sh restart otrs

#changing survey send time
sed -i "s/StateType/State/" /opt/otrs/Kernel/System/Ticket/Event/SurveySendRequest.pm
sed -i "s/closed/Waiting\ Approval/" /opt/otrs/Kernel/System/Ticket/Event/SurveySendRequest.pm

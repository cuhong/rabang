sudo apt-get update
sudo apt-get install supervisor
sudo service supervisor start
sudo service supervisor status

/etc/supervisor/conf.d/ <- 설정파일
/var/log/supervisor/ <- 로그


sudo pip3 install supervisor
sudo supervisorctl
supervisor> reread
supervisor> update
supervisor> `help`
supervisor> restart airsupply_celery

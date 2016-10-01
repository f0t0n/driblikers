#!/bin/sh -e

owner_user=$(stat -c %u .)
owner_group=$(stat -c %g .)
worker_user=$(id -u worker)
worker_group=$(id -g worker)

if [ "$owner_user" -ne "0" ] && [ "$owner_group" -ne "0" ] ; then
  [ "$owner_group" -ne "$worker_group" ] && update_worker=1
  [ "$owner_user" -ne "$worker_user" ] && update_worker=1
fi

if [ "$update_worker" -eq "1" ]; then
  deluser 'worker'
  addgroup -g "$owner_group" -S 'worker'
  adduser -u "$owner_user" -G 'worker' -S -s '/bin/false' \
    -h "$APP_DIR" 'worker'
fi

pip install --user --no-cache-dir --requirement ./requirements.txt
chown -R worker:worker .
exec su-exec worker "$@"


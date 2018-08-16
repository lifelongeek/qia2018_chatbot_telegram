#!/usr/bin/env bash

script_home=bot_code
script_name="$script_home/bot.py"
pid_file="$script_home/bot.pid"

# returns a boolean and optionally the pid
running() {
    local status=false
    if [[ -f $pid_file ]]; then
        # check to see it corresponds to the running script
        local pid=$(< "$pid_file")
        local cmdline=/proc/$pid/cmdline
        # you may need to adjust the regexp in the grep command
        if [[ -f $cmdline ]] && grep -q "$script_name" $cmdline; then
            status="true $pid"
        fi
    fi
    echo $status
}

start() {
    echo "starting $script_name"
    python $script_name &
    echo $! > "$pid_file"
}

stop() {
    kill $1 2>/dev/null
    rm "$pid_file"
    echo "stopped"
}

stopall() {
    kill $1 2>/dev/null
    rm "$pid_file"
}

read running pid < <(running)

case $1 in
    start)
        if $running; then
            echo "$script_name is already running with PID $pid"
        else
            start
        fi
        ;;
    stop)
        stop $pid
        ;;
    restart)
        stop $pid
        start
        ;;
    restartall)
        stopall $pid
        start
        ;;
    status)
        if $running; then
            echo "$script_name is running with PID $pid"
        else
            echo "$script_name is not running"
        fi
        ;;
    *)  echo "usage: $0 <start|stop|restart|status>"
        echo "stop is killing the bot only, while stopall shuts down all the services with it"
        exit
        ;;
esac

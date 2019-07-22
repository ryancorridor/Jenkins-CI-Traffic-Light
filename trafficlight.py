#! /usr/bin/env python
import argparse
import json
import math
import smtplib
import subprocess
import sys
import time
import urllib.request
from urllib.error import HTTPError

from pyfirmata import Arduino

# Initializing board
board = Arduino('<insert_board_serial_port_here>')

LEDS = {
    "red": board.get_pin('d:<insert_pin_number_here>:o'),
    "yellow": board.get_pin('d:<insert_pin_number_here>:o'),
    "green": board.get_pin('d:<insert_pin_number_here>:o')
}
JENKINS_SERVERS = {
    'insert_server_name_here': '<insert_server_url_here>',
}

EMAIL_RELAY = '<insert_email_relay_here>'
EMAIL_SENDER = '<insert_email_sender_here>'


# ----- LED FUNCTIONS ----- #


def select_led(color):
    return LEDS[color]


def light_on(color):
    select_led(color).write(1)


def light_off(color):
    select_led(color).write(0)


def pulse(color, delay):
    light_on(color)
    time.sleep(delay)
    light_off(color)
    time.sleep(delay)


# ----- MISC FUNCTIONS ----- #
def convert_milliseconds(millis):
    millis = int(millis)
    hours = millis / 1000 / 60 / 60
    minutes = hours * 60 % 60
    hours = hours % 60
    seconds = minutes * 60 % 60
    minutes = minutes % 60

    return math.floor(hours), math.floor(minutes), seconds


def paginate(items, page_size, target):
    display_lists = []
    number_of_pages = len(items) / math.ceil(page_size)
    for i in range(int(number_of_pages)):
        temp_list = []
        for j in range(page_size):
            item_number = (i * page_size) + j
            temp_list.append("(" + str(item_number + 1) + ") " + str(items[item_number][str(target)]))
        display_lists.append(temp_list)
    return display_lists


def send_email(server, job, build, status, estimated_finish, recipient_email):
    estimated_finish = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(estimated_finish / 1000))

    sender = EMAIL_SENDER
    receivers = recipient_email

    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient_email
    msg['Subject'] = 'Build #{0} is {1}'.format(build, status.upper())

    body = """\
        Server: {0}
        Job: {1}
        Build: {2}

        Status has changed to {3}
        Estimated finish time is {4}
        
        {5}""".format(server, job, build, status.upper(), estimated_finish, server + "job/" + job + "/" + build)

    msg.attach(MIMEText(body, 'plain'))
    message = msg.as_string()

    try:
        HOST = EMAIL_RELAY
        PORT = '25'
        SERVER = smtplib.SMTP()
        SERVER.connect(HOST, PORT)
        SERVER.sendmail(sender, receivers, message)
        print("\nSuccessfully sent status change notification to " + recipient_email)
        SERVER.quit()
    except smtplib.SMTPException:
        print("\nError: unable to send status change notification")
        SERVER.quit()


# ----- CORE FUNCTIONS ----- #
def select_jenkins_server():
    subprocess.call('clear')  # Clear page
    print('Select a Jenkins server:')

    options = {}
    option_number = 1

    for server in JENKINS_SERVERS:  # Populate with dictionary hard coded
        options[option_number] = server
        print('\t(' + str(option_number) + ') ' + server)
        option_number += 1
    print()

    selected_server = None
    while selected_server == None:  # Looping until successful input is found
        num = input('Enter selection (i.e. \"1\") >>> ')
        if not int(num) in options:
            print('\nInvalid entry. Please use a number to specify your entry.')
        else:
            selected_server = JENKINS_SERVERS[options[int(num)]]

    print("Selected " + JENKINS_SERVERS[options[int(num)]])
    time.sleep(1)
    select_job(selected_server)  # Move to next stage


def select_job(selected_server):
    subprocess.call('clear')  # Clear page

    options = {}
    option_number = 1

    url = selected_server + '/api/json'
    try:  # Attempt to find json return, if found continue
        response = urllib.request.urlopen(url)
    except HTTPError as e:  # Catching in cases of the url being malformed
        print("Error code", e.code, "when accessing Jenkins server", selected_server)
        print("Sending back to Jenkins server selection")
        time.sleep(5)
        select_jenkins_server()

    if response.status is not 200:  # If not a success when pinging
        print("Something went wrong when trying to access Jenkins")
        print("Sending back to Jenkins server selection")
        time.sleep(5)
        select_jenkins_server()
    else:  # Parse the data
        data = json.loads(response.read())

        jobs = paginate(data['jobs'], 10, "name")

        for job in data['jobs']:  # Populate
            options[option_number] = job['name']
            option_number += 1

        selected_job = None
        page_number = 1;

        while selected_job == None:  # Looping until successful input is found
            subprocess.call('clear')
            print('Jenkins Server: ' + selected_server)
            print('\nSelect a job:')

            for job in jobs[page_number - 1]:
                print("\t" + job)

            print('\n\t(0) Go back')

            num = input('\nEnter selection (i.e. \"1\" or p/n for moving pages) >>> ')
            if num == "0":
                selected_job = 'Go back'
            elif (num == "n" or num == "next"):
                if page_number < len(jobs):
                    page_number += 1
            elif (num == "p" or num == "prev"):
                if page_number > 1:
                    page_number -= 1
            elif num.isdigit():
                if not int(num) in options:
                    print('\nInvalid entry. Please use a valid number to specify your entry.')
                    time.sleep(1)
                else:
                    selected_job = options[int(num)]
            else:
                print('\nInvalid entry. Please use a valid number to specify your entry.')
                time.sleep(1)
        if selected_job == 'Go back':  # Move back a stage
            print("Going back to select a Jenkins server")
            time.sleep(1)
            select_jenkins_server()
        else:  # Move to next stage
            print("Selected " + options[int(num)])
            time.sleep(1)
            select_build(selected_server, selected_job)


def select_build(selected_server, selected_job):
    subprocess.call('clear')  # Clear page

    options = {}
    option_number = 1

    url = selected_server + "/job/" + selected_job + '/api/json'
    try:  # Attempt to find json return, if found continue
        response = urllib.request.urlopen(url)
    except HTTPError as e:  # Catching in cases of the url being malformed
        print("Error code", e.code, "when accessing Jenkins job", selected_job)
        print("Sending back to Jenkins job selection")
        time.sleep(5)
        select_job(selected_server)

    if response.status is not 200:  # If not a success when pinging
        print("Something went wrong when trying to access Jenkins")
        print("Sending back to Jenkins job selection")
        time.sleep(5)
        select_job(selected_server)
    else:  # Parse the data
        data = json.loads(response.read())

        builds = paginate(data['builds'], 10, "number")

        for build in data['builds']:  # Populate
            options[option_number] = build['number']
            option_number += 1

        selected_build = None
        page_number = 1

        while selected_build is None:  # Looping until successful input is found
            subprocess.call('clear')
            print('Jenkins Server: ' + selected_server)
            print('Job: ' + selected_job)
            print('\nSelect a Build:')
            if len(builds) == 0:
                print("\nJob is empty. Returning back to job selection.")
                time.sleep(3)
                select_job(selected_server)
            for build in builds[page_number - 1]:
                print("\t" + build)

            print('\n\t(0) Go back')

            num = input('\nEnter selection (i.e. \"1\" or p/n for moving pages) >>> ')
            if num == "0":
                selected_build = 'Go back'
            elif num == "n" or num == "next":
                if page_number < len(builds):
                    page_number += 1
            elif num == "p" or num == "prev":
                if page_number > 1:
                    page_number -= 1
            elif num.isdigit():
                if not int(num) in options:
                    print('\nInvalid entry. Please use a valid number to specify your entry.')
                    time.sleep(1)
                else:
                    selected_build = options[int(num)]
            else:
                print('\nInvalid entry. Please use a valid number to specify your entry.')
                time.sleep(1)
        if selected_build == 'Go back':  # Move back a stage
            print("Going back to select a Jenkins job")
            time.sleep(1)
            select_job(selected_server)
        else:  # Move to next stage
            print("Selected " + str(options[int(num)]))
            time.sleep(1)
            select_email(selected_server, selected_job, str(selected_build))


def select_email(selected_server, selected_job, selected_build):
    subprocess.call("clear")  # Clear page
    print('Jenkins Server: ' + selected_server)
    print('Job: ' + selected_job)
    print('Build: ' + str(selected_build))
    print('\nDo you want email notifications?')

    selected_opt_in = None
    while selected_opt_in == None:  # Looping until successful input is found
        choice = input('Enter selection (yes/no/y/n) >>> ')
        if choice.lower() == "yes" or choice.lower() == "y":
            selected_opt_in = True
        elif choice.lower() == "no" or choice.lower() == "n":
            selected_opt_in = False
        else:
            print('\nInvalid entry. Please enter your choice again.')

    selected_email = None
    if selected_opt_in:
        selected_email = input('Enter email (i.e. bob@gmail.com) >>> ')

    monitor(selected_server, selected_job, selected_build, selected_opt_in, selected_email)  # Move to next stage


def monitor(selected_server, selected_job, selected_build, wants_email, selected_email):
    subprocess.call("clear")  # Clear page
    print('Jenkins Server: ' + selected_server)
    print('Job: ' + selected_job)
    print('Build: ' + str(selected_build))
    if wants_email:
        print('Email: ' + selected_email)

    url = selected_server + "/job/" + selected_job + "/" + selected_build + "/api/json"

    finished = False
    delayed = False
    currently_building = False

    while not finished:
        try:
            response = urllib.request.urlopen(url)
            if response.status is not 200:  # If not a success when pinging
                print("Something went wrong with the Jenkins request")
                print("Exiting Jenkins insight...")
                time.sleep(3)
                exit(1)
        except HTTPError:
            print("\nSomething went wrong with the Jenkins request")
            print("Did you enter the right information?")
            print("Exiting Jenkins insight...")
            time.sleep(3)
            exit(1)
        data = json.loads(response.read())
        status = data['result']

        # Inflating by 20% because Jenkins is too optimistic
        estimated_finish_time = int(data['estimatedDuration']) * 1.2 + int(data['timestamp'])

        if status == "SUCCESS":  # Displays SUCCESS when build succeeded
            print()
            print("Build result is " + status)

            light_off("yellow")  # in-case of delay
            light_on("green")

            finished = True
            if wants_email:
                send_email(selected_server, selected_job, selected_build, "SUCCESS", estimated_finish_time,
                           selected_email)
            exit(1)
        elif status == "FAILURE" or status == "ABORTED":  # Displays FAILURE or ABORTED when build stops
            print()
            print("Build result is " + status)

            light_off("yellow")  # in-case of delay
            light_on("red")

            finished = True
            if wants_email:
                send_email(selected_server, selected_job, selected_build, status.upper(), estimated_finish_time,
                           selected_email)
            exit(1)
        elif time.time() > estimated_finish_time / 1000 and not delayed:  # Checking to see if job is taking too long
            light_on("yellow")
            print("\nJob is taking longer than expected.")
            if wants_email:
                print("Sending delayed notification.")
                send_email(selected_server, selected_job, selected_build, "DELAYED", estimated_finish_time,
                           selected_email)
            delayed = True
        elif data['building'] == True and not delayed:  # Displays true when building
            pulse("yellow", .5)

            if currently_building is False:
                currently_building = True
                print("\nCurrent status is BUILDING")
                print("Build should finish by " + time.strftime('%Y-%m-%d %H:%M:%S',
                                                                time.localtime(estimated_finish_time / 1000)))
                if wants_email:
                    send_email(selected_server, selected_job, selected_build, "BUILDING", estimated_finish_time,
                               selected_email)

        time.sleep(1)  # Pulse every second


if __name__ == '__main__':
    if not len(sys.argv) > 1:  # If not arguments, go through setup steps
        select_jenkins_server()
    else:  # Get args and parse them
        parser = argparse.ArgumentParser()
        parser.add_argument("server", help="Jenkins server name")
        parser.add_argument("job", help="Jenkins job")
        parser.add_argument("build", help="Build number")
        parser.add_argument("-e", "--email", help="Email to send notification emails to")
        args = parser.parse_args()
        if args.email:  # If client passed email arg
            monitor(JENKINS_SERVERS[args.server], args.job, args.build, True, args.email)
        else:
            monitor(JENKINS_SERVERS[args.server], args.job, args.build, False, None)

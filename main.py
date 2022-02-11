# import everything needed - upip will only install things after the network is configured so will happen later or from
# static prepacked package
from machine import ADC, Pin
import utime
import network
import umail
import urequests
import esp32

# give it a bit to make sure that everything booted up
utime.sleep(3)

# set wifi access details here
ESSID = "your_wifi_network_name"
WLAN_PASS = "Your_wifi_password"
# ADC is only on port 32-39 in esp32
PORT_CONNECTED_TO_SIREN = 32
# email app config
MAIL_PASS = "your_email_password"
MAIL_ADDRESS = "your_email_address"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
# telegram config, set your telegram bot token here
TELEGRAM_CHAT_ID = 0123456789 # your telegram chat id should be here
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
# general configuration details
LED_PIN = 2
MAX_OK_TEMP = 65
FIRE_ALARM_LOCATION = "electric box"
SENSOR_TYPE = "alarm"
# influxdb config
INFLUXDB_BUCKET = "influxdb_bucket_name"
INFLUXDB_ORG = "influxdb_org"
INFLUCDB_TOKEN = "influxdb_token"


led = Pin(LED_PIN, Pin.OUT)
alarm_pin = Pin(PORT_CONNECTED_TO_SIREN, Pin.IN, Pin.PULL_DOWN)
health_counter = 0


# network class
class Networking:

    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def check_net_connection(self):
        return self.wlan.isconnected()

    def connect_to_net(self, essid_name, wlan_pass):
        print('connecting to network...')
        self.wlan.connect(essid_name, wlan_pass)
        utime.sleep_ms(100)
        led.value(1)
        # wait until wif connected
        while not self.check_net_connection():
            led.value(0)
            utime.sleep_ms(100)
            led.value(1)
            utime.sleep_ms(100)
        print('network config:', self.wlan.ifconfig())


# things that should only run once at start
networking = Networking()


# check alarm triggered function
def alarm_triggered(alarm_pin_object):
    read_value = alarm_pin_object.value()
    if read_value == 1:
        print("port_value: " + str(read_value))
        print("alrarm triggered")
        return True
    else:
        return False


# send email function
def send_email(email_subject, email_message):
    print("sending email")
    smtp = umail.SMTP(MAIL_SERVER, MAIL_PORT, username=MAIL_ADDRESS, password=MAIL_PASS)
    smtp.to(MAIL_ADDRESS)
    smtp.write("From: " + MAIL_ADDRESS + "\n")
    smtp.write("To: " + MAIL_ADDRESS + "\n")
    smtp.write("Subject: " + email_subject + "\n\n")
    smtp.write(email_message + "\n")
    smtp.send()
    smtp.quit()
    print("email sent")


# send telegram message
def send_telegram(telegram_message):
    print("sending telegram alert")
    url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage"
    payload = "{\"chat_id\": \"" + str(TELEGRAM_CHAT_ID) + "\", \"text\": \"" + telegram_message + "\"}"
    headers = {
        'Content-Type': 'application/json'
    }
    response = urequests.post(url, headers=headers, data=payload)
    print(str(response.text))


def convert_fahrenheit_to_celsius(temp_in_f):
    temp_in_c = ((temp_in_f - 32) * 5) / 9
    return temp_in_c


def check_current_temp():
    return convert_fahrenheit_to_celsius(esp32.raw_temperature())


def write_health_ping_to_influxdb(sensor_type):
    influx_url = "https://eu-central-1-1.aws.cloud2.influxdata.com/api/v2/write?org=" + str(INFLUXDB_ORG) + \
          "&bucket=" + str(INFLUXDB_BUCKET) + "&precision=s"
    influx_payload = "sensor_health,sensor_type=" + str(sensor_type) + " sensor_value=1" + "\n"
    influx_headers = {
        'Authorization': "Token " + str(INFLUCDB_TOKEN),
        'Content-Type': 'text/plain'
    }
    influx_response = urequests.post(influx_url, headers=influx_headers, data=influx_payload)
    print(str(influx_response.text))


# main never ending loop
while True:
    try:
        if networking.check_net_connection() is False:
            networking.connect_to_net(ESSID, WLAN_PASS)
        # check for alarm triggered function
        if alarm_triggered(alarm_pin) is True:
            led.value(0)
            send_email("Burglar alarm raised", "An burglar alarm has been raised at the house")
            send_telegram("A burglar alarm has been raised at the house")
            led.value(1)
            # let's give it a few minutes before spamming the mailbox
            utime.sleep(600)
        if check_current_temp() >= MAX_OK_TEMP:
            led.value(0)
            send_email("fire alarm at house raised", "fire alarm at house raised with current temperature being " +
                       str(check_current_temp()) + ", location of sensor is at " + FIRE_ALARM_LOCATION)
            send_telegram("fire alarm at house raised, current temperature is " + str(check_current_temp()) +
                          ", location of sensor is at " + FIRE_ALARM_LOCATION)
            led.value(1)
            # let's give it a few minutes before spamming the mailbox
            utime.sleep(600)
        # wait 100 milliseconds between each time you check if the alarm is raised
        utime.sleep_ms(100)
        # write the sensor health into influxdb
        health_counter = health_counter + 1
        print(health_counter)
        if health_counter == 100:
            write_health_ping_to_influxdb(SENSOR_TYPE)
            health_counter = 0
    except Exception as e:
        print(e)

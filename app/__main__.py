import os
import datetime
import lib.spl_meter as spl
from lib.google_iot import GoogleIoT, generateKeys
from lib.mqtt_client import get_client, download_google_ca_cert

if __name__ == "__main__":
    # Set parameters
    # Project
    project_id = os.environ.get("GOOGLE_IOT_PROJECT")
    cloud_region = os.environ.get("GOOGLE_IOT_REGION")
    registry_id = os.environ.get("GOOGLE_IOT_REGISTRY")
    service_account = os.environ.get("GOOGLE_IOT_SERVICE_ACCOUNT_TOKEN")
    device_id = "rpi-pa-{}".format(os.environ.get("RESIN_DEVICE_UUID"))
    device_name = os.environ.get("DEVICE_NAME")
    # Security
    credentialPath = "data/"
    ca_certs = "{}{}".format(credentialPath, os.environ.get("GOOGLE_CA_CERT"))
    algorithm = os.environ.get("ALGORITHM")
    private_key_file = "{}{}".format(credentialPath, os.environ.get("PRIVATE_KEY_FILE"))
    # MQTT
    mqtt_bridge_hostname = os.environ.get("MQTT_BRIDGE_HOSTNAME")
    mqtt_bridge_port = os.environ.get("MQTT_BRIDGE_PORT")

    #Set location and recording time values
    recording_time = int(os.environ.get("RECORDING_TIME"))
    longitude = float(os.environ.get("LONGITUDE"))
    latitude = float(os.environ.get("LATITUDE"))

    # Register the device using google iot core api if it doesnt exist
    google = GoogleIoT(project_id, cloud_region, registry_id, device_id, str(service_account))
    if not google.is_existing_device(device_id):
        google.registerDevice()

    # Verify if google ca certification package exist
    if not os.path.isfile("/home/decibelsmeter/data/roots.pem"):
        print("Downloading Google ca certification package...")
        download_google_ca_cert()
    
    # Set mqqt topic
    sub_topic = 'events'
    mqtt_topic = '/devices/{}/{}'.format(device_id, sub_topic)

    # Get current time and expiration time
    jwt_iat = datetime.datetime.utcnow()
    jwt_exp_mins = 20

    # Get the mqtt client
    client = get_client(project_id, cloud_region, registry_id, device_id, 
        private_key_file, algorithm, ca_certs, mqtt_bridge_hostname, int(mqtt_bridge_port))

    while True:

        # Process network events.
        client.loop()

        # Listen to the microphone
        pa = spl.getPyAudio()
        stream = spl.getStream(pa)
        decibels = spl.record(stream, recording_time)
        print("Location: {}, {}".format(longitude, latitude))
        print('Average decibels for %d seconds: {:+.2f} dB'.format(decibels) % (recording_time))

        # [START iot_mqtt_jwt_refresh]
        seconds_since_issue = (datetime.datetime.utcnow() - jwt_iat).seconds
        if seconds_since_issue > 60 * jwt_exp_mins:
            print('Refreshing token after {}s'.format(seconds_since_issue))
            jwt_iat = datetime.datetime.utcnow()
            client.loop()
            client.disconnect()
            client = get_client(project_id, cloud_region, registry_id, device_id, 
                private_key_file, algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port)
        # [END iot_mqtt_jwt_refresh]


        # Set data to be published
        payload = '{},{},{},{},{}'.format(latitude, longitude, format(decibels, '.2f'), device_name, os.environ.get("RESIN_DEVICE_UUID"))
        print(payload)

        # Publish the data on the topic over mqtt bridge
        client.publish(mqtt_topic, payload, qos=1)

        # Process network events.
        client.loop()
        
        #Close the stream and pyaudio when finished
        spl.close_stream(pa, stream)

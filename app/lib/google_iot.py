from google.cloud import iot_v1
from google.oauth2 import service_account
import subprocess
import json
import re
import io


class GoogleIoT:
  def __init__(self, project_id, cloud_region, registry_id, device_id, service_account_token):
    self.project_id = project_id
    self.cloud_region = cloud_region
    self.registry_id = registry_id
    self.device_id = device_id
    self.service_account_token = json.loads(re.sub(r"/\n/g", '\\n', service_account_token))
    self.credentials_path = 'data/'

    credentials = service_account.Credentials.from_service_account_info(self.service_account_token)
    scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/cloudiot', 'https://www.googleapis.com/auth/pubsub'])
    self.client = iot_v1.DeviceManagerClient(credentials=scoped_credentials)

  def is_existing_device(self, device_id):
    parent = self.client.registry_path(self.project_id, self.cloud_region, self.registry_id)
    devices = list(self.client.list_devices(request={"parent": parent}))
    for device in devices:
        if device_id == device.id:
          return True
    return False
  
  def registerDevice(self):
    parent = self.client.registry_path(self.project_id, self.cloud_region, self.registry_id)

    generateKeys()

    with io.open('{}rsa_public.pem'.format(self.credentials_path)) as f:
      rsa_pub_key = f.read()

    # Set device configuration
    device_template = {
      "id": self.device_id,
      "credentials": [
        {
          "public_key": {
              "format": iot_v1.PublicKeyFormat.RSA_PEM,
              "key": rsa_pub_key,
          }
        }
      ],
    }

    return self.client.create_device(request={"parent": parent, "device": device_template})

def generateKeys():
  subprocess.check_call(["chmod", "+x", "./scripts/generate_keys.sh"])
  keygen = subprocess.check_call(["./scripts/generate_keys.sh"])
  if keygen != 0:
    raise Exception("Error generating keys.")

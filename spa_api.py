import logging
import hashlib
import random
import string
import time
import json
import aiohttp

_LOGGER = logging.getLogger(__name__)

async def authenticate(session, config):
    BASE_URL = "https://smarthub-eu.bestwaycorp.com"
    APPID = "AhFLL54HnChhrxcl9ZUJL6QNfolTIB"
    APPSECRET = "4ECvVs13enL5AiYSmscNjvlaisklQDz7vWPCCWXcEFjhWfTmLT"

    def generate_auth():
        nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        ts = str(int(time.time()))
        sign = hashlib.md5((APPID + APPSECRET + nonce + ts).encode("utf-8")).hexdigest().upper()
        return nonce, ts, sign

    push_type = config.get("push_type", "fcm")

    payload = {
        "app_id": APPID,
        "lan_code": "en",
        "location": "GB",
        "push_type": push_type,
        "timezone": "GMT",
        "visitor_id": config["visitor_id"],
        "registration_id": config["registration_id"]
    }

    if push_type == "fcm":
        payload["client_id"] = config["client_id"]

    nonce, ts, sign = generate_auth()
    headers = {
        "pushtype": push_type,
        "appid": APPID,
        "nonce": nonce,
        "ts": ts,
        "accept-language": "en",
        "sign": sign,
        "Authorization": "token",
        "Host": "smarthub-eu.bestwaycorp.com",
        "Connection": "Keep-Alive",
        "User-Agent": "okhttp/4.9.0",
        "Content-Type": "application/json; charset=UTF-8"
    }

    _LOGGER.debug("Authenticating with payload: %s", payload)

    async with session.post(
        f"{BASE_URL}/api/enduser/visitor",
        headers=headers,
        json=payload,
        ssl=False
    ) as resp:
        data = await resp.json()
        _LOGGER.debug("Auth response: %s", data)
        return data.get("data", {}).get("token")


class BestwaySpaAPI:
    BASE_URL = "https://smarthub-eu.bestwaycorp.com"
    APPID = "AhFLL54HnChhrxcl9ZUJL6QNfolTIB"
    APPSECRET = "4ECvVs13enL5AiYSmscNjvlaisklQDz7vWPCCWXcEFjhWfTmLT"

    def __init__(self, session: aiohttp.ClientSession, config: dict):
        self.session = session
        self.token = config["token"]
        self.device_id = config.get("device_id") or config["device_name"]
        self.product_id = config.get("product_id") or config["device_name"]
        self.client_id = config.get("client_id")
        self.registration_id = config.get("registration_id")
        self.push_type = config.get("push_type", "fcm")

    def _generate_auth_headers(self):
        nonce = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
        ts = str(int(time.time()))
        sign = hashlib.md5((self.APPID + self.APPSECRET + nonce + ts).encode("utf-8")).hexdigest().upper()
        return {
            "pushtype": self.push_type,
            "appid": self.APPID,
            "nonce": nonce,
            "ts": ts,
            "accept-language": "en",
            "sign": sign,
            "Authorization": f"token {self.token}",
            "Host": "smarthub-eu.bestwaycorp.com",
            "Connection": "Keep-Alive",
            "User-Agent": "okhttp/4.9.0",
            "Content-Type": "application/json; charset=UTF-8"
        }

    async def get_status(self):
        payload = {
            "device_id": self.device_id,
            "product_id": self.product_id
        }

        _LOGGER.debug("Sending get_status payload: %s", payload)

        async with self.session.post(
            f"{self.BASE_URL}/api/device/thing_shadow/",
            headers=self._generate_auth_headers(),
            json=payload,
            ssl=False
        ) as resp:
            data = await resp.json()
            _LOGGER.debug("Full API response: %s", data)
            
            # Extract the actual device state from the nested structure
            raw_data = data.get("data", {})
            _LOGGER.debug("Raw data from API: %s", raw_data)
            
            # The device state is likely nested in state.reported or similar
            if "state" in raw_data:
                if "reported" in raw_data["state"]:
                    device_state = raw_data["state"]["reported"]
                    _LOGGER.debug("Found reported state: %s", device_state)
                    return device_state
                elif "desired" in raw_data["state"]:
                    device_state = raw_data["state"]["desired"]
                    _LOGGER.debug("Found desired state: %s", device_state)
                    return device_state
                else:
                    _LOGGER.debug("Found state object: %s", raw_data["state"])
                    return raw_data["state"]

            _LOGGER.warning("Could not find nested state, returning raw data: %s", raw_data)
            return raw_data

    async def set_state(self, key, value):
        if isinstance(value, bool):
            value = int(value)

        payload = {
            "device_id": self.device_id,
            "product_id": self.product_id,
            "desired": {
                "state": {
                    "desired": {
                        key: value
                    }
                }
            }
        }

        _LOGGER.debug("Sending set_state payload: %s", payload)

        async with self.session.post(
            f"{self.BASE_URL}/api/device/command/",
            headers=self._generate_auth_headers(),
            json=payload,
            ssl=False
        ) as resp:
            response = await resp.json()
            _LOGGER.debug("set_state response: %s", response)
            return response

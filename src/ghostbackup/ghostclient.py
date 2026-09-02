# ghostclient.py
import logging
import requests
import datetime
import jwt

from dateutil import parser
from urllib.error import HTTPError
from urllib.parse import urlparse
from . import LOGGER_NAME

class GhostClient:

    __default_algo = "HS256"
    __path_admin = "/ghost/api/admin"
    __slug_actions = "/actions/"
    __slug_db = "/db/"

    def __init__(self, host, accesstoken):
        self.__host = host
        self.__secret = bytes.fromhex(accesstoken.split(":")[1])
        self.__kid = accesstoken.split(":")[0]
        self.__log = logging.getLogger(LOGGER_NAME)
    
    def lastModified(self) -> datetime:
        resp = self.__request(GhostClient.__slug_actions, {"limit":"1"})
        if len(resp) and len(resp.get("actions")):
            return  parser.isoparse(resp.get("actions")[0].get("created_at"))
        else:
            return datetime.datetime.now()
    
    def backUp(self):
        return self.__request(GhostClient.__slug_db)
        
    def __request(self, action, filter={}) -> any:
        try:
            url = self.__host + GhostClient.__path_admin + action
            response = requests.get(url, headers=self.__buildHeaders(), params=filter)
            if response:
                return response.json()
            else:
                self.__log.debug("Could not connect to %s: %s: Reason: %s",
                                 response.raw.url,
                                 response.status_code,
                                 response.text)
                raise HTTPError(url = response.raw.url,
                                code = response.raw.status,
                                msg = response.text,
                                hdrs = response.raw.headers,
                                fp = None)
        except requests.ConnectionError as e:
            self.__log.error("Could not connect to %s ", e.request.url)
            raise e
        except requests.HTTPError as e:
            self.__log.error("Failed to access Ghost-Instance %s: %s", self.__host, e.response.reason)
            raise e
            
    def __buildHeaders(self) -> dict:
        headers = {
            "Authorization": f"Ghost {self.__buildToken()}",
            "Content-Type": "application/json",
            "Accept-Version": "v5.0"
        }
        if urlparse(self.__host).scheme != "https":
            headers["X-Forwarded-Proto"] = "https"
        return headers
        
    def __buildToken(self) -> str:
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "iat": int(now.timestamp()),
            "aud": "/admin/", 
            "exp": now + datetime.timedelta(minutes=5)
            }
        return jwt.encode(payload=payload, key=self.__secret, algorithm=GhostClient.__default_algo, headers={"kid":self.__kid})

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

def get_logger(name: str,
                 file_name: str = "api.log",
                 file_mode: str = "+w",
                 level: int = logging.DEBUG) -> logging.Logger:
    root_logger = logging.getLogger(name)
    
    if not root_logger.hasHandlers():
        logging.basicConfig(level=level,
                            filename=file_name,
                            filemode=file_mode,
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    return root_logger

logger = get_logger(__name__)

def create_client(secret_file: str | None = None, 
                  api_key: str | None = None, 
                  scopes: list | None = None,
                  api_service_name: str = "youtube",
                  api_version: str = "v3"):
    try:
        if secret_file is not None:
            # Get credentials and create an API client
            flow = InstalledAppFlow.from_client_secrets_file(secret_file, scopes)
            credentials = flow.run_local_server() 
            auth = {"credentials": credentials,}
            
        elif api_key is not None:
            auth = {"developerKey": api_key,}
        
        else:
            raise Exception("The api_key and secret_file are missing")
        
        client = build(api_service_name, 
                       api_version, 
                       **auth)
        
        return client
    except FileNotFoundError:
        logger.debug(f"Credential file {secret_file} not found")
    
    except Exception as err:
        logger.debug(f"Unexpected {err=}, {type(err)=}")
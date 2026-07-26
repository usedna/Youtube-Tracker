from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd
import os
import json
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

    
def save_json(data: dict[str, any], filename: str):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

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

    
def add_counting_prefix_to_file(base_name: str, file_dir: str) -> str:    
    dir_list = [f for f in os.listdir(file_dir) if base_name in f]
    
    return f"{base_name}_0{len(dir_list) + 1}.csv"


def check_directory(file_dir: str):
    file_path_dir = os.path.join(os.getcwd(), file_dir)

    if not os.path.exists(file_path_dir):
        os.makedirs(file_path_dir)


def get_file_path(file_name: str, file_dir: str, ext: str, count_file: bool = True) -> str:
    check_directory(file_dir)
    
    base_name = os.path.basename(file_name)

    if base_name.strip() == "":
        base_name = "result"
    
    if count_file:
        file_name = add_counting_prefix_to_file(base_name, file_dir)
                
    return f"{file_dir}/{file_name}.{ext}"


def unnest_dictionary(data: dict, 
                      prefix: str = "", 
                      excluded_key_prefix: list[str] = ["details", "statistics"]) -> dict:
    result = {}
    
    for key, value in data.items():
        if key in excluded_key_prefix:
            new_prefix = f"{prefix}"
        
        else:
            new_prefix = f"{prefix}{key}_"
        
        if isinstance(value, dict):
            nested_result = unnest_dictionary(value, new_prefix, excluded_key_prefix)
            result.update(nested_result)
        else:
            result[new_prefix] = value
            
    return result

def extract_items_from_data_list(data: dict) -> list[dict]:
    items = list(data.values())[0]
    if isinstance(items, list):
        data_items = [unnest_dictionary(item) for item in items]
        
    elif isinstance(items, dict):
        data_items = [unnest_dictionary(data)]
    else:
        TypeError(f"Expected a list or dict, but got {type(items)}")
        
    return data_items

def export_to_pandas(data: dict|list[dict]) -> pd.DataFrame:
    data_items = []
    
    if isinstance(data, list):
        for objects in data:
            data_items.extend(extract_items_from_data_list(objects))
    else:
        data_items = extract_items_from_data_list(data)
            
    df = pd.DataFrame(data_items)
    return df


def export_to_json(data: dict, file_name: str = "result", file_dir: str = "results/json", replace: bool = False):        
    file_path = get_file_path(file_name, file_dir, "json", count_file=not replace)
    
    save_json(data, file_path)


def export_to_csv(data: dict, file_name: str = "result", file_dir: str = "results/csv", replace: bool = False):
    file_path = get_file_path(file_name, file_dir, "csv", replace)

    df = export_to_pandas(data)
    df.to_csv(file_path, index=False)


def export_to_excel(data: dict, file_name: str = "result", file_dir: str = "results/excel", replace: bool = False):
    file_path = get_file_path(file_name, file_dir, "xlsx", replace)
    
    df = export_to_pandas(data)
    df.to_excel(file_path, index=False)
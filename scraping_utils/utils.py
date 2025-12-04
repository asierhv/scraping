import json
from typing import TypedDict, List, Dict

class AudioFeed(TypedDict):
    id: int
    pub_date: str
    title: str
    duration: str
    audio_filepath: str
    url: str

class Feed(TypedDict):
    source: str
    name: str
    rss_url: str
    audio_list: List[AudioFeed]
    
def read_json(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    return data

def write_json(filepath: str, data: List[Dict]):
    with open(filepath, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
import os
import json
import requests
import feedparser
import time
from urllib.parse import urlparse, unquote
from typing import TypedDict, List, Dict
import argparse

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
    
def read_feeds(filepath: str):
    feeds = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            feeds.append(json.loads(line))
    return feeds

def write_feeds(filepath: str, feed_rss: List[Feed]):
    with open(filepath, "w", encoding="utf-8") as f:
        for feed in feed_rss:
            f.write(json.dumps(feed, ensure_ascii=False) + "\n")

def download_file(url: str, output_path: str):
    if os.path.exists(output_path):
        print(f"Already downloaded: {output_path}")
        return
    try:
        print(f"Downloading {url} → {output_path}")
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(1024 * 64):
                f.write(chunk)
        print(" - Done.")
        return True
    except Exception as e:
        print(f" - Error downloading {url}: {e}")
        return False

def process_feed(feed_info: Feed, output_dir: str):
    source = feed_info.get("source")
    name = feed_info.get("name")
    rss_url = feed_info.get("rss_url")
    audio_list = feed_info.get("audio_list", None)
    id_list = [audio["id"] for audio in audio_list] if audio_list else None

    if any(v is None for v in (source, name, rss_url)):
        raise ValueError(f"ERROR: Missing required field in feed_info: {feed_info}")
    
    print(f"\n=== Processing {source}/{name} ===")
    feed = feedparser.parse(rss_url)

    if feed.bozo:
        raise ValueError(f"ERROR parsing feed: {feed.bozo_exception}")
        

    base_dir = os.path.join(output_dir, source, name)
    os.makedirs(base_dir, exist_ok=True)

    new_audio_list = []
    for entry in feed.entries:
        # Enclosure URL (the MP3 file)
        if "enclosures" not in entry or not entry.enclosures:
            continue

        url = entry.enclosures[0].get("url")
        if not url:
            continue
        
        full_id = entry.get("id")
        _id = int(os.path.split(full_id)[1])
        if id_list:
            if _id in id_list:
                continue
        
        pub_date = entry.get("published_parsed")
        title = entry.get("title")
        duration = entry.get("itunes_duration")
        
        season = entry.get("itunes_season")
        episode = entry.get("itunes_episode")
        if season is not None and episode is not None:
            filename = f"{season}x{episode}_{_id}"
        else:
            filename = f"{_id}"
        audio_filepath = f"{base_dir}/{filename}.mp3"
        
        if download_file(url=url, output_path=audio_filepath):        
            audio = {
                "id": _id,
                "pub_date": time.strftime("%Y-%m-%d",pub_date),
                "title": title,
                "duration": duration,
                "audio_filepath": audio_filepath,
                "url": url
            }        
            new_audio_list.append(audio)

    print(f"\n==== End Processing {source}/{name} ====")

    return new_audio_list

def print_summary(feed_rss: List[Feed], title: str):
    print(f"- {title}:")
    for feed in feed_rss:
        audio_list = feed['audio_list']
        n_files = len(audio_list)
        duration_list = [audio["duration"] for audio in audio_list]
        seconds = 0
        for d in duration_list:
            parts = d.split(":")
            t = [int(p) for p in parts]
            s = t[-1]
            m = t[-2] if len(t) > 1 else 0
            h = t[-3] if len(t) > 2 else 0
            seconds += h * 3600 + m * 60 + s
        hours = seconds / 3600
        print(f"    · {feed['source']}/{feed['name']}: {round(hours,2)} hours | {n_files} programs")
    
def main(args):
    feed_rss_file = args.feed_rss_file
    output_dir = args.output_dir
    only_stats = args.only_stats
    
    feed_rss = read_feeds(feed_rss_file)

    if not only_stats:
        new_feed_rss = []
        for feed in feed_rss:
            new_audio_list = process_feed(feed_info=feed, output_dir=output_dir)
            new_feed = dict(feed)
            new_feed['audio_list'] = new_audio_list
            new_feed_rss.append(new_feed)
            
            audio_list = feed.get("audio_list", [])
            feed["audio_list"] = new_audio_list + audio_list

        write_feeds(filepath=feed_rss_file, feed_rss=feed_rss)
        print("\n:::::: SUMMARY ::::::")
        print_summary(feed_rss=new_feed_rss, title="New Data")    

    print_summary(feed_rss=feed_rss, title="Total Data")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--feed_rss_file", help="(str): path to the JSON file wih the RSS urls.", required=True, type=str)
    parser.add_argument("--output_dir", help="(str): path to the output directory for the audio files.", required=True, type=str)
    parser.add_argument("--only_stats", help="(bool): show only stats", required=False, type=bool, default=False)
    args = parser.parse_args()
    main(args)

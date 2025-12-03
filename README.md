# iVoox Podcast Downloader

This project provides a command-line tool to download podcast audio
files from iVoox RSS feeds, track downloaded episodes, and generate
listening statistics.

The main script is:

    podcast/download_ivoox_podcast.py

It reads a list of podcast RSS feeds, downloads new audio files, updates
a JSONL file that tracks downloaded episodes, and prints summary
statistics.

## Features

-   Download podcast audio files from iVoox RSS feeds.

-   Avoid re-downloading episodes using a persistent JSONL database.

-   Extract episode metadata: id, title, date, duration, audio URL,
    season/episode.

-   Automatically name audio files based on episode metadata.

-   Store audio files in a clean directory structure:

        <output_dir>/<source>/<name>/<episode>.mp3

-   Generate summary statistics such as total listening time and number
    of downloaded episodes per feed.

## Feed File Format (feed_rss.json)

The feed file is a JSON Lines file: one feed per line.\
Each feed has the following structure:

``` json
{
  "source": "ivoox",
  "name": "my_podcast",
  "rss_url": "https://www.ivoox.com/example_rss.xml",
  "audio_list": [
    {
      "id": 123456,
      "pub_date": "2024-01-01",
      "title": "Episode title",
      "duration": "00:35:20",
      "audio_filepath": "path/to/file.mp3",
      "url": "https://example.mp3"
    }
  ]
}
```

`audio_list` is updated automatically after each run.

## Installation

Requirements:

    Python 3.9+

Install dependencies:

``` bash
pip install requests feedparser
```

## Usage

A helper script is provided to run the downloader automatically using a Conda environment and to generate timestamped log files.

``` bash
bash run_downloaded_ivoox_podcast.sh
```
This script performs the following steps:
1. Activates the Conda environment named scrap.
2. Loads configuration:
    - feed_rss.json as the feed list
    - audios/ as the output directory
    - ONLY_STATS=false to perform downloads

Generates a log file under logs/, for example:
```bash
logs/download_20240220_153210.log
```

## Output

The script prints summary tables showing new data and total accumulated
data.

Example:

    :::::: SUMMARY ::::::
    - New Data:
        · ivoox/my_podcast: 1.2 hours | 3 programs

    - Total Data:
        · ivoox/my_podcast: 52.6 hours | 142 programs

## How It Works

1.  Read feed list from `feed_rss.json`.
2.  Parse RSS feed using `feedparser`.
3.  Extract audio information from each entry.
4.  Skip episodes already downloaded.
5.  Download MP3 files using HTTP streaming.
6.  Store updated metadata in the feed file.
7.  Print summary statistics.

## Future Development

The `parliament/` module contains new tools under development, such as:

    parliament/download_audio.py

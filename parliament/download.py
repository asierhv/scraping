import os
import json
import requests
import argparse
from bs4 import BeautifulSoup
from bs4.element import Tag
from scraping_utils.utils import read_json, write_json

def download_xml(row: Tag, base_url: str, output_dir: str, xml_info_list):
    cells = row.find_all("td")
    if len(cells) < 2:
        raise ValueError("Skipping Malformed rows") # skip malformed rows
    
    # First <td> = legislature name
    name = cells[0].get_text(strip=True)
    if any(xml_info['name'] == name for xml_info in xml_info_list):
        raise ValueError(f"File already downloaded 'name': '{name}'")
    
    # Second <td> = contains <a> link
    a_tag = cells[1].find("a", href=True)
    if not a_tag:
        raise ValueError("'a_tag' not found")
    href = a_tag["href"]
    # Make relative URLs absolute
    if not href.startswith("http"):
        href = base_url + href

    filepath = f"{output_dir}/{href.split('=')[-1]}"
    
    # Download and write xml
    print(f"Downloading {href} ...")
    xml_response = requests.get(href)
    xml_response.raise_for_status()
    
    with open(filepath, "wb") as f:
        f.write(xml_response.content)
    
    # Create xml_info dictionary for update
    xml_info = {
        'name': name,
        'xml_filepath': filepath,
        'xml_url': href
    }
    return xml_info

def download_session(xml_file: str, output_dir):
    pass

def print_xml_summary(xml_metadata_list, title: str):
    print(f"- {title}:")
    for xml_metadata in xml_metadata_list:
        name = xml_metadata['name']
        xml_info_list = xml_metadata['xml_info_list']
        n_files = len(xml_info_list)
        print(f"  - {name}: {n_files} files")

def print_audio_summary(xml_info_list, title: str):
    for xml_info in xml_info_list:
        name = xml_info['name']
        audio_list = xml_info['audio_list']
        n_files = len(audio_list)
        duration_list = [audio["duration"] for audio in audio_list]
        hours = duration_list #logic
        print(f"    · {name}: {hours} hours | {n_files} sessions")


def main(args):
    xml_metadata_file = args.xml_metadata_file
    xml_output_dir = args.xml_output_dir

    xml_metadata_list = read_json(filepath=xml_metadata_file)

    new_xml_metadata_list = []
    for xml_metadata in xml_metadata_list:
        html_url = xml_metadata.get("html_url")
        name = xml_metadata.get("name")
        xml_info_list = xml_metadata.get("xml_info_list",[])
        
        output_dir = f"{xml_output_dir}/{name}"
        os.makedirs(output_dir, exist_ok=True)

        # Get page content
        response = requests.get(url=html_url)
        response.raise_for_status()  # Raise error if request fails
        soup = BeautifulSoup(response.content, "html.parser")

        base_url = f"https://{html_url.split('/')[2]}"
        new_xml_info_list = []
        for row in soup.find_all("tr"):
            try:
                xml_info = download_xml(row=row, base_url=base_url, output_dir=output_dir, xml_info_list=xml_info_list)
                new_xml_info_list.append(xml_info)
            except ValueError as e:
                print(f"Caught exception: {e}")

        new_xml_metadata = dict(xml_metadata)
        new_xml_metadata["xml_info_list"] = new_xml_info_list       
        new_xml_metadata_list.append(new_xml_metadata)

        xml_metadata["xml_info_list"] = new_xml_info_list + xml_info_list

    write_json(filepath=xml_metadata_file, data=xml_metadata_list)
    print("\n:::::: XML SUMMARY ::::::")
    print_xml_summary(xml_metadata_list=new_xml_metadata_list, title="New Data")
    print_xml_summary(xml_metadata_list=xml_metadata_list, title="Total Data")

if __name__=="__main__":
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--xml_metadata_file", help="(str): path to the JSON file with the HTML URLs.", required=True, type=str)
    parser.add_argument("--xml_output_dir", help="(str): path to the output directory for the xml files.", required=True, type=str)
    args = parser.parse_args()
    main(args)


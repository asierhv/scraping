"""
Extract video stream information from XML files.
This script parses the pleno XML files and extracts video URLs with start/end timestamps.
"""

import xml.etree.ElementTree as ET
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Optional
import re


class XMLVideoExtractor:
    """Extract video information from parliament XML files."""
    
    def __init__(self, xml_file_path: str):
        """Initialize the extractor with an XML file."""
        self.xml_file = xml_file_path
        self.videos = []
        self.session_info = {}
        
    def parse(self):
        """Parse the XML file and extract video information."""
        try:
            tree = ET.parse(self.xml_file)
            root = tree.getroot()
            
            # Extract session-level information
            self._extract_session_info(root)
            
            # Find all video links
            self._extract_video_links(root)
            
            return True
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return False
    
    def _extract_session_info(self, root):
        """Extract basic session information."""
        sesion = root.find('.//sesiones_pleno')
        if sesion is None:
            return
            
        self.session_info = {
            'legislatura': self._get_text(sesion, 'sesiones_pleno_legislatura'),
            'num_sesion': self._get_text(sesion, 'sesiones_pleno_num_sesion'),
            'fecha_inicio': self._get_text(sesion, 'sesiones_pleno_fecha_inicio'),
            'hora_inicio': self._get_text(sesion, 'sesiones_pleno_hora_inicio'),
            'tipo_sesion': self._get_text(sesion, 'sesiones_pleno_tipo_sesion'),
        }
    
    def _get_text(self, element, tag: str) -> Optional[str]:
        """Safely get text from an XML element."""
        elem = element.find(tag)
        if elem is not None and elem.text:
            return elem.text.strip()
        return None
    
    def _extract_video_links(self, root):
        """Extract all video links from the XML."""
        # Find all elements that contain video links
        for element in root.iter():
            if element.text and isinstance(element.text, str):
                text = element.text.strip()
                if 'legebiltzarra.eus' in text and 'videos' in text:
                    video_info = self._parse_video_url(text)
                    if video_info:
                        # Get context information
                        video_info['description'] = self._get_description(element)
                        self.videos.append(video_info)
    
    def _parse_video_url(self, url: str) -> Optional[Dict]:
        """Parse video URL and extract stream parameters."""
        if 'streamlegealdia' not in url and 'streamdbstart' not in url:
            return None
        
        # Parse URL query parameters
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Extract parameters (they come as lists in parse_qs)
        get_param = lambda key: params.get(key, [None])[0]
        
        video_info = {
            'url': url,
            'stream_legealdia': get_param('streamlegealdia'),
            'stream_organoa': get_param('streamorganoa'),
            'stream_data': get_param('streamdata'),
            'stream_name': get_param('streamname'),
            'start_time': get_param('streamdbstart'),
            'end_time': get_param('streamdbend'),
        }
        
        # Only include if we have timestamps
        if video_info['start_time'] or video_info['end_time']:
            return video_info
        
        return None
    
    def _get_description(self, element) -> Optional[str]:
        """Get description from parent elements."""
        # Try to find description in sibling elements
        parent = element
        for _ in range(5):  # Check up to 5 levels up
            parent = parent.find('..')
            if parent is None:
                break
            
            desc_elem = parent.find('.//sesiones_pleno_asunto_indice_descripcion')
            if desc_elem is not None and desc_elem.text:
                return desc_elem.text.strip()
        
        return None
    
    def get_videos(self) -> List[Dict]:
        """Return extracted video information."""
        return self.videos
    
    def get_session_info(self) -> Dict:
        """Return extracted session information."""
        return self.session_info
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'session_info': self.session_info,
            'videos': self.videos,
            'total_videos': len(self.videos)
        }
    
    def print_summary(self):
        """Print a summary of extracted videos."""
        print(f"\n{'='*70}")
        print(f"File: {self.xml_file}")
        print(f"{'='*70}")
        print(f"Session: Legislature {self.session_info.get('legislatura')} - "
              f"Session {self.session_info.get('num_sesion')}")
        print(f"Date: {self.session_info.get('fecha_inicio')} - "
              f"Time: {self.session_info.get('hora_inicio')}")
        print(f"Total videos found: {len(self.videos)}\n")
        
        for i, video in enumerate(self.videos, 1):
            print(f"Video {i}:")
            print(f"  Description: {video.get('description', 'N/A')}")
            print(f"  Start time: {video.get('start_time', 'N/A')}")
            print(f"  End time:   {video.get('end_time', 'N/A')}")
            print(f"  Stream data: {video.get('stream_data')}")
            print()


def extract_all_videos(directory: str, pattern: str = "*.xml") -> List[Dict]:
    """Extract videos from all XML files in a directory."""
    all_videos = []
    
    xml_files = Path(directory).glob(pattern)
    
    for xml_file in sorted(xml_files):
        extractor = XMLVideoExtractor(str(xml_file))
        if extractor.parse():
            all_videos.append({
                'file': str(xml_file),
                'data': extractor.to_dict()
            })
    
    return all_videos


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        xml_file = sys.argv[1]
        extractor = XMLVideoExtractor(xml_file)
        
        if extractor.parse():
            extractor.print_summary()
            
            # Optional: save to JSON
            if len(sys.argv) > 2 and sys.argv[2] == '--save':
                output_file = xml_file.replace('.xml', '_videos.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(extractor.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"\nSaved to: {output_file}")
        else:
            print("Failed to parse XML file")
    else:
        # Default: extract from experiments directory
        xml_dir = "experiments/xml_files"
        print(f"Extracting videos from: {xml_dir}")
        
        all_data = extract_all_videos(xml_dir)
        
        for item in all_data:
            data = item['data']
            print(f"\n📁 File: {Path(item['file']).name}")
            print(f"   Sessions: L{data['session_info'].get('legislatura')} - "
                  f"S{data['session_info'].get('num_sesion')}")
            print(f"   Videos: {data['total_videos']}")
            
            # Show first 2 videos as example
            for i, video in enumerate(data['videos'][:2], 1):
                print(f"   └─ Video {i}: {video.get('start_time')} → {video.get('end_time')}")

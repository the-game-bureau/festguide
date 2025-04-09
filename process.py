import xml.etree.ElementTree as ET
from xml.dom import minidom
import urllib.parse
import os
import shutil

def load_song_lookup(lookup_path):
    """Loads artist-to-song mapping from mostpopular.xml"""
    tree = ET.parse(lookup_path)
    root = tree.getroot()
    lookup = {}
    for entry in root.findall("performance"):
        name_elem = entry.find("name")
        song_elem = entry.find("most_popular_song")
        if name_elem is not None and song_elem is not None:
            lookup[name_elem.text.strip()] = song_elem.text.strip()
    return lookup

def enhance_with_popular_songs(data_path="data.xml", lookup_path="mostpopular.xml", output_path="dataprocessed.xml"):
    if not os.path.exists(data_path):
        print(f"❌ Source file {data_path} not found.")
        return

    # Copy original data.xml to dataprocessed.xml
    shutil.copyfile(data_path, output_path)

    # Parse the copied XML
    tree = ET.parse(output_path)
    root = tree.getroot()
    song_lookup = load_song_lookup(lookup_path)

    for performance in root.findall("performance"):
        def get_or_create(tag):
            elem = performance.find(tag)
            if elem is None:
                elem = ET.SubElement(performance, tag)
            return elem

        name_elem = performance.find("name")
        song_elem = get_or_create("most_popular_song")

        spotify_elem = get_or_create("spotify_url")
        apple_elem = get_or_create("apple_music_url")
        youtube_elem = get_or_create("youtube_music_url")
        chatgpt_elem = get_or_create("chatgpt_url")

        bandcamp_elem = get_or_create("bandcamp_url")
        pandora_elem = get_or_create("pandora_url")
        amazon_elem = get_or_create("amazon_music_url")
        soundcloud_elem = get_or_create("soundcloud_url")

        if name_elem is None:
            continue

        artist = name_elem.text.strip()
        song = song_lookup.get(artist, "unknown")
        song_elem.text = song

        # Search query logic
        query = f"{artist} by {song}" if song.lower() != "unknown" else artist
        encoded_query = urllib.parse.quote(query)

        # Update URLs
        spotify_elem.text = f"https://open.spotify.com/search/{encoded_query}"
        apple_elem.text = f"https://music.apple.com/us/search?term={encoded_query}"
        youtube_elem.text = f"https://music.youtube.com/search?q={encoded_query}"
        bandcamp_elem.text = f"https://bandcamp.com/search?q={encoded_query}"
        pandora_elem.text = f"https://www.pandora.com/search/{encoded_query}/all"
        amazon_elem.text = f"https://music.amazon.com/search/{encoded_query}"
        soundcloud_elem.text = f"https://soundcloud.com/search?q={encoded_query}"

        # ChatGPT query
        prompt = f"Tell me about the musician {artist} and any ties they have to New Orleans Also give me a link to their most popular songs"
        chatgpt_elem.text = f"https://chat.openai.com/?q={urllib.parse.quote(prompt)}"

    # Format XML
    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"✅ {output_path} has been generated and enhanced successfully.")

if __name__ == "__main__":
    enhance_with_popular_songs()

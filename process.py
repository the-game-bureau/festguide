
import xml.etree.ElementTree as ET
from xml.dom import minidom
import urllib.parse
import os
import shutil
import html
import unicodedata

def normalize_name(name):
    if not name:
        return ""
    name = html.unescape(name)
    name = unicodedata.normalize("NFKD", name)
    name = name.replace("’", "'").replace("‘", "'")
    name = name.replace("“", '"').replace("”", '"')
    name = ''.join(c for c in name if c.isalnum() or c.isspace())  # strip punctuation
    return name.strip().lower()

def load_song_lookup(lookup_path):
    tree = ET.parse(lookup_path)
    root = tree.getroot()
    lookup = {}
    for entry in root.findall(".//performance"):
        name_elem = entry.find("name")
        song_elem = entry.find("most_popular_song")
        if name_elem is not None and song_elem is not None:
            artist_name = normalize_name(name_elem.text)
            lookup[artist_name] = song_elem.text.strip()
    print(f"🎵 Loaded {len(lookup)} normalized entries from {lookup_path}")
    return lookup

def enhance_with_popular_songs(data_path="data.xml", lookup_path="mostpopular.xml", output_path="dataprocessed.xml"):
    if not os.path.exists(data_path):
        print(f"❌ Source file {data_path} not found.")
        return

    shutil.copyfile(data_path, output_path)

    tree = ET.parse(output_path)
    root = tree.getroot()
    song_lookup = load_song_lookup(lookup_path)

    for performance in root.findall(".//performance"):
        def get_or_create(tag):
            elem = performance.find(tag)
            if elem is None:
                elem = ET.SubElement(performance, tag)
            return elem

        name_elem = performance.find("name")
        if name_elem is None:
            continue

        artist = name_elem.text.strip()
        normalized_artist = normalize_name(artist)

        song_elem = get_or_create("most_popular_song")
        song = song_lookup.get(normalized_artist, "unknown")
        song_elem.text = song

        print(f"🔍 {artist} → {normalized_artist} → {song}")

        if song.lower() == "unknown":
            query = artist
        else:
            query = f"{song} {artist}"

        encoded_query = urllib.parse.quote(query)

        get_or_create("spotify_url").text = f"https://open.spotify.com/search/{encoded_query}"
        get_or_create("apple_music_url").text = f"https://music.apple.com/us/search?term={encoded_query}"
        get_or_create("youtube_music_url").text = f"https://music.youtube.com/search?q={encoded_query}"
        get_or_create("bandcamp_url").text = f"https://bandcamp.com/search?q={encoded_query}"
        get_or_create("pandora_url").text = f"https://www.pandora.com/search/{encoded_query}/all"
        get_or_create("amazon_music_url").text = f"https://music.amazon.com/search/{encoded_query}"
        get_or_create("soundcloud_url").text = f"https://soundcloud.com/search?q={encoded_query}"

        prompt = f"Tell me about the musician {artist} and any ties they have to New Orleans. Also give links to their most popular songs"
        get_or_create("chatgpt_url").text = f"https://chat.openai.com/?q={urllib.parse.quote(prompt)}"

    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"✅ {output_path} has been generated and enhanced successfully.")

if __name__ == "__main__":
    enhance_with_popular_songs()

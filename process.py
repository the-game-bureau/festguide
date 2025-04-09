import xml.etree.ElementTree as ET
from xml.dom import minidom
import urllib.parse

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

def enhance_with_popular_songs(input_path="dataprocessed.xml", lookup_path="mostpopular.xml"):
    # Load the original XML and the lookup table
    tree = ET.parse(input_path)
    root = tree.getroot()
    song_lookup = load_song_lookup(lookup_path)

    # Update each performance
    for performance in root.findall("performance"):
        name_elem = performance.find("name")
        song_elem = performance.find("most_popular_song")
        spotify_elem = performance.find("spotify_url")
        apple_elem = performance.find("apple_music_url")
        youtube_elem = performance.find("youtube_music_url")
        chatgpt_elem = performance.find("chatgpt_url")

        if name_elem is None or song_elem is None:
            continue

        artist = name_elem.text.strip()
        if artist in song_lookup:
            song = song_lookup[artist]
            song_elem.text = song

            # Check if it's not unknown
            if song.lower() != "unknown":
                encoded_query = urllib.parse.quote(f"{song} by {artist}")
                
                if spotify_elem is not None:
                    spotify_elem.text = f"https://open.spotify.com/search/{encoded_query}"
                if apple_elem is not None:
                    apple_elem.text = f"https://music.apple.com/us/search?term={encoded_query}"
                if youtube_elem is not None:
                    youtube_elem.text = f"https://music.youtube.com/search?q={encoded_query}"
                if chatgpt_elem is not None:
                    prompt = f"Tell me about the musician {artist} and any ties they have to New Orleans Also give me a link to their most popular songs"
                    chatgpt_elem.text = f"https://chat.openai.com/?q={urllib.parse.quote(prompt)}"

    # Pretty format the new XML
    xml_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

    # Overwrite the original input file
    with open(input_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"✅ dataprocessed.xml has been updated with song-enhanced streaming links.")

if __name__ == "__main__":
    enhance_with_popular_songs()

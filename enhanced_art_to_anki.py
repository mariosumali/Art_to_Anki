#!/usr/bin/env python3
"""
Enhanced Art to Anki Deck Generator using genanki

This script creates actual Anki deck files (.apkg) with images embedded directly.
"""

import os
import re
import random
import genanki
from pathlib import Path

def parse_filename(filename):
    """
    Parse filename to extract artist and artwork names.
    Same logic as before but optimized for genanki.
    """
    # Remove file extension
    name = os.path.splitext(filename)[0]
    
    # Remove the trailing --S pattern
    name = re.sub(r'--S$', '', name)
    name = re.sub(r'-S$', '', name)
    
    # Handle different separator patterns
    parts = name.split('-')
    if len(parts) < 2:
        parts = name.split('_')
    
    if len(parts) < 2:
        return None, None
    
    # Common artwork title indicators
    artwork_indicators = [
        'the', 'a', 'an', 'portrait', 'self', 'untitled', 'study', 'landscape',
        'still', 'life', 'scene', 'view', 'garden', 'bridge', 'river', 'mountain',
        'woman', 'man', 'child', 'family', 'christ', 'madonna', 'saint', 'angel',
        'battle', 'war', 'peace', 'death', 'birth', 'creation', 'fall', 'rise',
        'morning', 'evening', 'night', 'day', 'sunset', 'sunrise', 'winter', 'summer',
        'spring', 'autumn', 'fall', 'snow', 'rain', 'storm', 'calm', 'wild'
    ]
    
    # Special handling for known compound artist names
    compound_artists = {
        'Albert-Charles-Lebourg': 3,
        'Albert-Marie-Lebourg': 3,
        'Diego-Rodriguez-De-Silva-Y-Velazquez': 5,
        'Diego-Velazquez': 2,
        'Michelangelo-Merisi': 2,
        'Caravaggio-Michelangelo-Merisi': 3
    }
    
    # Check if this matches a known compound artist
    for compound_name, length in compound_artists.items():
        if '-'.join(parts[:length]) == compound_name:
            artist_parts = parts[:length]
            artwork_parts = parts[length:]
            
            if artwork_parts:
                artist = ' '.join(artist_parts)
                artwork = ' '.join(artwork_parts)
                artist = artist.replace('_', ' ').strip()
                artwork = artwork.replace('_', ' ').strip()
                artist = re.sub(r'\s+', ' ', artist)
                artwork = re.sub(r'\s+', ' ', artwork)
                return artist, artwork
    
    # Try different artist name lengths
    for artist_length in [2, 3, 1]:
        if artist_length <= len(parts):
            artist_parts = parts[:artist_length]
            artwork_parts = parts[artist_length:]
            
            if artwork_parts:
                first_artwork_part = artwork_parts[0].lower()
                
                if (first_artwork_part in artwork_indicators or 
                    len(artwork_parts) > 1 or
                    artist_length == 2):
                    
                    artist = ' '.join(artist_parts)
                    artwork = ' '.join(artwork_parts)
                    artist = artist.replace('_', ' ').strip()
                    artwork = artwork.replace('_', ' ').strip()
                    artist = re.sub(r'\s+', ' ', artist)
                    artwork = re.sub(r'\s+', ' ', artwork)
                    return artist, artwork
    
    # Fallback
    if len(parts) >= 3:
        artist = ' '.join(parts[:2])
        artwork = ' '.join(parts[2:])
        artist = artist.replace('_', ' ').strip()
        artwork = artwork.replace('_', ' ').strip()
        artist = re.sub(r'\s+', ' ', artist)
        artwork = re.sub(r'\s+', ' ', artwork)
        return artist, artwork
    
    return None, None

def create_art_model():
    """Create the Anki model for art flashcards."""
    # Generate a unique model ID
    model_id = random.randrange(1 << 30, 1 << 31)
    
    model = genanki.Model(
        model_id,
        'Art History Model',
        fields=[
            {'name': 'Image'},
            {'name': 'Artist'},
            {'name': 'Artwork'},
        ],
        templates=[
            {
                'name': 'Art Recognition',
                'qfmt': '{{Image}}',
                'afmt': '{{FrontSide}}<hr id="answer"><div style="text-align: center; font-size: 18px;"><strong>{{Artist}}</strong><br><em>{{Artwork}}</em></div>',
            },
        ],
        css='''
        .card {
            font-family: Arial, sans-serif;
            text-align: center;
        }
        img {
            max-width: 100%;
            max-height: 400px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        '''
    )
    
    return model

def generate_anki_deck(art_folder, output_file):
    """Generate Anki deck with embedded images."""
    
    # Create the model
    model = create_art_model()
    
    # Create the deck
    deck_id = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id, 'Art History Collection')
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    image_files = []
    media_files = []
    
    for file in os.listdir(art_folder):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(file)
            media_files.append(os.path.join(art_folder, file))
    
    print(f"Found {len(image_files)} image files")
    
    # Parse each filename and create notes
    parsed_count = 0
    failed_count = 0
    
    for filename in image_files:
        artist, artwork = parse_filename(filename)
        
        if artist and artwork:
            # Create note with image reference
            note = genanki.Note(
                model=model,
                fields=[
                    f'<img src="{filename}">',  # Image field
                    artist,                     # Artist field
                    artwork                     # Artwork field
                ],
                tags=[f'art_{artist.replace(" ", "_").lower()}', 'art_history']
            )
            
            deck.add_note(note)
            parsed_count += 1
        else:
            print(f"Failed to parse: {filename}")
            failed_count += 1
    
    print(f"Successfully parsed: {parsed_count}")
    print(f"Failed to parse: {failed_count}")
    
    # Create package with media files
    package = genanki.Package(deck)
    package.media_files = media_files
    
    # Write to file
    package.write_to_file(output_file)
    print(f"Anki deck saved as: {output_file}")
    
    return parsed_count, failed_count

def main():
    """Main function."""
    art_folder = "/Users/mariosumali/Documents/GitHub/Art_to_Anki/ART"
    output_file = "/Users/mariosumali/Documents/GitHub/Art_to_Anki/art_history_deck.apkg"
    
    print("Generating Anki deck with genanki...")
    print("This will create a complete .apkg file with embedded images.")
    
    try:
        parsed_count, failed_count = generate_anki_deck(art_folder, output_file)
        
        print(f"\n✅ Deck generation completed!")
        print(f"📊 Successfully created: {parsed_count} flashcards")
        print(f"❌ Failed to parse: {failed_count} images")
        print(f"📁 Deck saved as: {output_file}")
        print(f"\n📖 How to import:")
        print(f"1. Open Anki")
        print(f"2. Go to File > Import")
        print(f"3. Select: {output_file}")
        print(f"4. Click Import")
        print(f"\n🎨 The deck will be called 'Art History Collection'")
        
    except Exception as e:
        print(f"❌ Error generating deck: {e}")
        print("Make sure you have genanki installed: pip install genanki")

if __name__ == "__main__":
    main()

#!/usr/bin/env python

"""Uses Google Text to Speech to Generate AudioBooks from Text

Example usage:
    python text_to_audio.py --gender MALE -o output.mp3 textfile.txt
"""

import os
import sys
import argparse
from glob import glob
from textwrap import wrap

from google.cloud import texttospeech
from pydub import AudioSegment

# Google Speen Synthesize limit per request
# See https://cloud.google.com/text-to-speech/quotas
CHUNK_SIZE = 5000


def synthesize_text_file(text, gender, output):
    """Synthesizes speech from the input file of text."""
    client = texttospeech.TextToSpeechClient()

    print("Synthesizing...")
    input_text = texttospeech.types.SynthesisInput(text=text)
    
    gender_dict = {'MALE': texttospeech.enums.SsmlVoiceGender.MALE,
                   'FEMALE': texttospeech.enums.SsmlVoiceGender.FEMALE,
                   'NEUTRAL': texttospeech.enums.SsmlVoiceGender.NEUTRAL}
    ssml_gender = gender_dict[gender]

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=ssml_gender)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.
    with open(output, 'wb') as out:
        out.write(response.audio_content)
        print('Audio content written to file "{:s}"'.format(output))


def main(args):
    # read input text file
    with open(args.textfile, 'r', encoding='utf-8') as f:
        text = f.read()
        if args.length != 0:
            text = text[:args.length]
    
    # create temporary directory
    if not os.path.exists('.tmp'):
        os.makedirs('.tmp')

    # split and synthesize the audio
    for i, line in enumerate(wrap(text, CHUNK_SIZE)):
        ofn = '{:03d}_{:s}'.format(i, args.output)
        opath = os.path.join('.tmp', ofn)
        if os.path.exists(opath):
            print("Existing... skipped")
        else:
            synthesize_text_file(line, args.gender, opath)

    # join audio files
    silence = AudioSegment.silent(duration=200)
    playlist = None
    for fn in sorted(glob('.tmp/*_{:s}'.format(args.output))):
        print('Joining audio file: {:s}'.format(fn))
        if playlist is None:
            playlist = AudioSegment.from_mp3(fn)
        else:
            playlist += silence
            playlist += AudioSegment.from_mp3(fn)
        os.unlink(fn)
        playlist_length = int(len(playlist) / 1000)
        print('Current audio length: {:d} seconds'.format(playlist_length))

    # save the audio output file
    print('Saving the output file: {:s}'.format(args.output))
    playlist.export(args.output, format='mp3')

    os.removedirs('.tmp')
    print("Complete!!!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('textfile', default=None,
                        help='Input text file')
    parser.add_argument('-c', '--credentials', default=None,
                        help='Google Applicaiton Credentials file')
    parser.add_argument('-g', '--gender', default='NEUTRAL',
                        choices=['NEUTRAL', 'MALE', 'FEMALE'],
                        help='Gender of speech')
    parser.add_argument('-l', '--length', type=int, default=0,
                        help='Text length to be converted')
    parser.add_argument('-o', '--output', default='output.mp3',
                        help='Output audio filename (MP3)')

    args = parser.parse_args()

    if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        if args.credentials is None:
            print("ERROR: Please make sure have a Google credentials file.\n"
                  "See https://cloud.google.com/docs/authentication/getting-started")
            sys.exit(-1)
        else:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = args.credentials

    print(args)

    main(args)

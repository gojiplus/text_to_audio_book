## Text to Audio (Books)

Audio is great. You can listen to things when commuting, doing your household chores, on the beach---wherever you please. 

Some of the things you want to listen to are things where the text is not under copyright, for instance, everything published in the U.S. before 1923 is not copyrighted, or where you have bought the electronic text. And now that the speech synthesis is good enough, it doesn't make sense to buy an audio book of something that you can very cheaply create using the [Google Speech Synthesis API](https://cloud.google.com/text-to-speech/). 

This simple script lowers the bar for producing audio from text yet further by wrapping the process. It takes a text file (or a SSML file where available) as input along with a parameter for which voice you want to use and produces a mp3.

### Functionality

Google speech synthesis API breaks the document into 5k character chunks, automatically truncating at word boundaries and adding a 200ms lag between two 5k character chunks. We chunk by sentence, getting as many full sentences as possible within the 5k limit. For plays, e.g., [here](http://www.gutenberg.org/files/37431/37431-h/37431-h.htm) (Pride and Prejudice), we also take a separate character, gender file that lists the gender of each character, e.g., [here](character_gender_pap.csv) for Pride and Prejudice, so that we can switch between male and female voices.

### Prerequisites

`pydub` need either `ffmpeg` or `libav` to support MP3. Please look at [getting `ffmpeg` set up](https://github.com/jiaaro/pydub#getting-ffmpeg-set-up)

### Running the Script

```
pip install -r requirements.txt
python text_to_audio.py -o sample_audio.mp3 sample_text.txt
```

### Illustration

[Project Gutenberg](https://www.gutenberg.org/) provides text of books in various formats for which the copyright has lapsed. We illustrate the use of the script, we use it to get the mp3 for Jane Austen's [Pride and Prejudice](https://www.gutenberg.org/files/1342/1342-0.txt). (We don't use plain text as there are a lot of places where there is 'underscore' etc.)

CLI and GUI interfaces for using several of the most recent Automatic Speech Recognition models (Whisper, Faster-Whisper, Nemotron, Parakeet, Qwen3) written in python (with some use of transformers library).

> [!NOTE]  
> Parts of current python code had been AI-generated, then human-reviewed, tested, modified.
> - A short function from `transcript_cli.py` (hugely human-cleaned).
> - First draft of `transcript_gui.py` then highly human-modified and human-revamped.
> - Github actions `build.yml` and `transcript.spec` files were "co-written" by both human and AI.
> - `magic_install.cmd` is fully human-written.

 # Windows lazy easy install
 
 Go to the last release, download `magic_install.cmd`. Put this file in a specific directory and run it. The `.exe` files, `.txt` config files and `_internal` library directory will thus appear (and the cmd file will auto-delete itself).
 
 You won't have FFmpeg installed (unless you did install it earlier by some other ways). Remind it.

 # Windows easy not lazy install
 
Python 3.14 highly recommended for latest `transformers` library use.

FFmpeg 9 isn't supported by all ASR models so need to fallback to 8.1; shared libraries are needed to be found by some models (plus some lines of code in `transcript_cli.py` looking for them).

Faster-Whisper only supports cuda 12.6 at the moment.

```cmd
winget install -e --id Python.Python.3.14
winget install -e --id BtbN.FFmpeg.LGPL.Shared.8.1
pip install --upgrade pip
pip install torch torchcodec --index-url https://download.pytorch.org/whl/cu126
pip install transformers accelerate librosa content-types nagisa soynlp openai-whisper faster-whisper
```

Now you can clone/download this repo and execute python files.

# Linux install

```bash
apt install python3-venv libpython3.13 # tested on Debian trixie
apt install --no-install-recommends ffmpeg

python3 -m venv asr_stuff
source asr_stuff/bin/activate
pip install torch torchcodec --index-url https://download.pytorch.org/whl/cu126
pip install transformers accelerate librosa content-types nagisa soynlp openai-whisper faster-whisper
```

Don't forget to activate your python-venv before using scripts.

# How-to use script or UI

## Script

```bash
python3 transcript_cli.py <model_name> --<model>-params="tiny" -i <input_file_1> -i <input_file_2> \
--online --cpu --srt --whisper-translate --int8 --beam-size \
--warnings --no-ffmpeg --vocabulary --prompt="<your prompt>"
```

See `python3 transcript_cli.py -h` for more details about params and languages for each model.

If transcription works, it will output a txt file with the same name as input file, in the same directory.

`--online` allows connections to HuggingFace for downloading model if you never used it before. Only Whisper directly downloads from its own sources (not Faster-Whipser nor Whisper-Afr as they are from HuggingFace).

`--cpu` will let model run on CPU only.

`--srt` will also transcript to srt file.

`--whisper-translate` will translate transcription into english.

`--int8` will enable int8 quantization (Faster-Whisper and Whisper-Afr only).

`--beam-size` will set how many alternative words model can try (integer from 1 to 10; Whisper, Faster-Whisper, Whisper-Afr and Qwen3 only). 

`--warnings` will allow more verbosity (transcription unchanged!).

`--no-ffmpeg` will use librosa to decode audio (wav, mp3, ogg, flac files are only guaranteed to work). 

`--vocabulary` will add content of file `vocabulary.txt` (one line per word) to prompt as technical words or names specific to your transcription (Whisper, Faster-Whisper, Whisper-Afr and Qwen3 only).

`--prompt` allows you to add a prompt to help model for transcripting (Whisper, Faster-Whisper, Whisper-Afr and Qwen3 only; only around 150 words for Whipser-like models, only the last ~150 words if too many given).

`-i` before file to input (`all` and `*` allowed).

## UI

See cli options for explanations.

<img width="902" height="940" alt="image" src="https://github.com/user-attachments/assets/46bdea0d-bbce-45dd-8820-bc5492bac3ff" />

## Special use case of Whisper-Afr

This model requires connection to HuggingFace, being logged in, so you have to ask for access to this model (https://huggingface.co/Sunbird/faster-whisper-51-african-languages) then fill an access token in the file `token.txt` to be able to use it.

# Sources, References and Resources

### Whisper ASR and some useful use cases.
- https://github.com/openai/whisper
- https://pypi.org/project/whisper-openai/
- https://www.saytowords.com/blogs/Whisper-Python-Example

### Faster-Whisper
- https://pypi.org/project/faster-whisper/

### Distil-Whisper (EN only)
- https://huggingface.co/distil-whisper/distil-large-v3
- https://huggingface.co/distil-whisper/distil-large-v3.5

### Faster-Whisper implementation for african languages and dialects (available in my scripts)
- https://huggingface.co/Sunbird/faster-whisper-51-african-languages

### Other Whisper-like implementations for african languages and dialects that did not work as great as `faster-whisper-51-african-languages` (so not available in my scripts)
- https://www.dsfsi.co.za/za-african-next-voices/
- https://huggingface.co/dsfsi-anv/models
- https://huggingface.co/dsfsi-anv/za-anv-multilingual-whisper-v3-turbo
- https://huggingface.co/TheirStory/whisper-medium-zulu
- https://huggingface.co/TheirStory/whisper-small-xhosa
- https://huggingface.co/zionia/whisper-small-isizulu-0.9x
- https://huggingface.co/Sunbird/asr-whisper-51-african-languages

### Using prompts with Whisper/Faster-Whisper (thus my implementation choices)
- https://github.com/openai/whisper/discussions/1080
- https://github.com/openai/whisper/discussions/117#discussioncomment-3727051
- https://github.com/openai/whisper/blob/main/whisper/transcribe.py

### Nemotron ASR
- https://huggingface.co/nvidia/nemotron-speech-streaming-en-0.6b
- https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b

### Parakeet ASR
- https://github.com/achetronic/parakeet
- https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3

### Qwen3 ASR
- https://huggingface.co/Qwen/Qwen3-ASR-0.6B-hf
- https://huggingface.co/Qwen/Qwen3-ASR-1.7B-hf
- https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B-hf

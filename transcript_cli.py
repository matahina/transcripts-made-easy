import argparse, os, warnings, gc

import glob
import click
import torch
import traceback
from pathlib import Path
import mimetypes

   
try:
    winget_base = os.path.expandvars(r"%LocalAppData%\Microsoft\WinGet\Packages")
    search_pattern = os.path.join(winget_base, "*FFmpeg*Shared*", "**", "bin")
    matching_paths = glob.glob(search_pattern, recursive=True)
    os.add_dll_directory(matching_paths[0])
except:
    pass

def elem_to_item(elem, afr=False, nv=False, qw=False):
    if type(elem) != dict:
        import dataclasses
        elem = dataclasses.asdict(elem)

    start="start"
    end="end"
    text="text"
    if afr:
        text="word"
    elif nv:
        text="token"
    elif qw:
        start = start+"_time"
        end = end+"_time"

    try:
        item = {'start': elem[start], 'end': elem[end], 'text': elem[text]}
    except:
        item = {'start': elem[start], 'text': elem[text]}
    return item

def get_vocab():
    with open('vocabulary.txt') as f:
        lines = [line.rstrip('\n') for line in f]
    return ", ".join(lines)

def transcribe_to_srt(the_output, path, afr=False, nv=False, qw=False):
    srt_content = ""
    the_sentences = []
    the_starts = []
    the_ends = []
    current_one = []

    new_one = True

    joinbit = "" if not qw else " "
    if afr or nv or qw:

        for i in range(0,len(the_output)):
            the_item=(elem_to_item(the_output[i],afr,nv,qw))
            try:
                the_next_item=(elem_to_item(the_output[i+1],afr,nv,qw))
                next_bit = the_next_item["text"][0]
            except:
                next_bit = ""
            if new_one:
                the_starts.append(the_item['start'])
                current_one = []
                new_one=False
                llast = the_item['end']
                very_first = False
            current_one.append(the_item['text'])
            if (((the_item['end'] - the_item['start']) > 0.5) or (the_item['start'] - llast > 0)) and not(nv and next_bit != " "):
                the_ends.append(the_item['end'])
                the_sentences.append(joinbit.join(current_one))
                new_one=True
            llast = the_item['end']

        if len(the_starts)>len(the_ends):
            the_ends.append(llast)
            the_sentences.append(joinbit.join(current_one))

    else:
        for elem in the_output:
            the_item=(elem_to_item(elem,afr,nv,qw))
            the_starts.append(the_item['start'])
            the_sentences.append(the_item['text'])
            the_ends.append(the_item['end'])

    for i in range(0,len(the_sentences)):
        start_time = format_timestamp(the_starts[i])
        end_time = format_timestamp(the_ends[i])
        text = the_sentences[i].strip()

        srt_content += f"{i}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{text}\n\n"

    with open(path+".srt", "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"SRT file saved: {path}.srt")


def transcribe_to_txt(txt_content, path, afr=False, nv=False, qw=False):
    with open(path+".txt", "w", encoding="utf-8") as f:
        f.write(txt_content)

    print(f"TXT file saved: {path}.txt")


def filenameonly(filenamefull):
    vari_p = filenamefull.split('.')
    res = ['.'.join(vari_p[:-1]), vari_p[-1]]
    return res[0]


def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def prompt_into_input(the_input, the_prompt, the_processor, the_model):
    '''This function has been written thanks to AI-generated code, then reviewed and cleaned up by me (a human!)'''
    prompt_tokens = the_processor.tokenizer.encode(the_prompt, add_special_tokens=False)
    prompt_tensor = torch.tensor(prompt_tokens,
                                # dtype=torch.long,
                                device=the_model.device)

    the_input["input_ids"] = torch.cat([prompt_tensor, the_input["input_ids"].squeeze(0)]).unsqueeze(0)

    if "attention_mask" in the_input:
        ones = torch.ones(len(prompt_tokens),
                          # dtype=torch.long,
                          device=the_model.device)
        the_input["attention_mask"] = torch.cat([ones, the_input["attention_mask"].squeeze(0)]).unsqueeze(0)

    return the_input

def check_files(file_list, no_ffmpeg, cli):
    da_effective_list = da_list if not no_ffmpeg else da_list_no_ffmpeg
    clean_list = []
    for filito in file_list:
        if cli and (any(char_key in filito for char_key in ["all","*"])):
            if filito == "all":
                path = "*"
            elif filito[-4:] == f"{'/' or '\\'}all":
                path = filito[:-3]+"*"
            else:
                path= filito.replace(f"{'/' or '\\'}all.",f"{'/' or '\\'}*.")
            globery = glob.glob(path)

            for filitito in globery:
                if Path(filitito).suffix in da_effective_list:
                    clean_list.append(filitito)
        else:
            if Path(filito).suffix in da_effective_list:
                clean_list.append(filito)

    return clean_list


mimetypes.init()
all_types = {**mimetypes.types_map, **mimetypes.common_types}

media_map = {}
for ext, mime in all_types.items():
    if mime.startswith(('audio/', 'video/')):
        media_map.setdefault(mime, []).append(ext)

da_list = []
for mime, exts in sorted(media_map.items()):
    da_list = da_list + exts

da_list_no_ffmpeg = [".wav", ".flag", ".ogg", ".mp3"]

the_languages = {}
the_helps = {}

the_languages["whisper"] = ["af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu", "ha", "haw", "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jw", "ka", "kk", "km", "kn", "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt", "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt", "ro", "ru", "sa", "sd", "si", "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl", "tr", "tt", "uk", "ur", "uz", "vi", "yi", "yo", "yue", "zh", "Afrikaans", "Albanian", "Amharic", "Arabic", "Armenian", "Assamese", "Azerbaijani", "Bashkir", "Basque", "Belarusian", "Bengali", "Bosnian", "Breton", "Bulgarian", "Burmese", "Cantonese", "Castilian", "Catalan", "Chinese", "Croatian", "Czech", "Danish", "Dutch", "English", "Estonian", "Faroese", "Finnish", "Flemish", "French", "Galician", "Georgian", "German", "Greek", "Gujarati", "Haitian", "Haitian Creole", "Hausa", "Hawaiian", "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Italian", "Japanese", "Javanese", "Kannada", "Kazakh", "Khmer", "Korean", "Lao", "Latin", "Latvian", "Letzeburgesch", "Lingala", "Lithuanian", "Luxembourgish", "Macedonian", "Malagasy", "Malay", "Malayalam", "Maltese", "Mandarin", "Maori", "Marathi", "Moldavian", "Moldovan", "Mongolian", "Myanmar", "Nepali", "Norwegian", "Nynorsk", "Occitan", "Panjabi", "Pashto", "Persian", "Polish", "Portuguese", "Punjabi", "Pushto", "Romanian", "Russian", "Sanskrit", "Serbian", "Shona", "Sindhi", "Sinhala", "Sinhalese", "Slovak", "Slovenian", "Somali", "Spanish", "Sundanese", "Swahili", "Swedish", "Tagalog", "Tajik", "Tamil", "Tatar", "Telugu", "Thai", "Tibetan", "Turkish", "Turkmen", "Ukrainian", "Urdu", "Uzbek", "Valencian", "Vietnamese", "Welsh", "Yiddish", "Yoruba"]

the_helps["whisper"] = ""

the_languages["whisper-afr"] = ["ach", "afr", "aka", "amh", "teo", "bam", "bem", "ber", "nya", "dga", "dag", "eng", "ewe", "fra", "ful", "hau", "ibo", "kpo", "kab", "kln", "kau", "kik", "kin", "rwm", "led", "lin", "lug", "lgg", "luy", "myx", "luo", "xog", "mlg", "nbl", "pcm", "orm", "cgg", "koo", "nyn", "ruc", "ttj", "sna", "som", "sot", "swa", "lth", "tsn", "wol", "xho", "yor", "zul"]

the_helps["whisper-afr"] = "Acholi (ach), Afrikaans (afr), Akan (aka), Amharic (amh), Ateso (teo), Bambara (bam), Bemba (bem), Berber (ber), Chichewa (nya), Dagaare (dga), Dagbani (dag), English (eng), Ewe (ewe), French (fra), Fulani (ful), Hausa (hau), Igbo (ibo), Ikposo (kpo), Kabyle (kab), Kalenjin (kln), Kanuri (kau), Kikuyu (kik), Kinyarwanda (kin), Kwamba (rwm), Lendu (led), Lingala (lin), Luganda (lug), Lugbara (lgg), Luhya (luy), Lumasaba (myx), Luo (luo), Lusoga (xog), Malagasy (mlg), Ndebele (nbl), Nigerian Pidgin (pcm), Oromo (orm), Rukiga (cgg), Rukonjo (koo), Runyankole (nyn), Ruruuli (ruc), Rutooro (ttj), Shona (sna), Somali (som), Sotho (sot), Swahili (swa), Thur (lth), Tswana (tsn), Wolof (wol), Xhosa (xho), Yoruba (yor), Zulu (zul)"

the_languages["nemotron"] = ['ar-AR', 'de-DE', 'en-GB', 'en-US', 'es-ES', 'es-US', 'fr-CA', 'fr-FR', 'hi-IN', 'it-IT', 'ja-JP', 'ko-KR', 'nl-NL', 'pt-BR', 'pt-PT', 'ru-RU', 'tr-TR', 'uk-UA', 'vi-VN',
    'bg-BG', 'cs-CZ', 'da-DK', 'et-EE', 'fi-FI', 'hr-HR', 'hu-HU', 'nb-NO', 'pl-PL', 'ro-RO', 'sk-SK', 'sv-SE', 'zh-CN',
    'el-GR', 'he-IL', 'lt-LT', 'lv-LV', 'mt-MT', 'nn-NO', 'sl-SI', 'th-TH',
    'ar', 'de', 'en', 'es', 'fr', 'hi', 'it', 'ja', 'ko', 'nl', 'pt', 'ru', 'tr', 'uk', 'vi',
    'bg', 'cs', 'da', 'et', 'fi', 'hr', 'hu', 'nb', 'pl', 'ro', 'sk', 'sv', 'zh',
    'el', 'he', 'lt', 'lv', 'mt', 'nn', 'sl', 'th']

the_helps["nemotron"] = '''- transcription-ready for English (en-US, en-GB), Spanish (es-US, es-ES), French (fr-FR, fr-CA), Italian (it-IT), Portuguese (pt-BR, pt-PT), Dutch (nl-NL), German (de-DE), Turkish (tr-TR), Russian (ru-RU), Arabic (ar-AR), Hindi (hi-IN), Japanese (ja-JP), Korean (ko-KR), Vietnamese (vi-VN), Ukrainian (uk-UA);
    - broad-coverage for Polish (pl-PL), Swedish (sv-SE), Czech (cs-CZ), Norwegian Bokmål (nb-NO), Danish (da-DK), Bulgarian (bg-BG), Finnish (fi-FI), Croatian (hr-HR), Slovak (sk-SK), Mandarin (zh-CN), Hungarian (hu-HU), Romanian (ro-RO), Estonian (et-EE);
    - fine-tuning needed but recognizable for Greek (el-GR), Lithuanian (lt-LT), Latvian (lv-LV), Maltese (mt-MT), Slovenian (sl-SI), Hebrew (he-IL), Thai (th-TH), Norwegian Nynorsk (nn-NO).'''

the_helps["parakeet"] = "it will autodetect among Bulgarian (bg), Croatian (hr), Czech (cs), Danish (da), Dutch (nl), English (en), Estonian (et), Finnish (fi), French (fr), German (de), Greek (el), Hungarian (hu), Italian (it), Latvian (lv), Lithuanian (lt), Maltese (mt), Polish (pl), Portuguese (pt), Romanian (ro), Slovak (sk), Slovenian (sl), Spanish (es), Swedish (sv), Russian (ru), Ukrainian (uk)."

the_languages["qwen3"] = ['Arabic', 'Cantonese', 'Chinese', 'Czech', 'Danish', 'Dutch', 'English', 'Filipino', 'Finnish', 'French', 'German', 'Greek', 'Hindi', 'Hungarian', 'Indonesian', 'Italian', 'Japanese', 'Korean', 'Macedonian', 'Malay', 'Persian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Spanish', 'Swedish', 'Thai', 'Turkish', 'Vietnamese', 'ar', 'cs', 'da', 'de', 'el', 'en', 'es', 'fa', 'fi', 'fil', 'fr', 'hi', 'hu', 'id', 'it', 'ja', 'ko', 'mk', 'ms', 'nl', 'pl', 'pt', 'ro,', 'ru', 'sv', 'th', 'tr', 'vi', 'yue', 'zh']

the_languages["qwen3_srt"] = ['Cantonese', 'Chinese', 'English', 'French', 'German', 'Italian', 'Japanese', 'Korean', 'Portuguese', 'Russian', 'Spanish', 'de', 'en', 'es', 'fr', 'it', 'ja', 'ko', 'pt', 'ru', 'yue', 'zh']

the_helps["qwen3"] = '''additional possible dialects from China: Anhui, Dongbei, Fujian, Gansu, Guizhou, Hebei, Henan, Hubei, Hunan, Jiangxi, Ningxia, Shandong, Shaanxi, Shanxi, Sichuan, Tianjin, Yunnan, Zhejiang, Cantonese (HK), Cantonese (Guangdong), Wu, Minnan.'''

the_models = ["whisper", "faster-whisper", "whisper-afr", "nemotron", "nemotron-en", "parakeet", "qwen3"]

whisper_models = ["tiny", "base", "small", "medium", "large", "turbo", "tiny.en", "base.en", "small.en", "medium.en", "distil-small.en", "distil-medium.en", "distil-large-v3.5"]

the_general_help = '''For [whisper] languages, it will autodetect unless you use --language-whisper (see options below); you can also choose to translate into english with --whisper-translate. Default is turbo.
    You can also use [whisper-afr] for some other languages, so use of --language-whisper-afr will be required.
    For [nemotron] languages, it will autodetect unless you use --language-nemotron (see options below).
    You can also use [nemotron-en] as it is recommanded for english-only transcription.
    For [parakeet] languages, it will autodetect among Bulgarian (bg), Croatian (hr), Czech (cs), Danish (da), Dutch (nl), English (en), Estonian (et), Finnish (fi), French (fr), German (de), Greek (el), Hungarian (hu), Italian (it), Latvian (lv), Lithuanian (lt), Maltese (mt), Polish (pl), Portuguese (pt), Romanian (ro), Slovak (sk), Slovenian (sl), Spanish (es), Swedish (sv), Russian (ru), Ukrainian (uk).
    For [qwen3] languages, it will autodetect unless you use --language-qwen3 (see options below). Default param is 0.6b, and you can give .

    Default is running offline without querying/updating data from HF. If model had not been downloaded before, you need to set --online once.

    Default is running gpu (with cuda), you can force cpu only with --cpu.

    Default is exporting .txt file only, you can also generate subtitles with --srt'''


def launch_transcript(the_model, input_files, the_language_whisper, the_language_whisper_afr, the_language_nemotron, the_language_qwen3, the_params_whisper, the_params_qwen3, mode_whisper_translate, mode_cpu, mode_int8, mode_no_ffmpeg, the_beam_size, mode_srt, mode_online, the_prompt, mode_vocabulary, mode_warnings, cli_mode=True):

    if not mode_warnings:
        os.environ["TORCH_CPP_LOG_LEVEL"] = "ERROR"
        os.environ["TRANSFORMERS_VERBOSITY"]="critical"
        os.environ["CT2_VERBOSE"] = "-1"
        warnings.filterwarnings("ignore", module=r"torch.*")
        warnings.filterwarnings("ignore", module="librosa")
        warnings.filterwarnings("ignore", category=UserWarning)
        # warnings.filterwarnings("ignore", message="PySoundFile failed")
        # warnings.filterwarnings("ignore", message="expandable_segments not supported on this platform")

    if not mode_cpu:
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

    if mode_online:
        # os.environ["HF_DATASETS_OFFLINE"] = "0"
        # os.environ["TRANSFORMERS_OFFLINE"] = "0"
        # os.environ["HF_HUB_OFFLINE"] = "0"
        try:
            file_path = 'token.txt'
            with open(file_path, 'r') as file:
                your_hf_token = file.read()
            your_hf_token = your_hf_token.replace("\n","")
            import huggingface_hub
            huggingface_hub.login(token=your_hf_token)
        except:
            pass
    # else:
        # os.environ["HF_DATASETS_OFFLINE"] = "1"
        # os.environ["TRANSFORMERS_OFFLINE"] = "1"
        # os.environ["HF_HUB_OFFLINE"] = "1"

    if not the_prompt is None:
        user_prompt = f"{the_prompt.strip() if the_prompt[-1] !="." and the_prompt[-3:] !="..." else the_prompt[:-1].strip()}.\n"
    else:
        user_prompt=""

    user_vocabulary = ""
    if mode_vocabulary:
        try:
            user_vocabulary = f"Vocabulary: {get_vocab()}.\n"
        except:
            pass
    full_prompt = user_prompt + user_vocabulary

    if (not the_prompt is None or mode_vocabulary) and the_model in ["whisper", "whisper-afr", "qwen3"]:
        print("#### THIS FULL PROMPT WILL BE INSERTED:")
        print (full_prompt)
        print("####")


    file_source = check_files(input_files, mode_no_ffmpeg, cli_mode)


    if cli_mode:

        print(f"Are you sure you want to transcribe that list of {len(file_source)} file{'s' if len(file_source)>1 else ''}?")
        for elem in file_source:
            print(elem)

        if click.confirm("Do you want to continue?", default=True):
            print("Here we go!\n")
        else:
            quit()


    if the_model == "whisper":
        import whisper

        if mode_online:
            print("Allowing connections to Hugging Face isn't necessary with openai-whisper. Option [--online] ignored.")

        if mode_int8:
            print(f"int8 dtype only works for faster-whisper and whisper-afr, option ignored for {the_model}.")

        if not the_language_whisper_afr is None:
            print("Using whisper. Option [--language-whisper-afr] ignored.")

        if not the_language_nemotron is None:
            print("Using whisper. Option [--language-nemotron] ignored.")

        if not the_language_qwen3 is None:
            print("Using whisper. Option [--language-qwen3] ignored.")

        if not the_params_qwen3 is None:
            print("Using whisper. Option [--qwen3-params] ignored.")

        if not the_params_whisper is None and "distil" in the_params_whisper:
            print("distil models only available with faster-whisper.")
            quit()

        if torch.cuda.is_available():
            the_device = "cuda"
        elif torch.backends.mps.is_available():
            the_device = "mps"
        else:
            the_device = "cpu"

        try:
            model = whisper.load_model((the_params_whisper if not the_params_whisper is None else "turbo"), device=the_device  if not mode_cpu else "cpu", download_root="cache/whisper")

            the_task = "transcribe" if not mode_whisper_translate else "translate"
            the_language = the_language_whisper
            generation_config = {
                "task": the_task,
                "language": the_language,
            }
            if full_prompt != "":
                generation_config["initial_prompt"] = full_prompt



            for filito in file_source:
                try:
                    if mode_no_ffmpeg:
                        import librosa
                        audio_data,sr = librosa.load(filito, sr = 16000)
                    else:
                        audio_data = filito
                    result = model.transcribe(audio_data,
                                              # task=the_task,
                                              # language=the_language,
                                              # initial_prompt=None, #if set, even empty, it changes output transcript!!!!!
                                              beam_size= 5 if the_beam_size is None else the_beam_size,      # Greedy search
                                              # temperature=0.0   # Désactive l'échantillonnage aléatoire
                                              **generation_config
                                              )

                    if the_params_whisper is None:
                        print("\n#### Language detected: "+result["language"]+"\n")
                    print(result["text"])

                    if mode_srt:
                        transcribe_to_srt(result["segments"], filenameonly(filito))

                    transcribe_to_txt(result["text"], filenameonly(filito))

                except Exception as e:
                    if mode_warnings:
                        traceback.print_exc()
                    print("It failed for "+filito)

        except Exception as e:
            if mode_warnings:
                traceback.print_exc()
            print("Can't load model.")


    if the_model == "whisper-afr":
        import json
        from faster_whisper import WhisperModel
        from huggingface_hub import hf_hub_download
        import huggingface_hub

        if not mode_online:
            print("Allowing connections to Hugging Face is necessary with whisper-afr.")

        if not the_language_whisper is None:
            print("Using whisper-afr. Option [--language-whisper] ignored.")

        if the_language_whisper_afr is None:
            print("Using whisper-afr. Option [--language-whisper-afr] is mandatory.")
            quit()

        if not the_language_nemotron is None:
            print("Using whisper-afr. Option [--language-nemotron] ignored.")

        if not the_language_qwen3 is None:
            print("Using whisper-afr. Option [--language-qwen3] ignored.")

        if not the_params_qwen3 is None:
            print("Using whisper-afr. Option [--qwen3-params] ignored.")

        if not the_params_whisper is None:
            print("Using whisper-afr. Option [--whisper-params] ignored.")

        if mode_whisper_translate:
            print("Using whisper-afr. Option [--whisper-translate] ignored.")

        repo = "Sunbird/faster-whisper-51-african-languages"
        lang_map = json.load(open(hf_hub_download(repo, "language_map.json")))

        model_config = {}
        if mode_int8:
            model_config["compute_type"] = "int8"
        # if not mode_online:
        #     model_config["local_files_only"] = True



        if torch.cuda.is_available():
            the_device = "cuda"
        elif torch.backends.mps.is_available():
            the_device = "mps"
        else:
            the_device = "cpu"

        try:
            model = WhisperModel(repo, device=the_device  if not mode_cpu else "cpu",
                                 # compute_type="float16" if torch.cuda.is_available() and not mode_cpu else "float32"
                                 download_root="cache/huggingface",
                                 **model_config
                                 )

            generation_config = {
                "language" : lang_map[the_language_whisper_afr],
                "task": "transcribe"
            }
            if full_prompt != "":
                generation_config["initial_prompt"] = full_prompt

            for filito in file_source:
                try:
                    if mode_no_ffmpeg:
                        import librosa
                        audio_data,sr = librosa.load(filito, sr = 16000)
                    else:
                        audio_data = filito
                    segments, info = model.transcribe(
                        audio_data,
                        # language=lang_map[the_language_whisper_afr],
                        # task="transcribe",
                        beam_size= 5 if the_beam_size is None else the_beam_size,
                        vad_filter=True,
                        condition_on_previous_text=False,
                        word_timestamps = True,
                        **generation_config
                    )

                    transcription = []
                    timestamps = []
                    for segment in segments:
                        transcription.append(segment.text)
                        timestamps = timestamps + segment.words
                        print(f"[{segment.start:.2f} -> {segment.end:.2f}] {segment.text}")
                        if info.duration - segment.end < 1:
                            break

                    transcribe_to_txt("".join(transcription), filenameonly(filito), afr=True)

                    if mode_srt:
                        transcribe_to_srt(timestamps, filenameonly(filito), afr=True)

                except Exception as e:
                    if mode_warnings:
                        traceback.print_exc()
                    print("It failed for "+filito)

        except Exception as e:
            if mode_warnings:
                traceback.print_exc()
            print("Can't load model.")


    if the_model == "faster-whisper":
        from faster_whisper import WhisperModel

        if not the_language_whisper_afr is None:
            print(f"Using {the_model}. Option [--language-whisper-afr] ignored.")

        if not the_language_nemotron is None:
            print(f"Using {the_model}. Option [--language-nemotron] ignored.")

        if not the_language_qwen3 is None:
            print(f"Using {the_model}. Option [--language-qwen3] ignored.")

        if not the_params_qwen3 is None:
            print(f"Using {the_model}. Option [--qwen3-params] ignored.")

        from faster_whisper import WhisperModel

        model_size = the_params_whisper if not the_params_whisper is None else "turbo"

        if mode_whisper_translate and "distill" in model_size:
            print("Translating isn't possible with distil-whisper.")

        if not the_language_whisper is None and "distill" in model_size:
            print("Only english language is possible with distil-whisper.")

        model_config = {}
        if mode_int8:
            model_config["compute_type"] = "int8"
        if not mode_online:
            model_config["local_files_only"] = True



        if torch.cuda.is_available():
            the_device = "cuda"
        elif torch.backends.mps.is_available():
            the_device = "mps"
        else:
            the_device = "cpu"

        try:
            model = WhisperModel(model_size, device=the_device  if not mode_cpu else "cpu",
                                 download_root="cache/huggingface",
                                 # compute_type="float16" if torch.cuda.is_available() and not mode_cpu else "float32"
                                 **model_config
                                 )


            the_task = "translate" if (mode_whisper_translate and not "distil" in model_size) else "transcribe"

            generation_config = {
                "language" : the_language_whisper if not "distil" in model_size else None,
                "task": the_task
            }
            if full_prompt != "":
                generation_config["initial_prompt"] = full_prompt

            for filito in file_source:
                try:

                    if mode_no_ffmpeg:
                        import librosa
                        audio_data,sr = librosa.load(filito, sr = 16000)
                    else:
                        audio_data = filito

                    segments, info = model.transcribe(
                        audio_data,
                        # language=the_language_whisper,
                        # task="transcribe",
                        beam_size= 5 if the_beam_size is None else the_beam_size,
                        vad_filter=True,
                        condition_on_previous_text=False,
                        word_timestamps = True,
                        **generation_config
                    )

                    # if the_language_whisper is None:
                    print("\n#### Language detected: "+info.language+"\n")

                    transcription = []
                    timestamps = []
                    for segment in segments:
                        transcription.append(segment.text)
                        timestamps = timestamps + segment.words
                        print(f"[{segment.start:.2f} -> {segment.end:.2f}] {segment.text}")
                        if info.duration - segment.end < 1:
                            break

                    transcribe_to_txt("".join(transcription), filenameonly(filito), afr=True)

                    if mode_srt:
                        transcribe_to_srt(timestamps, filenameonly(filito), afr=True)

                except Exception as e:
                    if mode_warnings:
                        traceback.print_exc()
                    print("It failed for "+filito)

        except Exception as e:
            if mode_warnings:
                traceback.print_exc()
            print("Can't load model.")




    if "nemotron" in the_model:
        from transformers import AutoModelForRNNT, AutoProcessor
        from transformers.audio_utils import load_audio
        if not mode_warnings:
            from transformers.utils import logging
            logging.set_verbosity_error()

        if mode_int8:
            print(f"int8 dtype only works for faster-whisper and whisper-afr, option ignored for {the_model}.")

        if not the_language_whisper is None:
            print(f"Using {the_model}. Option [--language-whisper] ignored.")

        if not the_language_whisper_afr is None:
            print(f"Using {the_model}. Option [--language-whisper-afr] ignored.")

        if not the_language_nemotron is None and the_model == "nemotron-en":
            print(f"Using {the_model}. Option [--language-nemotron] ignored.")

        if not the_language_qwen3 is None:
            print(f"Using {the_model}. Option [--language-qwen3] ignored.")

        if not the_params_qwen3 is None:
            print(f"Using {the_model}. Option [--qwen3-params] ignored.")

        if not the_params_whisper is None:
            print(f"Using {the_model}. Option [--whisper-params] ignored.")

        if mode_whisper_translate:
            print(f"Using {the_model}. Option [--whisper-translate] ignored.")

        if (not the_prompt is None or mode_vocabulary):
            print(f"Using {the_model}. Prompts ignored.")

        if (the_beam_size):
            print(f"Using {the_model}. Beam size ignored.")

        try:
            model_id = "nvidia/nemotron-speech-streaming-en-0.6b" if "en" in the_model else "nvidia/nemotron-3.5-asr-streaming-0.6b"
            processor = AutoProcessor.from_pretrained(model_id, cache_dir="cache/huggingface", local_files_only=not mode_online)
            model = AutoModelForRNNT.from_pretrained(model_id, device_map="auto" if not mode_cpu else "cpu", cache_dir="cache/huggingface", local_files_only=not mode_online)

            the_language = "auto" if "en" in the_model or the_language_nemotron is None else the_language_nemotron

            for filito in file_source:
                try:
                    if mode_no_ffmpeg:
                        import librosa
                        audio_data,sr = librosa.load(filito, sr = 16000)
                    else:
                        audio_data = filito
                    audio = load_audio(
                        audio_data,
                        sampling_rate=processor.feature_extractor.sampling_rate
                    )
                    inputs = processor(audio, sampling_rate=processor.feature_extractor.sampling_rate, language=the_language)
                    inputs.to(model.device, dtype=model.dtype)

                    output = model.generate(**inputs, return_dict_in_generate=True, max_new_tokens=16384)
                    da_res_ln = processor.decode(output.sequences)
                    da_res = processor.decode(output.sequences, skip_special_tokens=True)

                    print(da_res_ln)

                    transcribe_to_txt(" ".join(da_res), filenameonly(filito), nv=True)

                    if mode_srt:
                        decoded_output, decoded_timestamps = processor.decode(
                            output.sequences,
                            durations=output.durations,
                            skip_special_tokens=True,
                        )
                        transcribe_to_srt(decoded_timestamps[0], filenameonly(filito), nv=True)

                except Exception as e:
                    if mode_warnings:
                        traceback.print_exc()
                    print("It failed for "+filito)

        except Exception as e:
            if mode_warnings:
                traceback.print_exc()
            print("Can't load model.")




    if "parakeet" in the_model:
        from transformers import AutoModelForTDT, AutoProcessor
        from transformers.audio_utils import load_audio

        if mode_int8:
            print(f"int8 dtype only works for faster-whisper and whisper-afr, option ignored for {the_model}.")

        if not the_language_whisper is None:
            print(f"Using {the_model}. Option [--language-whisper] ignored.")

        if not the_language_whisper_afr is None:
            print(f"Using {the_model}. Option [--language-whisper-afr] ignored.")

        if not the_language_nemotron is None:
            print(f"Using {the_model}. Option [--language-nemotron] ignored.")

        if not the_language_qwen3 is None:
            print(f"Using {the_model}. Option [--language-qwen3] ignored.")

        if not the_params_qwen3 is None:
            print(f"Using {the_model}. Option [--qwen3-params] ignored.")

        if not the_params_whisper is None:
            print(f"Using {the_model}. Option [--whisper-params] ignored.")

        if mode_whisper_translate:
            print(f"Using {the_model}. Option [--whisper-translate] ignored.")

        if (not the_prompt is None or mode_vocabulary):
            print(f"Using {the_model}. Prompts ignored.")

        if (the_beam_size):
            print(f"Using {the_model}. Beam size ignored.")

        if torch.cuda.is_available():
            the_device = "cuda"
        elif torch.backends.mps.is_available():
            the_device = "mps"
        else:
            the_device = "cpu"

        try:
            model_id = "nvidia/parakeet-tdt-0.6b-v3"
            processor = AutoProcessor.from_pretrained(model_id, cache_dir="cache/huggingface", local_files_only=not mode_online)
            model = AutoModelForTDT.from_pretrained(model_id, dtype="auto", device_map=the_device if not mode_cpu else "cpu", cache_dir="cache/huggingface", local_files_only=not mode_online)

            for filito in file_source:
                try:
                    if mode_no_ffmpeg:
                        import librosa
                        audio_data,sr = librosa.load(filito, sr = 16000)
                    else:
                        audio_data = filito
                    audio = load_audio(
                        audio_data,
                        sampling_rate=processor.feature_extractor.sampling_rate
                    )
                    inputs = processor(audio, sampling_rate=processor.feature_extractor.sampling_rate)
                    inputs.to(model.device, dtype=model.dtype)


                    output = model.generate(**inputs, return_dict_in_generate=True, max_new_tokens=16384)
                    da_res = processor.decode(output.sequences, skip_special_tokens=True)
                    print(da_res)

                    transcribe_to_txt(" ".join(da_res), filenameonly(filito), nv=True)

                    if mode_srt:
                        decoded_output, decoded_timestamps = processor.decode(
                            output.sequences,
                            durations=output.durations,
                            skip_special_tokens=True,
                        )
                        transcribe_to_srt(decoded_timestamps[0], filenameonly(filito), nv=True)

                except Exception as e:
                    if mode_warnings:
                        traceback.print_exc()
                    print("It failed for "+filito)

        except Exception as e:
            if mode_warnings:
                traceback.print_exc()
            print("Can't load model.")





    if "qwen3" in the_model:
        from transformers import AutoProcessor, AutoModelForMultimodalLM, AutoModelForTokenClassification, SequenceBiasLogitsProcessor
        if not mode_warnings:
            from transformers.utils import logging
            logging.set_verbosity_error()

        if mode_int8:
            print(f"int8 dtype only works for faster-whisper and whisper-afr, option ignored for {the_model}.")

        if not the_language_whisper is None:
            print(f"Using {the_model}. Option [--language-whisper] ignored.")

        if not the_language_whisper_afr is None:
            print(f"Using {the_model}. Option [--language-whisper-afr] ignored.")

        if not the_language_nemotron is None:
            print(f"Using {the_model}. Option [--language-nemotron] ignored.")

        if not the_params_whisper is None:
            print(f"Using {the_model}. Option [--whisper-params] ignored.")

        if mode_whisper_translate:
            print(f"Using {the_model}. Option [--whisper-translate] ignored.")

        if the_params_qwen3 is None or the_params_qwen3 == "0.6":
            print(f"Using default 0.6b model.")
        else:
            print(f"Using 1.7b model.")

        try:
            asr_model_id = "Qwen/Qwen3-ASR-0.6B-hf" if the_params_qwen3 is None or the_params_qwen3 == "0.6" else "Qwen/Qwen3-ASR-1.7B-hf"
            asr_processor = AutoProcessor.from_pretrained(asr_model_id, cache_dir="cache/huggingface", local_files_only=not mode_online)
            asr_model = AutoModelForMultimodalLM.from_pretrained(asr_model_id, device_map="auto" if not mode_cpu else "cpu", cache_dir="cache/huggingface", local_files_only=not mode_online)





            for filito in file_source:
                try:
                    if mode_no_ffmpeg:
                        import librosa
                        audio_data,sr = librosa.load(filito, sr = 16000)
                    else:
                        audio_data = filito
                    inputs = asr_processor.apply_transcription_request(audio=audio_data, language=the_language_qwen3)
                    inputs = inputs.to(asr_model.device, asr_model.dtype)

                    if full_prompt != "":
                        inputs = prompt_into_input(inputs, full_prompt, asr_processor, asr_model)

                    output_ids = asr_model.generate(**inputs, max_new_tokens=16384,
                                                    use_cache=True,
                                                    num_beams= 1 if the_beam_size is None else the_beam_size,
                                                    do_sample=False)
                    generated_ids = output_ids[:, inputs["input_ids"].shape[1]:]

                    parsed = asr_processor.decode(generated_ids, return_format="parsed")[0]
                    transcript = parsed["transcription"]
                    language = (parsed["language"] or "English") if the_language_qwen3 is None else (parsed["language"] or the_language_qwen3)

                    print("\n#### Language detected: "+language+"\n")
                    print(transcript)

                    transcribe_to_txt(transcript, filenameonly(filito))


                    if mode_srt:
                        if not language in the_languages["qwen3_srt"]:
                            print(f"Language {language} not supported for timestamps alignment (subtitles generation).")
                            quit()
                        try:
                            aligner_model_id = "Qwen/Qwen3-ForcedAligner-0.6B-hf"
                            aligner_processor = AutoProcessor.from_pretrained(aligner_model_id, cache_dir="cache/huggingface", local_files_only=not mode_online)
                            aligner_model = AutoModelForTokenClassification.from_pretrained(
                                aligner_model_id,
                                device_map="auto" if not mode_cpu else "cpu",
                                cache_dir="cache/huggingface", local_files_only=not mode_online
                            )

                            aligner_inputs, word_lists = aligner_processor.prepare_forced_aligner_inputs(
                                audio=audio_url, transcript=transcript, language=language)
                            aligner_inputs = aligner_inputs.to(aligner_model.device, aligner_model.dtype)

                            if full_prompt != "":
                                aligner_inputs = prompt_into_input(aligner_inputs, full_prompt, aligner_processor, aligner_model)

                            with torch.inference_mode():
                                outputs = aligner_model(**aligner_inputs, max_new_tokens=16384,
                                                        use_cache=True,
                                                        num_beams= 1 if the_beam_size is None else the_beam_size,
                                                        do_sample=False)

                            timestamps = aligner_processor.decode_forced_alignment(
                                logits=outputs.logits,
                                input_ids=aligner_inputs["input_ids"],
                                word_lists=word_lists,
                                timestamp_token_id=aligner_model.config.timestamp_token_id,
                            )[0]

                            transcribe_to_srt(timestamps, filenameonly(filito), qw=True)

                        except Exception as e:
                            if mode_warnings:
                                traceback.print_exc()
                            print("Can't load srt model.")
                except Exception as e:
                    if mode_warnings:
                        traceback.print_exc()
                    print("It failed for "+filito)

        except Exception as e:
            if mode_warnings:
                traceback.print_exc()
            print("Can't load model.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("model", choices=the_models, type=str,
    help=the_general_help)

    parser.add_argument("--online", action="store_true", help="to allow connections with Hugging Face")
    parser.add_argument("--cpu", action="store_true", help="to run without GPU")
    parser.add_argument("--srt", action="store_true", help="to generate subtitle")


    parser.add_argument("--language-whisper", type=str, choices=the_languages["whisper"])

    parser.add_argument("--language-whisper-afr", type=str, choices=the_languages["whisper-afr"], help=the_helps["whisper-afr"])

    parser.add_argument("--language-nemotron", type=str, choices=the_languages["nemotron"], help=the_helps["nemotron"])

    parser.add_argument("--language-qwen3", type=str, choices=the_languages["qwen3"], help=the_helps["qwen3"])

    parser.add_argument("--whisper-translate", action="store_true",
    help='''translating into english.''')

    parser.add_argument("--qwen3-params", type=str, choices=["0.6", "1.7"],
    help='''using with either 0.6b or 1.7b.''')

    parser.add_argument("--whisper-params", type=str, choices=whisper_models,
    help='''pick model size, distil ones only works with faster-whisper.''')

    parser.add_argument("--vocabulary", action="store_true", help="adds vocabulary.txt as Vocabulary prompt (whisper and qwen3 only)")

    parser.add_argument("--prompt", type=str, help='''type your prompt if needed (whisper and qwen3 only)''')

    parser.add_argument("--beam-size", type=int, choices=list(range(1,11)), help='''tweak words possibilities (whisper and qwen3 only)''')

    parser.add_argument("--int8", action="store_true", help="force using int8 dtype (whisper-afr and faster-whisper only)")

    parser.add_argument("--no-ffmpeg", action="store_true", help="if ffmpeg not install(able) on your computer, use WAV files only then!")

    parser.add_argument("--warnings", action="store_true", help="show user warnings")

    parser.add_argument("-i", "--input", action="append", type=str,
    help="source file")

    args = parser.parse_args()

    try:
        launch_transcript(args.model, args.input, args.language_whisper, args.language_whisper_afr, args.language_nemotron, args.language_qwen3, args.whisper_params, args.qwen3_params, args.whisper_translate, args.cpu, args.int8, args.no_ffmpeg, args.beam_size, args.srt, args.online, args.prompt, args.vocabulary, args.warnings, cli_mode=True)
    except Exception as e:
        if args.warnings:
            traceback.print_exc()
        print("It failed.")

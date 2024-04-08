import base64
import wave
import io

def convert_audio_to_base64_with_info(audio_file_path):
    """
    Converts an audio file to base64 encoding, and extracts its format and sampling rate.

    Args:
        audio_file_path (str): The path to the audio file.

    Returns:
        tuple: A tuple containing:
            * base64_data (str): The base64-encoded audio data.
            * audio_format (str): The audio file format (e.g., "wav", "mp3").
            * sampling_rate (int): The sampling rate of the audio file in Hz.
    """

    with open(audio_file_path, 'rb') as audio_file:
        audio_data = audio_file.read()

    base64_data = base64.b64encode(audio_data).decode('utf-8')

    return base64_data

# print(convert_audio_to_base64_with_info('./1.wav'))

def convert_base64_to_wav(base64_audio, output_filename):
    """
    Decodes Base64-encoded audio data and saves it as a WAV file.

    Args:
        base64_audio (str): The Base64-encoded audio string.
        output_filename (str): The desired filename for the output WAV file.
    """
    wav_file = open(output_filename, "wb")
    decode_string = base64.b64decode(base64_audio)
    wav_file.write(decode_string)


# base64_audio_string = "your_base64_audio_data"  
# output_filename = "my_audio.wav"
# convert_base64_to_wav(base64_audio_string, output_filename)



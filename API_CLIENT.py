import requests
import json

from utils import convert_audio_to_base64_with_info, convert_base64_to_wav

authorization_key = "cwiM9LU3hwudurE3TwUGec8D0_82_LPbzkUWY5zE-mHIjdhE1NqKBLIqN1EnXF0e"  

class API_CLIENT:
    def __init__(self, authorization_key):
        self.authorization_key = authorization_key
        self.base_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"

    def _build_headers(self):
        return {
            'Accept': '*/*',
            'User-Agent': 'Thunder Client (https://www.thunderclient.com)',
            'Authorization': self.authorization_key,
            'Content-Type': 'application/json'
        }

    def synthesize_audio_translate(self, audio_content, source_language, target_language, audio_format, sampling_rate):
        url = self.base_url

        payload = json.dumps({
          "pipelineTasks": [
            {
              "taskType": "asr",
              "config": {
                "language": {
                  "sourceLanguage": source_language
                },
                "serviceId": "ai4bharat/conformer-hi-gpu--t4",
                "audioFormat": audio_format,
                "samplingRate": sampling_rate
              }
            },
            {
              "taskType": "translation",
              "config": {
                "language": {
                  "sourceLanguage": source_language,
                  "targetLanguage": target_language
                },
                "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
              }
            },
          ],
          "inputData": {
            "audio": [
              {
                "audioContent": audio_content
              }
            ]
          }
        })

        headers = self._build_headers()
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.text
    
    def translate_and_synthesize_speech(self, text, source_language, target_language, tts_gender="female", tts_sampling_rate=8000):
        """Performs translation followed by text-to-speech."""

        url = self.base_url

        payload = json.dumps({
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_language,
                            "targetLanguage": target_language
                        },
                        "serviceId": "ai4bharat/indictrans-v2-all-gpu--t4"
                    }
                },
                {
                    "taskType": "tts",
                    "config": {
                        "language": {
                            "sourceLanguage": target_language 
                        },
                        "serviceId": "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4", 
                        "gender": tts_gender,
                        "samplingRate": tts_sampling_rate
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": text 
                    }
                ]
            }
        })

        headers = self._build_headers()
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.text

client = API_CLIENT(authorization_key)

audio_content = convert_audio_to_base64_with_info('./1.wav')
source_language = "hi"
target_language = "en"
audio_format = "flac"
sampling_rate = 16000

# result = client.synthesize_audio_translate(audio_content, source_language, target_language, audio_format, sampling_rate)
# print(type(json.loads(result))) 

# text = "My name is Vihir and I am using the language Varsh."
# result = json.loads(client.translate_and_synthesize_speech(text, source_language="en", target_language="hi"))
# audio_base_64 = result["pipelineResponse"][1]['audio'][0]['audioContent']
# # print(result["pipelineResponse"][1]['config'])
# print(audio_base_64)
# convert_base64_to_wav(audio_base_64, "output.wav")
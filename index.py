import gradio as gr
import os
import time

def click_js():
    return """function audioRecord() {
    var xPathRes = document.evaluate ('//*[contains(@class, "record")]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null); 
    xPathRes.singleNodeValue.click();}"""

def action(btn):
    """Changes button text on click"""
    if btn == 'Speak':
        return 'Stop'
    else:
        return 'Speak'

def check_btn(btn):
    """Checks for correct button text before invoking transcribe()"""
    if btn != 'Speak':
        raise Exception('Recording...')

def save_audio(audio_content):
    # Save the audio content to a file named "audio.wav"
    print(audio_content)
    filename = "audio.wav"
    with open(filename, "wb") as f:
        f.write(audio_content)
    return f"Audio saved as: {filename}"

with gr.Blocks() as demo:
    msg = gr.Textbox()
    audio_box = gr.Audio(label="Audio", sources="microphone", type="numpy", elem_id='audio')

    with gr.Row():
        audio_btn = gr.Button('Speak')
        clear = gr.Button("Clear")

    audio_btn.click(fn=action, inputs=audio_btn, outputs=audio_btn).\
              then(fn=lambda: None, js=click_js()).\
              then(fn=check_btn, inputs=audio_btn).\
              success(fn=save_audio, inputs=audio_box, outputs=msg)

    clear.click(lambda: None, None, msg, queue=False)

demo.queue().launch(debug=True, share=True)

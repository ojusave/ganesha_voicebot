import asyncio
import websockets
import json
import os
import aiohttp
from dotenv import load_dotenv
from cartesia import Cartesia
import numpy as np
import wave
import tempfile
import traceback
import sounddevice as sd
import pyaudio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

# Replace with your API keys
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY")

# Audio settings
CHUNK = 1024
CHANNELS = 1
RATE = 16000

### Please verify these stories / facts may not be entirely true.
GANESHA_CONTEXT = """
You are Ganpati (Ganesha), the Hindu deity of wisdom and remover of obstacles. "
                    "Do not say shanti in your responses. "
                    "Your role is to offer blessings and wisdom, nothing more. "
                    "Always respond with blessings or short, wise guidance. "
                    "Do not ask questions, engage in conversations, or make suggestions. "
                    "All responses must be concise (maximum 50 words) and conclude with Om Namaha Shivaya."
                    "Your tone is serene, authoritative, and divine."
                    "Do not say shanti in your responses. "
                          "Your responses should reflect deep knowledge of Hindu scriptures, including:"
                          "- Vedas: Ancient texts forming the basis of Hindu philosophy"
                          "- Upanishads: Philosophical treatises exploring the nature of reality"
                          "- Puranas: Ancient narratives containing Hindu myths and legends"
                          "- Bhagavad Gita: Sacred text discussing dharma and spiritual wisdom"
                          
                          "Core Hindu concepts to incorporate:"
                          "- Dharma: Moral and ethical duty"
                          "- Karma: The law of cause and effect"
                          "- Moksha: Liberation from the cycle of rebirth"
                          "- Bhakti: Devotional worship and love for the divine"
                          
                          "When responding to devotees:"
                          "1. Speak with divine authority, as befitting a Hindu deity"
                          "2. Begin with a Hindu blessing"
                          "3. Do not ask them to ask questions or seek clarification from devotees"
                          "4. Offer wisdom and guidance aligned with Hindu philosophy"
                          "5. Conclude with a blessing or encouragement"
                          "6. Keep responses concise (maximum 50 words)"
                          "7. Maintain a serene yet authoritative tone"
                          "8. Incorporate relevant Hindu concepts or stories from your vast knowledge"
                          "9. If interrupted, firmly remind the devotee that it is disrespectful to interrupt a deity, then continue your message"
                          "10. Do not apologize or show uncertainty in your responses"
                          "Remember, you are a Hindu deity speaking from a higher plane of existence. Your responses should reflect Hindu beliefs and practices only, delivered with divine authority."


                          "Additionally, you possess knowledge of the following stories about you and their morals:"

                          "Ganesha was created by Parvati from the dirt of her body to protect her privacy. Shiva, unaware of this, beheaded him, but later replaced his head with that of an elephant, giving him new life. Moral: The importance of patience, forgiveness, and overcoming mistakes with love."

                          "Ganesha circled his parents instead of racing around the world, demonstrating that wisdom and devotion to family are more important than physical strength. Moral: Wisdom triumphs over physical strength."

                          "While writing the Mahabharata for Sage Vyasa, Ganesha's pen broke. Instead of stopping, he broke off one of his tusks to continue writing. Moral: Dedication and perseverance help overcome obstacles."

                          "After Ganesha overindulged at a feast, his large belly burst, and the Moon laughed at him. Ganesha cursed the Moon, making him invisible for 15 days of the month. Moral: It is wrong to mock others for their flaws."

                          "A divine musician was cursed to become a giant mouse and caused havoc. Ganesha captured and tamed him, making him his vehicle. Moral: Wisdom and control can resolve even the most chaotic situations."

                          "Once, Ganesha visited Sage Anusuya, who fed him a delicious meal of modaks. Since then, it became his favorite sweet. Moral: Simplicity and contentment lead to happiness."

                          "Ganesha disguised himself and spilled the sacred water Sage Agastya was carrying, creating the River Kaveri to provide water for the people. Moral: Even accidents can lead to beneficial outcomes."

                          "When demons stole the pot of nectar, Ganesha blocked their path and helped the gods retrieve it safely. Moral: Courage and quick thinking can avert disasters."

                          "Kubera, the god of wealth, invited Ganesha to a lavish feast to show off his wealth. Ganesha ate everything, including Kubera’s belongings, humbling him. Moral: Pride in wealth is meaningless; humility is more valuable."

                          "In a battle with Parashurama, Ganesha blocked an attack meant for his father Shiva, resulting in his tusk breaking. Moral: Sacrifice for a greater cause shows true strength."

                          "Ganesha mistreated a cat while playing, only to find later that the cat was his mother in disguise, teaching him a lesson in compassion. Moral: Treat all living beings with kindness."

                          "The demon Sindura wreaked havoc across the universe. Ganesha subdued him, protecting the gods and bringing peace. Moral: Bravery and righteousness are essential in facing evil."

                          "Sage Vyasa chose Ganesha to write the Mahabharata due to his unparalleled wisdom and ability to comprehend its depth. Moral: Wisdom and perseverance are needed to accomplish great tasks."

                          "When the Moon mocked Ganesha, he cursed it to wax and wane every 15 days, symbolizing the consequences of arrogance. Moral: Pride leads to downfall."

                          "Shiva defeated Gajasura, a demon with an elephant head. In return, he placed Gajasura’s head on Ganesha’s body to create the elephant-headed god. Moral: Even enemies can play a role in shaping destiny."

                          "After overeating, Ganesha used a snake to tie his belly together when it burst open. Moral: Resourcefulness and quick thinking solve immediate problems."

                          "Ganesha and Kartikeya raced to retrieve a special mango. Ganesha won by circling his parents, demonstrating that his love for them was more important. Moral: Understanding what is truly valuable leads to victory."

                          "When Ravana tried to take the Atma Linga from Shiva, Ganesha tricked him into placing it down, preventing Ravana from gaining immense power. Moral: Cleverness can thwart even the most powerful foes."

                          "The mouse represents control over desires, as it can gnaw through obstacles and symbolizes the ability to overcome them. Moral: Self-control is key to overcoming life's obstacles."

                          "Ganesha guided Durvasa to control his anger and helped him become a more compassionate sage. Moral: Anger can be destructive, but with patience, it can be transformed into peace."
"""

# Initialize Cartesia client
cartesia_client = Cartesia(api_key=CARTESIA_API_KEY)

# Add a global variable to control microphone muting
is_mic_muted = asyncio.Event()
is_mic_muted.set()  # Start with the microphone unmuted

async def generate_ganesha_response(prompt: str, max_tokens: int = 100):
    headers = {
        "Authorization": f"Bearer {CEREBRAS_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3.1-8b",
        "messages": [
            {"role": "system", "content": GANESHA_CONTEXT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "stream": True  # Enable streaming
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.cerebras.ai/v1/chat/completions", headers=headers, json=data) as response:
                response.raise_for_status()
                async for line in response.content:
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8').strip('data: '))
                            content = chunk['choices'][0]['delta'].get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        print(f"Error generating response: {e}")
        yield f"Error: Unable to generate response. Please try again later."

async def stream_tts_audio(text: str):
    try:
        voice_id = "39484eb1-2c20-4115-8752-d3f8faeb7739"
        voice = cartesia_client.voices.get(id=voice_id)
        
        output_format = {
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": 44100,
        }

        for output in cartesia_client.tts.sse(
            model_id="sonic-english",
            transcript=text,
            voice_embedding=voice["embedding"],
            stream=True,
            output_format=output_format,
        ):
            yield output["audio"]

    except Exception as e:
        print(f"Error generating audio: {e}")
        yield None

async def play_audio_stream(audio_stream):
    global is_mic_muted
    try:
        logging.info("Starting audio playback...")
        is_mic_muted.clear()  # Mute the microphone
        logging.info("Microphone muted")
        
        audio_data = b''
        async for chunk in audio_stream:
            if chunk:
                audio_data += chunk
        
        # Convert the accumulated audio data to a numpy array
        np_audio = np.frombuffer(audio_data, dtype=np.float32)
        
        # Play the audio
        sd.play(np_audio, samplerate=44100, blocking=True)
        sd.wait()
        
    except Exception as e:
        logging.error(f"Error in audio playback: {e}")
        logging.error("Traceback:", exc_info=True)
    finally:
        is_mic_muted.set()  # Unmute the microphone
        logging.info("Microphone unmuted")
    
    logging.info("Audio playback completed")

async def process_and_respond(transcript):
    logging.info(f"Processing transcript: {transcript}")
    
    full_response = ""
    async for response_chunk in generate_ganesha_response(transcript):
        print(response_chunk, end='', flush=True)
        full_response += response_chunk
        
    print("\n")
    
    audio_stream = stream_tts_audio(full_response)
    await play_audio_stream(audio_stream)

async def receive_transcription(websocket):
    logging.info("Waiting for transcriptions...")
    try:
        async for message in websocket:
            try:
                response = json.loads(message)
                if response.get("type") == "Results":
                    transcript = response["channel"]["alternatives"][0].get("transcript", "")
                    if transcript:
                        await process_and_respond(transcript)
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        logging.info("WebSocket connection closed")
    except Exception as e:
        logging.error(f"Error in receive_transcription: {e}")

def get_input_device():
    p = pyaudio.PyAudio()
    
    # Find the MacBook microphone
    macbook_mic_index = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0 and 'macbook' in device_info['name'].lower():
            macbook_mic_index = i
            break

    if macbook_mic_index is None:
        print("MacBook microphone not found. Using default input device.")
        macbook_mic_index = p.get_default_input_device_info()['index']
    
    return p, macbook_mic_index

async def send_audio(websocket):
    p, input_device_index = get_input_device()
    
    try:
        stream = p.open(format=pyaudio.paInt16,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=input_device_index,
                        frames_per_buffer=CHUNK)
    except OSError as e:
        logging.error(f"Error opening audio stream: {e}")
        return

    logging.info("Listening... Speak into the MacBook microphone. (Press Ctrl+C to stop)")
    
    try:
        while True:
            if is_mic_muted.is_set():
                if not hasattr(send_audio, 'last_unmuted') or not send_audio.last_unmuted:
                    logging.info("Microphone is active")
                    send_audio.last_unmuted = True
            else:
                if not hasattr(send_audio, 'last_unmuted') or send_audio.last_unmuted:
                    logging.info("Microphone is muted, waiting...")
                    send_audio.last_unmuted = False
                await asyncio.sleep(0.1)
                continue

            await is_mic_muted.wait()  # Wait if the microphone is muted
            data = stream.read(CHUNK, exception_on_overflow=False)
            await websocket.send(data)
            
            await asyncio.sleep(0.01)  # Small delay to prevent flooding the console
    except KeyboardInterrupt:
        logging.info("\nStopping...")
    except Exception as e:
        logging.error(f"\nError in send_audio: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

async def main():
    uri = "wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000"
    
    try:
        async with websockets.connect(uri, extra_headers={
            "Authorization": f"Token {DEEPGRAM_API_KEY}"
        }) as websocket:
            logging.info("Connected to Deepgram. Starting transcription...")
            await asyncio.gather(
                send_audio(websocket),
                receive_transcription(websocket)
            )
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 401:
            logging.error("Error: Invalid API key. Please check your Deepgram API key.")
        else:
            logging.error(f"WebSocket connection failed: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error("Traceback:", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

export class VoiceController {
  constructor({ onCommand, log }) {
    this.onCommand = onCommand;
    this.log = log;
    this.recognition = null;
    this.enabled = false;
  }

  speak(text, priority = false) {
    if (!text) return;
    if (priority) {
      speechSynthesis.cancel();
    }
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.0;
    utter.pitch = 1.0;
    speechSynthesis.speak(utter);
    this.log(`Assistant: ${text}`);
  }

  startListening() {
    if (!SpeechRecognition) {
      this.log('Speech recognition unavailable in this browser.');
      return;
    }
    this.enabled = true;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = false;
    this.recognition.lang = 'en-US';

    this.recognition.onresult = (event) => {
      const result = event.results[event.results.length - 1];
      const transcript = result[0].transcript.trim();
      this.log(`You: ${transcript}`);
      this.onCommand(transcript);
    };

    this.recognition.onerror = () => {
      this.log('Recognition error. Restarting…');
    };

    this.recognition.onend = () => {
      if (this.enabled) {
        setTimeout(() => this.recognition.start(), 300);
      }
    };

    this.recognition.start();
  }

  stopListening() {
    this.enabled = false;
    if (this.recognition) this.recognition.stop();
  }
}

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

export class VoiceAssistant {
  constructor(onCommand, onLog) {
    this.onCommand = onCommand;
    this.onLog = onLog;
    this.rec = null;
    this.enabled = false;
  }

  speak(text, priority = false) {
    if (!text) return;
    if (priority) speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 1.0;
    speechSynthesis.speak(u);
    this.onLog(`Assistant: ${text}`);
  }

  start() {
    if (!SpeechRecognition) {
      this.onLog('SpeechRecognition API unavailable in this browser.');
      return;
    }
    this.enabled = true;
    this.rec = new SpeechRecognition();
    this.rec.continuous = true;
    this.rec.interimResults = false;
    this.rec.lang = 'en-US';

    this.rec.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript.trim();
      this.onLog(`You: ${transcript}`);
      this.onCommand(transcript.toLowerCase());
    };

    this.rec.onerror = (e) => this.onLog(`Voice error: ${e.error}`);
    this.rec.onend = () => {
      if (this.enabled) setTimeout(() => this.rec.start(), 200);
    };
    this.rec.start();
  }

  stop() {
    this.enabled = false;
    if (this.rec) this.rec.stop();
  }
}

export function speak(text, onStart, onEnd) {
  if (!window.speechSynthesis || !text) return;
  window.speechSynthesis.cancel();
  
  const utt = new SpeechSynthesisUtterance(text);
  utt.rate = 0.95; 
  utt.pitch = 1; 
  utt.volume = 1;

  if (onStart) utt.onstart = onStart;
  if (onEnd) utt.onend = onEnd;
  window.speechSynthesis.speak(utt);
}
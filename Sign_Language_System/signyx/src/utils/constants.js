export const AUDIO_MODES = {
  OFF:       'off',
  ON_ADD:    'on_add',
  ON_DETECT: 'on_detect',
  SENTENCE:  'sentence',
};

export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8088";
export const CAPTURE_INTERVAL = 300;
export const HISTORY_MAX = 30;
export const SMOOTHING_FRAMES = 5;
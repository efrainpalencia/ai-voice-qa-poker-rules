export const resetAudioState = (
    setFinalResponse: (response: null) => void,
    setAudioKey: (key: (prev: number) => number) => void,
    audioRef: React.RefObject<HTMLAudioElement>
  ) => {
    setFinalResponse(null);
    setAudioKey((prev) => prev + 1);
    if (audioRef.current) {
      audioRef.current.src = "";
      audioRef.current.load();
    }
  };
  
  export const handleAudioPlayback = (
    audioRef: React.RefObject<HTMLAudioElement>,
    speechUrl: string,
    baseApiUrl: string
  ) => {
    if (audioRef.current) {
      audioRef.current.src = `${baseApiUrl}${speechUrl}?t=${Date.now()}`;
      audioRef.current.load();
  
      audioRef.current.oncanplaythrough = () => {
        audioRef.current.play().catch((err) =>
          console.error("🔊 Playback failed:", err)
        );
      };
    } else {
      console.warn("⚠️ Audio player not found.");
    }
  };
  
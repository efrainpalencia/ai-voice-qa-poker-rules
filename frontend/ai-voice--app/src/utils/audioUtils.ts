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
    if (!audioRef.current) {
      console.warn("⚠️ Audio element not found. Retrying...");
      return;
    }
  
    const fullUrl = `${baseApiUrl}${speechUrl}?cache_bust=${Date.now()}`;
    console.log("🎯 Final Audio URL:", fullUrl);
  
    audioRef.current.src = fullUrl;
  
    audioRef.current.oncanplaythrough = () => {
      audioRef.current?.play().catch((err) =>
        console.error("🔊 Playback failed:", err)
      );
    };
  
    audioRef.current.load();
  };
  
  
  
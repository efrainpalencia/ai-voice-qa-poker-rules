export const resetAudioState = (
  setFinalResponse: React.Dispatch<React.SetStateAction<any>>,
  audioRef: React.RefObject<HTMLAudioElement>
) => {
  setFinalResponse(null);
  if (audioRef.current) {
    audioRef.current.pause();
    audioRef.current.currentTime = 0;
    audioRef.current.src = "";
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
  
  
  
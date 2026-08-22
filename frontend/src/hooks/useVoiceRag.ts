import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, API_BASE_URL, checkHealth, postQuery, postVoice } from "@/services/api";
import { demoAnswer } from "@/services/demo";
import type { RagResponse, VoiceState } from "@/types/rag";

export type BackendStatus = "checking" | "online" | "offline";

export function useVoiceRag() {
  const [state, setState] = useState<VoiceState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RagResponse | null>(null);
  const [backend, setBackend] = useState<BackendStatus>("checking");
  const [selectedLanguage, setSelectedLanguage] = useState<string>("auto");

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const refreshHealth = useCallback(async () => {
    if (!API_BASE_URL) {
      setBackend("offline");
      return false;
    }
    setBackend("checking");
    const ok = await checkHealth();
    setBackend(ok ? "online" : "offline");
    return ok;
  }, []);

  useEffect(() => {
    void refreshHealth();
  }, [refreshHealth]);

  const run = useCallback(
    async (task: () => Promise<RagResponse>) => {
      setState("processing");
      setError(null);
      try {
        const response = await task();
        setResult(response);
        setState("completed");
      } catch (err) {
        const apiError = err as ApiError;
        setBackend("offline");
        setError(apiError?.message ?? "Something went wrong while answering.");
        setState("error");
      }
    },
    [],
  );

  const askText = useCallback(
    async (question: string) => {
      const trimmed = question.trim();
      if (!trimmed) return;
      if (backend !== "online") {
        await run(() => demoAnswer(trimmed));
        return;
      }
      await run(() => postQuery(trimmed, selectedLanguage === "auto" ? undefined : selectedLanguage));
    },
    [backend, run, selectedLanguage],
  );

  const stopRecording = useCallback(() => {
    recorderRef.current?.stop();
  }, []);

  const startRecording = useCallback(async () => {
    setError(null);
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      setError("This browser does not support microphone capture. Use the text input instead.");
      setState("error");
      return;
    }

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setError("Microphone permission denied. Allow access in your browser, or type your question.");
      setState("error");
      return;
    }

    try {
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
        const audio = new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" });
        if (backend !== "online") {
          void run(() => demoAnswer("How does grounded retrieval work?", true));
          return;
        }
        if (audio.size === 0) {
          setError("No audio was captured. Try recording again.");
          setState("error");
          return;
        }
        void run(() => postVoice(audio, selectedLanguage === "auto" ? undefined : selectedLanguage));
      };
      recorder.start();
      recorderRef.current = recorder;
      setState("recording");
    } catch {
      stream.getTracks().forEach((track) => track.stop());
      setError("Recording failed to start on this device. Use the text input instead.");
      setState("error");
    }
  }, [backend, run]);

  const toggleRecording = useCallback(() => {
    if (state === "recording") stopRecording();
    else if (state !== "processing") void startRecording();
  }, [state, startRecording, stopRecording]);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setState("idle");
  }, []);

  return {
    state,
    error,
    result,
    backend,
    demoMode: backend !== "online",
    askText,
    toggleRecording,
    refreshHealth,
    reset,
    selectedLanguage,
    setSelectedLanguage,
  };
}
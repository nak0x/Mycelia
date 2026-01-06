import { useEffect, useRef, useState } from 'react';
import { Howl, Howler } from 'howler';
import type { Frame } from '../types/frame';

// On map les sons ici
const SOUNDS: Record<string, string> = {
  '01-interaction-done': '/sounds/01-interaction-done.mp3',
  '02-interaction-done': '/sounds/02-interaction-done.mp3',
  'background': '/sounds/background.mp3',
  'stop-sound': '',
};

export const useSocketAudio = (url: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<Frame[]>([]);
  const [lastFrame, setLastFrame] = useState<Frame | null>(null);
  
  const soundInstances = useRef<Record<string, Howl>>({});
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // 1. Initialisation des sons
  useEffect(() => {
    Object.entries(SOUNDS).forEach(([action, src]) => {
      if (src) {
        soundInstances.current[action] = new Howl({
          src: [src],
          preload: true,
          volume: 1.0,
        });
      }
    });
  }, []);

  // 2. Gestion WebSocket
  useEffect(() => {
    const connect = () => {
      console.log('Connexion au WS...');
      socketRef.current = new WebSocket(url);

      socketRef.current.onopen = () => {
        console.log('WS Connecté');
        setIsConnected(true);
      };

      socketRef.current.onclose = () => {
        console.log('WS Déconnecté, tentative de reconnexion dans 3s...');
        setIsConnected(false);
        reconnectTimeoutRef.current = setTimeout(connect, 3000); 
      };

      socketRef.current.onmessage = (event) => {
        try {
          const data: Frame = JSON.parse(event.data);
          setLastFrame(data);
          setLogs(prevLogs => [data, ...prevLogs].slice(0, 50)); // Garde les 50 derniers logs
          handleAction(data);
        } catch (e) {
          console.error("Erreur parsing JSON", e);
        }
      };
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.onclose = null;
        socketRef.current.close();
      }
    };
  }, [url]);

  // 3. Lancement des sons
  const handleAction = (frame: Frame) => {
    console.log(`Action reçue: ${frame.action}`);

    if (frame.action === 'stop-sound') {
        Howler.stop(); 
        return;
    }

    const sound = soundInstances.current[frame.action];
    if (sound) {
      if (frame.value === true) {
          console.log(`Lancement du son: ${frame.action}`);
          sound.play();
      }
    }
  };

  const [volume, setVolume] = useState(1.0);
  const [isMuted, setIsMuted] = useState(false);

  // ... (previous code)

  // 4. Gestion Volume & Mute Global
  useEffect(() => {
    Howler.volume(volume);
  }, [volume]);

  useEffect(() => {
    Howler.mute(isMuted);
  }, [isMuted]);

  return { 
    isConnected, 
    lastFrame, 
    logs,
    volume,
    setVolume,
    isMuted,
    setIsMuted 
  };
};
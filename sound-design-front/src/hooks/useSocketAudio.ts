import { useEffect, useRef, useState } from 'react';
import { Howl, Howler } from 'howler';
import type { Frame } from '../types/frame';
import { useWebSocket } from '../contexts/WebSocketContext';

// On map les sons ici
const SOUNDS: Record<string, string> = {
  'background': '/sounds/background.mp3',
  '01-rain-toggle': '/sounds/01-rain-toggle.mp3',
  '01-shroom-forest-lighten': '/sounds/01-shroom-forest-lighten.mp3',
  '01-wind-toggle': '/sounds/01-wind-toggle.mp3',
  '03-grow-mycelium': '/sounds/03-grow-mycelium.mp3',
  '03-grow-shroom': '/sounds/03-grow-shroom.mp3',
  '03-nutrient-start-animation': '/sounds/03-nutrient-start-animation.mp3',
  '03-interaction-done': '/sounds/03-interaction-done.mp3',
  '03-interaction-done-background': '/sounds/03-interaction-done-background.mp3',
  'stop-sound': '',
};

export const useSocketAudio = () => {
  const { isConnected, lastFrame, logs } = useWebSocket();
  const soundInstances = useRef<Record<string, Howl>>({});
  
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

  // 2. Gestion Playback via lastFrame du contexte
  useEffect(() => {
    if (lastFrame) {
        handleAction(lastFrame);
    }
  }, [lastFrame]);

  // 3. Lancement des sons
  const handleAction = (frame: Frame) => {
    console.log(`Action reçue: ${frame.action}`);

    if (frame.action === 'stop-sound') {
        Howler.stop(); 
        return;
    }

    const sound = soundInstances.current[frame.action];
    if (sound) {
      if (frame.value === true || frame.value === null) {
          console.log(`Lancement du son: ${frame.action}`);
          sound.play();
      }
    }
  };

  const [volume, setVolume] = useState(1.0);
  const [isMuted, setIsMuted] = useState(false);

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
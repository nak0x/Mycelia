import React, { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';
import type { Frame } from '../types/frame';

interface WebSocketContextType {
  isConnected: boolean;
  lastFrame: Frame | null;
  logs: Frame[];
  sendJson: (data: Frame) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider = ({ url, children }: { url: string; children: ReactNode }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<Frame[]>([]);
  const [lastFrame, setLastFrame] = useState<Frame | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

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
        reconnectTimeoutRef.current = setTimeout(connect, 3000) as unknown as number;
      };

      socketRef.current.onmessage = (event) => {
        try {
          const data: Frame = JSON.parse(event.data);
          setLastFrame(data);
          setLogs(prevLogs => [data, ...prevLogs].slice(0, 50));
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

  const sendJson = (data: Frame) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        const json = JSON.stringify(data);
        console.log("Sending WS message:", json);
        socketRef.current.send(json);
    } else {
        console.warn("WebSocket not connected, cannot send:", data);
    }
  };

  return (
    <WebSocketContext.Provider value={{ isConnected, lastFrame, logs, sendJson }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

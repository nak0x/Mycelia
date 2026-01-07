import type { Frame } from '../types/frame';
import { useWebSocket } from '../contexts/WebSocketContext';

export const useSendAction = () => {
    const { sendJson } = useWebSocket();

    const sendAction = (action: string, value: boolean | null = null, senderId: string = "CLIENT-WEB") => {
        const frame: Frame = {
            metadata: {
                timestamp: Math.floor(Date.now() / 1000),
                senderId
            },
            action,
            value
        };
        sendJson(frame);
    };

    return { sendAction };
};
import type { Log } from '../../hooks/useSocketAudio';

interface LogsDrawerProps {
    isOpen: boolean;
    setIsLogsOpen: (open: boolean) => void;
    isUIHidden: boolean;
    logs: Log[];
}

export function LogsDrawer({ isOpen, setIsLogsOpen, isUIHidden, logs }: LogsDrawerProps) {
    return (
        <div 
            className={`fixed bottom-0 left-0 w-full h-[50vh] bg-black/90 backdrop-blur-xl border-t border-white/20 transform transition-transform duration-300 ease-in-out z-40 flex flex-col ${
                isOpen && !isUIHidden ? 'translate-y-0' : 'translate-y-full'
            }`}
        >
            <div className="flex justify-between items-center p-4 border-b border-white/10 bg-white/5">
                <h2 className="font-bold tracking-widest text-sm">SYSTEM LOGS</h2>
                <button onClick={() => setIsLogsOpen(false)} className="text-gray-400 hover:text-white cursor-pointer px-2">
                    CLOSE [X]
                </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 font-mono text-xs">
                {logs.length === 0 ? (
                    <div className="text-gray-600 italic p-4 text-center">No logs available</div>
                ) : (
                    <div className="space-y-2">
                        {[...logs].sort((a, b) => b.metadata.timestamp - a.metadata.timestamp).map((log, index) => (
                            <div key={index} className="flex gap-4 border-b border-white/5 pb-2 hover:bg-white/5 transition-colors p-2">
                                <span className="text-gray-500 w-24 shrink-0">{new Date(log.metadata.timestamp * 1000).toLocaleTimeString()}</span>
                                <span className="text-green-400 w-32 shrink-0 font-bold">{log.action}</span>
                                <span className="text-gray-400 w-32 shrink-0 border-r border-white/10 pr-4">{log.metadata.senderId}</span>
                                <span className="text-gray-300 break-all">{JSON.stringify(log.value)}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

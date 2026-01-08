import { useState, useRef, useEffect } from 'react';
import { useSocketAudio } from './hooks/useSocketAudio';
import { useSendAction } from './hooks/useSendAction';
import { WebSocketProvider } from './contexts/WebSocketContext';
import actionsData from './actions.json';
import type { Frame } from './types/frame';

interface ActionDef {
    action: string;
    type: 'boolean' | null;
}

function AppContent() {
  const { isConnected, lastFrame, logs, volume, setVolume, isMuted, setIsMuted } = useSocketAudio();
  const [hasInteracted, setHasInteracted] = useState(false);
  const [isLogsOpen, setIsLogsOpen] = useState(false);
  const [isCommandsOpen, setIsCommandsOpen] = useState(false);
  const [isUIHidden, setIsUIHidden] = useState(false);
  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [isVideoDone, setIsVideoDone] = useState(false);  
  const videoRef = useRef<HTMLVideoElement>(null);
  const playTimeoutRef = useRef<number | null>(null);
  const lastProcessedFrameRef = useRef<Frame | null>(null);
  const { sendAction } = useSendAction();
  
  let videoPlayTime = 20000/80;

  const handleStart = () => {
    setHasInteracted(true);
    if (videoRef.current) {
        videoRef.current.pause();
        videoRef.current.currentTime = 0;
    }
  };

  useEffect(() => {
    if (!lastFrame || lastFrame === lastProcessedFrameRef.current) return;
    lastProcessedFrameRef.current = lastFrame;

    if (lastFrame.action === '03-grow-mycelium') {
        if (videoRef.current) {
            if (isVideoDone) {
                return;
            }
            if (videoRef.current.ended) {
                setIsVideoDone(true);
                sendAction('03-nutrient-start-animation');
                return;
            }

            if (playTimeoutRef.current) {
                clearTimeout(playTimeoutRef.current);
            }

            videoRef.current.play().catch(e => console.error("Video play failed", e));
            
            playTimeoutRef.current = setTimeout(() => {
                if (videoRef.current) {
                    videoRef.current.pause();
                }
            }, videoPlayTime);
        }
    }
    
    return () => {
        if (playTimeoutRef.current) {
            clearTimeout(playTimeoutRef.current);
        }
    };
  }, [lastFrame, sendAction, isVideoDone]);

  const handleActionClick = (action: string) => {
    setSelectedAction(action);
  };

  const handleValueSend = (value: boolean | null) => {
    if (selectedAction) {
        sendAction(selectedAction, value);
    }
  };

  const getActionDef = (actionName: string): ActionDef | undefined => {
    return actionsData.actions.find(a => a.action === actionName) as ActionDef | undefined;
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-black font-mono text-white selection:bg-white selection:text-black">
      
      {isUIHidden && hasInteracted && (
          <div 
              className="absolute inset-0 z-50 cursor-pointer" 
              onClick={() => setIsUIHidden(false)}
          ></div>
      )}

      <video
        ref={videoRef}
        muted
        playsInline
        className={`absolute top-0 left-0 w-full h-full object-cover z-0 transition-all duration-700 ${isUIHidden ? 'opacity-100 grayscale-0' : 'opacity-50 grayscale'}`}
      >
        <source src="/mycelium.mp4" type="video/mp4" />
      </video>

      {!isUIHidden && (
         <div className="absolute inset-0 z-0 bg-[url('/grid.png')] opacity-10 pointer-events-none"></div>
      )}
      {!isUIHidden && (
        <div className="relative z-10 w-full h-full flex flex-col justify-between p-6 animate-in fade-in duration-300">
            
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div className="border border-white/20 bg-black/40 backdrop-blur-md p-4 w-full md:w-auto">
                <h1 className="text-xl font-bold tracking-widest">MYCELIA SOUND</h1>
                <p className="text-xs text-gray-400">AUDIO ENGINE V1.0</p>
            </div>

            <div className="flex flex-col gap-4 items-end w-full md:w-auto">
                <div className="flex flex-wrap md:flex-nowrap items-center gap-4 w-full md:w-auto justify-end">
                    
                    <div className="border border-white/30 bg-white/5 backdrop-blur-sm px-4 py-2 flex items-center gap-4">
                        <button 
                            onClick={() => setIsMuted(!isMuted)}
                            className="hover:text-gray-300 transition-colors"
                        >
                            {isMuted ? (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 9.75 19.5 12m0 0 2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6 4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
                                </svg>
                            ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.114 5.636a9 9 0 0 1 0 12.728M16.463 8.288a5.25 5.25 0 0 1 0 7.424M6.75 8.25l4.72-4.72a.75.75 0 0 1 1.28.53v15.88a.75.75 0 0 1-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.009 9.009 0 0 1 2.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75Z" />
                                </svg>
                            )}
                        </button>
                        
                        <input 
                            type="range" 
                            min="0" 
                            max="1" 
                            step="0.01"
                            value={isMuted ? 0 : volume}
                            onChange={(e) => {
                                setVolume(parseFloat(e.target.value));
                                if (isMuted) setIsMuted(false);
                            }}
                            className="w-24 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-white"
                        />
                    </div>
                    
                    <div className="border border-white/30 bg-white/5 backdrop-blur-sm px-4 py-2 flex items-center gap-3 justify-between">
                        <span className="text-sm font-bold tracking-wider">SERVER:</span>
                        <div className="flex items-center gap-3">
                            <span className={`text-sm font-bold ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
                                {isConnected ? 'ON' : 'OFF'}
                            </span>
                            <div className="flex relative">
                            <span className={`absolute top-0 left-0 -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></span>
                            <span className={`absolute top-0 left-0 -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full animate-ping ${isConnected ? 'shadow-[0_0_10px_rgba(34,197,94,0.8)]' : 'shadow-[0_0_10px_rgba(239,68,68,0.8)]'}`}></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            </header>

            <main className="flex-1 flex items-center justify-center p-4">
                {lastFrame && (
                    <div className="border border-white/40 bg-black/60 backdrop-blur-xl p-4 md:p-8 max-w-2xl w-full">
                        <div className="flex justify-between items-center border-b border-white/20 pb-4 mb-6">
                            <h2 className="text-sm md:text-lg font-bold">LATEST FRAME</h2>
                            <span className="text-xs text-gray-400">{new Date().toLocaleTimeString()}</span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8">
                            <div>
                                <p className="text-xs text-gray-500 mb-1">ACTION</p>
                                <p className="text-lg md:text-2xl font-bold text-white break-words">{lastFrame.action}</p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-500 mb-1">SOURCE</p>
                                <p className="text-sm md:text-xl font-mono text-white/80">{lastFrame.metadata.senderId}</p>
                            </div>
                            <div className="md:col-span-2">
                                <p className="text-xs text-gray-500 mb-1">PAYLOAD VALUE</p>
                                <pre className="text-xs bg-black/50 p-4 border border-white/10 text-green-400 overflow-x-auto">
                                    {JSON.stringify(lastFrame.value, null, 2)}
                                </pre>
                            </div>
                        </div>
                    </div>
                )}
            </main>

            <footer className="flex flex-wrap md:flex-nowrap items-end gap-4 md:gap-12 mt-4 md:mt-8 border-t border-white/10 pt-4 md:pt-6">
                <button className="flex-1 md:flex-none border border-white bg-white text-black px-4 md:px-8 py-2 md:py-3 font-bold text-sm md:text-lg tracking-wider hover:bg-gray-200 transition-colors uppercase cursor-pointer">
                    MONITOR
                </button>
                <button 
                    onClick={() => setIsCommandsOpen(!isCommandsOpen)}
                    className={`flex-1 md:flex-none px-4 py-2 md:py-3 font-bold text-sm md:text-lg tracking-wider transition-colors uppercase cursor-pointer ${isCommandsOpen ? 'text-white border-b-2 border-white' : 'text-gray-500 hover:text-white'}`}
                >
                    CMDS
                </button>
                <button 
                    onClick={() => setIsLogsOpen(!isLogsOpen)}
                    className={`flex-1 md:flex-none px-4 py-2 md:py-3 font-bold text-sm md:text-lg tracking-wider transition-colors uppercase cursor-pointer ${isLogsOpen ? 'text-white border-b-2 border-white' : 'text-gray-500 hover:text-white'}`}
                >
                    LOGS
                </button>
                <button 
                    onClick={() => setIsUIHidden(true)}
                    className="flex-1 md:flex-none text-gray-500 px-4 py-2 md:py-3 font-bold text-sm md:text-lg tracking-wider hover:text-white transition-colors uppercase cursor-pointer whitespace-nowrap"
                >
                    VIDEO ONLY
                </button>
                <div className="hidden md:block flex-1"></div>
                <div className="w-full md:w-auto text-center md:text-right text-[10px] md:text-xs text-gray-600 font-mono">
                    SYSTEM READY
                </div>
            </footer>
        </div>
      )}

      {/* CMDS Drawer */}
      <div 
        className={`fixed bottom-0 left-0 w-full h-[50vh] bg-black/90 backdrop-blur-xl border-t border-white/20 transform transition-transform duration-300 ease-in-out z-40 flex flex-col ${
            isCommandsOpen && !isUIHidden ? 'translate-y-0' : 'translate-y-full'
        }`}
      >
        <div className="flex justify-between items-center p-4 border-b border-white/10 bg-white/5">
            <h2 className="font-bold tracking-widest text-sm">
                COMMANDS {selectedAction ? `> ${selectedAction}` : ''}
            </h2>
            <button onClick={() => { setIsCommandsOpen(false); setSelectedAction(null); }} className="text-gray-400 hover:text-white cursor-pointer px-2">
                CLOSE [X]
            </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 font-mono">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {actionsData.actions.map(action => {
                    const isSelected = selectedAction === action.action;
                    
                    if (isSelected) {
                        return (
                            <div key={action.action} className="border border-white bg-white/10 p-4 flex flex-col gap-4 animate-in zoom-in-95 duration-200">
                                <div className="flex justify-between items-start border-b border-white/20 pb-2">
                                    <span className="text-xs font-bold text-gray-400 break-all">{action.action}</span>
                                    <button 
                                        onClick={(e) => { e.stopPropagation(); setSelectedAction(null); }} 
                                        className="text-white hover:text-gray-300 ml-2"
                                    >
                                        [X]
                                    </button>
                                </div>
                                
                                <div className="flex-1 flex flex-col gap-2 justify-center">
                                    {action.type === 'boolean' ? (
                                        <>
                                            <div className="grid grid-cols-2 gap-2">
                                                <button
                                                    onClick={() => handleValueSend(true)}
                                                    className="bg-green-500/20 text-green-400 border border-green-500/50 p-2 text-sm font-bold hover:bg-green-500 hover:text-black transition-colors"
                                                >
                                                    TRUE
                                                </button>
                                                <button
                                                    onClick={() => handleValueSend(false)}
                                                    className="bg-red-500/20 text-red-400 border border-red-500/50 p-2 text-sm font-bold hover:bg-red-500 hover:text-black transition-colors"
                                                >
                                                    FALSE
                                                </button>
                                            </div>
                                            <button
                                                onClick={() => handleValueSend(null)}
                                                className="w-full bg-gray-500/20 text-gray-400 border border-gray-500/50 p-2 text-sm font-bold hover:bg-white hover:text-black transition-colors"
                                            >
                                                NULL
                                            </button>
                                        </>
                                    ) : (
                                        <button
                                            onClick={() => handleValueSend(null)}
                                            className="w-full h-full min-h-[80px] bg-white text-black border border-white p-2 text-lg font-bold hover:bg-gray-200 transition-colors"
                                        >
                                            TRIGGER
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    }

                    return (
                        <button
                            key={action.action}
                            onClick={() => handleActionClick(action.action)}
                            className="border border-white/30 bg-white/5 p-4 text-sm font-bold hover:bg-white hover:text-black transition-all uppercase min-h-[100px] flex items-center justify-center text-center break-words"
                        >
                            {action.action}
                        </button>
                    );
                })}
            </div>
        </div>
      </div>

      <div 
        className={`fixed bottom-0 left-0 w-full h-[50vh] bg-black/90 backdrop-blur-xl border-t border-white/20 transform transition-transform duration-300 ease-in-out z-40 flex flex-col ${
            isLogsOpen && !isUIHidden ? 'translate-y-0' : 'translate-y-full'
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

      {!hasInteracted && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-md">
          <div className="text-center">
             <h1 className="text-4xl font-bold text-white mb-2 tracking-[0.5em]">MYCELIA</h1>
             <p className="text-gray-400 mb-8 text-sm">AUDIO SYSTEM INTERFACE</p>
             
             <button
                onClick={handleStart}
                className="group relative px-8 py-4 bg-transparent overflow-hidden rounded-none border border-white transition-all hover:bg-white"
             >
                <span className="relative z-10 text-white font-bold tracking-widest group-hover:text-black transition-colors">
                    INITIALIZE SYSTEM
                </span>
             </button>
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
    return (
        <WebSocketProvider url="ws://192.168.10.163:8000/ws">
            <AppContent />
        </WebSocketProvider>
    );
}

export default App;
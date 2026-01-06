import { useState } from 'react';
import { useSocketAudio } from './hooks/useSocketAudio';

function App() {
  const { isConnected, lastFrame, logs, volume, setVolume, isMuted, setIsMuted } = useSocketAudio('ws://mycelia.kibishi47.ovh/ws');
  const [hasInteracted, setHasInteracted] = useState(false);
  const [isLogsOpen, setIsLogsOpen] = useState(false);
  const [isUIHidden, setIsUIHidden] = useState(false);

  const handleStart = () => {
    setHasInteracted(true);
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-black font-mono text-white selection:bg-white selection:text-black">
      
      {/* Click to restore UI when hidden */}
      {isUIHidden && hasInteracted && (
          <div 
              className="absolute inset-0 z-50 cursor-pointer" 
              onClick={() => setIsUIHidden(false)}
          ></div>
      )}

      {/* Background Video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className={`absolute top-0 left-0 w-full h-full object-cover z-0 transition-all duration-700 ${isUIHidden ? 'opacity-100 grayscale-0' : 'opacity-50 grayscale'}`}
      >
        <source src="/background.mp4" type="video/mp4" />
      </video>

      {/* Overlay Pattern - Hidden in fullscreen */}
      {!isUIHidden && (
         <div className="absolute inset-0 z-0 bg-[url('/grid.png')] opacity-10 pointer-events-none"></div>
      )}

      {/* Main UI Container */}
      {!isUIHidden && (
        <div className="relative z-10 w-full h-full flex flex-col justify-between p-6 animate-in fade-in duration-300">
            
            {/* Header */}
            <header className="flex justify-between items-start">
            <div className="border border-white/20 bg-black/40 backdrop-blur-md p-4">
                <h1 className="text-xl font-bold tracking-widest">MYCELIA SOUND</h1>
                <p className="text-xs text-gray-400">AUDIO ENGINE V1.0</p>
            </div>

            <div className="flex flex-col gap-4 items-end">
                <div className="flex items-center gap-4">
                    
                    {/* Audio Controls */}
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

                    <div className="border border-white/30 bg-white/5 backdrop-blur-sm px-4 py-2 flex items-center gap-3">
                        <span className="text-sm font-bold tracking-wider">MODE:</span>
                        <span className="text-sm font-bold">LIVE</span>
                    </div>
                    
                    <div className="border border-white/30 bg-white/5 backdrop-blur-sm px-4 py-2 flex items-center gap-3 min-w-[200px] justify-between">
                        <span className="text-sm font-bold tracking-wider">SERVER:</span>
                        <div className="flex items-center gap-3">
                            <span className={`text-sm font-bold ${isConnected ? 'text-green-500' : 'text-red-500'}`}>
                                {isConnected ? 'CONNECTED' : 'OFFLINE'}
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

            {/* Center Content / Monitor */}
            <main className="flex-1 flex items-center justify-center">
                {lastFrame && (
                    <div className="border border-white/40 bg-black/60 backdrop-blur-xl p-8 max-w-2xl w-full">
                        <div className="flex justify-between items-center border-b border-white/20 pb-4 mb-6">
                            <h2 className="text-lg font-bold">LATEST FRAME RECEIVED</h2>
                            <span className="text-xs text-gray-400">{new Date().toLocaleTimeString()}</span>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-8">
                            <div>
                                <p className="text-xs text-gray-500 mb-1">ACTION</p>
                                <p className="text-2xl font-bold text-white">{lastFrame.action}</p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-500 mb-1">SOURCE</p>
                                <p className="text-xl font-mono text-white/80">{lastFrame.metadata.senderId}</p>
                            </div>
                            <div className="col-span-2">
                                <p className="text-xs text-gray-500 mb-1">PAYLOAD VALUE</p>
                                <pre className="text-xs bg-black/50 p-4 border border-white/10 text-green-400 overflow-x-auto">
                                    {JSON.stringify(lastFrame.value, null, 2)}
                                </pre>
                            </div>
                        </div>
                    </div>
                )}
            </main>

            {/* Footer / Navigation */}
            <footer className="flex items-end gap-12 mt-8 border-t border-white/10 pt-6">
                <button className="border border-white bg-white text-black px-8 py-3 font-bold text-lg tracking-wider hover:bg-gray-200 transition-colors uppercase cursor-pointer">
                    MONITOR
                </button>
                <button 
                    onClick={() => setIsLogsOpen(!isLogsOpen)}
                    className={`px-4 py-3 font-bold text-lg tracking-wider transition-colors uppercase cursor-pointer ${isLogsOpen ? 'text-white border-b-2 border-white' : 'text-gray-500 hover:text-white'}`}
                >
                    LOGS
                </button>
                <button 
                    onClick={() => setIsUIHidden(true)}
                    className="text-gray-500 px-4 py-3 font-bold text-lg tracking-wider hover:text-white transition-colors uppercase cursor-pointer"
                >
                    VIDEO ONLY
                </button>
                <div className="flex-1"></div>
                <div className="text-xs text-gray-600 font-mono">
                    SYSTEM READY
                </div>
            </footer>
        </div>
      )}

      {/* Logs Drawer */}
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
                    {logs.map((log, index) => (
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

export default App;
interface HeaderProps {
    isConnected: boolean;
    isMuted: boolean;
    volume: number;
    setIsMuted: (muted: boolean) => void;
    setVolume: (volume: number) => void;
    isClientsOpen: boolean;
    setIsClientsOpen: (open: boolean) => void;
}

export function Header({ isConnected, isMuted, volume, setIsMuted, setVolume, isClientsOpen, setIsClientsOpen }: HeaderProps) {
    return (
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div className="border border-white/20 bg-black/40 backdrop-blur-md p-4 w-full md:w-auto">
                <h1 className="text-xl font-bold tracking-widest">MYCELIA SOUND</h1>
                <p className="text-xs text-gray-400">AUDIO ENGINE V1.0</p>
            </div>

            <div className="flex flex-col gap-4 items-end w-full md:w-auto">
                <div className="flex flex-wrap md:flex-nowrap items-center gap-4 w-full md:w-auto justify-end">

                    <button
                        onClick={() => setIsClientsOpen(!isClientsOpen)}
                        className={`border border-white/30 backdrop-blur-sm px-4 py-2 flex items-center gap-2 font-bold text-sm tracking-wider hover:bg-white hover:text-black transition-colors ${isClientsOpen ? 'bg-white text-black' : 'bg-white/5 text-white'}`}
                    >
                        CLIENTS
                    </button>
                    
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
    );
}

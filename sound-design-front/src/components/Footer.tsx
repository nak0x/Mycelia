interface FooterProps {
    isCommandsOpen: boolean;
    setIsCommandsOpen: (open: boolean) => void;
    isLogsOpen: boolean;
    setIsLogsOpen: (open: boolean) => void;
    setIsUIHidden: (hidden: boolean) => void;
}

export function Footer({ isCommandsOpen, setIsCommandsOpen, isLogsOpen, setIsLogsOpen, setIsUIHidden }: FooterProps) {
    return (
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
    );
}

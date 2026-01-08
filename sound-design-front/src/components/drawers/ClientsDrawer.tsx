import type { Client } from '../../types/client';

interface ClientsDrawerProps {
    isOpen: boolean;
    setIsClientsOpen: (open: boolean) => void;
    isUIHidden: boolean;
    clients: Client[];
}

export function ClientsDrawer({ isOpen, setIsClientsOpen, isUIHidden, clients }: ClientsDrawerProps) {
    return (
        <div 
            className={`fixed top-0 right-0 w-[300px] h-full bg-black/90 backdrop-blur-xl border-l border-white/20 transform transition-transform duration-300 ease-in-out z-50 flex flex-col ${
                isOpen && !isUIHidden ? 'translate-x-0' : 'translate-x-full'
            }`}
        >
            <div className="flex justify-between items-center p-4 border-b border-white/10 bg-white/5">
                <h2 className="font-bold tracking-widest text-sm">CONNECTED CLIENTS</h2>
                <button onClick={() => setIsClientsOpen(false)} className="text-gray-400 hover:text-white cursor-pointer px-2">
                    CLOSE [X]
                </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 font-mono">
                {clients.length === 0 ? (
                    <div className="text-gray-600 italic p-4 text-center text-xs">No clients detected</div>
                ) : (
                    <div className="flex flex-col gap-2">
                        {clients.map((client, index) => (
                            <div key={index} className="flex justify-between items-center p-3 border border-white/10 bg-white/5">
                                <span className="text-sm font-bold tracking-wider">{client.clientId}</span>
                                <div className={`w-3 h-3 rounded-full ${client.isConnected ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'}`}></div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

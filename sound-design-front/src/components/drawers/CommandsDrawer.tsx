import actionsData from '../../actions.json';

interface CommandsDrawerProps {
    isOpen: boolean;
    setIsCommandsOpen: (open: boolean) => void;
    isUIHidden: boolean;
    selectedAction: string | null;
    setSelectedAction: (action: string | null) => void;
    handleActionClick: (action: string) => void;
    handleValueSend: (value: boolean | null) => void;
}

interface ActionDef {
    action: string;
    type: 'boolean' | null;
}

export function CommandsDrawer({ isOpen, setIsCommandsOpen, isUIHidden, selectedAction, setSelectedAction, handleActionClick, handleValueSend }: CommandsDrawerProps) {
    return (
        <div 
            className={`fixed bottom-0 left-0 w-full h-[50vh] bg-black/90 backdrop-blur-xl border-t border-white/20 transform transition-transform duration-300 ease-in-out z-40 flex flex-col ${
                isOpen && !isUIHidden ? 'translate-y-0' : 'translate-y-full'
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
    );
}

interface StartOverlayProps {
    handleStart: () => void;
}

export function StartOverlay({ handleStart }: StartOverlayProps) {
    return (
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
    );
}

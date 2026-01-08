import type { Frame } from '../types/frame';

interface LatestFrameProps {
    lastFrame: Frame | null;
}

export function LatestFrame({ lastFrame }: LatestFrameProps) {
    if (!lastFrame) return null;
    
    return (
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
    );
}

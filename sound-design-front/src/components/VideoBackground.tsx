import type { RefObject } from 'react';

interface VideoBackgroundProps {
    videoRef: RefObject<HTMLVideoElement>;
    isUIHidden: boolean;
    hasInteracted: boolean;
    onInteract: () => void;
}

export function VideoBackground({ videoRef, isUIHidden, hasInteracted, onInteract }: VideoBackgroundProps) {
    return (
        <>
            {isUIHidden && hasInteracted && (
                <div 
                    className="absolute inset-0 z-50 cursor-pointer" 
                    onClick={onInteract}
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
        </>
    );
}

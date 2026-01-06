export interface FrameMetadata {
  senderId: string;
  timestamp: number;
}

export interface Frame {
  metadata: FrameMetadata;
  action: string; 
  value: string | number | boolean | null;
}
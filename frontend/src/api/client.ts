import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const api = axios.create({ baseURL });

export type GestureStatus = {
  latest?: { label: string; confidence: number; timestamp: string };
  enabled: boolean;
};

export type GestureMapping = {
  gesture: string;
  action: string;
  action_type: 'key' | 'shortcut' | 'macro';
  hold_ms?: number;
};

export type MappingConfig = { mappings: GestureMapping[] };

export async function getGestureStatus() {
  const { data } = await api.get<GestureStatus>('/api/gesture');
  return data;
}

export async function toggleGesture(enabled: boolean) {
  const { data } = await api.post<GestureStatus>('/api/gesture', { enabled });
  return data;
}

export async function getMappings() {
  const { data } = await api.get<MappingConfig>('/api/settings');
  return data;
}

export async function saveMappings(config: MappingConfig) {
  const { data } = await api.post<MappingConfig>('/api/settings', config);
  return data;
}

export async function pressKey(mapping: GestureMapping) {
  await api.post('/api/keyboard/press', mapping);
}

export function connectGestureStream(onMessage: (payload: any) => void) {
  const wsBase = baseURL.replace(/^http/, 'ws');
  const ws = new WebSocket(wsBase + '/ws/gestures');
  ws.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data);
      onMessage(parsed);
    } catch (err) {
      console.error('Failed to parse gesture payload', err);
    }
  };
  return ws;
}

export function isOffline(): boolean {
  return !navigator.onLine;
}

export function setupOfflineListener(callback: (offline: boolean) => void): void {
  window.addEventListener('online', () => callback(false));
  window.addEventListener('offline', () => callback(true));
}

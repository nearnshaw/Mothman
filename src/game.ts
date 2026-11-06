/**
 * Game reset. Every module that holds story state registers a handler; the kill (host.ts, !take) calls resetGame()
 * while the screen is black, so the player wakes up at the gate in a night that has not happened yet.
 */
const handlers: Array<() => void> = []

export function onReset(fn: () => void) { handlers.push(fn) }

export function resetGame() { for (const h of handlers) h() }

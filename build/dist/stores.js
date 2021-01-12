
import { writable, derived } from '../web_modules/svelte/store.js';

export const page = writable("Home")
export const flows = writable([])
export const flow_id = writable()
export const flow = derived([flows, flow_id], ([$flows, $flow_id]) => $flows[$flow_id])


// stores keep inter-component state

import { writable, derived } from '../web_modules/svelte/store.js';

export const page = writable("Home")
export const flows = writable([])
export const flow_id = writable()
export const flow = derived([flows, flow_id], ([$flows, $flow_id]) => $flows[$flow_id])

export const selected_run = writable()
export const selected_step_ix = writable() //TODO: steps are just an array but one day might have DAG structure.
export const selected_step = writable()
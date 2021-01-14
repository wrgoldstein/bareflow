// stores keep inter-component state
import { writable, derived } from 'svelte/store';

// Used by the router to keep track of what page we're on
export const page = writable("Home")

// This contains a full list of all flows, provided by a web socket
export const flows = writable([])

// When we get a flow_id from an API route we need to hydrate it to get the whole flow
export const flow_id = writable()
export const flow = derived([flows, flow_id], ([$flows, $flow_id]) => $flows[$flow_id])

// To keep track of state
export const selected_run = writable()
export const selected_step_ix = writable() //TODO: steps are just an array but one day might have DAG structure.
export const selected_step = writable()

// export const update_flows

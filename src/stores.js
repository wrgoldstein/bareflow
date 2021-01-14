// stores keep inter-component state
import { writable, derived } from 'svelte/store';

// Used by the router to keep track of what page we're on
export const page = writable("Home")

// This contains a full list of all flows, provided by a web socket
// To avoid nesting state, we break out the Flows, Runs, and Steps into
// separate state objects.
export const flows = writable([])
export const flow_runs = writable([])
export const flow_run_steps = writable([])

// When we get a flow_id from an API route we need to hydrate it to get the whole flow.
export const flow_id = writable()
export const flow = derived([flows, flow_id], ([$flows, $flow_id]) => $flows[$flow_id])

// To keep track of state
export const selected_run = writable()
export const selected_step_ix = writable() //TODO: steps are just an array but one day might have DAG structure.
export const selected_step = writable()

function get_store(store) {
  let $val
  store.subscribe($ => $val = $)()
  return $val
}

merge_arrays_on_id = (arr1, arr2) => {
  return Object.values([...arr1, ...arr2].reduce((result, { id, ...rest }) => {
    result[id] = { ...(result[id] || {}), id, ...rest };
    return result;
  }, {}))
}

// These functions make it simpler to update state from elsewhere in the app
export const update_flows = ($flows) => {
  flows.set($flows)
}

export const update_flow_runs = (updated_runs) => {
  $flow_runs = get_store(flow_runs)
  flow_runs.set(merge_arrays_on_id($flow_runs, updated_runs))
}

export const update_flow_run_steps = (updated_run_steps) => {
  $flow_run_steps = get_store(flow_run_steps)
  flow_run_steps.set(merge_arrays_on_id($flow_run_steps, updated_run_steps))
}

// stores keep inter-component state
import { writable, derived } from 'svelte/store';
import _ from "lodash"

// Used by the router to keep track of what page we're on
export const page = writable("Home")

// This contains a full list of all flows, provided by a web socket
// To avoid nesting state, we break out the Flows, Runs, and Steps into
// separate state objects.
export const flows = writable([])
export const flow_run_steps = writable([])

// The flow_id is set by API route and tells us which flow view page the user is
// viewing. This allows us to fetch the appropriate data into a `selection` variable.
export const state = writable({})
export const flow_runs = derived([flow_run_steps], ([$flow_run_steps]) => {
  // no good way to get the flow id in one grouping
  let flow_from_step = {}
  $flow_run_steps.forEach(step => flow_from_step[step.flow_run_id] = step.flow_id)
  let grouped = _.groupBy($flow_run_steps, (step) => step.flow_run_id)
  return Object.keys(grouped).map(id => ({ id: +id, flow_id: flow_from_step[id], flow_run_steps: grouped[id] }))
})

export const derived_state = derived(
  [state, flows, flow_runs, flow_run_steps],
  ([$state, $flows, $flow_runs, $flow_run_steps]) => {
    let _flow_runs = $flow_runs.filter(r => r.flow_id == $state.flow_id)
    let flow_run_ids = _flow_runs.map(r => r.id)
    let flow_run_steps = $flow_run_steps.filter(s => flow_run_ids.includes(s.flow_run_id))
    return {
      flow: $flows[$state.flow_id],
      flow_runs: _flow_runs,
      flow_run_steps: flow_run_steps
    }
  }
)
// These functions make it simpler to update state from elsewhere in the app

// get the value from a writable
function get_store(store) {
  let $val
  store.subscribe($ => $val = $)()
  return $val
}

const merge_arrays_on_id = (arr1, arr2) => {
  let o = Object.values([...arr1, ...arr2].reduce((result, { id, ...rest }) => {
    result[id] = { ...(result[id] || {}), id, ...rest };
    return result;
  }, {}))
  return o
}

export const update_flows = ($flows) => {
  flows.set($flows)
}

export const update_flow_run_steps = (updated_run_steps) => {
  flow_run_steps.update($flow_run_steps => merge_arrays_on_id($flow_run_steps, updated_run_steps))
}

export const update_state = (obj) => {
  state.update($state => Object.assign($state, obj))
}


import { writable, derived } from 'svelte/store';

export const page = writable("Home")
export const dags = writable([])
export const dag_id = writable()
export const dag = derived([dags, dag_id], ([$dags, $dag_id]) => $dags[$dag_id])



import { writable, derived } from '../web_modules/svelte/store.js';

export const page = writable("Home")
export const dags = writable([])
export const dag_id = writable()
export const dag = derived([dags, dag_id], ([$dags, $dag_id]) => $dags[$dag_id])


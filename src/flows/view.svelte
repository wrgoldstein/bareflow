<script>  
  import { state, derived_state, update_state, update_flow_runs, update_flow_run_steps } from "../stores.js";
  import RunButton from "../components/RunButton.svelte"
  import DockerTag from "../components/DockerTag.svelte"
  import K8sTag from "../components/K8sTag.svelte"
  // export let router

  let logs = {}
  let reading_logs_for = new Set()
  let uint8array = new TextDecoder("utf-8");

  let colors = {
    created: 'bg-gray-500',
    started: 'stripe-green',
    succeeded: 'bg-green-500',
    failed: 'bg-red-500',
    queued: 'stripe-yellow'
  }

  const runFlow = async () => {
    // This function is run when the user clicks the big "Run"
    // button for the Flow. It signals that the steps should be
    // scheduled on kubernetes, and the logs subscribed to.
    const res = await fetch(`/run/${$state.flow_id}`, { method: "POST" }).then(r => r.json())
    console.log(res)
    const [{ flow_run_steps, ...flow_run }] = res

    update_flow_runs([flow_run])
    update_flow_run_steps(flow_run_steps)

    const interval = setInterval(() => {
      // sometimes the event containing the run can be 
      // beaten by the response, so we make sure to wait
      // for the run to be in our store before selecting it
      if ($derived_state.flow_runs.map(r => r.id).includes(res.id)) {
          clearInterval(interval)
          select_run(flow_run.id)()
        }
      }, 100
    )
    
    // selected_run.set(runs[runs.length - 1])
    // selected_step_ix.set(0)
    showLogs();
  };

  function select_run(id){
    // This function is called when a run icon is clicked
    // to set the currently selected view (note it returns)
    // a function which can be called with no arguments, which
    // makes on:click directives less verbose.
    return () => {
      update_state({ flow_run_id: id })
    }
  }

  const showLogs = async (pod) => {
    // This function streams the pod logs from the disk
    // to a variable here keyed on the pod (todo)
    if (pod == undefined ) return
    if (reading_logs_for.has(pod)) {
      return
    }
    reading_logs_for.add(pod)
    const response = await fetch(`/api/logs/${pod}`)
    const reader = response.body.getReader()
    while (true){
      const { value, done } = await reader.read();
      logs[pod] += uint8array.decode(value) + "\n"
      if (done) break;
    }
    reading_logs_for.delete(pod)
  };

</script>

{#if $derived_state.flow}
  <!-- header -->
  <div class="lg:flex lg:items-center lg:justify-between pb-4">
    <div class="flex-1 min-w-0">
      <h2
        class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl
        sm:truncate">
        {$state.flow_id}
      </h2>
    </div>
    <div class="mt-5 flex lg:mt-0 lg:ml-4">
      <RunButton {runFlow} />
    </div>
  </div>

  <!-- For historical runs, show a colored badge showing its status -->
  {#if $derived_state.flow_runs.length > 0 }
    <div class="flex mb-4">
      {#each $derived_state.flow_runs as run}
        <div on:click={select_run(run.id)} class="cursor-pointer border rounded m-1 {$state.flow_run_id == run.id ? 'ring-4 ring-inset ring-gray-200' : ''}">
          {#each $derived_state.flow_run_steps.filter(s => s.flow_run_id == run.id) as step}
              <div class="p-1 h-4 w-4 m-1 {colors[step.status]}"></div>
          {/each}
        </div>
      {/each}
    </div>
  {:else}
    <div>No runs to show</div>
  {/if}

  <!-- For each step of the flow run, show more detail -->
  {#if $derived_state.flow_run_steps && $state.flow_run_id}
    Steps:
    <ol class="pt-3 border-t pb-3 border-b">
      {#each $derived_state.flow_run_steps.filter(s => s.flow_run_id == $state.flow_run_id) as step, i}
        <li>
          <div class="grid grid-cols-7 items-center justify-around">
            <div class="text-left ml-2 col-span-1">{step.name}</div>
            <div class="text-center ml-2 col-span-1">
              <DockerTag>{step.image}</DockerTag>
            </div>
            <div class="text-left ml-2 col-span-2">
              <span class="font-mono text-xs whitespace-nowrap">{JSON.stringify(step.command)}</span>
            </div>
            <div class="flex flex-col items-center">
              <span class="text-center text-xs text-white p-1 pl-2 pr-2 ml-2 rounded slow {step.status ? colors[step.status] : colors.created }">
                {step.status || 'created' }
              </span>
            </div>
            <div class="col-span-2 text-center ml-2 text-xs overflow-hidden whitespace-nobreak">
              <K8sTag pod_name={step.pod_name || 'not assigned'} />
            </div>
          </div>
        </li>
      {/each}
    </ol>
  {/if}

  <!-- If we have a selected flow run step and there is log content for it, show the log. -->
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      {#key $derived_state.flow_run_step}
        {#if $derived_state.flow_run_step && $derived_state.flow_run_step.pod_name && logs[$derived_state.flow_run_step.pod_name]}
          <pre class="whitespace-pre-wrap">{logs[$derived_state.flow_run_step.pod_name]}</pre>
        {/if}
      {/key}
    </div>
  </div>
{:else}
  loading
{/if}

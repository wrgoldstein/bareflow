<script>
  import { fade } from "svelte/transition"
  import { flows, flow, flow_id, selected_run, selected_step_ix, selected_step } from "./stores.js";
  import RunButton from "./RunButton.svelte"
  import DockerTag from "./DockerTag.svelte"
  import K8sTag from "./K8sTag.svelte"
  // export let router

  let logs = {}
  let uint8array = new TextDecoder("utf-8");

  let slowColors = {
    // the stripes are too flashy for the bigger status badges
    created: 'bg-gray-500',
    started: 'bg-green-500',
    succeeded: 'bg-green-500',
    failed: 'bg-red-500',
    queued: 'bg-yellow-500'
  }

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
    const res = await fetch(`/run/${$flow_id}`, { method: "POST" }).then(r => r.json())

    const interval = setInterval(() => {
      // sometimes the event containing the run can be 
      // beaten by the response, so we make sure to wait
      // for the run to be in our store before selecting it
      if ($flow.runs.map(r => r.id).includes(res.id)) {
          clearInterval(interval)
          select_run(res.id)()
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
      selected_run.set($flow.runs.find(r => r.id == id))
      selected_step_ix.set(0)
    }
  }

  const showLogs = async (pod) => {
    // This function streams the pod logs from the disk
    // to a variable here keyed on the pod (todo)
    console.log("lookin for ", pod)
    const response = await fetch(`/api/logs/${pod}`)
    const reader = response.body.getReader()
    while (true){
      const { value, done } = await reader.read();
      logs[pod] += uint8array.decode(value) + "\n"
      if (done) break;
    }
  };

  flow.subscribe( (f) => {
    // This sets the "selected run" to the last one if
    // it isn't already set. This allows us to auto focus
    // on page load and when the first run is kicked off.
    if (f == undefined) return
    if ($selected_run != undefined) return
    selected_run.set(f.runs[f.runs.length - 1])
  })

  selected_run.subscribe(async (run) => {
    // if the run has changed, refocus on its first step
    // rather than whatever step of the last run we were
    // looking at
    if (run == undefined) return
    selected_step.set(run.flow_run_steps[0])
  })

  selected_step_ix.subscribe(async (ix) => {
    // sort of annoying but because runs just have steps in an array
    // we need to keep track of the index AND the actual step
    // that has been selected
    if ($selected_run == undefined || $selected_run.flow_run_steps == undefined) return
    selected_step.set($selected_run.flow_run_steps[step])
  })

  selected_step.subscribe(async (step) => {
    // When the selected step changes, make sure we've asked for
    // the logs for that step
    if (step == undefined) return  // the first update is always undefined
    if (step.pod_name == undefined) return // we don't know the pod yet
    if (logs[step.pod_name]) return
    logs[step.pod_name] = ""
    await showLogs(step.pod_name)
  })

  $: runs = $flow && $flow.runs || []
</script>

{#if $flow}
  <!-- header -->
  <div class="lg:flex lg:items-center lg:justify-between pb-4">
    <div class="flex-1 min-w-0">
      <h2
        class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl
        sm:truncate">
        {$flow_id}
      </h2>
    </div>
    <div class="mt-5 flex lg:mt-0 lg:ml-4">
      <RunButton {runFlow} />
    </div>
  </div>

  <!-- run history -->
  {#if $flow.runs.length > 0 }
    <!-- {console.log($flow.runs)} -->
    <div class="flex mb-4">
      {#key $flows}
        {#each $flow.runs as run}
          {#if run.flow_run_steps}
            <div on:click={select_run(run.id)} class="cursor-pointer border rounded m-1 {$selected_run.id == run.id ? 'ring-4 ring-inset ring-gray-200' : ''}">
              {#each run.flow_run_steps as step}
                  <div class="p-1 h-4 w-4 m-1 {colors[step.status]}"></div>
              {/each}
            </div>
          {/if}
        {/each}
      {/key}
    </div>
  {:else}
    <div>No runs to show</div>
  {/if}

  {#if $selected_run && $selected_run.flow_run_steps}
    Steps:
    <ol class="pt-3 border-t pb-3 border-b">
      {#each $selected_run.flow_run_steps as step, i}
        <li>
          <div class="flex items-center justify-around">
            <div class="text-center ml-2">{step.name}</div>
            <div class="text-center ml-2">
              <div class="text-xs uppercase text-gray-500">image:</div>
              <DockerTag>{step.image}</DockerTag>
            </div>
            <div class="text-center ml-2">
              <div class="text-xs uppercase text-gray-500">command:</div>
              {JSON.stringify(step.command)}
            </div>
            <div class="flex flex-col items-center">
              <div class="text-xs uppercase text-gray-500">status:</div>
              <span class="text-center text-xs text-white p-1 pl-2 pr-2 ml-2 rounded bg-opacity-30 {step.status ? slowColors[step.status] : slowColors.created }">
                {step.status || 'created' }
              </span>
            </div>
            <div class="text-center ml-2">
              <div class="text-xs uppercase text-gray-500">pod:</div>
              <K8sTag>{step.pod_name || 'not assigned'}</K8sTag>
            </div>
          </div>
        </li>
      {/each}
    </ol>
  {/if}

  <!-- log output -->
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      {#key $selected_step}
        {#if $selected_step && $selected_step.pod_name && logs[$selected_step.pod_name]}
          <pre class="whitespace-pre-wrap">{logs[$selected_step.pod_name]}</pre>
        {/if}
      {/key}
    </div>
  </div>
{:else}
  loading
{/if}

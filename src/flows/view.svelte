<script>
  import {
    flows,
    state,
    derived_state,
    update_state,
    update_flow_run_steps,
  } from "../stores.js";
  import RunButton from "../components/RunButton.svelte";
  import DockerTag from "../components/DockerTag.svelte";
  import K8sTag from "../components/K8sTag.svelte";
  // export let router

  let flow_run_step;
  let logs = {};
  let reading_logs_for = new Set();
  let uint8array = new TextDecoder("utf-8");

  let colors = {
    created: "bg-gray-500",
    pending: "bg-brown-500",
    starting: "animated-stripe-green",
    running: "animated-stripe-green",
    succeeded: "bg-green-500",
    failed: "bg-red-500",
    skipped: "bg-red-800",
    pending: "animated-stripe-blue",
    queued: "animated-stripe-yellow",
    [undefined]: "animated-stripe-yellow",
  };

  const runFlow = async () => {
    // This function is run when the user clicks the big "Run"
    // button for the Flow. It signals that the steps should be
    // scheduled on kubernetes, and the logs subscribed to.
    const res = await fetch(`/run/${$state.flow_id}`, {
      method: "POST",
    }).then((r) => r.json());

    const flow_run_steps = res;

    update_flow_run_steps(flow_run_steps);

    // TODO: auto focus on the first flow run step of the newly
    // triggered flow

    // const interval = setInterval(() => {
    //   // sometimes the event containing the run can be
    //   // beaten by the response, so we make sure to wait
    //   // for the run to be in our store before selecting it
    //   if ($derived_state.flow_runs.map((r) => r.id).includes(res.id)) {
    //     clearInterval(interval);
    //     select_run(flow_run.id)();
    //   }
    // }, 100);

    // selected_run.set(runs[runs.length - 1])
    // selected_step_ix.set(0)
    // showLogs();
  };

  function select_run(id) {
    // This function is called when a run icon is clicked
    // to set the currently selected view (note it returns)
    // a function which can be called with no arguments, which
    // makes on:click directives less verbose.
    return () => {
      flow_run_step = undefined
      update_state({ flow_run_id: id });
    };
  }

  const showLogs = async (flow_run_step) => {
    // This function streams the pod logs from the disk
    // to a variable here keyed on the pod (todo)
    let pod = flow_run_step.pod_name
    if (pod == undefined) return;
    if (reading_logs_for.has(pod)) {
      return;
    }
    reading_logs_for.add(pod);
    const response = await fetch(`/api/logs/${pod}`);
    const reader = response.body.getReader();
    logs[pod] = ''
    while (true) {
      const { value, done } = await reader.read();
      logs[pod] += uint8array.decode(value) + "\n";
      if (done) break;
    }
    reading_logs_for.delete(pod);
  };

  const viewDetails = (step_id) => {
    // This will be how we select which pod to look at.
    return () => {
      flow_run_step = $derived_state.flow_run_steps.find(s => s.id == step_id)
      if (flow_run_step && flow_run_step.pod_name){
        if (logs[flow_run_step.pod_name] == undefined){
          showLogs(flow_run_step)
        }
      }
    };
  };
  const showState = () => {
    console.log($derived_state)
  }
</script>
<!-- <button on:click={showState}>show state</button> -->
{#if $derived_state.flow}
  <!-- header -->
  <div class="lg:flex lg:items-center lg:justify-between pb-4">
    <div class="flex-1 min-w-0">
      <h2
        class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl
        sm:truncate"
      >
        {$state.flow_id}
      </h2>
    </div>
    <div class="mt-5 flex lg:mt-0 lg:ml-4">
      <RunButton {runFlow} />
    </div>
  </div>

  <!-- For each step of the flow run, show more detail -->
  {#if $derived_state.flow}
    <div class="flex flex-col">
      <div class="grid grid-cols-4 items-center text-xs uppercase">
        <div class="pl-8 mr-8">Step name</div>
        <div>Image</div>
        <div>Depends on</div>
      </div>
      {#each $derived_state.flow.steps as step}
        <div class="grid grid-cols-4 items-center">
          <div class="text-left ml-2 mr-8 pl-8 ">{step.name}</div>
          <div class="">
            <DockerTag>{step.image}</DockerTag>
          </div>
          <div class="font-mono text-xs whitespace-nowrap">
            {JSON.stringify(step.depends_on)}
          </div>
        </div>
      {/each}
    </div>
  {/if}

  <!-- For historical runs, show a colored badge showing its status -->
  {#if $derived_state.flow_runs.length > 0 }
    <div class="block mb-4">
      <div class="block m-2 mt-6">Run history</div>
      <div class="flex">
        {#each $derived_state.flow_runs as run}
          <div on:click={select_run(run.id)} class="cursor-pointer border rounded m-1 {$state.flow_run_id == run.id ? 'ring-4 ring-inset ring-gray-200' : ''}">
            {#each $derived_state.flow_run_steps.filter(s => s.flow_run_id == run.id) as step}
                <div class="p-1 h-4 w-4 m-1 {colors[step.status]}"></div>
            {/each}
          </div>
        {/each}
      </div>
    </div>
  {/if}

  {#if $derived_state.flow_run_steps && $state.flow_run_id}
    <ol class="pt-3 border-t pb-3 border-b">
      {#each $derived_state.flow_run_steps.filter(s => s.flow_run_id == $state.flow_run_id) as step, i}
        <li>
          <div class="flex items-center">
            <div class="flex flex-col items-center">
              <span class="w-36 text-center text-xs text-white p-1 pl-2 pr-2 ml-2 rounded slow {colors[step.status] }">
                {step.status || 'pending' }
              </span>
            </div>
            <div class=" text-center ml-2 text-xs overflow-hidden whitespace-nobreak">
              <K8sTag pod_name={step.pod_name || 'not assigned'} />
            </div>
            <button on:click={viewDetails(step.id)} class="
              cursor-pointer border focus:outline-none pl-2 pr-2 rounded pt-2 pb-2 text-center ml-2 text-xs overflow-hidden whitespace-nobreak">
              view log
            </button>
          </div>
        </li>
      {/each}
    </ol>
  {/if}
  <!-- If we have a selected flow run step and there is log content for it, show the log. -->
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      {#key flow_run_step}
        {#if flow_run_step && flow_run_step.pod_name}
          {#if logs[flow_run_step.pod_name] }
            <pre class="whitespace-pre-wrap">
              {logs[flow_run_step.pod_name]}
            </pre>
          {/if}
        {/if}
      {/key}
    </div>
  </div>
{:else}
  loading
{/if}

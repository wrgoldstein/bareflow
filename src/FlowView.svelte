<script>
  import { flow, flow_id } from "./stores.js";
  import RunButton from "./RunButton.svelte"
  // export let router

  let pod;
  let logs = "";
  let uint8array = new TextDecoder("utf-8");

  const runFlow = async () => {
    // todo have some sort of ui state that shows its running
    const res = await fetch(`/run/${$flow_id}`, { method: "POST" });
    // to get to a POC just storing the current pod run after a triggered run
    // no history yet
    showLogs();
  };

  const view = () => {};

  const showLogs = async () => {
    logs = "";
    // const response = await fetch(`/api/logs/${pod}`)
    // const reader = response.body.getReader()
    // while (true){
    //   const { value, done } = await reader.read();
    //   logs += uint8array.decode(value) + "\n"
    //   if (done) break;
    // }
  };
</script>

{#if $flow}
  <!-- header -->
  <div class="lg:flex lg:items-center lg:justify-between">
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
  <div>
    
  </div>

  <!-- log output -->
  <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
    <div class="px-4 py-6 sm:px-0">
      <div class="flex mb-4">
        <span class="sm:ml-3">
          {#if pod}
            Running on pod
            <span class="p-1 rounded bg-blue-200">{pod}</span>
          {/if}
        </span>
      </div>
      <pre class="whitespace-pre-wrap">{logs}</pre>
    </div>
  </div>
{:else}loading{/if}

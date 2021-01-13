<script>
  export let runs
  console.log(runs)
  $: max_run_duration = Math.max(...runs.map(r => +r.duration))

  let colors = {
    succeeded: 'green',
    failed: 'red',
    pending: 'yellow'
  }

  function toTimeString(seconds) {
    return (new Date(seconds * 1000)).toUTCString().match(/(\d\d:\d\d:\d\d)/)[0];
  }
</script>

<div class="flex items-end border-b border-t m-4">
  <div class="flex flex-col justify-between" style="height: 5em; width: 2em">
    <span class="text-gray-200">{toTimeString(max_run_duration)}</span>
    <span class="text-gray-200">{toTimeString(0)}</span>
  </div>
  {#each runs as run}
    {#if run.status}
      <div class="p-2 w-4 m-1" style="height: {run.duration}em; background-color: {colors[run.status]};"></div>
    {:else}
    <div class="p-2 w-4 m-1" style="height: {run.duration}em; background-color: {colors['pending']};"></div>
    {/if}
  {/each}
</div>


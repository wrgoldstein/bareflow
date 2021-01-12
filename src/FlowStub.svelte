<script>
  export let flow, router
  const [ flow_id, steps ] = flow
</script>

<tr>
  <td class="px-6 py-4 whitespace-nowrap">
    <div class="flex items-center">
      <div class="ml-4">
        <div class="text-sm font-medium text-gray-900">
          {flow_id}
        </div>
        <div class="text-sm text-gray-500">
          
        </div>
      </div>
    </div>
  </td>
  <td class="px-6 py-4 whitespace-nowrap">
    <div class="text-sm text-gray-900">schedule will go here</div>
    <div class="text-sm text-gray-500">human readable schedule</div>
  </td>
  <td class="px-6 py-4 whitespace-nowrap">
    <!-- placeholder -->
    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
      Active
    </span>
  </td>
  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
    <!-- placeholder -->
    {#each [1,2,3,4,5] as i}
      {Math.random() > .4 ? '🍏' : '🍎'}
    {/each} 
  </td>
  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
    <a on:click={() => router.route(`/flows/${flow_id}`, true)} class="text-indigo-600 hover:text-indigo-900">View</a>
  </td>
</tr>

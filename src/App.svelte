<script>
  
  import { onMount } from "svelte"

  import FlowIndex from "./flows/index.svelte"
  import FlowView from "./flows/view.svelte"

  import { flows, page, flow_id, selected_run } from "./stores.js"
  import { socket } from "./sockets.js"
  import { router } from "./routes.js"

</script>

<header class="h-full bg-blue-800 h-6" />
<div>
  <!--  -->
  <nav>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-b">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <div class="flex-shrink-0">
          </div>
          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <a href="#" on:click={() => router.route("/", true)} class=" px-3 py-2 rounded-md text-sm">Flows</a>
          </div>
        </div>
      </div>
    </div>
  </nav>
  <main>
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
          {#if $page == 'home'}
            <FlowIndex {router} />
          {:else if $page == 'view_flow'}
            <FlowView {router} />
          {:else}
            <div>404 Not found</div>
          {/if}
      </div>
    </div>
  </main>
</div>

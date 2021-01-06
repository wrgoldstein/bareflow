<script>
  import navaid from "navaid"
  import { onMount } from "svelte"
  import Dags from "./ListDags.svelte"
  import Dag from "./ViewDag.svelte"
  import { dags, page, dag_id } from "./stores.js"

  let sid
  let router = navaid()

  onMount(() => {
    router
      .on("/", () => {
        page.set("home")
      })
      .on("/dags/:dag_id", params => {
        page.set("view_dag")
        dag_id.set(params.dag_id)
        console.log($page, $dag_id)
      })

    router.listen()
    const socket = new WebSocket(
      `${import.meta.env.SNOWPACK_PUBLIC_SOCKET_URL}/ws`
    )

    socket.addEventListener("open", function(event) {
      console.log("connected")
    })

    socket.addEventListener("message", event => {
      const message = JSON.parse(event.data)
      switch (message.type) {
        case "sid":
          sid = message.sid
          break
        case "dags":
          dags.set(message.dags)
          break
        case "update":
          console.log(message)
          break
      }
    })
  })
</script>

<header class="h-full bg-blue-400 h-6" />
<div>
  <nav class="bg-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <img class="h-8 w-8" src="https://tailwindui.com/img/logos/workflow-mark-indigo-500.svg" alt="Workflow">
          </div>
          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <!-- Current: "bg-gray-900 text-white", Default: "text-gray-300 hover:bg-gray-700 hover:text-white" -->
              <a href="#" on:click={() => router.route("/", true)} class="bg-gray-900 text-white px-3 py-2 rounded-md text-sm font-medium">Dags</a>

              <a href="#" class="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Placeholder</a>

              <a href="#" class="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Placeholder</a>

              <a href="#" class="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Placeholder</a>

              <a href="#" class="text-gray-300 hover:bg-gray-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Placeholder</a>
          </div>
        </div>
      </div>
    </div>
  </nav>
  <main>
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
          {#if $page == 'home'}
            <Dags {router} />
          {:else if $page == 'view_dag'}
            <Dag {router} />
          {:else}
            <div>404 Not found</div>
          {/if}
      </div>
    </div>
  </main>
</div>

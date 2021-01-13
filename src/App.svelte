<script>
  import navaid from "navaid"
  import { onMount } from "svelte"
  import FlowIndex from "./FlowIndex.svelte"
  import FlowView from "./FlowView.svelte"

  import { flows, page, flow_id } from "./stores.js"

  let sid
  let router = navaid()

  function updateFlow(_flow_id, body){
    if (!(_flow_id in $flows)){
      console.log("tried to update non existing flow", _flow_id)
      return
    }
    let temp = $flows[_flow_id]
    temp = {...temp, ...body}  
    flows.update(self => {
      self[_flow_id] = temp
      return self
    })
  }

  function updateFlowRun(flow_id_, run_id, body){
    console.log("updatin'")
    let flow = $flows[flow_id_]
    console.log("found flow", flow)
    if (!("runs" in flow)){
      return
    }
    console.log("continuing")
    let new_runs
    if (run_id in flow.runs.map(r => r.flow_run_id)){
      new_runs = flow.runs.map(r => 
        r.flow_run_id == run_id ? { ...r, ...body } : r
      )
    } else {
      new_runs = flow.runs
      new_runs.push(body)
    }
    flow.runs = new_runs
    flows.update(self => {
      self[flow_id_] = flow
      return self
    })
    console.log($flows)
  }

  onMount(async () => {
    setInterval( () => console.log($flows), 5000)
    router
      .on("/", () => {
        page.set("home")
      })
      .on("/flows/:flow_id", params => {
        page.set("view_flow")
        flow_id.set(params.flow_id)
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
      console.log(message)
      switch (message.type) {
        case "flows":
          flows.set(message.flows)
          break

        case "event":
          if ("flow_run" in message){
            let flow_run = message.flow_run
            updateFlowRun(flow_run.flow_id, flow_run.id, flow_run)
          }
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
              <a href="#" on:click={() => router.route("/", true)} class="bg-gray-900 text-white px-3 py-2 rounded-md text-sm font-medium">Flows</a>

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

<script>
  import navaid from "navaid"
  import { onMount } from "svelte"
  import FlowIndex from "./FlowIndex.svelte"
  import FlowView from "./FlowView.svelte"

  import { flows, page, flow_id, selected_run } from "./stores.js"

  let sid
  let router = navaid()


  function updateFlow(_flow_id, body){
    // update a flow, by id
    if (!(_flow_id in $flows)){
      console.log("tried to update non existing flow", _flow_id)
      return
    }
    let copied = Object.assign({}, $flows[_flow_id], body)
    flows.set(copied)
  }

  function updateFlowRun(flow_id_, run_id, body){
    // update a flow run, by flow id and run id
    let flow = $flows[flow_id_]
    let i = flow.runs.findIndex(x => x.id == run_id)
    if (i == -1){
      flow.runs = [...flow.runs, body]
    } else {
      flow.runs[i] = {...flow.runs[i], ...body}
    }
    let copied = Object.assign($flows, { [flow_id_]: flow})
    flows.set(copied)
  }

  function updateFlowRunStep(flow_id_, run_id, step_id, body){
    // update a flow run step, using all three ids
    let flow = $flows[flow_id_]
    let i = flow.runs.findIndex(x => x.id == run_id)
    if (i == -1){
      console.log("tried to update a step belonging to an unknown run")
      return
    }
    
    let ii = flow.runs[i].flow_run_steps.findIndex(x => x.id == step_id)
    flow.runs[i].flow_run_steps[ii] = {...flow.runs[i].flow_run_steps[ii], ...body}
    let copied = Object.assign($flows, { [flow_id_]: flow})
    flows.set(copied)
  }

  onMount(async () => {
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
          else if ("flow_run_step" in message) {
            let flow_run_step = message.flow_run_step
            let flow_run = message.flow_run_step.flow_run
            selected_run.set($selected_run)
            updateFlowRunStep(flow_run.flow_id, flow_run.id, flow_run_step.id, flow_run_step)
          }
      }
    })
  })
</script>

<header class="h-full bg-blue-800 h-6" />
<div>
  <nav class="bg-gray-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <div class="flex-shrink-0">
          </div>
          <div class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <a href="#" on:click={() => router.route("/", true)} class="text-white px-3 py-2 rounded-md text-sm font-bold">Flows</a>
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

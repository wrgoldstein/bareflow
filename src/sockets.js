import { flows, selected_run } from "./stores.js"


function updateFlow(_flow_id, update){
  // update a flow, by id
  flows.set(Object.assign({}, $flows[_flow_id], update))
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

export const socket = new WebSocket(
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
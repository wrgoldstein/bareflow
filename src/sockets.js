import {
  update_flows,
  update_flow_run_steps,
} from "./stores.js";

export const socket = new WebSocket(
  `${import.meta.env.SNOWPACK_PUBLIC_SOCKET_URL}/ws`
);

socket.addEventListener("open", function () {
  console.log("connected");
});

socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  console.log(message);
  switch (message.type) {
    case "initialize":
      update_flows(message.flows);
      update_flow_run_steps(message.flow_run_steps);
      break;

    case "event":
      console.log("yes")
      update_flow_run_steps([message.event])
  }
});

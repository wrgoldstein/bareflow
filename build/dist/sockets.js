import __SNOWPACK_ENV__ from '../__snowpack__/env.js';
import.meta.env = __SNOWPACK_ENV__;


export default setup = () => {
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
      case "flows":
        flows.set(message.flows)
        break
      case "stats":
  
        // assign the initial stats to their flows
        for (let _flow_id in message.stats){
          if (_flow_id in $flows){
            let temp = $flows[_flow_id]
            temp["runs"] = message.stats[_flow_id]
            flows.update(self => {
              self[_flow_id] = temp
              return self
            })
          }
        }
  
      case "event":
        console.log(message)
        break
    }
  })
  return socket  
}

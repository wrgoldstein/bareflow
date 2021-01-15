import navaid from "navaid"
import { update_state, page } from "./stores.js"

export let router = navaid()

router
  .on("/", () => {
    page.set("home")
  })
  .on("/flows/:flow_id", params => {
    page.set("view_flow")
    update_state({flow_id: params.flow_id})
  })

router.listen()

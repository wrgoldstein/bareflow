import navaid from "../web_modules/navaid.js"
import { flow_id, page } from "./stores.js"

export let router = navaid()

router
  .on("/", () => {
    page.set("home")
  })
  .on("/flows/:flow_id", params => {
    page.set("view_flow")
    flow_id.set(params.flow_id)
  })

router.listen()

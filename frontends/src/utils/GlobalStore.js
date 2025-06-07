
import { reactive } from "vue";

const globalStore = reactive({
    UserSchedules : [],
    UserName : "dev",
})

export default globalStore;
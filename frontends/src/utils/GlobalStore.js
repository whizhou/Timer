
import { reactive } from "vue";

const globalStore = reactive({
    UserSchedules : [],
    UserName : "dev",
    UserID : -1,
})

export default globalStore;
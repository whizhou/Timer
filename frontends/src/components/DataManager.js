
import axios from "axios"

const serverURL = 'http://127.0.0.1:5000/schedule'

var UserSchedules = [];

function GetDataFromServer (user_id=1) {
    axios({
        methods : 'GET',
        url : serverURL,
    }).then((res)=>{
        UserSchedules = res.data.schedules;
        console.log("Get Schedules!");
    })
}

function PostDataToServer (user_id=1) {
    axios({
        methods : 'POST',
        url : serverURL,
        params : {
            id : user_id
        }
    })
}

function ModifySchedules (newSchedules) {
    UserSchedules = newSchedules;
}

function Schedules () { return UserSchedules }

export {
    GetDataFromServer,
    PostDataToServer,
    ModifySchedules,
    Schedules,
}
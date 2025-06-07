
import axios from "axios"

const serverURL = 'http://127.0.0.1:5000/schedule/'

var UserSchedules = [];

// import { PGAddCard,PGDelCard } from "../views/HomeView.vue";

function AddSchedule (data) {
    let len = 1
    if (UserSchedules.length>0)
        len = UserSchedules[UserSchedules.length-1].id+1
    data.id = len;
    UserSchedules.push(data)
    // PGAddCard(data);
    // console.log(UserSchedules)
    console.log(data)
}

function DeleteSchedule (id) {
    let index = 0; console.log(id);
    while (index<UserSchedules.length && UserSchedules[index].id!=id) index+=1;
    if (index<UserSchedules.length) {
        UserSchedules.splice(index,1);
        // PGDelCard(index);
    } else console.log("Error When Deleting");
}

function GetDataFromServer (user_id=1) {
    axios({
        method : 'get',
        url : serverURL,
    }).then((res)=>{
        UserSchedules = res.data.schedules;
        // console.log("Get Schedules!");
        // console.log(UserSchedules);
    })
}

function PostDataToServer (user_id=1) {
    axios({
        method : 'post',
        url : serverURL,
        data : {
            auth : "dev",
            schedules : UserSchedules,
        }
    }).then((res)=>{
        UserSchedules = res.data.schedules;
        // console.log("Get Schedules!");
        // console.log(UserSchedules);
    })
}

// function ModifySchedules (newSchedules) {
//     UserSchedules = newSchedules;
// }

// function Schedules () { return UserSchedules }

export {
    AddSchedule,
    DeleteSchedule,
    GetDataFromServer,
    PostDataToServer,
    // ModifySchedules,
    UserSchedules
    // Schedules,
}
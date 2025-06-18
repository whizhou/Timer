
import axios from "axios"
import globalStore from "./GlobalStore"

const serverURL = 'http://127.0.0.1:5000/';

function AddSchedule (data) {
    let max = 1;
    if (globalStore.UserSchedules.length>0) {
        for (schedule in globalStore.UserSchedules)
            if (schedule.id>max) max=schedule.id
        max = max+1;
    }
    if (data.type==undefined)
        data.type = (data.content.begin_time==undefined || data.content.begin_time=="")?"reminder":"schedule";
    data.id = max;
    data.status = false;
    globalStore.UserSchedules.push(data);
    let retValue = data;
    let resopnse = PostDataToServer(serverURL+"schedule/",{schedules:[data]});
    return retValue;
    // console.log(resopnse);
}

function DeleteSchedule (id) {
    console.log(id);
    console.log(globalStore.UserSchedules);
    let index = 0;
    while (index<globalStore.UserSchedules.length && globalStore.UserSchedules[index].id!=id) index+=1;
    if (index<globalStore.UserSchedules.length) {
        globalStore.UserSchedules.splice(index,1);
        DeleteFromServer(serverURL+"schedule/"+String(id));
    } else console.log("Error When Deleting");
    console.log("11",globalStore.UserSchedules);
}

function GetSchedule (id) {
    let index = 0;
    while (index<globalStore.UserSchedules.length && globalStore.UserSchedules[index].id!=id) index+=1;
    if (index<globalStore.UserSchedules.length) {
        return globalStore.UserSchedules[index];
    } else return {};
}

function GetScheduleIndex (id) {
    let index = 0;
    while (index<globalStore.UserSchedules.length && globalStore.UserSchedules[index].id!=id) index+=1;
    if (index<globalStore.UserSchedules.length) {
        return index;
    } else return -1;
}

function GetDataFromServer (TargetURL) {
    axios({
        method : 'get',
        url : TargetURL,
    }).then((res)=>{
        return res;
    }).catch(()=>{
        console.log(TargetURL);
        return undefined;
    })
}

function PostDataToServer (TargetURL,DATA) {
    axios({
        method : 'post',
        url : TargetURL,
        data : DATA
    }).then((res)=>{
        return res;
    }).catch(()=>{
        return undefined;
    })
}

function DeleteFromServer (TargetURL) {
    axios({
        method : 'delete',
        url : TargetURL
    }).then((res)=>{
        return res;
    })
}

function SyncFromServer () {
    axios({
        method : 'get',
        url : serverURL+"schedule/",
    }).then((res)=>{
        globalStore.UserSchedules = res.data.schedules;
        console.log(globalStore.UserSchedules);
    }).catch(()=>{
        console.log("server error");
    })
}

export {
    AddSchedule,
    DeleteSchedule,
    GetSchedule,
    GetScheduleIndex,
    GetDataFromServer,
    PostDataToServer,
    DeleteFromServer,
    SyncFromServer,
    serverURL,
}
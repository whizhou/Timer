
import axios from "axios"
import globalStore from "./GlobalStore"

const serverURL = 'https://whizhou.pythonanywhere.com/';

async function AddSchedule(data) {
    if (data.finished == undefined)
        data.finished = false;
    if (data.archive == undefined)
        data.archive = false;
    const maxId = globalStore.UserSchedules.reduce((max, item) => 
        Math.max(max, item.id), 0);
    const newId = maxId + 1;
    if (data.type === undefined) {
        data.type = (data.content.begin_time === undefined || data.content.begin_time === "") ? 
            "reminder" : "schedule";
    }
    const newSchedule = {
        ...data,
        id: newId,
        status: false
    };
    globalStore.UserSchedules.push(newSchedule);
    try {
        await PostDataToServer(serverURL + "schedule/", { schedules: [newSchedule] });
        return newSchedule;
    } catch (error) {
        const index = globalStore.UserSchedules.findIndex(s => s.id === newId);
        if (index !== -1) {
            globalStore.UserSchedules.splice(index, 1);
        }
        throw new Error("添加日程到服务器失败: " + error.message);
    }
}

async function DeleteSchedule(id) {
    const index = globalStore.UserSchedules.findIndex(item => item.id === id);
    if (index === -1) {
        throw new Error("未找到要删除的日程");
    }
    const deletedItem = globalStore.UserSchedules[index];
    globalStore.UserSchedules.splice(index, 1);
    try {
        await DeleteFromServer(serverURL + "schedule/" + String(id));
    } catch (error) {
        globalStore.UserSchedules.splice(index, 0, deletedItem);
        throw new Error("从服务器删除日程失败: " + error.message);
    }
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
    return axios({
        method : 'get',
        url : TargetURL,
        // data : { user_id : globalStore.UserID },
        params : { user_id : globalStore.UserID },
        // withCredentials : true,
    }).then((res)=>{
        return res;
    }).catch(()=>{
        // console.log(TargetURL);
        return undefined;
    })
}

function PostDataToServer (TargetURL,DATA) {
    // console.log(globalStore.UserID);
    return axios({
        method : 'post',
        url : TargetURL,
        data : DATA,
        params : { user_id : globalStore.UserID },
        withCredentials : true,
    }).then((res)=>{
        return res;
    }).catch(()=>{
        return undefined;
    })
}

function PutDataToServer (TargetURL,DATA) {
    return axios({
        method : 'put',
        url : TargetURL,
        data : { schedule : DATA },
        params : { user_id : globalStore.UserID },
        withCredentials : true,
    }).then((res)=>{
        return res;
    }).catch(()=>{
        return undefined;
    })
}

function DeleteFromServer (TargetURL) {
    return axios({
        method : 'delete',
        url : TargetURL,
        // data : { user_id : globalStore.UserID },
        params : { user_id : globalStore.UserID },
        withCredentials : true,
    }).then((res)=>{
        return res;
    })
}

function SyncFromServer() {
  return axios({
    method: 'get',
    url: serverURL + "schedule/",
    // data : { user_id : globalStore.UserID },
    params : { user_id : globalStore.UserID },
    withCredentials : true,
  }).then((res) => {
    globalStore.UserSchedules = res.data.schedules;
    // console.log(globalStore.UserSchedules);
  }).catch((error) => {
    // console.log("server error");
    throw error; 
  });
}
 
// function ModifyServerURL (URL){
//     serverURL=URL;
//     return;
// }

export {
    AddSchedule,
    DeleteSchedule,
    GetSchedule,
    GetScheduleIndex,
    GetDataFromServer,
    PostDataToServer,
    PutDataToServer,
    DeleteFromServer,
    SyncFromServer,
    serverURL,
    // ModifyServerURL,
}

import axios from "axios"
import globalStore from "./GlobalStore"

const serverURL = 'http://127.0.0.1:5000/';

async function AddSchedule(data) {
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
    }).then((res)=>{
        return res;
    }).catch(()=>{
        console.log(TargetURL);
        return undefined;
    })
}

function PostDataToServer (TargetURL,DATA) {
    return axios({
        method : 'post',
        url : TargetURL,
        data : DATA
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
        data : { schedule : DATA }
    }).then((res)=>{
        return res;
    }).catch(()=>{
        return undefined;
    })
}

function DeleteFromServer (TargetURL) {
    return axios({
        method : 'delete',
        url : TargetURL
    }).then((res)=>{
        return res;
    })
}

function SyncFromServer() {
  return axios({
    method: 'get',
    url: serverURL + "schedule/",
  }).then((res) => {
    globalStore.UserSchedules = res.data.schedules;
    console.log(globalStore.UserSchedules);
  }).catch((error) => {
    console.log("server error");
    throw error; 
  });
}

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
}
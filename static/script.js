import { initMap} from './map.js';
import { deleteData,addTestData,switchDvEnv,loadGoogleMapsScript,renderGeminiText, allEvents } from './api.js';
import { updateHeatmapAndChart,applyFilter} from './api.js';


const deleteBtn = document.getElementById("deleteButton");
deleteBtn.addEventListener("click", () => {
    console.log("デリートボタンが押された");
    deleteData();
});

const addBtn = document.getElementById("testButton");
addBtn.addEventListener("click", () => {
    console.log("テストボタンが押された");
    addTestData();
});

document.querySelectorAll('input[name="db_env"]').forEach(radio => {
    radio.addEventListener("change", (event) => {
        const value = event.target.value;
        console.log("選択された値:", value)
        switchDvEnv(value);
    });
});

document.getElementById("vehicleSelect").addEventListener("change", (e) => {
    updateHeatmapAndChart(e.target.value);
});



document.getElementById("filterButton").addEventListener("click", () => {
    applyFilter();
});


loadGoogleMapsScript().then(() => {
    window.initMap = initMap;
    initMap();    
})
.catch(error => {
    console.error("Failed to load Google Maps script:", error);
});






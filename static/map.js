import { fetchEvents } from "./api.js";

export let map;
export let heatmap;

export async function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 16,
        center: { lat: 34.702485, lng: 135.495951 },
    });

    heatmap = new google.maps.visualization.HeatmapLayer({
        data: [],
        map: map
    });
    await fetchEvents();
    // await console.log(getGeminiText(allEvents));
}




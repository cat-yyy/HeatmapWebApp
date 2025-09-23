import { heatmap } from "./map.js";
import { processEvents} from "./chart.js"

export let allEvents = [];

// /api/aiへのポストリクエスト、結果をJSONで返す
export async function getGeminiResponse(data) {
    const url = `/api/ai`;
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data) //文字列に変換
        });
        const jsonData = await response.json();
        console.log(data);
        return jsonData;

    } catch (err) {
        console.error("/api/aiへのリクエスト失敗", err);
    }

}

// Geminiからのレスポンスをtextで描画する
export async function renderGeminiText(data){
    const response= await getGeminiResponse(data);
    // JSONを文字列化して見やすく整形
    const text = JSON.stringify(response, null, 2);
    //ai IDのテキストを更新
    document.getElementById("ai").textContent=text;
}

export function addTestData() {
    const url = `/add_test_data`;
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error("テストデータ追加失敗")
            }
            console.log("テストデータ追加成功");
            return fetchEvents();
        })
        .catch(error => {
            console.error("エラー:", error);
        });
}

//DB環境切り替え
export function switchDvEnv(env) {
    const url = `/switch_db_env?db_env=${env}`;
    console.log("switch_db_envリクエスト送信");
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error("db_env切り替え失敗");
            }
            console.log("db_env切り替え成功");
            return fetchEvents();
        })
        .catch(error => {
            console.error("エラー:", error);
        });
}

//期間を指定してイベントを取得する
export async function fetchEvents(start = null, end = null) {
    let url = "/get_events";
    if (start && end) {
        url += `?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;
    }
    const res = await fetch(url);
    const data = await res.json();
    allEvents = data;
    updateDropdown(data);
    updateHeatmapAndChart(document.getElementById("vehicleSelect").value);
    renderGeminiText(allEvents);
}

export function deleteData() {
    const url = `/delete_events`;
    fetch(url, { method: "DELETE" })
        .then(response => {
            if (!response.ok) {
                throw new Error("データ削除失敗");
            }
            console.log("データ削除成功");
            return fetchEvents();
        })
        .catch(error => {
            console.error("エラー:", error);
        });
}

export function loadGoogleMapsScript() {
    return new Promise((resolve, reject) => {
        const scriptUrl = "/api/get_maps_data?language=ja";
        const script = document.createElement("script");
        script.src = scriptUrl;
        script.async = true;
        script.defer = true;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

//ドロップダウンメニューの項目更新
export function updateDropdown(data) {
    const select = document.getElementById("vehicleSelect");
    const names = [...new Set(data.map(e => e.name))];
    select.innerHTML = "<option value='All'>All</option>";
    names.forEach(name => {
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        select.appendChild(opt);
    });
}

//ヒートマップとチャートの更新
export function updateHeatmapAndChart(vehicleType) {
    let filtered = allEvents;
    if (vehicleType !== "All") {
        filtered = allEvents.filter(e => e.name === vehicleType);
    }
    updateHeatmap(filtered);
    processEvents(filtered);
}

//マップにフィルターを適用する
export function applyFilter() {
    const start = document.getElementById("start").value;
    const end = document.getElementById("end").value;
    fetchEvents(start, end);
}

export function updateHeatmap(filtered) {
    if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
        console.error("Google Maps API is not loaded yet.");
        return;
    }
    if (filtered.length === 0) {
        heatmap.setData([]);
        return;
    }
    const heatmapData = filtered.map(e =>
        new google.maps.LatLng(e.location.lat, e.location.lon)
    );
    heatmap.setData(heatmapData);
}
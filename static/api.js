import { heatmap } from "./map.js";
import { processEvents } from "./chart.js";

export let allEvents = [];

/* ---------- 共通ローディング制御 ---------- */
export function showLoading(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add("active");
}

export function hideLoading(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove("active");
}

/* ---------- Gemini API ---------- */
// /api/aiへのポストリクエスト、結果をJSONで返す
export async function getGeminiResponse(data) {
    const url = `/api/ai`;
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        const jsonData = await response.json();
        console.log(data);
        return jsonData;
    } catch (err) {
        console.error("/api/aiへのリクエスト失敗", err);
    }
}

// Geminiからのレスポンスをtextで描画する
export async function renderGeminiText(data) {
    showLoading("ai-loading");
    try {
        const response = await getGeminiResponse(data);
        const text = JSON.stringify(response, null, 2);
        document.getElementById("ai").textContent = text;
    } finally {
        hideLoading("ai-loading");
    }
}

/* ---------- DB操作 ---------- */
export function addTestData() {
    showLoading("map-loading");
    showLoading("chart-loading");
    showLoading("ai-loading");

    const url = `/add_test_data`;
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error("テストデータ追加失敗");
            }
            console.log("テストデータ追加成功");
            return fetchEvents();
        })
        .catch(error => {
            console.error("エラー:", error);
        });
}

export function switchDvEnv(env) {
    showLoading("map-loading");
    showLoading("chart-loading");
    showLoading("ai-loading");

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

/* ---------- イベント取得 ---------- */
export async function fetchEvents(start = null, end = null) {
    showLoading("map-loading");
    showLoading("chart-loading");
    showLoading("ai-loading");

    try {
        let url = "/get_events";
        if (start && end) {
            url += `?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`;
        }
        const res = await fetch(url);
        const data = await res.json();
        allEvents = data;

        updateDropdown(data);

        // マップとチャート更新
        updateHeatmapAndChart(document.getElementById("vehicleSelect").value);

        // AI レポート更新
        await renderGeminiText(allEvents);
    } catch (err) {
        console.error("イベント取得エラー:", err);
    } finally {
        hideLoading("map-loading");
        hideLoading("chart-loading");
        hideLoading("ai-loading");
    }
}

/* ---------- データ削除 ---------- */
export function deleteData() {
    showLoading("map-loading");
    showLoading("chart-loading");
    showLoading("ai-loading");

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

/* ---------- Google Maps API ---------- */
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

/* ---------- UI更新 ---------- */
// ドロップダウンメニューの項目更新
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

// ヒートマップとチャートの更新
export function updateHeatmapAndChart(vehicleType) {
    showLoading("map-loading");
    showLoading("chart-loading");

    let filtered = allEvents;
    if (vehicleType !== "All") {
        filtered = allEvents.filter(e => e.name === vehicleType);
    }
    updateHeatmap(filtered);
    processEvents(filtered);

    hideLoading("map-loading");
    hideLoading("chart-loading");
}

// マップにフィルターを適用する
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

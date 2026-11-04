/**
 * TRAFFICVISION ENTERPRISE - CLIENT APPLICATION CONTROLLER
 * Architecture: 7-Tab SaaS System, Real-time Multicam, Strict Data Integrity,
 * Traffic Forecasting with Backtest Errors (MAE, RMSE, MAPE).
 */

// Global fallback if clicked before DOM fully ready
window.switchTab = function(tabId) {
    if (window._internalSwitchTab) {
        window._internalSwitchTab(tabId);
    } else {
        window.location.hash = tabId;
    }
};

document.addEventListener("DOMContentLoaded", () => {

    // Global Chart.js instances
    let overviewFlowChart = null;
    let flowHistoryChart = null;
    let densityPcuChart = null;
    let speedHistoryChart = null;
    let analyticsVehicleMixChart = null;
    let flowForecastChart = null;

    // =========================================================================
    // 1. APPLICATION STATE
    // =========================================================================
    const AppState = {
        activeTab: "overview",      // 'overview', 'live', 'analytics', 'forecast', 'sources', 'logs', 'settings'
        theme: localStorage.getItem("tv_theme") || "dark",
        user: null,

        cameras: [],
        selectedCameraIds: new Set(["CAM-01", "CAM-02", "CAM-03", "CAM-04", "CAM-05", "CAM-06"]),
        focusedCameraId: null,      // null = grid mode; "CAM-01" = focused single camera
        inspectedCameraId: "CAM-01", // Camera dang theo doi chi tiet o cot KPI phai
        currentLayout: "3x3",       // "1x1", "2x2", "3x3"
        
        // Analytics & Forecast Filters
        analyticsRange: "5m",
        forecastHorizon: 15,
        forecastModel: "holt_winters",

        soundEnabled: false,
        alarmActive: false,
        roiEditing: false,
        activeRoiHandle: -1,
        isStreamPaused: false,

        densityThresholds: [121, 220, 350],
        sseSource: null
    };
    window.AppState = AppState;

    // Apply saved theme immediately
    document.documentElement.setAttribute("data-theme", AppState.theme);

    // =========================================================================
    // 2. DOM REFERENCES
    // =========================================================================
    const el = {
        // Header
        liveClock: document.getElementById("liveClock"),
        gpuStatusText: document.getElementById("gpuStatusText"),
        fpsStatusText: document.getElementById("fpsStatusText"),
        latencyStatusText: document.getElementById("latencyStatusText"),
        btnThemeToggle: document.getElementById("btnThemeToggle"),
        iconTheme: document.getElementById("iconTheme"),
        lblTheme: document.getElementById("lblTheme"),
        btnSoundToggle: document.getElementById("btnSoundToggle"),
        lblSound: document.getElementById("lblSound"),
        iconSound: document.getElementById("iconSound"),
        alarmAudio: document.getElementById("alarmAudio"),
        btnLogout: document.getElementById("btnLogout"),
        activeCamCountBadge: document.getElementById("activeCamCountBadge"),

        // Navigation Tabs
        navTabs: document.querySelectorAll(".nav-tab"),
        tabPanels: document.querySelectorAll(".tab-panel"),

        // Overview Tab
        ovFlow: document.getElementById("ovFlow"),
        ovDensity: document.getElementById("ovDensity"),
        ovTotalVeh: document.getElementById("ovTotalVeh"),
        ovNetworkStatus: document.getElementById("ovNetworkStatus"),
        overviewStationCards: document.getElementById("overviewStationCards"),
        ovVehicleMixBars: document.getElementById("ovVehicleMixBars"),
        ovPctMotorcycle: document.getElementById("ovPctMotorcycle"),
        ovPctCar: document.getElementById("ovPctCar"),
        ovPctBus: document.getElementById("ovPctBus"),
        ovPctTruck: document.getElementById("ovPctTruck"),
        ovPctBicycle: document.getElementById("ovPctBicycle"),
        ovBarMotorcycle: document.getElementById("ovBarMotorcycle"),
        ovBarCar: document.getElementById("ovBarCar"),
        ovBarBus: document.getElementById("ovBarBus"),
        ovBarTruck: document.getElementById("ovBarTruck"),
        ovBarBicycle: document.getElementById("ovBarBicycle"),

        // Live Tab - Left Sidebar
        cameraItemList: document.getElementById("cameraItemList"),
        cameraSearchInput: document.getElementById("cameraSearchInput"),
        btnToggleTuning: document.getElementById("btnToggleTuning"),
        tuningChevron: document.getElementById("tuningChevron"),
        tuningBody: document.getElementById("tuningBody"),
        sliderConfidence: document.getElementById("sliderConfidence"),
        lblConfidence: document.getElementById("lblConfidence"),

        // Live Tab - Center Grid & Focus
        gridTitle: document.getElementById("gridTitle"),
        btnExitFocus: document.getElementById("btnExitFocus"),
        layoutBtnGroup: document.getElementById("layoutBtnGroup"),
        cameraGridStage: document.getElementById("cameraGridStage"),
        cameraFocusStage: document.getElementById("cameraFocusStage"),
        focusStreamImg: document.getElementById("focusStreamImg"),
        focusRoiCanvas: document.getElementById("focusRoiCanvas"),
        focusCamName: document.getElementById("focusCamName"),
        focusCamBearing: document.getElementById("focusCamBearing"),
        focusCamFps: document.getElementById("focusCamFps"),
        btnFocusPause: document.getElementById("btnFocusPause"),
        btnFocusSnapshot: document.getElementById("btnFocusSnapshot"),
        btnFocusEditRoi: document.getElementById("btnFocusEditRoi"),
        lblEditRoiState: document.getElementById("lblEditRoiState"),

        // Live Tab - Right Column KPI
        liveCamInspectorSelect: document.getElementById("liveCamInspectorSelect"),
        liveMixCamBadge: document.getElementById("liveMixCamBadge"),
        kpiFlow: document.getElementById("kpiFlow"),
        kpiDensity: document.getElementById("kpiDensity"),
        kpiPcu: document.getElementById("kpiPcu"),
        kpiSpeed: document.getElementById("kpiSpeed"),
        pctMotorcycle: document.getElementById("pctMotorcycle"),
        pctCar: document.getElementById("pctCar"),
        pctBus: document.getElementById("pctBus"),
        pctTruck: document.getElementById("pctTruck"),
        pctBicycle: document.getElementById("pctBicycle"),
        barMotorcycle: document.getElementById("barMotorcycle"),
        barCar: document.getElementById("barCar"),
        barBus: document.getElementById("barBus"),
        barTruck: document.getElementById("barTruck"),
        barBicycle: document.getElementById("barBicycle"),
        signalStatusBadge: document.getElementById("signalStatusBadge"),
        signalTimer: document.getElementById("signalTimer"),
        signalAdviceText: document.getElementById("signalAdviceText"),

        // Analytics Tab
        analyticsCameraSelect: document.getElementById("analyticsCameraSelect"),
        pillsRange: document.querySelectorAll(".pill-range"),
        anFlow: document.getElementById("anFlow"),
        anFlowSub: document.getElementById("anFlowSub"),
        anDensity: document.getElementById("anDensity"),
        anPcuSub: document.getElementById("anPcuSub"),
        anSpeed: document.getElementById("anSpeed"),
        anSpeedSub: document.getElementById("anSpeedSub"),
        anStatusBadge: document.getElementById("anStatusBadge"),
        anVehSub: document.getElementById("anVehSub"),

        // Forecast Tab
        forecastCamSelect: document.getElementById("forecastCamSelect"),
        forecastModelSelect: document.getElementById("forecastModelSelect"),
        pillsForecast: document.querySelectorAll(".pill-forecast"),
        valMae: document.getElementById("valMae"),
        valRmse: document.getElementById("valRmse"),
        valMape: document.getElementById("valMape"),
        valSampleCount: document.getElementById("valSampleCount"),
        forecastMetaNote: document.getElementById("forecastMetaNote"),

        // Sources Tab
        btnTriggerUploadModal: document.getElementById("btnTriggerUploadModal"),
        sourcesCameraGrid: document.getElementById("sourcesCameraGrid"),
        uploadedVideosTableBody: document.getElementById("uploadedVideosTableBody"),

        // Logs Tab
        logFilterCam: document.getElementById("logFilterCam"),
        logFilterLevel: document.getElementById("logFilterLevel"),
        logSearchInput: document.getElementById("logSearchInput"),
        logTotalCount: document.getElementById("logTotalCount"),
        logsTableBody: document.getElementById("logsTableBody"),
        btnClearLogs: document.getElementById("btnClearLogs"),

        // Settings Tab
        settingsCamSelect: document.getElementById("settingsCamSelect"),
        settingsBannerCamId: document.getElementById("settingsBannerCamId"),
        settingsBannerCamName: document.getElementById("settingsBannerCamName"),
        settingsBannerDistrict: document.getElementById("settingsBannerDistrict"),
        settingsBannerLanes: document.getElementById("settingsBannerLanes"),
        settingsBannerCapacity: document.getElementById("settingsBannerCapacity"),
        inputRoiLength: document.getElementById("inputRoiLength"),
        inputRoiWidth: document.getElementById("inputRoiWidth"),
        inputFreeThr: document.getElementById("inputFreeThr"),
        inputJamThr: document.getElementById("inputJamThr"),
        inputJamSpeed: document.getElementById("inputJamSpeed"),
        inputThrL2: document.getElementById("inputThrL2"),
        inputThrL3: document.getElementById("inputThrL3"),
        inputThrL4: document.getElementById("inputThrL4"),
        btnSaveSystemSettings: document.getElementById("btnSaveSystemSettings"),
        btnResetDefaultSettings: document.getElementById("btnResetDefaultSettings"),
        settingsSaveStatusText: document.getElementById("settingsSaveStatusText"),

        // Mini Footer
        miniLogTicker: document.getElementById("miniLogTicker"),
        btnJumpToLogsTab: document.getElementById("btnJumpToLogsTab"),

        // Upload Modal
        uploadModal: document.getElementById("uploadModal"),
        modalUploadCamSelect: document.getElementById("modalUploadCamSelect"),
        modalVideoFileInput: document.getElementById("modalVideoFileInput"),
        uploadProgressContainer: document.getElementById("uploadProgressContainer"),
        uploadProgressBar: document.getElementById("uploadProgressBar"),
        uploadStatusText: document.getElementById("uploadStatusText"),
        btnCloseUploadModal: document.getElementById("btnCloseUploadModal"),
        btnCancelUploadModal: document.getElementById("btnCancelUploadModal"),
        btnConfirmUpload: document.getElementById("btnConfirmUpload")
    };

    function refreshIcons() {
        if (window.lucide && typeof window.lucide.createIcons === "function") {
            window.lucide.createIcons();
        }
    }
    refreshIcons();

    // =========================================================================
    // 3. THEME & AUTH CONTROLLER
    // =========================================================================
    function updateThemeUI() {
        const isDark = AppState.theme === "dark";
        document.documentElement.setAttribute("data-theme", AppState.theme);
        localStorage.setItem("tv_theme", AppState.theme);
        el.lblTheme.textContent = isDark ? "Tối" : "Sáng";
        el.iconTheme.setAttribute("data-lucide", isDark ? "moon" : "sun");
        refreshIcons();

        // Cập nhật lại màu biểu đồ Chart.js theo theme
        if (window.Chart) {
            Chart.defaults.color = isDark ? "#94a3b8" : "#475569";
            if (overviewFlowChart) overviewFlowChart.update();
            if (flowHistoryChart) flowHistoryChart.update();
            if (densityPcuChart) densityPcuChart.update();
            if (speedHistoryChart) speedHistoryChart.update();
            if (analyticsVehicleMixChart) analyticsVehicleMixChart.update();
            if (flowForecastChart) flowForecastChart.update();
        }
    }

    el.btnThemeToggle.addEventListener("click", () => {
        AppState.theme = AppState.theme === "dark" ? "light" : "dark";
        updateThemeUI();
    });
    updateThemeUI();

    // Auth Logout
    el.btnLogout.addEventListener("click", async () => {
        try {
            await fetch("/api/auth/logout", { method: "POST" });
            window.location.href = "/login";
        } catch (e) {
            window.location.href = "/login";
        }
    });

    // Clock
    function updateClock() {
        const now = new Date();
        el.liveClock.textContent = now.toLocaleTimeString("vi-VN", { hour12: false }) + " UTC+7";
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Telemetry
    async function fetchSystemTelemetry() {
        try {
            const res = await fetch("/api/system_telemetry");
            if (!res.ok) {
                if (res.status === 401) window.location.href = "/login";
                return;
            }
            const data = await res.json();
            if (data.success) {
                el.gpuStatusText.textContent = `GPU: ${data.device_name || "RTX 3060"}`;
            }
        } catch (e) {}
    }
    fetchSystemTelemetry();
    setInterval(fetchSystemTelemetry, 15000);

    // =========================================================================
    // 4. TAB NAVIGATION & URL HASH ROUTING
    // =========================================================================
    function switchTab(tabId) {
        if (!tabId) tabId = "overview";
        AppState.activeTab = tabId;
        try {
            if (window.location.hash !== `#${tabId}`) {
                history.replaceState(null, null, `#${tabId}`);
            }
        } catch (e) {}

        // 1. Cập nhật trạng thái active cho các nút tab
        document.querySelectorAll(".nav-tab").forEach(t => {
            const match = t.getAttribute("data-tab") === tabId;
            t.classList.toggle("active", match);
        });

        // 2. Cập nhật trạng thái hiển thị cho các panels (chuyển màn hình ngay lập tức 100%)
        document.querySelectorAll(".tab-panel").forEach(p => {
            const isTarget = p.id === `tabPanel-${tabId}`;
            p.classList.toggle("active", isTarget);
            if (isTarget) {
                p.style.setProperty("display", "block", "important");
            } else {
                p.style.setProperty("display", "none", "important");
            }
        });

        // 3. Kích hoạt render nội dung tương ứng với từng tab trong try...catch an toàn
        try {
            if (tabId === "overview") {
                renderOverviewStationCards();
                updateOverviewCharts();
            } else if (tabId === "live") {
                renderCameraGrid();
                renderLeftCameraList();
            } else if (tabId === "analytics") {
                updateAnalyticsCharts();
            } else if (tabId === "forecast") {
                updateForecastTab();
            } else if (tabId === "sources") {
                loadSourcesTab();
            } else if (tabId === "logs") {
                loadLogsTab();
            } else if (tabId === "settings") {
                loadSettingsTab();
            }
        } catch (err) {
            console.warn("Lỗi khi cập nhật dữ liệu tab " + tabId, err);
        }

        refreshIcons();
    }

    // Helper: Đồng bộ hóa camera đang kiểm tra (inspected camera) xuyên suốt tất cả các Tab
    function syncActiveCamera(camId) {
        if (!camId) return;
        AppState.inspectedCameraId = camId;
        if (el.liveCamInspectorSelect && el.liveCamInspectorSelect.value !== camId) {
            el.liveCamInspectorSelect.value = camId;
        }
        if (el.analyticsCameraSelect && el.analyticsCameraSelect.value !== camId) {
            el.analyticsCameraSelect.value = camId;
        }
        if (el.forecastCamSelect && el.forecastCamSelect.value !== camId) {
            el.forecastCamSelect.value = camId;
        }
        if (el.logFilterCam && el.logFilterCam.value !== camId && el.logFilterCam.value !== "ALL") {
            el.logFilterCam.value = camId;
        }
        if (el.settingsCamSelect && el.settingsCamSelect.value !== camId) {
            el.settingsCamSelect.value = camId;
            loadSettingsForCamera(camId);
        }
    }

    // Expose ra window để có thể gọi từ inline onclick nếu cần
    window._internalSwitchTab = switchTab;
    window.switchTab = switchTab;

    // Gán sự kiện click cho tất cả các nút nav-tab
    document.querySelectorAll(".nav-tab").forEach(t => {
        t.addEventListener("click", function(e) {
            e.preventDefault();
            const targetTab = this.getAttribute("data-tab");
            if (targetTab) {
                switchTab(targetTab);
            }
        });
    });

    // Jump from footer to logs tab
    if (el.btnJumpToLogsTab) {
        el.btnJumpToLogsTab.addEventListener("click", () => {
            switchTab("logs");
        });
    }

    // Handle back/forward hash changes
    window.addEventListener("hashchange", () => {
        const h = window.location.hash.replace("#", "");
        if (h && h !== AppState.activeTab) {
            switchTab(h);
        }
    });

    // =========================================================================
    // 5. CHART.JS INITIALIZATIONS
    // =========================================================================
    function initAllCharts() {
        if (!window.Chart) return;

        const isDark = AppState.theme === "dark";
        Chart.defaults.color = isDark ? "#94a3b8" : "#475569";
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.font.size = 11;

        // 1. Overview Flow Chart
        const ctxOv = document.getElementById("overviewFlowChart");
        if (ctxOv) {
            overviewFlowChart = new Chart(ctxOv.getContext("2d"), {
                type: "line",
                data: {
                    labels: [],
                    datasets: [{
                        label: "Lưu lượng bình quân (xe/h)",
                        data: [],
                        borderColor: "#3b82f6",
                        backgroundColor: "rgba(59, 130, 246, 0.08)",
                        borderWidth: 2,
                        tension: 0.25,
                        fill: true,
                        pointRadius: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: isDark ? "#202632" : "#e2e8f0" } },
                        y: {
                            grid: { color: isDark ? "#202632" : "#e2e8f0" },
                            title: { display: true, text: "xe/h", font: { size: 10 } }
                        }
                    }
                }
            });
        }

        // 2. Analytics Flow Chart
        const ctxFlow = document.getElementById("flowHistoryChart");
        if (ctxFlow) {
            flowHistoryChart = new Chart(ctxFlow.getContext("2d"), {
                type: "line",
                data: {
                    labels: [],
                    datasets: [{
                        label: "Lưu lượng Q (xe/h)",
                        data: [],
                        borderColor: "#3b82f6",
                        backgroundColor: "rgba(59, 130, 246, 0.08)",
                        borderWidth: 2,
                        tension: 0.2,
                        fill: true,
                        pointRadius: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: isDark ? "#202632" : "#e2e8f0" } },
                        y: { grid: { color: isDark ? "#202632" : "#e2e8f0" } }
                    }
                }
            });
        }

        // 3. Density & PCU Chart
        const ctxDp = document.getElementById("densityPcuChart");
        if (ctxDp) {
            densityPcuChart = new Chart(ctxDp.getContext("2d"), {
                type: "line",
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: "Mật độ K (xe/km)",
                            data: [],
                            borderColor: "#f59e0b",
                            borderWidth: 2,
                            tension: 0.2,
                            pointRadius: 2,
                            yAxisID: "y"
                        },
                        {
                            label: "Chỉ số PCU",
                            data: [],
                            borderColor: "#8b5cf6",
                            borderWidth: 2,
                            tension: 0.2,
                            pointRadius: 2,
                            yAxisID: "y1"
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { color: isDark ? "#202632" : "#e2e8f0" } },
                        y: {
                            type: "linear",
                            position: "left",
                            grid: { color: isDark ? "#202632" : "#e2e8f0" },
                            title: { display: true, text: "xe/km" }
                        },
                        y1: {
                            type: "linear",
                            position: "right",
                            grid: { display: false },
                            title: { display: true, text: "PCU" }
                        }
                    }
                }
            });
        }

        // 4. Forecast Chart (Holt-Winters Confidence Band)
        const ctxFc = document.getElementById("flowForecastChart");
        if (ctxFc) {
            flowForecastChart = new Chart(ctxFc.getContext("2d"), {
                type: "line",
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: "Vùng cận trên (Upper 95%)",
                            data: [],
                            borderColor: "transparent",
                            backgroundColor: "rgba(59, 130, 246, 0.12)",
                            pointRadius: 0,
                            fill: "+1"
                        },
                        {
                            label: "Vùng cận dưới (Lower 95%)",
                            data: [],
                            borderColor: "transparent",
                            backgroundColor: "transparent",
                            pointRadius: 0,
                            fill: false
                        },
                        {
                            label: "Lưu lượng quan sát thực",
                            data: [],
                            borderColor: "#3b82f6",
                            borderWidth: 2,
                            pointRadius: 3,
                            fill: false
                        },
                        {
                            label: "Đường dự báo tương lai",
                            data: [],
                            borderColor: "#10b981",
                            borderWidth: 2,
                            borderDash: [5, 4],
                            pointRadius: 3,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: "top", labels: { boxWidth: 12 } }
                    },
                    scales: {
                        x: { grid: { color: isDark ? "#202632" : "#e2e8f0" } },
                        y: {
                            grid: { color: isDark ? "#202632" : "#e2e8f0" },
                            title: { display: true, text: "Lưu lượng Q (xe/h)" }
                        }
                    }
                }
            });
        }

        // 5. Speed History Chart (V - km/h)
        const ctxSp = document.getElementById("speedHistoryChart");
        if (ctxSp) {
            speedHistoryChart = new Chart(ctxSp.getContext("2d"), {
                type: "line",
                data: {
                    labels: [],
                    datasets: [{
                        label: "Tốc độ trung bình (km/h)",
                        data: [],
                        borderColor: "#06b6d4",
                        backgroundColor: "rgba(6, 182, 212, 0.08)",
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true,
                        pointRadius: 2.5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { color: isDark ? "#202632" : "#e2e8f0" } },
                        y: {
                            grid: { color: isDark ? "#202632" : "#e2e8f0" },
                            title: { display: true, text: "V (km/h)" },
                            min: 0,
                            max: 70
                        }
                    }
                }
            });
        }

        // 6. Analytics Vehicle Mix Doughnut Chart
        const ctxVm = document.getElementById("analyticsVehicleMixChart");
        if (ctxVm) {
            analyticsVehicleMixChart = new Chart(ctxVm.getContext("2d"), {
                type: "doughnut",
                data: {
                    labels: ["Xe máy", "Ô tô con", "Xe khách", "Xe tải", "Xe đạp"],
                    datasets: [{
                        data: [60, 25, 6, 4, 5],
                        backgroundColor: ["#06b6d4", "#f59e0b", "#3b82f6", "#ef4444", "#22c55e"],
                        borderWidth: 1,
                        borderColor: isDark ? "#161a21" : "#ffffff"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: "62%",
                    plugins: {
                        legend: {
                            position: "right",
                            labels: { boxWidth: 12, padding: 12, font: { size: 11 } }
                        }
                    }
                }
            });
        }
    }
    initAllCharts();

    // =========================================================================
    // 6. REAL-TIME DATA & STATE SYNCHRONIZER
    // =========================================================================
    async function fetchCameras() {
        try {
            const res = await fetch("/api/cameras");
            if (!res.ok) {
                if (res.status === 401) window.location.href = "/login";
                return;
            }
            const data = await res.json();
            if (data.success && data.cameras) {
                AppState.cameras = data.cameras;
                updateAllViews();
            }
        } catch (e) {}
    }

    function updateAllViews() {
        el.activeCamCountBadge.textContent = `${AppState.cameras.length} camera trực tuyến`;

        // Đồng bộ danh sách options của tất cả các selector camera ở các Tab
        const camSelects = [
            { sel: el.liveCamInspectorSelect, includeAll: false },
            { sel: el.analyticsCameraSelect, includeAll: false },
            { sel: el.forecastCamSelect, includeAll: false },
            { sel: el.settingsCamSelect, includeAll: false },
            { sel: el.logFilterCam, includeAll: true }
        ];

        camSelects.forEach(item => {
            const sel = item.sel;
            if (!sel || AppState.cameras.length === 0) return;
            const targetCount = item.includeAll ? AppState.cameras.length + 1 : AppState.cameras.length;
            if (sel.options.length !== targetCount) {
                const curVal = sel.value || (item.includeAll ? "ALL" : (AppState.inspectedCameraId || "CAM-01"));
                let html = item.includeAll ? '<option value="ALL">Tất cả 6 trạm Camera (Toàn mạng lưới)</option>' : '';
                html += AppState.cameras.map(c => `<option value="${c.id}">${c.id} · ${c.name}</option>`).join("");
                sel.innerHTML = html;
                sel.value = curVal;
            }
        });

        updateAggregatedKpis();

        if (AppState.activeTab === "overview") {
            renderOverviewStationCards();
        } else if (AppState.activeTab === "live") {
            if (AppState.focusedCameraId) {
                const cam = AppState.cameras.find(c => c.id === AppState.focusedCameraId);
                if (cam) {
                    const m = cam.metrics || {};
                    const flowDisplay = m.flow !== null && m.flow !== undefined ? `${Math.round(m.flow)} xe/h` : "—";
                    if (el.focusCamFps) el.focusCamFps.textContent = `${(m.fps || 25.0).toFixed(1)} FPS`;
                    const focusVeh = document.getElementById("focusBottomVehicles");
                    if (focusVeh) focusVeh.textContent = `Bộ đếm: ${m.cumulative_vehicles || 0} xe · Trong zone: ${m.total_vehicles || 0} xe`;
                    const focusDet = document.getElementById("focusBottomDetails");
                    if (focusDet) focusDet.textContent = `PCU: ${(m.pcu || 0).toFixed(1)} · Mật độ: ${(m.density || 0).toFixed(1)} xe/km · Lưu lượng: ${flowDisplay} · Vận tốc: ${m.speed || 0} km/h`;
                }
            } else {
                renderCameraGrid();
            }
            renderLeftCameraList();
        } else if (AppState.activeTab === "logs") {
            renderLogsStationsOverview();
        }
    }

    function updateAggregatedKpis() {
        // --- 1. CẬP NHẬT OVERVIEW TAB (TỔNG QUAN TOÀN MẠNG LƯỚI) ---
        let ovFlowSum = 0, ovFlowCount = 0;
        let ovDensitySum = 0, ovDensityCount = 0;
        let ovTotalVehInRoi = 0;
        let ovTotalCumulativeVeh = 0;
        let ovCumulativeCounts = { xe_may: 0, o_to_con: 0, xe_khach: 0, xe_tai: 0, xe_dap: 0 };
        let ovCounts = { xe_may: 0, o_to_con: 0, xe_khach: 0, xe_tai: 0, xe_dap: 0 };

        AppState.cameras.forEach(c => {
            const m = c.metrics || {};
            if (m.flow !== null && m.flow !== undefined) {
                ovFlowSum += m.flow;
                ovFlowCount++;
            }
            if (m.density !== null && m.density !== undefined) {
                ovDensitySum += m.density;
                ovDensityCount++;
            }
            ovTotalVehInRoi += (m.total_vehicles || 0);
            ovTotalCumulativeVeh += (m.cumulative_vehicles || 0);

            const cc = m.cumulative_counts || {};
            ovCumulativeCounts.xe_may += (cc.xe_may || 0);
            ovCumulativeCounts.o_to_con += (cc.o_to_con || 0);
            ovCumulativeCounts.xe_khach += (cc.xe_khach || 0);
            ovCumulativeCounts.xe_tai += (cc.xe_tai || 0);
            ovCumulativeCounts.xe_dap += (cc.xe_dap || 0);

            const mc = m.counts || {};
            ovCounts.xe_may += (mc.xe_may || 0);
            ovCounts.o_to_con += (mc.o_to_con || 0);
            ovCounts.xe_khach += (mc.xe_khach || 0);
            ovCounts.xe_tai += (mc.xe_tai || 0);
            ovCounts.xe_dap += (mc.xe_dap || 0);
        });

        if (el.ovFlow) el.ovFlow.textContent = ovFlowCount > 0 ? Math.round(ovFlowSum / ovFlowCount).toLocaleString("vi-VN") : "—";
        if (el.ovDensity) el.ovDensity.textContent = ovDensityCount > 0 ? (ovDensitySum / ovDensityCount).toFixed(1) : "—";
        if (el.ovTotalVeh) el.ovTotalVeh.textContent = ovTotalCumulativeVeh;
        const ovSub = document.getElementById("ovTotalVehSub");
        if (ovSub) ovSub.textContent = `Hiện diện trong zone: ${ovTotalVehInRoi} xe`;

        // Cơ cấu phương tiện toàn mạng ở Tab Tổng quan
        const ovTotalCum = (ovCumulativeCounts.xe_may + ovCumulativeCounts.o_to_con + ovCumulativeCounts.xe_khach + ovCumulativeCounts.xe_tai + ovCumulativeCounts.xe_dap);
        const ovUse = ovTotalCum > 0 ? ovCumulativeCounts : ovCounts;
        const ovTotal = (ovUse.xe_may + ovUse.o_to_con + ovUse.xe_khach + ovUse.xe_tai + ovUse.xe_dap);
        if (ovTotal > 0) {
            const pM = Math.round(ovUse.xe_may / ovTotal * 100);
            const pC = Math.round(ovUse.o_to_con / ovTotal * 100);
            const pB = Math.round(ovUse.xe_khach / ovTotal * 100);
            const pT = Math.round(ovUse.xe_tai / ovTotal * 100);
            const pK = Math.max(0, 100 - (pM + pC + pB + pT));

            if (el.ovPctMotorcycle) el.ovPctMotorcycle.textContent = `${pM}% (${ovUse.xe_may} xe)`;
            if (el.ovPctCar) el.ovPctCar.textContent = `${pC}% (${ovUse.o_to_con} xe)`;
            if (el.ovPctBus) el.ovPctBus.textContent = `${pB}% (${ovUse.xe_khach} xe)`;
            if (el.ovPctTruck) el.ovPctTruck.textContent = `${pT}% (${ovUse.xe_tai} xe)`;
            if (el.ovPctBicycle) el.ovPctBicycle.textContent = `${pK}% (${ovUse.xe_dap} xe)`;

            if (el.ovBarMotorcycle) el.ovBarMotorcycle.style.width = `${pM}%`;
            if (el.ovBarCar) el.ovBarCar.style.width = `${pC}%`;
            if (el.ovBarBus) el.ovBarBus.style.width = `${pB}%`;
            if (el.ovBarTruck) el.ovBarTruck.style.width = `${pT}%`;
            if (el.ovBarBicycle) el.ovBarBicycle.style.width = `${pK}%`;
        }

        // --- 2. CẬP NHẬT LIVE TAB (CHỈ SỐ & CƠ CẤU PHƯƠNG TIỆN CỦA TỪNG CAMERA ĐỘC LẬP) ---
        // Xác định trạm camera đang được theo dõi
        let targetCamId = AppState.focusedCameraId || AppState.inspectedCameraId || "CAM-01";
        let targetCam = AppState.cameras.find(c => c.id === targetCamId);
        if (!targetCam && AppState.cameras.length > 0) {
            targetCam = AppState.cameras[0];
            targetCamId = targetCam.id;
        }

        // Đồng bộ Dropdown và Badge trên giao diện
        if (el.liveCamInspectorSelect && el.liveCamInspectorSelect.value !== targetCamId) {
            el.liveCamInspectorSelect.value = targetCamId;
        }
        if (el.liveMixCamBadge && targetCam) {
            el.liveMixCamBadge.textContent = `${targetCam.id} · ${targetCam.name}`;
        }

        if (targetCam) {
            const m = targetCam.metrics || {};

            // 2.1. Cập nhật 4 KPI chính ĐỘC LẬP của riêng camera này
            el.kpiFlow.textContent = (m.flow !== null && m.flow !== undefined) ? Math.round(m.flow).toLocaleString("vi-VN") : "—";
            el.kpiDensity.textContent = (m.density !== null && m.density !== undefined) ? Number(m.density).toFixed(1) : "—";
            el.kpiPcu.textContent = (m.pcu !== null && m.pcu !== undefined) ? Number(m.pcu).toFixed(1) : "0.0";
            el.kpiSpeed.textContent = (m.speed !== null && m.speed !== undefined) ? Math.round(m.speed) : "—";

            // 2.2. Cơ cấu phương tiện ĐẾM ĐÚNG XE ĐANG CÓ MẶT TRONG ZONE (ROI) CỦA CAMERA NÀY
            const mc = m.counts || {};
            const nMotor = mc.xe_may || 0;
            const nCar = mc.o_to_con || 0;
            const nBus = mc.xe_khach || 0;
            const nTruck = mc.xe_tai || 0;
            const nBike = mc.xe_dap || 0;
            const sumZoneVeh = nMotor + nCar + nBus + nTruck + nBike;
            const zoneVeh = (m.total_vehicles !== undefined && m.total_vehicles !== null) ? Math.max(m.total_vehicles, sumZoneVeh) : sumZoneVeh;

            // Hiển thị badge số xe trong zone
            if (el.liveMixCamBadge && targetCam) {
                el.liveMixCamBadge.textContent = `${targetCam.id} · Trong zone: ${zoneVeh} xe`;
            }

            let pMotor = 0, pCar = 0, pBus = 0, pTruck = 0, pBike = 0;
            if (zoneVeh > 0 && sumZoneVeh > 0) {
                pMotor = Math.round(nMotor / sumZoneVeh * 100);
                pCar = Math.round(nCar / sumZoneVeh * 100);
                pBus = Math.round(nBus / sumZoneVeh * 100);
                pTruck = Math.round(nTruck / sumZoneVeh * 100);
                pBike = Math.max(0, 100 - (pMotor + pCar + pBus + pTruck));

                if (el.pctMotorcycle) el.pctMotorcycle.textContent = `${pMotor}% (${nMotor} xe)`;
                if (el.pctCar) el.pctCar.textContent = `${pCar}% (${nCar} xe)`;
                if (el.pctBus) el.pctBus.textContent = `${pBus}% (${nBus} xe)`;
                if (el.pctTruck) el.pctTruck.textContent = `${pTruck}% (${nTruck} xe)`;
                if (el.pctBicycle) el.pctBicycle.textContent = `${pBike}% (${nBike} xe)`;
            } else {
                if (el.pctMotorcycle) el.pctMotorcycle.textContent = "0% (0 xe)";
                if (el.pctCar) el.pctCar.textContent = "0% (0 xe)";
                if (el.pctBus) el.pctBus.textContent = "0% (0 xe)";
                if (el.pctTruck) el.pctTruck.textContent = "0% (0 xe)";
                if (el.pctBicycle) el.pctBicycle.textContent = "0% (0 xe)";
            }

            if (el.barMotorcycle) el.barMotorcycle.style.width = `${pMotor}%`;
            if (el.barCar) el.barCar.style.width = `${pCar}%`;
            if (el.barBus) el.barBus.style.width = `${pBus}%`;
            if (el.barTruck) el.barTruck.style.width = `${pTruck}%`;
            if (el.barBicycle) el.barBicycle.style.width = `${pBike}%`;

            // 2.3. Khuyến nghị điều tiết tín hiệu đồng bộ 100% với trạng thái của chính camera này
            updateSignalCard(targetCam);
        }
    }

    function updateSignalCard(targetCam) {
        if (!targetCam) return;
        const m = targetCam.metrics || {};
        const level = m.congestion_level || 1;
        const vcRatio = (m.vc_ratio !== undefined && m.vc_ratio !== null) ? m.vc_ratio : (m.flow ? m.flow / 5400 : 0.2);
        const speed = m.speed || 35.0;

        let badge = "Thông thoáng (LOS A-B)", badgeClass = "normal", timer = "Chu kỳ chuẩn 5p";
        let advice = `${targetCam.id}: Lưu lượng ổn định dưới ngưỡng thiết kế (V/C=${vcRatio.toFixed(2)}). Duy trì chu kỳ chuẩn 5 phút (pha xanh trục chính 150s).`;

        if (level === 4) {
            badge = "Ùn tắc nghiêm trọng (LOS F)";
            badgeClass = "congested";
            timer = "Ưu tiên khẩn cấp 5p";
            advice = `BÁO ĐỘNG ĐỎ! ${targetCam.id}: Dòng xe tê liệt, V/C=${vcRatio.toFixed(2)}, vận tốc ${Math.round(speed)} km/h. Kích hoạt xả luồng khẩn cấp chu kỳ 5 phút.`;
        } else if (level === 3) {
            badge = "Ùn tắc giao thông (LOS E)";
            badgeClass = "congested";
            timer = "Pha giải tỏa 5p";
            advice = `CẢNH BÁO: ${targetCam.id}: Xuất hiện ùn ứ (V/C=${vcRatio.toFixed(2)}), vận tốc giảm mạnh. Tối ưu thời lượng thoát xe trong chu kỳ 5 phút.`;
        } else if (level === 2) {
            badge = "Đông đúc (LOS C-D)";
            badgeClass = "moderate";
            timer = "Pha thích ứng 5p";
            advice = `${targetCam.id}: Dòng xe tăng cao (V/C=${vcRatio.toFixed(2)}). Kéo dài pha xanh trục chính trong chu kỳ 5 phút để hạn chế tích tụ hàng chờ.`;
        } else {
            badge = "Thông thoáng (LOS A-B)";
            badgeClass = "normal";
            timer = "Chu kỳ chuẩn 5p";
            advice = `${targetCam.id}: Dòng xe lưu thông tự do, thông thoáng (V/C=${vcRatio.toFixed(2)}). Duy trì chu kỳ chuẩn 5 phút (pha xanh trục chính 150s).`;
        }

        if (el.signalStatusBadge) {
            el.signalStatusBadge.textContent = badge;
            el.signalStatusBadge.className = `signal-badge ${badgeClass}`;
        }
        if (el.signalTimer) el.signalTimer.textContent = timer;
        if (el.signalAdviceText) el.signalAdviceText.textContent = advice;

        // Trạng thái tổng quan mạng lưới ở Tab 1
        if (el.ovNetworkStatus) {
            const maxLvl = AppState.cameras.reduce((max, c) => Math.max(max, (c.metrics && c.metrics.congestion_level) || 1), 1);
            let netBadge = "Thông thoáng (LOS A-B)", netClass = "normal";
            if (maxLvl >= 3) { netBadge = "Ùn tắc giao thông"; netClass = "congested"; }
            else if (maxLvl === 2) { netBadge = "Đông đúc cục bộ"; netClass = "moderate"; }
            el.ovNetworkStatus.textContent = netBadge;
            el.ovNetworkStatus.className = `signal-badge ${netClass}`;
        }

        // Alarm Audio
        if (level >= 3 && AppState.soundEnabled) {
            if (!AppState.alarmActive) {
                AppState.alarmActive = true;
                el.alarmAudio.currentTime = 0;
                el.alarmAudio.play().catch(() => { AppState.alarmActive = false; });
            }
        } else {
            el.alarmAudio.pause();
            AppState.alarmActive = false;
        }
    }

    // =========================================================================
    // =========================================================================
    // SNAPSHOT STREAM MANAGER (Khắc phục triệt để giới hạn 6 kết nối HTTP/1.1 của trình duyệt)
    // =========================================================================
    const activeSnapshotStreams = new WeakMap();

    function attachSnapshotStream(imgEl, camId, fps = 5) {
        if (!imgEl) return;
        const existing = activeSnapshotStreams.get(imgEl);
        if (existing && existing.camId === camId && existing.active) {
            return;
        }
        if (existing) {
            existing.active = false;
            if (existing.timer) clearTimeout(existing.timer);
        }

        const state = {
            camId: camId,
            active: true,
            timer: null,
            inFlight: false
        };
        activeSnapshotStreams.set(imgEl, state);

        function loadNext() {
            if (!state.active || !imgEl.isConnected) {
                state.active = false;
                return;
            }
            // Nếu phần tử đang bị ẩn (thuộc tab không hoạt động) hoặc tab trình duyệt đang minimize
            const isVisible = imgEl.offsetParent !== null && !document.hidden;
            if (!isVisible) {
                state.timer = setTimeout(loadNext, 1000);
                return;
            }
            if (state.inFlight) {
                state.timer = setTimeout(loadNext, 100);
                return;
            }

            state.inFlight = true;
            const tempImg = new Image();
            const startT = performance.now();

            tempImg.onload = () => {
                if (state.active && imgEl.isConnected) {
                    imgEl.src = tempImg.src;
                    imgEl.style.opacity = "1";
                }
                state.inFlight = false;
                const elapsed = performance.now() - startT;
                const delay = Math.max(60, Math.round(1000 / fps) - elapsed);
                state.timer = setTimeout(loadNext, delay);
            };

            tempImg.onerror = () => {
                state.inFlight = false;
                state.timer = setTimeout(loadNext, 500);
            };

            tempImg.src = `/api/snapshot/${camId}?quality=low&_t=${Date.now()}`;
        }

        loadNext();
    }

    // =========================================================================
    // 7. OVERVIEW TAB CONTROLLER
    // =========================================================================
    function renderOverviewStationCards() {
        if (!el.overviewStationCards) return;

        const existingCards = Array.from(el.overviewStationCards.querySelectorAll(".station-card"));
        if (existingCards.length === AppState.cameras.length) {
            AppState.cameras.forEach(c => {
                const m = c.metrics || {};
                const lvlClass = m.congestion_level === 1 ? "normal" : (m.congestion_level === 2 ? "moderate" : "congested");
                const flowDisplay = m.flow !== null && m.flow !== undefined ? `${Math.round(m.flow)} xe/h` : "—";
                const densityDisplay = m.density !== null && m.density !== undefined ? `${m.density} xe/km` : "—";
                const card = el.overviewStationCards.children[AppState.cameras.indexOf(c)];
                if (card) {
                    const badge = card.querySelector(".signal-badge");
                    if (badge) {
                        badge.className = `signal-badge ${lvlClass}`;
                        badge.textContent = m.congestion_name || 'Thông thoáng';
                    }
                    const statVals = card.querySelectorAll(".station-stat-val");
                    if (statVals.length >= 3) {
                        statVals[0].textContent = flowDisplay;
                        statVals[1].textContent = densityDisplay;
                        statVals[2].textContent = `${m.cumulative_vehicles || 0} xe (${m.total_vehicles || 0} trong zone)`;
                    }
                    const img = card.querySelector(".station-card-img");
                    if (img) attachSnapshotStream(img, c.id, 5);
                }
            });
            return;
        }

        el.overviewStationCards.innerHTML = AppState.cameras.map(c => {
            const m = c.metrics || {};
            const lvlClass = m.congestion_level === 1 ? "normal" : (m.congestion_level === 2 ? "moderate" : "congested");
            const flowDisplay = m.flow !== null && m.flow !== undefined ? `${Math.round(m.flow)} xe/h` : "—";
            const densityDisplay = m.density !== null && m.density !== undefined ? `${m.density} xe/km` : "—";

            return `
                <div class="station-card" onclick="window.switchTab('live'); setTimeout(() => { if (typeof enterFocusMode === 'function') enterFocusMode('${c.id}'); }, 50);">
                    <img src="/api/snapshot/${c.id}?quality=low" data-cam-id="${c.id}" class="station-card-img" alt="${c.id}" onerror="this.style.opacity='0.2';">
                    <div class="station-card-body">
                        <div class="station-card-title">
                            <span>${c.id} · ${c.name}</span>
                            <span class="signal-badge ${lvlClass}">${m.congestion_name || 'Thông thoáng'}</span>
                        </div>
                        <div class="station-card-meta">${c.bearing} · ${c.district}</div>
                        <div class="station-card-stats">
                            <div class="station-stat-item">
                                <span>Lưu lượng</span>
                                <span class="station-stat-val tabular-nums">${flowDisplay}</span>
                            </div>
                            <div class="station-stat-item">
                                <span>Mật độ</span>
                                <span class="station-stat-val tabular-nums">${densityDisplay}</span>
                            </div>
                            <div class="station-stat-item">
                                <span>Bộ đếm (Lũy kế)</span>
                                <span class="station-stat-val tabular-nums">${m.cumulative_vehicles || 0} xe (${m.total_vehicles || 0} trong zone)</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join("");

        el.overviewStationCards.querySelectorAll(".station-card-img").forEach(img => {
            const cid = img.dataset.camId;
            if (cid) attachSnapshotStream(img, cid, 5);
        });
    }

    async function updateOverviewCharts() {
        if (!overviewFlowChart) return;
        try {
            const res = await fetch("/api/metrics?camera_id=ALL&range=15m");
            const data = await res.json();
            if (data.success && data.history) {
                overviewFlowChart.data.labels = data.history.map(h => h.time_str);
                overviewFlowChart.data.datasets[0].data = data.history.map(h => h.flow);
                overviewFlowChart.update("none");
            }
        } catch (e) {}
    }

    // =========================================================================
    // 8. LIVE TAB CONTROLLER (MULTI-CAMERA GRID & FOCUS)
    // =========================================================================
    function renderLeftCameraList() {
        if (!el.cameraItemList) return;
        const query = el.cameraSearchInput ? el.cameraSearchInput.value.toLowerCase().trim() : "";

        const filtered = AppState.cameras.filter(c => {
            return c.id.toLowerCase().includes(query) || c.name.toLowerCase().includes(query) || c.district.toLowerCase().includes(query);
        });

        const existingItems = Array.from(el.cameraItemList.querySelectorAll(".camera-item"));
        if (existingItems.length === filtered.length && existingItems.every((it, i) => it.dataset.camId === filtered[i].id)) {
            filtered.forEach((c, idx) => {
                const item = existingItems[idx];
                const isFocused = AppState.focusedCameraId === c.id;
                const isInspected = AppState.inspectedCameraId === c.id;
                item.className = `camera-item ${isFocused ? 'focused' : ''} ${isInspected ? 'inspected' : ''}`;
                const chk = item.querySelector(".cam-chk");
                if (chk) chk.checked = AppState.selectedCameraIds.has(c.id);
                const flowRow = item.querySelector(".cam-flow-row");
                const m = c.metrics || {};
                const flowDisplay = m.flow !== null && m.flow !== undefined ? `${Math.round(m.flow)} xe/h` : "—";
                if (flowRow) flowRow.textContent = `Đã đếm: ${m.cumulative_vehicles || 0} xe · ${flowDisplay}`;
                const thumb = item.querySelector(".cam-thumb");
                if (thumb) attachSnapshotStream(thumb, c.id, 1);
            });
            return;
        }

        el.cameraItemList.innerHTML = filtered.map(c => {
            const isChecked = AppState.selectedCameraIds.has(c.id);
            const isFocused = AppState.focusedCameraId === c.id;
            const isInspected = AppState.inspectedCameraId === c.id;
            const m = c.metrics || {};
            const flowDisplay = m.flow !== null && m.flow !== undefined ? `${Math.round(m.flow)} xe/h` : "—";

            return `
                <div class="camera-item ${isFocused ? 'focused' : ''} ${isInspected ? 'inspected' : ''}" data-cam-id="${c.id}" title="Nhấp để theo dõi chỉ số · Nhấp đúp để phóng to">
                    <input type="checkbox" class="cam-chk" data-cam-id="${c.id}" ${isChecked ? 'checked' : ''} onclick="event.stopPropagation();">
                    <img src="/api/snapshot/${c.id}?quality=low" data-cam-id="${c.id}" class="cam-thumb" alt="${c.id}">
                    <div class="cam-meta">
                        <div class="cam-name-row">${c.id} · ${c.name}</div>
                        <div class="cam-flow-row">Đã đếm: ${m.cumulative_vehicles || 0} xe · ${flowDisplay}</div>
                    </div>
                </div>
            `;
        }).join("");

        el.cameraItemList.querySelectorAll(".cam-thumb").forEach(thumb => {
            const cid = thumb.dataset.camId;
            if (cid) attachSnapshotStream(thumb, cid, 1);
        });

        // Attach listeners
        el.cameraItemList.querySelectorAll(".camera-item").forEach(item => {
            item.addEventListener("click", () => {
                AppState.inspectedCameraId = item.dataset.camId;
                updateAggregatedKpis();
                renderCameraGrid();
                renderLeftCameraList();
            });
            item.addEventListener("dblclick", () => {
                enterFocusMode(item.dataset.camId);
            });
        });

        el.cameraItemList.querySelectorAll(".cam-chk").forEach(chk => {
            chk.addEventListener("change", (e) => {
                const cid = e.target.dataset.camId;
                if (e.target.checked) AppState.selectedCameraIds.add(cid);
                else AppState.selectedCameraIds.delete(cid);
                renderCameraGrid();
                updateAggregatedKpis();
            });
        });
    }

    function renderCameraGrid() {
        if (!el.cameraGridStage) return;
        if (AppState.focusedCameraId) return; // In focus mode

        const activeCams = AppState.cameras.filter(c => AppState.selectedCameraIds.has(c.id));
        el.cameraGridStage.className = `camera-grid-stage layout-${AppState.currentLayout}`;

        if (activeCams.length === 0) {
            el.cameraGridStage.innerHTML = `
                <div style="grid-column:1/-1; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#64748b; gap:8px;">
                    <i data-lucide="video-off" style="width:32px; height:32px;"></i>
                    <p>Chưa chọn camera nào để hiển thị trong lưới. Hãy chọn camera ở cột bên trái.</p>
                </div>
            `;
            refreshIcons();
            return;
        }

        // Cập nhật DOM tại chỗ (in-place) để đồng bộ số xe tức thời và tránh làm gián đoạn stream video
        const existingTiles = Array.from(el.cameraGridStage.querySelectorAll(".grid-tile"));
        const existingIds = existingTiles.map(t => t.dataset.camId);
        const targetIds = activeCams.map(c => c.id);
        const idsMatch = existingIds.length === targetIds.length && existingIds.every((id, i) => id === targetIds[i]);

        if (idsMatch) {
            activeCams.forEach(c => {
                const tile = el.cameraGridStage.querySelector(`[data-cam-id="${c.id}"]`);
                if (!tile) return;

                if (c.id === AppState.inspectedCameraId) {
                    tile.classList.add("active-inspected");
                } else {
                    tile.classList.remove("active-inspected");
                }

                const m = c.metrics || {};
                const lvlClass = m.congestion_level === 1 ? "normal" : (m.congestion_level === 2 ? "moderate" : "congested");
                const flowDisplay = m.flow !== null && m.flow !== undefined ? `${Math.round(m.flow)} xe/h` : "—";

                const statusSpan = tile.querySelector(".tile-status");
                if (statusSpan) {
                    statusSpan.className = `tile-status ${lvlClass}`;
                    statusSpan.textContent = m.congestion_name || "Thông thoáng";
                }
                const metricsSpan = tile.querySelector(".tile-bottom-metrics .tabular-nums");
                if (metricsSpan) {
                    metricsSpan.textContent = `Đã đếm: ${m.cumulative_vehicles || 0} xe · Trong zone: ${m.total_vehicles || 0} xe · ${flowDisplay}`;
                }
                const img = tile.querySelector(".grid-tile-img");
                if (img) attachSnapshotStream(img, c.id, 5);
            });
            return;
        }

        el.cameraGridStage.innerHTML = activeCams.map(c => {
            const m = c.metrics || {};
            const lvlClass = m.congestion_level === 1 ? "normal" : (m.congestion_level === 2 ? "moderate" : "congested");
            const flowDisplay = m.flow !== null && m.flow !== undefined ? `${Math.round(m.flow)} xe/h` : "—";
            const isInspected = AppState.inspectedCameraId === c.id;

            return `
                <div class="grid-tile ${isInspected ? 'active-inspected' : ''}" data-cam-id="${c.id}" title="Nhấp để xem chỉ số camera ${c.id} · Nhấp đúp để phóng to">
                    <img src="/api/snapshot/${c.id}?quality=low" data-cam-id="${c.id}" class="grid-tile-img" alt="${c.id}" onerror="this.style.opacity='0.2';">
                    <div class="tile-overlay-header">
                        <span class="tile-title">${c.id} · ${c.name}</span>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span class="tile-status ${lvlClass}">${m.congestion_name || 'Thông thoáng'}</span>
                            <button class="btn-tile-focus" data-focus-id="${c.id}" title="Phóng to camera này" style="pointer-events:auto; background:rgba(15,17,21,0.85); border:1px solid rgba(255,255,255,0.25); color:#fff; border-radius:4px; padding:2px 6px; cursor:pointer; font-size:11px; display:inline-flex; align-items:center;">
                                <i data-lucide="maximize-2" style="width:12px;height:12px;"></i>
                            </button>
                        </div>
                    </div>
                    <div class="tile-bottom-metrics">
                        <span>${c.bearing}</span>
                        <span class="tabular-nums">Đã đếm: ${m.cumulative_vehicles || 0} xe · Trong zone: ${m.total_vehicles || 0} xe · ${flowDisplay}</span>
                    </div>
                </div>
            `;
        }).join("");

        el.cameraGridStage.querySelectorAll(".grid-tile-img").forEach(img => {
            const cid = img.dataset.camId;
            if (cid) attachSnapshotStream(img, cid, 5);
        });


        el.cameraGridStage.querySelectorAll(".grid-tile").forEach(t => {
            t.addEventListener("click", (e) => {
                if (e.target.closest(".btn-tile-focus")) {
                    enterFocusMode(t.dataset.camId);
                    return;
                }
                AppState.inspectedCameraId = t.dataset.camId;
                updateAggregatedKpis();
                renderCameraGrid();
                renderLeftCameraList();
            });
            t.addEventListener("dblclick", () => enterFocusMode(t.dataset.camId));
        });
        refreshIcons();
    }

    function enterFocusMode(camId) {
        const cam = AppState.cameras.find(c => c.id === camId);
        if (!cam) return;

        AppState.focusedCameraId = camId;
        el.gridTitle.textContent = `Chi tiết giám sát · ${cam.id}`;
        el.btnExitFocus.style.display = "inline-flex";

        el.cameraGridStage.style.display = "none";
        el.cameraFocusStage.style.display = "flex";

        el.focusStreamImg.src = cam.stream_url_high;
        el.focusCamName.textContent = `${cam.id} · ${cam.name}`;
        el.focusCamBearing.textContent = cam.bearing.toUpperCase();
        el.focusCamFps.textContent = `${(cam.metrics.fps || 29.4).toFixed(1)} FPS`;

        renderLeftCameraList();
        updateAggregatedKpis();
        refreshIcons();
    }

    function exitFocusMode() {
        AppState.focusedCameraId = null;
        el.gridTitle.textContent = "Lưới camera trực tiếp";
        el.btnExitFocus.style.display = "none";

        el.cameraFocusStage.style.display = "none";
        el.cameraGridStage.style.display = "grid";
        el.focusStreamImg.src = "";

        renderLeftCameraList();
        renderCameraGrid();
        updateAggregatedKpis();
    }

    el.btnExitFocus.addEventListener("click", exitFocusMode);

    if (el.liveCamInspectorSelect) {
        el.liveCamInspectorSelect.addEventListener("change", (e) => {
            AppState.inspectedCameraId = e.target.value;
            updateAggregatedKpis();
            renderCameraGrid();
            renderLeftCameraList();
        });
    }

    // =========================================================================
    // FOCUS ACTIONS: PAUSE / RESUME, SNAPSHOT, CHỈNH ROI
    // =========================================================================
    let currentRoiPoints = null; // [[x0,y0], [x1,y1], [x2,y2], [x3,y3]] in normalized [0..1]
    let draggingHandleIndex = -1;

    function initRoiCanvas() {
        const canvas = el.focusRoiCanvas;
        if (!canvas) return;
        const rect = el.focusStreamImg.getBoundingClientRect();
        canvas.width = rect.width || canvas.clientWidth || 640;
        canvas.height = rect.height || canvas.clientHeight || 360;
    }

    function drawRoiCanvas() {
        const canvas = el.focusRoiCanvas;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const w = canvas.width;
        const h = canvas.height;
        ctx.clearRect(0, 0, w, h);

        if (!AppState.roiEditing || !currentRoiPoints || currentRoiPoints.length !== 4) return;

        // Draw polygon
        ctx.beginPath();
        const p0 = [currentRoiPoints[0][0] * w, currentRoiPoints[0][1] * h];
        ctx.moveTo(p0[0], p0[1]);
        for (let i = 1; i < 4; i++) {
            ctx.lineTo(currentRoiPoints[i][0] * w, currentRoiPoints[i][1] * h);
        }
        ctx.closePath();

        // Fill with semi-transparent yellow
        ctx.fillStyle = "rgba(234, 179, 8, 0.22)";
        ctx.fill();

        // Stroke line
        ctx.strokeStyle = "#eab308";
        ctx.lineWidth = 3;
        ctx.setLineDash([6, 3]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw 4 corner handles
        const handleNames = ["Đáy trái (Gần)", "Đáy phải (Gần)", "Đỉnh phải (Xa)", "Đỉnh trái (Xa)"];
        currentRoiPoints.forEach((pt, idx) => {
            const px = pt[0] * w;
            const py = pt[1] * h;

            ctx.beginPath();
            ctx.arc(px, py, 8, 0, 2 * Math.PI);
            ctx.fillStyle = idx === draggingHandleIndex ? "#ef4444" : "#ffffff";
            ctx.fill();
            ctx.strokeStyle = "#eab308";
            ctx.lineWidth = 3;
            ctx.stroke();

            // Label
            ctx.font = "bold 11px sans-serif";
            ctx.fillStyle = "#ffffff";
            ctx.fillText(`P${idx + 1}`, px + 10, py - 6);
        });
    }

    // Toggle Edit ROI
    if (el.btnFocusEditRoi) {
        el.btnFocusEditRoi.addEventListener("click", async () => {
            if (!AppState.focusedCameraId) return;
            const cam = AppState.cameras.find(c => c.id === AppState.focusedCameraId);
            if (!cam) return;

            if (!AppState.roiEditing) {
                // BẮT ĐẦU CHỈNH ROI
                AppState.roiEditing = true;
                el.focusRoiCanvas.classList.add("active-edit");
                el.btnFocusEditRoi.classList.add("btn-primary");
                if (el.lblEditRoiState) el.lblEditRoiState.textContent = "Lưu ROI";

                // Lấy tọa độ ROI hiện tại của camera (hoặc mặc định)
                currentRoiPoints = cam.roi_norm ? JSON.parse(JSON.stringify(cam.roi_norm)) : [
                    [0.12, 0.98], [0.88, 0.98], [0.66, 0.40], [0.34, 0.40]
                ];

                initRoiCanvas();
                drawRoiCanvas();
            } else {
                // LƯU VÀ ÁP DỤNG ROI
                try {
                    const res = await fetch(`/api/cameras/${cam.id}/roi`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ roi: currentRoiPoints })
                    });
                    const data = await res.json();
                    if (data.success) {
                        cam.roi_norm = currentRoiPoints;
                        alert(`Đã lưu và áp dụng vùng ROI mới cho trạm ${cam.id}!`);
                    } else {
                        alert(data.error || "Không thể lưu ROI.");
                    }
                } catch (err) {
                    alert("Lỗi kết nối khi cập nhật ROI.");
                } finally {
                    AppState.roiEditing = false;
                    el.focusRoiCanvas.classList.remove("active-edit");
                    el.btnFocusEditRoi.classList.remove("btn-primary");
                    if (el.lblEditRoiState) el.lblEditRoiState.textContent = "Chỉnh ROI";
                    const ctx = el.focusRoiCanvas.getContext("2d");
                    ctx.clearRect(0, 0, el.focusRoiCanvas.width, el.focusRoiCanvas.height);
                }
            }
        });
    }

    // Canvas mouse events for dragging 4 ROI handles
    if (el.focusRoiCanvas) {
        const getCanvasPos = (e) => {
            const rect = el.focusRoiCanvas.getBoundingClientRect();
            return {
                x: (e.clientX - rect.left) / rect.width,
                y: (e.clientY - rect.top) / rect.height
            };
        };

        el.focusRoiCanvas.addEventListener("mousedown", (e) => {
            if (!AppState.roiEditing || !currentRoiPoints) return;
            initRoiCanvas();
            const pos = getCanvasPos(e);
            const w = el.focusRoiCanvas.width;
            const h = el.focusRoiCanvas.height;

            // Check if user clicked near any handle (radius ~ 18px)
            let clickedIndex = -1;
            let minDist = 0.04; // ~ 4% of screen
            currentRoiPoints.forEach((pt, i) => {
                const dx = pt[0] - pos.x;
                const dy = pt[1] - pos.y;
                const d = Math.sqrt(dx * dx + dy * dy);
                if (d < minDist) {
                    minDist = d;
                    clickedIndex = i;
                }
            });

            draggingHandleIndex = clickedIndex;
            drawRoiCanvas();
        });

        window.addEventListener("mousemove", (e) => {
            if (!AppState.roiEditing || draggingHandleIndex < 0 || !currentRoiPoints) return;
            const pos = getCanvasPos(e);
            // Clamp within [0..1]
            const cx = Math.max(0.01, Math.min(0.99, pos.x));
            const cy = Math.max(0.01, Math.min(0.99, pos.y));
            currentRoiPoints[draggingHandleIndex] = [parseFloat(cx.toFixed(3)), parseFloat(cy.toFixed(3))];
            drawRoiCanvas();
        });

        window.addEventListener("mouseup", () => {
            if (draggingHandleIndex >= 0) {
                draggingHandleIndex = -1;
                drawRoiCanvas();
            }
        });

        window.addEventListener("resize", () => {
            if (AppState.roiEditing) {
                initRoiCanvas();
                drawRoiCanvas();
            }
        });
    }

    // Focus Pause / Resume
    if (el.btnFocusPause) {
        el.btnFocusPause.addEventListener("click", () => {
            AppState.isStreamPaused = !AppState.isStreamPaused;
            if (AppState.isStreamPaused) {
                el.focusStreamImg.dataset.savedSrc = el.focusStreamImg.src;
                el.focusStreamImg.src = ""; // Stop network fetch
                el.btnFocusPause.innerHTML = '<i data-lucide="play" class="icon-sm"></i>';
                el.btnFocusPause.title = "Tiếp tục";
            } else {
                const cam = AppState.cameras.find(c => c.id === AppState.focusedCameraId);
                el.focusStreamImg.src = (cam && cam.stream_url_high) || el.focusStreamImg.dataset.savedSrc;
                el.btnFocusPause.innerHTML = '<i data-lucide="pause" class="icon-sm"></i>';
                el.btnFocusPause.title = "Tạm dừng";
            }
            refreshIcons();
        });
    }

    // Focus Snapshot
    if (el.btnFocusSnapshot) {
        el.btnFocusSnapshot.addEventListener("click", () => {
            if (!el.focusStreamImg) return;
            const tempCanvas = document.createElement("canvas");
            tempCanvas.width = el.focusStreamImg.naturalWidth || el.focusStreamImg.width || 1280;
            tempCanvas.height = el.focusStreamImg.naturalHeight || el.focusStreamImg.height || 720;
            const ctx = tempCanvas.getContext("2d");
            try {
                ctx.drawImage(el.focusStreamImg, 0, 0, tempCanvas.width, tempCanvas.height);
                const dataUrl = tempCanvas.toDataURL("image/jpeg", 0.95);
                const a = document.createElement("a");
                a.href = dataUrl;
                a.download = `snapshot_${AppState.focusedCameraId || 'traffic'}_${Date.now()}.jpg`;
                a.click();
            } catch (err) {
                // If CORS blocks canvas export of cross-domain MJPEG, open high-res snapshot in new tab
                window.open(el.focusStreamImg.src, "_blank");
            }
        });
    }

    // Layout buttons
    el.layoutBtnGroup.querySelectorAll(".btn-layout").forEach(btn => {
        btn.addEventListener("click", () => {
            el.layoutBtnGroup.querySelectorAll(".btn-layout").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            AppState.currentLayout = btn.dataset.layout;
            renderCameraGrid();
        });
    });

    // =========================================================================
    // 9. ANALYTICS & FORECAST CONTROLLER
    // =========================================================================
    async function updateAnalyticsCharts() {
        const camId = el.analyticsCameraSelect ? el.analyticsCameraSelect.value : (AppState.inspectedCameraId || "CAM-01");

        // 1. Cập nhật thẻ KPI tức thời của camera đang chọn trên Tab Phân tích
        const targetCam = AppState.cameras.find(c => c.id === camId);
        if (targetCam && targetCam.metrics) {
            const m = targetCam.metrics;
            const flowDisplay = m.flow !== null && m.flow !== undefined ? Math.round(m.flow) : 0;
            const densityDisplay = m.density !== null && m.density !== undefined ? Number(m.density).toFixed(1) : "0.0";
            const speedDisplay = m.speed !== null && m.speed !== undefined ? Number(m.speed).toFixed(1) : "0.0";
            const pcuDisplay = m.pcu !== null && m.pcu !== undefined ? Number(m.pcu).toFixed(1) : "0.0";
            const lvlClass = m.congestion_level === 1 ? "normal" : (m.congestion_level === 2 ? "moderate" : "congested");

            if (el.anFlow) el.anFlow.textContent = flowDisplay.toLocaleString("vi-VN");
            if (el.anFlowSub) el.anFlowSub.textContent = `Năng lực: ${m.capacity || 4300} xe/h (V/C: ${(m.vc_ratio || 0).toFixed(2)})`;
            if (el.anDensity) el.anDensity.textContent = densityDisplay;
            if (el.anPcuSub) el.anPcuSub.textContent = `PCU: ${pcuDisplay} · Đạt ${(m.density_pcu || 0).toFixed(1)} PCU/km`;
            if (el.anSpeed) el.anSpeed.textContent = speedDisplay;
            if (el.anSpeedSub) el.anSpeedSub.textContent = `V tới hạn ùn tắc: ${m.jam_speed || 14} km/h`;
            if (el.anStatusBadge) {
                el.anStatusBadge.className = `signal-badge ${lvlClass}`;
                el.anStatusBadge.textContent = `${m.congestion_name || 'Thông thoáng'} (${m.los || 'LOS A'})`;
            }
            if (el.anVehSub) el.anVehSub.textContent = `Lũy kế: ${m.cumulative_vehicles || 0} xe · Trong zone: ${m.total_vehicles || 0} xe`;
        }

        // 2. Tải chuỗi dữ liệu lịch sử từ database của camera đó
        try {
            const res = await fetch(`/api/metrics?camera_id=${camId}&range=${AppState.analyticsRange}`);
            const data = await res.json();
            if (data.success && data.history) {
                let history = data.history;
                if (history.length === 0 && targetCam && targetCam.metrics) {
                    const m = targetCam.metrics;
                    const nowStr = new Date().toLocaleTimeString();
                    history = [{
                        time_str: nowStr,
                        flow: m.flow || 0,
                        density: m.density || 0,
                        pcu: m.pcu || 0,
                        speed: m.speed || 30.0,
                        counts: m.counts || {}
                    }];
                }

                if (history.length > 0) {
                    const labels = history.map(h => h.time_str);

                    if (flowHistoryChart) {
                        flowHistoryChart.data.labels = labels;
                        flowHistoryChart.data.datasets[0].label = `Lưu lượng Q trạm ${camId} (xe/h)`;
                        flowHistoryChart.data.datasets[0].data = history.map(h => h.flow);
                        flowHistoryChart.update("none");
                    }

                    if (densityPcuChart) {
                        densityPcuChart.data.labels = labels;
                        densityPcuChart.data.datasets[0].label = `Mật độ K trạm ${camId} (xe/km)`;
                        densityPcuChart.data.datasets[0].data = history.map(h => h.density);
                        densityPcuChart.data.datasets[1].label = `PCU trạm ${camId}`;
                        densityPcuChart.data.datasets[1].data = history.map(h => h.pcu);
                        densityPcuChart.update("none");
                    }

                    if (speedHistoryChart) {
                        speedHistoryChart.data.labels = labels;
                        speedHistoryChart.data.datasets[0].label = `Vận tốc V trạm ${camId} (km/h)`;
                        speedHistoryChart.data.datasets[0].data = history.map(h => h.speed || 30.0);
                        speedHistoryChart.update("none");
                    }

                    if (analyticsVehicleMixChart) {
                        let sumM = 0, sumC = 0, sumB = 0, sumT = 0, sumD = 0;
                        history.forEach(h => {
                            const cnt = h.counts || {};
                            sumM += cnt.xe_may || 0;
                            sumC += cnt.o_to_con || 0;
                            sumB += cnt.xe_khach || 0;
                            sumT += cnt.xe_tai || 0;
                            sumD += cnt.xe_dap || 0;
                        });
                        // Ưu tiên số đếm tích lũy thực tế của camera đang chọn nếu chuỗi trong lịch sử chưa có phương tiện
                        if (sumM + sumC + sumB + sumT + sumD === 0 && targetCam && targetCam.metrics) {
                            const cumCounts = targetCam.metrics.cumulative_counts || targetCam.metrics.counts || {};
                            sumM = cumCounts.xe_may || 0;
                            sumC = cumCounts.o_to_con || 0;
                            sumB = cumCounts.xe_khach || 0;
                            sumT = cumCounts.xe_tai || 0;
                            sumD = cumCounts.xe_dap || 0;
                        }
                        if (sumM + sumC + sumB + sumT + sumD === 0) {
                            sumM = 1; // tránh chia cho 0 khi đường trống
                        }
                        analyticsVehicleMixChart.data.datasets[0].data = [sumM, sumC, sumB, sumT, sumD];
                        analyticsVehicleMixChart.update("none");
                    }
                }
            }
        } catch (e) {
            console.warn("Lỗi cập nhật biểu đồ phân tích:", e);
        }
    }

    if (el.analyticsCameraSelect) {
        el.analyticsCameraSelect.addEventListener("change", () => {
            syncActiveCamera(el.analyticsCameraSelect.value);
            updateAnalyticsCharts();
        });
    }
    el.pillsRange.forEach(p => {
        p.addEventListener("click", () => {
            el.pillsRange.forEach(b => b.classList.remove("active"));
            p.classList.add("active");
            AppState.analyticsRange = p.dataset.range;
            updateAnalyticsCharts();
        });
    });

    async function updateForecastTab() {
        if (!flowForecastChart) return;
        const camId = el.forecastCamSelect ? el.forecastCamSelect.value : (AppState.inspectedCameraId || "CAM-01");
        const model = el.forecastModelSelect ? el.forecastModelSelect.value : "holt_winters";
        try {
            const res = await fetch(`/api/forecast?camera_id=${camId}&horizon=${AppState.forecastHorizon}&model=${model}`);
            const data = await res.json();
            if (data.success) {
                const hist = data.history || [];
                const fore = data.forecast || [];
                const lower = data.lower_bound || [];
                const upper = data.upper_bound || [];

                const labels = [...hist.map(h => h.time_str), ...fore.map(f => f.time_str)];
                const histData = [...hist.map(h => h.flow), ...fore.map(() => null)];

                const lastVal = hist.length > 0 ? hist[hist.length - 1].flow : null;
                const foreData = [...hist.slice(0, -1).map(() => null), lastVal, ...fore.map(f => f.flow)];
                const lowerData = [...hist.slice(0, -1).map(() => null), lastVal, ...lower.map(l => l.flow)];
                const upperData = [...hist.slice(0, -1).map(() => null), lastVal, ...upper.map(u => u.flow)];

                flowForecastChart.data.labels = labels;
                flowForecastChart.data.datasets[0].data = upperData;
                flowForecastChart.data.datasets[1].data = lowerData;
                flowForecastChart.data.datasets[2].data = histData;
                flowForecastChart.data.datasets[3].data = foreData;
                flowForecastChart.update("none");

                // Update Backtest Metrics Cards
                const m = data.metrics || {};
                el.valMae.textContent = m.mae !== null && m.mae !== undefined ? m.mae : "—";
                el.valRmse.textContent = m.rmse !== null && m.rmse !== undefined ? m.rmse : "—";
                el.valMape.textContent = m.mape !== null && m.mape !== undefined ? `${m.mape}%` : "—";
                el.valSampleCount.textContent = m.sample_count || hist.length;

                el.forecastMetaNote.textContent = data.message ? `[${camId}] ${data.message}` : `Dự báo trạm ${camId} bằng mô hình ${model.toUpperCase()}`;
            }
        } catch (e) {}
    }

    if (el.forecastCamSelect) {
        el.forecastCamSelect.addEventListener("change", () => {
            syncActiveCamera(el.forecastCamSelect.value);
            updateForecastTab();
        });
    }
    if (el.forecastModelSelect) el.forecastModelSelect.addEventListener("change", updateForecastTab);
    el.pillsForecast.forEach(p => {
        p.addEventListener("click", () => {
            el.pillsForecast.forEach(b => b.classList.remove("active"));
            p.classList.add("active");
            AppState.forecastHorizon = parseInt(p.dataset.horizon);
            updateForecastTab();
        });
    });

    // =========================================================================
    // 10. SOURCES TAB & UPLOAD MODAL
    // =========================================================================
    async function loadSourcesTab() {
        if (!el.sourcesCameraGrid) return;

        // Render current camera sources
        el.sourcesCameraGrid.innerHTML = AppState.cameras.map(c => {
            const m = c.metrics || {};
            const queueText = m.queue_vehicles !== undefined ? `${m.queue_vehicles} xe (${m.queue_length_m || 0}m)` : "—";
            return `
            <div class="video-source-card" style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 8px; padding: 14px; display: flex; flex-direction: column; gap: 8px;">
                <div class="vsource-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: var(--accent-blue); font-size: 13px;">${c.id}</strong>
                    <span class="signal-badge ${c.status === 'ONLINE' ? 'normal' : 'danger'}" style="font-size: 10px; padding: 2px 8px;">${c.status}</span>
                </div>
                <div style="font-size: 12px; font-weight: 600; color: var(--text-primary);">${c.name}</div>
                <div class="vsource-file" style="font-size: 11px; color: var(--text-muted); word-break: break-all;">
                    <i data-lucide="map-pin" style="width: 12px; height: 12px; display: inline-block; vertical-align: middle;"></i>
                    ${c.district}
                </div>
                <div style="background: rgba(0,0,0,0.25); border-radius: 6px; padding: 8px; font-size: 11px; display: flex; flex-direction: column; gap: 4px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">Vùng Zone ROI:</span>
                        <span style="color: #10b981; font-weight: 600;">L=${c.length_m}m · W=${c.width_m}m</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">Xe trong Zone:</span>
                        <strong style="color: var(--text-primary);">${m.total_vehicles || 0} xe</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">Hàng chờ:</span>
                        <strong style="color: #f59e0b;">${queueText}</strong>
                    </div>
                </div>
                <div class="vsource-actions" style="margin-top: 4px; display: flex; gap: 8px;">
                    <button class="btn btn-sm btn-outline" style="flex: 1; justify-content: center;" onclick="openUploadForCam('${c.id}')">
                        <i data-lucide="refresh-cw" class="icon-xs"></i> Đổi video
                    </button>
                    <button class="btn btn-sm btn-outline" style="padding: 6px 10px;" onclick="focusCamera('${c.id}')" title="Xem trực tiếp">
                        <i data-lucide="eye" class="icon-xs"></i>
                    </button>
                </div>
            </div>
            `;
        }).join("");

        // Load uploaded videos list
        try {
            const res = await fetch("/api/videos");
            const data = await res.json();
            if (data.success && el.uploadedVideosTableBody) {
                if (data.videos.length === 0) {
                    el.uploadedVideosTableBody.innerHTML = `<tr class="empty-state-row"><td colspan="8">Chưa có video tải lên nào.</td></tr>`;
                } else {
                    el.uploadedVideosTableBody.innerHTML = data.videos.map(v => `
                        <tr>
                            <td><strong>${v.original_name}</strong></td>
                            <td><span class="badge-subtle">${v.camera_id}</span></td>
                            <td class="tabular-nums">${v.duration_sec.toFixed(1)}s</td>
                            <td class="tabular-nums">${v.resolution}</td>
                            <td class="tabular-nums">${v.fps.toFixed(1)}</td>
                            <td class="tabular-nums">${v.file_size_mb.toFixed(1)} MB</td>
                            <td>${v.uploaded_by}</td>
                            <td>
                                <button class="btn btn-sm btn-outline danger" onclick="deleteVideo('${v.id}')">Xóa</button>
                            </td>
                        </tr>
                    `).join("");
                }
            }
        } catch (e) {}
        refreshIcons();
    }

    window.openUploadForCam = function(camId) {
        if (el.modalUploadCamSelect) el.modalUploadCamSelect.value = camId;
        el.uploadModal.style.display = "flex";
    };

    window.deleteVideo = async function(videoId) {
        if (!confirm("Bạn có chắc chắn muốn xóa tệp video này khỏi hệ thống?")) return;
        try {
            const res = await fetch(`/api/videos/${videoId}`, { method: "DELETE" });
            const data = await res.json();
            if (data.success) {
                loadSourcesTab();
            } else {
                alert(data.error || "Không thể xóa video.");
            }
        } catch (e) {
            alert("Lỗi kết nối máy chủ.");
        }
    };

    if (el.btnTriggerUploadModal) {
        el.btnTriggerUploadModal.addEventListener("click", () => {
            el.uploadModal.style.display = "flex";
        });
    }

    function closeUploadModal() {
        el.uploadModal.style.display = "none";
        el.uploadProgressContainer.style.display = "none";
        el.modalVideoFileInput.value = "";
    }

    if (el.btnCloseUploadModal) el.btnCloseUploadModal.addEventListener("click", closeUploadModal);
    if (el.btnCancelUploadModal) el.btnCancelUploadModal.addEventListener("click", closeUploadModal);

    if (el.btnConfirmUpload) {
        el.btnConfirmUpload.addEventListener("click", async () => {
            const file = el.modalVideoFileInput.files[0];
            const camId = el.modalUploadCamSelect.value;
            if (!file) {
                alert("Vui lòng chọn một tệp video từ máy tính!");
                return;
            }

            const formData = new FormData();
            formData.append("file", file);

            el.uploadProgressContainer.style.display = "block";
            el.uploadProgressBar.style.width = "40%";
            el.uploadStatusText.textContent = "Đang tải tệp lên máy chủ...";
            el.btnConfirmUpload.disabled = true;

            try {
                const res = await fetch(`/api/cameras/${camId}/source`, {
                    method: "POST",
                    body: formData
                });
                el.uploadProgressBar.style.width = "100%";

                const data = await res.json();
                if (data.success) {
                    alert(`Thành công: Đã gán video mới cho ${camId} và tạo phiên phân tích mới.`);
                    closeUploadModal();
                    await fetchCameras();
                    loadSourcesTab();
                } else {
                    alert(data.error || "Tải lên không thành công.");
                }
            } catch (e) {
                alert("Lỗi mạng khi tải lên video.");
            } finally {
                el.btnConfirmUpload.disabled = false;
            }
        });
    }

    // =========================================================================
    // 10.1 IMAGE UPLOAD & YOLO AI PREDICT CONTROLLER
    // =========================================================================
    const imageFileInput = document.getElementById("imageFileInput");
    const imageModeSelect = document.getElementById("imageModeSelect");
    const imageConfSlider = document.getElementById("imageConfSlider");
    const lblImageConfVal = document.getElementById("lblImageConfVal");
    const btnAnalyzeImage = document.getElementById("btnAnalyzeImage");
    const imagePreviewArea = document.getElementById("imagePreviewArea");
    const imagePlaceholderText = document.getElementById("imagePlaceholderText");
    const imagePreviewImg = document.getElementById("imagePreviewImg");
    const imageAnalysisResultCard = document.getElementById("imageAnalysisResultCard");
    const imageResultAnnotated = document.getElementById("imageResultAnnotated");

    if (imageConfSlider && lblImageConfVal) {
        imageConfSlider.addEventListener("input", () => {
            lblImageConfVal.textContent = `${imageConfSlider.value}%`;
        });
    }

    if (imageFileInput) {
        imageFileInput.addEventListener("change", () => {
            const file = imageFileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreviewImg.src = e.target.result;
                    imagePreviewImg.style.display = "block";
                    if (imagePlaceholderText) imagePlaceholderText.style.display = "none";
                };
                reader.readAsDataURL(file);
            } else {
                imagePreviewImg.style.display = "none";
                if (imagePlaceholderText) imagePlaceholderText.style.display = "block";
            }
        });
    }

    if (btnAnalyzeImage) {
        btnAnalyzeImage.addEventListener("click", async () => {
            const file = imageFileInput ? imageFileInput.files[0] : null;
            if (!file) {
                alert("Vui lòng chọn một tệp ảnh từ máy tính để phân tích!");
                return;
            }

            const formData = new FormData();
            formData.append("file", file);
            formData.append("mode", imageModeSelect ? imageModeSelect.value : "detection");
            formData.append("conf", (parseFloat(imageConfSlider ? imageConfSlider.value : 25) / 100.0).toString());

            btnAnalyzeImage.disabled = true;
            btnAnalyzeImage.innerHTML = `<span>Đang phân tích YOLO...</span>`;

            try {
                const res = await fetch("/api/predict", {
                    method: "POST",
                    body: formData
                });
                const data = await res.json();
                if (data.success) {
                    if (imageAnalysisResultCard) imageAnalysisResultCard.style.display = "block";
                    if (imageResultAnnotated) imageResultAnnotated.src = data.annotated_image;

                    const elTotal = document.getElementById("resImgTotalVeh");
                    if (elTotal) elTotal.textContent = data.total_vehicles || 0;

                    const elPcu = document.getElementById("resImgPcu");
                    if (elPcu) elPcu.textContent = (data.pcu_score || 0).toFixed(1);

                    const elLat = document.getElementById("resImgLatency");
                    if (elLat) elLat.textContent = `${data.process_time_ms || 0} ms`;

                    const cg = data.congestion || {};
                    const cgBadge = document.getElementById("resImgCongestionBadge");
                    if (cgBadge) {
                        const lvlClass = cg.level === 1 ? "normal" : (cg.level === 2 ? "moderate" : "congested");
                        cgBadge.className = `signal-badge ${lvlClass}`;
                        cgBadge.textContent = cg.name || "Thông thoáng";
                    }

                    const counts = data.counts || {};
                    const setVal = (id, val) => { const e = document.getElementById(id); if (e) e.textContent = val; };
                    setVal("resImgCountMotorcycle", counts.xe_may || 0);
                    setVal("resImgCountCar", counts.o_to_con || 0);
                    setVal("resImgCountBus", counts.xe_khach || 0);
                    setVal("resImgCountTruck", counts.xe_tai || 0);
                    setVal("resImgCountBicycle", counts.xe_dap || 0);

                    refreshIcons();
                    imageAnalysisResultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
                } else {
                    alert(data.error || "Không thể phân tích ảnh.");
                }
            } catch (err) {
                alert("Lỗi kết nối khi gửi ảnh lên máy chủ.");
            } finally {
                btnAnalyzeImage.disabled = false;
                btnAnalyzeImage.innerHTML = `<i data-lucide="sparkles" class="icon-xs"></i> <span>Bắt đầu phân tích hình ảnh</span>`;
                refreshIcons();
            }
        });
    }

    // =========================================================================
    // 11. AUDIT LOGS TAB
    // =========================================================================
    function renderLogsStationsOverview() {
        const grid = document.getElementById("logsStationsGrid");
        if (!grid || !AppState.cameras || AppState.cameras.length === 0) return;

        const currentFilter = el.logFilterCam ? el.logFilterCam.value : "ALL";
        const btnAll = document.getElementById("btnFilterAllLogs");
        if (btnAll) {
            if (currentFilter === "ALL") {
                btnAll.className = "btn btn-sm btn-primary";
            } else {
                btnAll.className = "btn btn-sm btn-outline";
            }
        }

        grid.innerHTML = AppState.cameras.map(c => {
            const m = c.metrics || {};
            const isSelected = currentFilter === c.id;
            const lvl = m.congestion_level || 1;
            const lvlClass = lvl === 1 ? "normal" : (lvl === 2 ? "moderate" : "congested");
            const flowDisplay = m.flow !== null && m.flow !== undefined ? Math.round(m.flow) : 0;
            const densityDisplay = m.density !== null && m.density !== undefined ? Number(m.density).toFixed(1) : "0.0";
            const speedDisplay = m.speed !== null && m.speed !== undefined ? Number(m.speed).toFixed(1) : "0.0";
            const inZone = m.total_vehicles || 0;
            const cumVeh = m.cumulative_vehicles || 0;

            const cardBorder = isSelected 
                ? "border: 2px solid var(--accent-color, #3b82f6); box-shadow: 0 0 12px rgba(59, 130, 246, 0.25); background: rgba(59, 130, 246, 0.05);" 
                : "border: 1px solid var(--border-default); background: var(--bg-panel);";

            return `
                <div class="log-station-card ${isSelected ? 'active-filter' : ''}" 
                     onclick="window.filterLogsByCamera('${c.id}')"
                     title="Nhấp để xem nhật ký của trạm ${c.id}"
                     style="border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s ease; ${cardBorder}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; gap: 6px;">
                        <div>
                            <div style="font-weight: 700; font-size: 13px; color: var(--text-primary); display: flex; align-items: center; gap: 6px;">
                                <span style="background: rgba(59, 130, 246, 0.15); color: #3b82f6; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-family: var(--font-mono); font-weight: 700;">${c.id}</span>
                                <span style="max-width: 135px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${c.name}">${c.name}</span>
                            </div>
                            <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${c.bearing || ''} · ${c.district || 'Giám sát'}</div>
                        </div>
                        <span class="signal-badge ${lvlClass}" style="font-size: 10px; padding: 3px 6px; white-space: nowrap;">${m.congestion_name || 'Thông thoáng'}</span>
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; background: var(--bg-card); padding: 8px; border-radius: 6px; font-size: 11px;">
                        <div>
                            <span style="color: var(--text-muted); font-size: 10px; display: block;">Lưu lượng Q:</span>
                            <span style="font-weight: 600; font-family: var(--font-mono); color: var(--text-primary);">${flowDisplay} xe/h</span>
                        </div>
                        <div>
                            <span style="color: var(--text-muted); font-size: 10px; display: block;">Vận tốc V:</span>
                            <span style="font-weight: 600; font-family: var(--font-mono); color: var(--text-primary);">${speedDisplay} km/h</span>
                        </div>
                        <div>
                            <span style="color: var(--text-muted); font-size: 10px; display: block;">Mật độ K:</span>
                            <span style="font-weight: 600; font-family: var(--font-mono); color: var(--text-primary);">${densityDisplay} xe/km</span>
                        </div>
                        <div>
                            <span style="color: var(--text-muted); font-size: 10px; display: block;">Xe trong zone:</span>
                            <span style="font-weight: 600; font-family: var(--font-mono); color: var(--text-primary);">${inZone} xe (${cumVeh})</span>
                        </div>
                    </div>

                    <div style="margin-top: 8px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: ${isSelected ? '#3b82f6' : 'var(--text-muted)'}; font-weight: ${isSelected ? '600' : '400'};">
                        <span>${isSelected ? '● Đang lọc trạm này' : 'Nhấp để lọc nhật ký'}</span>
                        <i data-lucide="${isSelected ? 'check' : 'chevron-right'}" class="icon-xs"></i>
                    </div>
                </div>
            `;
        }).join("");

        refreshIcons();
    }

    window.filterLogsByCamera = function(camId) {
        if (el.logFilterCam) {
            el.logFilterCam.value = camId;
            if (camId !== "ALL") {
                syncActiveCamera(camId);
            }
        }
        loadLogsTab();
    };

    async function loadLogsTab() {
        renderLogsStationsOverview();
        if (!el.logsTableBody) return;
        const cam = el.logFilterCam ? el.logFilterCam.value : "ALL";
        const lvl = el.logFilterLevel ? el.logFilterLevel.value : "ALL";
        const search = el.logSearchInput ? el.logSearchInput.value : "";

        // Đồng bộ link xuất CSV theo camera và mức độ đang chọn
        if (el.btnExportCsvLogs) {
            el.btnExportCsvLogs.href = `/api/logs/export?camera_id=${cam}&level=${lvl}`;
        }

        try {
            const res = await fetch(`/api/logs?camera_id=${cam}&level=${lvl}&search=${encodeURIComponent(search)}&limit=100`);
            const data = await res.json();
            if (data.success) {
                el.logTotalCount.textContent = `${data.total} bản ghi (${cam === 'ALL' ? 'Tất cả 6 trạm' : cam})`;

                // Update Mini Footer ticker with latest logs
                if (data.logs.length > 0 && el.miniLogTicker) {
                    const top3 = data.logs.slice(0, 3).map(l => `[${l.time_str}] ${l.camera_id || 'Hệ thống'}: ${l.status_text} ${l.flow ? `(${l.flow} xe/h)` : ''}`).join("  |  ");
                    el.miniLogTicker.textContent = top3;
                }

                if (data.logs.length === 0) {
                    el.logsTableBody.innerHTML = `<tr class="empty-state-row"><td colspan="9">Không có bản ghi nhật ký phù hợp cho ${cam === 'ALL' ? 'toàn bộ 6 trạm' : cam}.</td></tr>`;
                    return;
                }

                el.logsTableBody.innerHTML = data.logs.map(l => {
                    const lvlClass = l.status_level === 1 ? "normal" : (l.status_level === 2 ? "moderate" : "congested");
                    return `
                        <tr>
                            <td class="tabular-nums">${l.time_str}</td>
                            <td><span class="badge-subtle">${l.camera_id || 'ALL'}</span></td>
                            <td class="tabular-nums">${l.flow !== null && l.flow !== undefined ? l.flow : '—'}</td>
                            <td class="tabular-nums">${l.density !== null && l.density !== undefined ? l.density : '—'}</td>
                            <td class="tabular-nums">${l.pcu !== null && l.pcu !== undefined ? l.pcu : '—'}</td>
                            <td class="tabular-nums">${l.speed !== null && l.speed !== undefined ? `${l.speed} km/h` : '—'}</td>
                            <td><span class="signal-badge ${lvlClass}">${l.status_text}</span></td>
                            <td>${l.advice || '—'}</td>
                            <td style="color:var(--text-muted); font-size:11px;">${l.details || ''}</td>
                        </tr>
                    `;
                }).join("");
            }
        } catch (e) {}
    }

    if (el.logFilterCam) {
        el.logFilterCam.addEventListener("change", () => {
            if (el.logFilterCam.value !== "ALL") {
                syncActiveCamera(el.logFilterCam.value);
            }
            loadLogsTab();
        });
    }
    if (el.logFilterLevel) el.logFilterLevel.addEventListener("change", loadLogsTab);
    if (el.logSearchInput) el.logSearchInput.addEventListener("input", () => {
        clearTimeout(window._logSearchDebounce);
        window._logSearchDebounce = setTimeout(loadLogsTab, 300);
    });

    if (el.btnClearLogs) {
        el.btnClearLogs.addEventListener("click", async () => {
            if (!confirm("Bạn có chắc chắn muốn xóa toàn bộ lịch sử sự kiện trong SQLite?")) return;
            try {
                const res = await fetch("/api/logs/clear", { method: "POST" });
                const data = await res.json();
                if (data.success) {
                    loadLogsTab();
                } else {
                    alert(data.error || "Không thể xóa nhật ký.");
                }
            } catch (e) {
                alert("Lỗi kết nối.");
            }
        });
    }

    // =========================================================================
    // 12. SETTINGS TAB CONTROLLER (CẤU HÌNH & HIỆU CHUẨN TỪNG CAMERA)
    // =========================================================================
    async function loadSettingsForCamera(camId) {
        if (!camId) camId = el.settingsCamSelect ? el.settingsCamSelect.value : (AppState.inspectedCameraId || "CAM-01");
        
        let cam = AppState.cameras.find(c => c.id === camId);
        
        // Fetch trực tiếp cấu hình chi tiết từ backend
        try {
            const res = await fetch(`/api/cameras/${camId}/config`);
            const data = await res.json();
            if (data.success && data.config) {
                const cfg = data.config;
                if (el.settingsBannerCamId) el.settingsBannerCamId.textContent = cfg.cam_id || camId;
                if (el.settingsBannerCamName) el.settingsBannerCamName.textContent = cfg.name || `Trạm ${camId}`;
                if (el.settingsBannerDistrict) el.settingsBannerDistrict.textContent = cfg.district || '';
                if (el.settingsBannerLanes) el.settingsBannerLanes.textContent = `${cfg.lanes || 4.0}`;
                if (el.settingsBannerCapacity) el.settingsBannerCapacity.textContent = `${Math.round((cfg.lanes || 4.0) * 1800)}`;

                if (el.inputRoiLength) el.inputRoiLength.value = cfg.length_m || 45.0;
                if (el.inputRoiWidth) el.inputRoiWidth.value = cfg.width_m || 14.0;
                if (el.inputFreeThr) el.inputFreeThr.value = cfg.free_thr || 7;
                if (el.inputJamThr) el.inputJamThr.value = cfg.jam_thr || 15;
                if (el.inputJamSpeed) el.inputJamSpeed.value = cfg.jam_speed || 13.0;
                return;
            }
        } catch (e) {}

        // Fallback từ local cache nếu fetch bị chậm
        if (cam) {
            if (el.settingsBannerCamId) el.settingsBannerCamId.textContent = cam.id;
            if (el.settingsBannerCamName) el.settingsBannerCamName.textContent = cam.name;
            if (el.settingsBannerDistrict) el.settingsBannerDistrict.textContent = cam.district || '';
            const lanes = cam.lanes || Math.max(1, (cam.width_m / 3.5).toFixed(1));
            if (el.settingsBannerLanes) el.settingsBannerLanes.textContent = `${lanes}`;
            if (el.settingsBannerCapacity) el.settingsBannerCapacity.textContent = `${Math.round(lanes * 1800)}`;

            if (el.inputRoiLength) el.inputRoiLength.value = cam.length_m || 45.0;
            if (el.inputRoiWidth) el.inputRoiWidth.value = cam.width_m || 14.0;
            if (el.inputFreeThr) el.inputFreeThr.value = cam.free_thr || (cam.metrics && cam.metrics.free_thr ? cam.metrics.free_thr : 7);
            if (el.inputJamThr) el.inputJamThr.value = cam.jam_thr || (cam.metrics && cam.metrics.jam_thr ? cam.metrics.jam_thr : 15);
            if (el.inputJamSpeed) el.inputJamSpeed.value = cam.jam_speed || (cam.metrics && cam.metrics.jam_speed ? cam.metrics.jam_speed : 13.0);
        }
    }

    function loadSettingsTab() {
        const camId = el.settingsCamSelect ? el.settingsCamSelect.value : (AppState.inspectedCameraId || "CAM-01");
        if (el.settingsCamSelect) el.settingsCamSelect.value = camId;
        loadSettingsForCamera(camId);
    }

    if (el.settingsCamSelect) {
        el.settingsCamSelect.addEventListener("change", () => {
            const chosenCam = el.settingsCamSelect.value;
            syncActiveCamera(chosenCam);
            loadSettingsForCamera(chosenCam);
        });
    }

    if (el.btnResetDefaultSettings) {
        el.btnResetDefaultSettings.addEventListener("click", () => {
            const chosenCam = el.settingsCamSelect ? el.settingsCamSelect.value : "CAM-01";
            loadSettingsForCamera(chosenCam);
        });
    }

    if (el.btnSaveSystemSettings) {
        el.btnSaveSystemSettings.addEventListener("click", async () => {
            const camId = el.settingsCamSelect ? el.settingsCamSelect.value : (AppState.inspectedCameraId || "CAM-01");
            const length_m = parseFloat(el.inputRoiLength ? el.inputRoiLength.value : 45) || 45.0;
            const width_m = parseFloat(el.inputRoiWidth ? el.inputRoiWidth.value : 14) || 14.0;
            const free_thr = parseInt(el.inputFreeThr ? el.inputFreeThr.value : 7) || 7;
            const jam_thr = parseInt(el.inputJamThr ? el.inputJamThr.value : 15) || 15;
            const jam_speed = parseFloat(el.inputJamSpeed ? el.inputJamSpeed.value : 13) || 13.0;

            const thrVals = [
                parseFloat(el.inputThrL2.value) || 121,
                parseFloat(el.inputThrL3.value) || 220,
                parseFloat(el.inputThrL4.value) || 350
            ];

            try {
                const res = await fetch(`/api/cameras/${camId}/config`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        length_m: length_m,
                        width_m: width_m,
                        free_thr: free_thr,
                        jam_thr: jam_thr,
                        jam_speed: jam_speed,
                        density_thresholds: thrVals
                    })
                });
                const data = await res.json();
                if (data.success) {
                    AppState.densityThresholds = thrVals;
                    // Cập nhật ngay trong AppState local
                    const c = AppState.cameras.find(x => x.id === camId);
                    if (c) {
                        c.length_m = length_m;
                        c.width_m = width_m;
                        c.lanes = Math.max(1, (width_m / 3.5).toFixed(1));
                        c.free_thr = free_thr;
                        c.jam_thr = jam_thr;
                        c.jam_speed = jam_speed;
                    }
                    loadSettingsForCamera(camId);

                    if (el.settingsSaveStatusText) {
                        el.settingsSaveStatusText.style.display = "inline-flex";
                        setTimeout(() => {
                            if (el.settingsSaveStatusText) el.settingsSaveStatusText.style.display = "none";
                        }, 4000);
                    }
                    refreshIcons();
                } else {
                    alert(data.error || "Không thể lưu cấu hình.");
                }
            } catch (e) {
                alert("Lỗi kết nối khi lưu cấu hình camera.");
            }
        });
    }

    // Sound toggle button
    el.btnSoundToggle.addEventListener("click", () => {
        AppState.soundEnabled = !AppState.soundEnabled;
        el.btnSoundToggle.classList.toggle("btn-primary", AppState.soundEnabled);
        el.lblSound.textContent = AppState.soundEnabled ? "Bật" : "Còi";
        if (!AppState.soundEnabled) {
            el.alarmAudio.pause();
            AppState.alarmActive = false;
        }
    });

    // =========================================================================
    // 13. REAL-TIME SYNCHRONIZER (Non-blocking Polling)
    // =========================================================================
    function startRealtimeStream() {
        // Polling mỗi 1000ms giúp cập nhật dữ liệu camera tức thời mà KHÔNG giữ socket TCP vĩnh viễn,
        // giải phóng hoàn toàn giới hạn 6 kết nối tối đa của trình duyệt (tránh kẹt pending CAM-05/06).
        setInterval(fetchCameras, 1000);
    }

    // Auto-refresh định kỳ cho các biểu đồ động (Real-time dynamic charts)
    setInterval(() => {
        try {
            if (AppState.activeTab === "overview") {
                updateOverviewCharts();
            } else if (AppState.activeTab === "analytics") {
                updateAnalyticsCharts();
            } else if (AppState.activeTab === "forecast") {
                updateForecastTab();
            } else if (AppState.activeTab === "logs") {
                loadLogsTab();
            }
        } catch (err) {}
    }, 3000);

    // Initialize application
    const initialHash = window.location.hash.replace("#", "");
    switchTab(initialHash || "overview");
    fetchCameras();
    startRealtimeStream();
    loadLogsTab();

});

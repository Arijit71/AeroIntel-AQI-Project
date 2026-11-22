document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('aqi-form');
    const aqiScoreEl = document.getElementById('aqi-score');
    const gaugeCircle = document.getElementById('gauge-progress-circle');
    const categoryBanner = document.getElementById('category-banner');
    const categoryNameEl = document.getElementById('category-name');
    const categorySummaryEl = document.getElementById('category-summary');
    const categoryIcon = document.getElementById('category-icon');
    const dominantNameEl = document.getElementById('dominant-pollutant-name');
    const dominantSourceNameEl = document.getElementById('dominant-source-name');
    const healthAdvisoryText = document.getElementById('health-advisory-text');
    const sensitiveAdvisoryText = document.getElementById('sensitive-advisory-text');
    const breakdownBars = document.getElementById('breakdown-bars');
    const ambientGlow = document.getElementById('ambient-glow-primary');

    // Pollutant Identification Elements
    const primaryBadgeEl = document.getElementById('primary-pollutant-badge');
    const primarySymbolEl = document.getElementById('id-primary-symbol');
    const primaryFullnameEl = document.getElementById('id-primary-fullname');
    const primaryConcentrationEl = document.getElementById('id-primary-concentration');
    const primaryUnitEl = document.getElementById('id-primary-unit');
    const primaryRatioEl = document.getElementById('id-primary-ratio');
    const primaryHealthEl = document.getElementById('id-primary-health');
    const exceededCountBadge = document.getElementById('exceeded-count-badge');
    const secondaryPollutantsList = document.getElementById('secondary-pollutants-list');

    // Source Attribution Elements
    const sourceAttributionBars = document.getElementById('source-attribution-bars');
    const sourceDiagnosticText = document.getElementById('source-diagnostic-text');
    const sourceInterventionsList = document.getElementById('source-interventions-list');


    // Telemetry & Airshed Radar Elements
    const selectCity = document.getElementById('select-city');
    const btnDetectGps = document.getElementById('btn-detect-gps');
    const btnSyncRealtime = document.getElementById('btn-sync-realtime');
    const windSpeedText = document.getElementById('wind-speed-text');
    const windDirText = document.getElementById('wind-dir-text');
    const stationProviderBadge = document.getElementById('station-provider-badge');
    const stationNameLabel = document.getElementById('station-name-label');
    const nearbyThreatCount = document.getElementById('nearby-threat-count');
    const nearbyDiagnosticText = document.getElementById('nearby-diagnostic-text');
    const nearbyHotspotsList = document.getElementById('nearby-hotspots-list');

    // Action Controls
    const btnManualSync = document.getElementById('btn-manual-sync');
    const btnDownloadPdf = document.getElementById('btn-download-pdf');

    const GAUGE_CIRCUMFERENCE = 515.22;
    gaugeCircle.style.strokeDasharray = `${GAUGE_CIRCUMFERENCE}`;
    gaugeCircle.style.transition = 'stroke-dashoffset 0.7s ease-out, stroke 0.3s ease';

    let debounceTimer = null;
    let currentDisplayedAqi = 0;
    let latestReport = null;
    let latestNearbyData = null;

    let cityCoordinates = {
        "Delhi": { lat: 28.6139, lon: 77.2090 },
        "Mumbai": { lat: 19.0760, lon: 72.8777 },
        "Bengaluru": { lat: 12.9716, lon: 77.5946 },
        "Kolkata": { lat: 22.5726, lon: 88.3639 },
        "Chennai": { lat: 13.0827, lon: 80.2707 },
        "Hyderabad": { lat: 17.3850, lon: 78.4867 },
        "Ahmedabad": { lat: 23.0225, lon: 72.5714 },
        "Lucknow": { lat: 26.8467, lon: 80.9462 }
    };

    let currentCity = 'Mumbai';
    let currentLat = 19.0760;
    let currentLon = 72.8777;
    let currentWindDir = 240.0;
    let gpsTimeoutId = null;

    let leafletMap = null;
    let markersLayer = null;
    let userCenterMarker = null;


    // Map initialization
    function initMap() {
        const mapContainer = document.getElementById('sources-map');
        if (!mapContainer || typeof L === 'undefined') return;

        try {
            leafletMap = L.map('sources-map', { zoomControl: false, attributionControl: false }).setView([currentLat, currentLon], 11);
            L.control.zoom({ position: 'topright' }).addTo(leafletMap);

            // Free Keyless Dark Tiles (Zero Watermark, High Reliability)
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
                attribution: '&copy; Esri &copy; OpenStreetMap contributors',
                maxZoom: 16
            }).addTo(leafletMap);

            markersLayer = L.layerGroup().addTo(leafletMap);
            updateUserCenterMarker(currentLat, currentLon, currentCity);

            setTimeout(() => {
                if (leafletMap) leafletMap.invalidateSize();
            }, 300);
            window.addEventListener('resize', () => {
                if (leafletMap) leafletMap.invalidateSize();
            });
        } catch (e) {
            console.warn('Map initialization:', e);
        }
    }

    function updateUserCenterMarker(lat, lon, label) {
        if (!leafletMap) return;
        if (userCenterMarker) leafletMap.removeLayer(userCenterMarker);

        const centerIcon = L.divIcon({
            className: 'custom-center-pin',
            html: `
                <div class="relative flex items-center justify-center w-8 h-8">
                    <span class="absolute w-8 h-8 rounded-full bg-sky-500/30 animate-ping"></span>
                    <span class="relative w-4 h-4 rounded-full bg-sky-400 border-2 border-white shadow-lg flex items-center justify-center">
                        <span class="w-1.5 h-1.5 rounded-full bg-white"></span>
                    </span>
                </div>
            `,
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });

        userCenterMarker = L.marker([lat, lon], { icon: centerIcon }).addTo(leafletMap);
        userCenterMarker.bindPopup(`
            <div class="font-sans text-xs p-1">
                <strong class="text-sky-400 font-bold block text-sm">${label}</strong>
                <span class="text-slate-400 text-[11px]">Primary Monitoring Point</span>
            </div>
        `);
    }

    // Nearby sources fetch & render
    async function fetchNearbySources(lat, lon, windDir) {
        try {
            const res = await fetch(`/api/nearby-sources?lat=${lat}&lon=${lon}&radius=35&wind_dir=${windDir || ''}`);
            if (!res.ok) return;
            const json = await res.json();
            if (json.success && json.data) {
                latestNearbyData = json.data;
                renderNearbySources(json.data);
            }
        } catch (err) {
            console.warn('Nearby sources fetch error:', err);
        }
    }

    function getHotspotIconClass(src) {
        let raw = src.icon || '';
        if (!raw) {
            const cat = (src.category || '').toLowerCase();
            if (cat.includes('vehicular') || cat.includes('traffic')) raw = 'ph-car';
            else if (cat.includes('landfill') || cat.includes('waste')) raw = 'ph-fire';
            else if (cat.includes('petrochemical') || cat.includes('power')) raw = 'ph-lightning';
            else if (cat.includes('construction') || cat.includes('dust')) raw = 'ph-hard-hat';
            else raw = 'ph-factory';
        }
        return raw.includes('ph-bold') ? raw : `ph-bold ${raw}`;
    }

    function renderNearbySources(data) {
        if (!data) return;

        const count = data.total_hotspots_found || 0;
        const downwindCount = data.downwind_threat_count || 0;
        if (nearbyThreatCount) {
            nearbyThreatCount.textContent = `${count} facilities (${downwindCount} downwind)`;
            nearbyThreatCount.className = downwindCount > 0 ? "text-rose-400 font-bold text-[10px]" : "text-amber-400 font-bold text-[10px]";
        }
        if (modalThreatBadge) {
            modalThreatBadge.textContent = `${count} facilities (${downwindCount} downwind)`;
            modalThreatBadge.className = downwindCount > 0 ? "text-[10px] font-mono font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2.5 py-1 rounded-full" : "text-[10px] font-mono font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1 rounded-full";
        }

        if (nearbyDiagnosticText) {
            nearbyDiagnosticText.innerHTML = (data.diagnostic_summary || '').replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>');
        }
        if (modalDiagnosticSummary) {
            if (data.hotspots && data.hotspots.length > 0) {
                const closest = data.hotspots[0];
                modalDiagnosticSummary.innerHTML = `Nearest: <strong class="text-white">${closest.name}</strong> (${closest.distance_km} km • ${closest.category})${downwindCount > 0 ? ` • <span class="text-rose-400 font-semibold">${downwindCount} downwind</span>` : ''}`;
            } else {
                modalDiagnosticSummary.textContent = 'No major point sources within 35 km';
            }
        }

        if (markersLayer) markersLayer.clearLayers();
        if (nearbyHotspotsList) nearbyHotspotsList.innerHTML = '';

        const hotspots = data.hotspots || [];
        if (hotspots.length === 0) {
            if (nearbyHotspotsList) {
                nearbyHotspotsList.innerHTML = `<div class="p-3 text-center text-xs text-slate-500 font-mono italic">No major point sources recorded within 35 km.</div>`;
            }
            return;
        }

        hotspots.forEach(src => {
            const color = src.color || '#F59E0B';
            const iconClass = getHotspotIconClass(src);

            if (markersLayer) {
                const pinIcon = L.divIcon({
                    className: 'hotspot-pin',
                    html: `
                        <div class="relative group cursor-pointer transition-transform hover:scale-125" style="filter: drop-shadow(0 0 6px ${color}88);">
                            <div class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs border border-white/40" style="background-color: ${color};">
                                <i class="${iconClass}"></i>
                            </div>
                        </div>
                    `,
                    iconSize: [28, 28],
                    iconAnchor: [14, 14]
                });

                const marker = L.marker([src.lat, src.lon], { icon: pinIcon }).addTo(markersLayer);
                const windTagColor = src.wind_level === 'downwind' ? '#EF4444' : (src.wind_level === 'crosswind' ? '#F59E0B' : '#10B981');

                marker.bindPopup(`
                    <div class="p-1 font-sans text-xs max-w-xs">
                        <div class="font-bold text-white text-sm leading-tight">${src.name}</div>
                        <div class="flex items-center gap-2 mt-1">
                            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold" style="background: ${color}22; color: ${color}; border: 1px solid ${color}55;">
                                ${src.category}
                            </span>
                            <span class="text-slate-400 font-mono text-[11px]">${src.distance_km} km away</span>
                        </div>
                        <div class="mt-2 text-[11px] text-slate-300 font-medium">
                            <span style="color: ${windTagColor}; font-weight: bold;">${src.wind_alignment}</span>
                        </div>
                        <p class="text-[11px] text-slate-400 mt-1 leading-snug">${src.description}</p>
                    </div>
                `);

                src._marker = marker;
            }
        });

        if (nearbyHotspotsList) {
            nearbyHotspotsList.innerHTML = '';
            // Display top stationary facilities cleanly (4 facilities provides pristine balance)
            const displayHotspots = hotspots.slice(0, 4);

            displayHotspots.forEach(src => {
                const color = src.color || '#F59E0B';
                const iconClass = getHotspotIconClass(src);

                const card = document.createElement('div');
                card.className = 'hotspot-card group p-2.5 sm:p-3 rounded-xl bg-obsidian-950/70 hover:bg-obsidian-900/90 border border-white/[0.08] hover:border-sky-400/50 transition-all duration-200 cursor-pointer flex items-center justify-between gap-3 shadow-sm';

                const isDownwind = src.wind_level === 'downwind';
                const windBadgeClass = isDownwind 
                    ? "bg-rose-500/10 text-rose-400 border-rose-500/30 font-bold" 
                    : (src.wind_level === 'crosswind' ? "bg-amber-500/10 text-amber-400 border-amber-500/30" : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30");

                const pollutantsSummary = src.key_pollutants && src.key_pollutants.length > 0 
                    ? src.key_pollutants.slice(0, 3).join(', ') 
                    : 'Emissions monitored';

                card.innerHTML = `
                    <div class="flex items-center gap-3 min-w-0">
                        <div class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 border transition-transform group-hover:scale-105 shadow-sm" style="background-color: ${color}20; border-color: ${color}50; color: ${color};">
                            <i class="${iconClass} text-lg"></i>
                        </div>
                        <div class="min-w-0 flex flex-col justify-center">
                            <span class="font-heading font-bold text-xs text-white group-hover:text-sky-300 transition-colors truncate leading-tight">${src.name}</span>
                            <span class="text-[10px] text-slate-400 font-mono truncate mt-0.5">${src.category} • ${pollutantsSummary}</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 shrink-0">
                        <span class="px-2.5 py-1 rounded-lg bg-white/[0.05] text-slate-200 font-mono text-[10px] font-bold">${src.distance_km} km</span>
                        <span class="px-2.5 py-1 rounded-lg border ${windBadgeClass} text-[9px] font-bold font-mono">${src.wind_alignment.split('(')[0].trim()}</span>
                    </div>
                `;

                card.addEventListener('click', () => {
                    // 1. Tactile active state on clicked card
                    document.querySelectorAll('.hotspot-card').forEach(c => {
                        c.classList.remove('ring-2', 'ring-sky-400', 'bg-sky-500/20', 'border-sky-400', 'shadow-[0_0_15px_rgba(56,189,248,0.25)]');
                    });
                    card.classList.add('ring-2', 'ring-sky-400', 'bg-sky-500/20', 'border-sky-400', 'shadow-[0_0_15px_rgba(56,189,248,0.25)]');

                    // 2. Bring map into view if off-screen
                    const mapContainer = document.getElementById('sources-map');
                    if (mapContainer) {
                        const rect = mapContainer.getBoundingClientRect();
                        if (rect.top < 60 || rect.bottom > window.innerHeight) {
                            mapContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }

                    // 3. Immediately focus and open popup on the Leaflet map
                    if (leafletMap && src.lat && src.lon) {
                        leafletMap.invalidateSize();
                        leafletMap.setView([src.lat, src.lon], 13);
                        if (src._marker) {
                            src._marker.openPopup();
                        }
                    }

                    // 4. Update the diagnostic text above with rich immediate visual confirmation
                    if (nearbyDiagnosticText) {
                        const windColor = src.wind_level === 'downwind' ? '#EF4444' : (src.wind_level === 'crosswind' ? '#F59E0B' : '#10B981');
                        nearbyDiagnosticText.innerHTML = `
                            <div class="flex flex-col gap-1 w-full">
                                <div class="flex items-center justify-between">
                                    <span class="text-sky-400 font-bold flex items-center gap-1.5 text-xs"><i class="ph-bold ph-crosshair animate-pulse"></i> Focused Facility Telemetry</span>
                                    <span class="text-[10px] font-mono font-bold" style="color: ${windColor}">${src.wind_alignment}</span>
                                </div>
                                <div class="text-white font-bold text-xs">${src.name} <span class="text-slate-400 font-normal font-mono">(${src.category} • ${src.distance_km} km away)</span></div>
                                <p class="text-[11px] text-slate-300 leading-snug mt-0.5">${src.description}</p>
                            </div>
                        `;
                    }
                    if (modalDiagnosticSummary) {
                        const windColor = src.wind_level === 'downwind' ? '#EF4444' : (src.wind_level === 'crosswind' ? '#F59E0B' : '#10B981');
                        modalDiagnosticSummary.innerHTML = `Focused: <strong class="text-white">${src.name}</strong> • ${src.distance_km} km • <span style="color: ${windColor}">${src.wind_alignment}</span>`;
                    }
                });

                if (src._marker) {
                    src._marker.on('click', () => {
                        document.querySelectorAll('.hotspot-card').forEach(c => {
                            c.classList.remove('ring-2', 'ring-sky-400', 'bg-sky-500/20', 'border-sky-400', 'shadow-[0_0_15px_rgba(56,189,248,0.25)]');
                        });
                        card.classList.add('ring-2', 'ring-sky-400', 'bg-sky-500/20', 'border-sky-400', 'shadow-[0_0_15px_rgba(56,189,248,0.25)]');
                        if (nearbyDiagnosticText) {
                            const windColor = src.wind_level === 'downwind' ? '#EF4444' : (src.wind_level === 'crosswind' ? '#F59E0B' : '#10B981');
                            nearbyDiagnosticText.innerHTML = `
                                <div class="flex flex-col gap-1 w-full">
                                    <div class="flex items-center justify-between">
                                        <span class="text-sky-400 font-bold flex items-center gap-1.5 text-xs"><i class="ph-bold ph-crosshair animate-pulse"></i> Focused Facility Telemetry</span>
                                        <span class="text-[10px] font-mono font-bold" style="color: ${windColor}">${src.wind_alignment}</span>
                                    </div>
                                    <div class="text-white font-bold text-xs">${src.name} <span class="text-slate-400 font-normal font-mono">(${src.category} • ${src.distance_km} km away)</span></div>
                                    <p class="text-[11px] text-slate-300 leading-snug mt-0.5">${src.description}</p>
                                </div>
                            `;
                        }
                        if (modalDiagnosticSummary) {
                            const windColor = src.wind_level === 'downwind' ? '#EF4444' : (src.wind_level === 'crosswind' ? '#F59E0B' : '#10B981');
                            modalDiagnosticSummary.innerHTML = `Focused: <strong class="text-white">${src.name}</strong> • ${src.distance_km} km • <span style="color: ${windColor}">${src.wind_alignment}</span>`;
                        }
                    });
                }

                nearbyHotspotsList.appendChild(card);
            });
        }
    }

    let isManualTelemetry = false;
    let lastSyncedStationName = 'Bandra Kurla Complex (MPCB)';
    let lastSyncedCity = 'Mumbai';

    function setManualTelemetryMode() {
        // 0. Always reset GPS button and active state when parameters are manually modified
        isGpsActive = false;
        clearTimeout(gpsTimeoutId);
        if (btnDetectGps) {
            btnDetectGps.classList.remove('border-sky-400', 'bg-sky-500/20', 'text-white');
            btnDetectGps.innerHTML = '<i class="ph-bold ph-crosshair"></i> <span class="hidden sm:inline">GPS</span>';
        }

        if (isManualTelemetry) return;
        isManualTelemetry = true;

        // 1. Update Station Provider Badge
        const stationDot = document.getElementById('station-status-dot');
        const stationPrefix = document.getElementById('station-prefix-label');
        if (stationDot) {
            stationDot.className = 'w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0';
        }
        if (stationPrefix) {
            stationPrefix.textContent = 'Mode:';
        }
        if (stationNameLabel) {
            stationNameLabel.textContent = 'Manual';
            stationNameLabel.className = 'text-amber-300 font-semibold truncate max-w-[130px] sm:max-w-[170px] md:max-w-[210px] lg:max-w-[260px]';
            stationNameLabel.title = 'Manual parameter simulation';
        }
        if (stationProviderBadge) {
            stationProviderBadge.title = "Manual parameter simulation • Click 'Sync Station' to restore live telemetry";
        }

        // 2. Update City Dropdown to indicate Manual
        if (selectCity) {
            let manualOpt = selectCity.querySelector('option[value="manual"]');
            if (!manualOpt) {
                manualOpt = document.createElement('option');
                manualOpt.value = 'manual';
                manualOpt.textContent = 'Manual';
                manualOpt.disabled = true;
                manualOpt.hidden = true;
                selectCity.insertBefore(manualOpt, selectCity.firstChild);
            }
            selectCity.value = 'manual';
        }

        // 3. Update Matrix Header Badge
        const matrixModeDot = document.getElementById('matrix-mode-dot');
        const matrixModeText = document.getElementById('matrix-mode-text');
        const matrixModeBadge = document.getElementById('matrix-mode-badge');
        if (matrixModeBadge) {
            matrixModeBadge.className = 'text-[10px] font-mono text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2.5 py-0.5 rounded-full flex items-center gap-1.5';
        }
        if (matrixModeDot) {
            matrixModeDot.className = 'w-1.5 h-1.5 rounded-full bg-amber-400';
        }
        if (matrixModeText) {
            matrixModeText.textContent = 'Manual';
        }

        // 4. Update Engine Sync Tile
        const engineSyncDot = document.getElementById('engine-sync-dot');
        const engineSyncDesc = document.getElementById('engine-sync-desc');
        if (engineSyncDot) {
            engineSyncDot.className = 'w-1.5 h-1.5 rounded-full bg-amber-400';
        }
        if (engineSyncDesc) {
            engineSyncDesc.textContent = 'Manual parameter simulation';
        }
    }

    function setLiveTelemetryMode(stationName, city) {
        isManualTelemetry = false;
        if (stationName) lastSyncedStationName = stationName;
        if (city) lastSyncedCity = city;

        // 1. Update Station Provider Badge
        const stationDot = document.getElementById('station-status-dot');
        const stationPrefix = document.getElementById('station-prefix-label');
        if (stationDot) {
            stationDot.className = 'w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shrink-0';
        }
        if (stationPrefix) {
            stationPrefix.textContent = 'Station:';
        }
        if (stationNameLabel) {
            stationNameLabel.textContent = lastSyncedStationName || `${city || 'Ambient'} Station`;
            stationNameLabel.className = 'text-slate-200 font-medium truncate max-w-[130px] sm:max-w-[170px] md:max-w-[210px] lg:max-w-[260px]';
            stationNameLabel.title = lastSyncedStationName || '';
        }
        if (stationProviderBadge) {
            stationProviderBadge.title = `Live station telemetry: ${lastSyncedStationName}`;
        }

        // 2. Restore City Dropdown
        if (selectCity) {
            if (isGpsActive) {
                selectCity.value = 'GPS';
            } else if (lastSyncedCity) {
                selectCity.value = lastSyncedCity;
            }
        }

        // 3. Update Matrix Header Badge
        const matrixModeDot = document.getElementById('matrix-mode-dot');
        const matrixModeText = document.getElementById('matrix-mode-text');
        const matrixModeBadge = document.getElementById('matrix-mode-badge');
        if (matrixModeBadge) {
            matrixModeBadge.className = 'text-[10px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2.5 py-0.5 rounded-full flex items-center gap-1.5';
        }
        if (matrixModeDot) {
            matrixModeDot.className = 'w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse';
        }
        if (matrixModeText) {
            matrixModeText.textContent = 'Dynamic';
        }

        // 4. Update Engine Sync Tile
        const engineSyncDot = document.getElementById('engine-sync-dot');
        const engineSyncDesc = document.getElementById('engine-sync-desc');
        if (engineSyncDot) {
            engineSyncDot.className = 'w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse';
        }
        if (engineSyncDesc) {
            engineSyncDesc.textContent = 'Live telemetry feedback loop';
        }
    }

    // Real-time station telemetry sync
    async function syncRealtimeStationData(city, lat, lon, updateInputs = true) {
        if (btnSyncRealtime && updateInputs) {
            btnSyncRealtime.innerHTML = `<i class="ph-bold ph-spinner text-sky-400 animate-spin shrink-0"></i><span class="whitespace-nowrap">Syncing...</span>`;
            btnSyncRealtime.disabled = true;
        }

        try {
            const res = await fetch(`/api/realtime-air-quality?city=${encodeURIComponent(city)}&lat=${lat}&lon=${lon}`);
            if (!res.ok) throw new Error('Failed to fetch real-time data');

            const json = await res.json();
            if (json.success && json.telemetry) {
                const tel = json.telemetry;

                // 1. Update station label and restore live telemetry mode
                const stationName = tel.station_name || `${city} Ambient Station`;
                setLiveTelemetryMode(stationName, city);
                
                // 2. Update wind telemetry
                if (windSpeedText) windSpeedText.textContent = `${tel.wind_speed_kmh} km/h`;
                const compassStr = tel.wind_compass || (tel.meteorology && tel.meteorology.compass) || 'N/A';
                if (windDirText) windDirText.textContent = `${tel.wind_direction_deg}° (${compassStr})`;
                currentWindDir = tel.wind_direction_deg || 295.0;

                const windCompassIcon = document.getElementById('wind-compass-icon');
                if (windCompassIcon) {
                    windCompassIcon.style.transition = 'transform 0.5s ease';
                    windCompassIcon.style.transform = `rotate(${currentWindDir}deg)`;
                }

                // 3. Update all criteria pollutant inputs and range sliders with real-time API values
                if (updateInputs) {
                    const pollData = tel.pollutants || {};
                    const mapping = {
                        "PM2.5": pollData.pm25 !== undefined ? pollData.pm25 : pollData["PM2.5"],
                        "PM10": pollData.pm10 !== undefined ? pollData.pm10 : pollData["PM10"],
                        "NO": pollData.no !== undefined ? pollData.no : pollData["NO"],
                        "NO2": pollData.no2 !== undefined ? pollData.no2 : pollData["NO2"],
                        "NOx": pollData.nox !== undefined ? pollData.nox : pollData["NOx"],
                        "NH3": pollData.nh3 !== undefined ? pollData.nh3 : pollData["NH3"],
                        "CO": pollData.co !== undefined ? pollData.co : pollData["CO"],
                        "SO2": pollData.so2 !== undefined ? pollData.so2 : pollData["SO2"],
                        "O3": pollData.o3 !== undefined ? pollData.o3 : pollData["O3"],
                        "Benzene": pollData.benzene !== undefined ? pollData.benzene : pollData["Benzene"],
                        "Toluene": pollData.toluene !== undefined ? pollData.toluene : pollData["Toluene"]
                    };

                    Object.keys(mapping).forEach(key => {
                        const val = mapping[key];
                        if (val !== undefined && val !== null) {
                            const numInput = document.getElementById(`num-${key}`);
                            const sliderInput = document.getElementById(`slider-${key}`);
                            if (numInput) numInput.value = val;
                            if (sliderInput) {
                                sliderInput.value = val;
                                updateSliderFill(sliderInput);
                            }
                        }
                    });

                    // 4. Immediately recalculate AQI model prediction with fresh real-time data
                    await requestPrediction();
                }

                // 5. Update nearby point sources and recalculate plume alignment vectors
                await fetchNearbySources(lat, lon, currentWindDir);

                if (btnSyncRealtime && updateInputs) {
                    btnSyncRealtime.innerHTML = `<i class="ph-bold ph-check text-emerald-400 shrink-0"></i><span class="whitespace-nowrap">Synced!</span>`;
                    setTimeout(() => {
                        btnSyncRealtime.innerHTML = `<i class="ph-bold ph-broadcast text-sky-400 animate-pulse shrink-0"></i><span class="whitespace-nowrap">Sync Station</span>`;
                        btnSyncRealtime.disabled = false;
                    }, 2000);
                }
            }
        } catch (err) {
            console.error('Real-time sync error:', err);
            if (btnSyncRealtime && updateInputs) {
                btnSyncRealtime.innerHTML = `<i class="ph-bold ph-warning text-amber-400 shrink-0"></i><span class="whitespace-nowrap">Offline</span>`;
                setTimeout(() => {
                    btnSyncRealtime.innerHTML = `<i class="ph-bold ph-broadcast text-sky-400 animate-pulse shrink-0"></i><span class="whitespace-nowrap">Sync Station</span>`;
                    btnSyncRealtime.disabled = false;
                }, 2000);
            }
        }
    }

    if (btnSyncRealtime) {
        btnSyncRealtime.addEventListener('click', () => {
            syncRealtimeStationData(currentCity, currentLat, currentLon);
        });
    }

    let isGpsActive = false;
    let currentGpsLabel = "GPS Location";
    let deviceGpsCoords = null;

    async function resolveGpsLocality(lat, lon) {
        // 1. Try local server-side reverse geocode endpoint (CORS-immune)
        try {
            const res = await fetch(`/api/reverse-geocode?lat=${lat}&lon=${lon}`);
            if (res.ok) {
                const data = await res.json();
                if (data.success && data.locality) {
                    return data.locality;
                }
            }
        } catch (e) {
            // pass
        }

        // 2. Try direct BigDataCloud API
        try {
            const res = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
            if (res.ok) {
                const data = await res.json();
                const locality = data.locality || data.city || data.principalSubdivision;
                if (locality) return locality;
            }
        } catch (e) {
            // pass
        }

        // 3. Try OpenStreetMap Nominatim
        try {
            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=14`);
            if (res.ok) {
                const data = await res.json();
                const addr = data.address || {};
                const locality = addr.suburb || addr.town || addr.city_district || addr.city || addr.village || addr.county;
                if (locality) return locality;
            }
        } catch (e) {
            // pass
        }

        return null;
    }

    function findClosestCity(lat, lon) {
        let closest = null;
        let minDistance = Infinity;

        for (const [cityName, info] of Object.entries(cityCoordinates)) {
            const dLat = (info.lat - lat) * Math.PI / 180;
            const dLon = (info.lon - lon) * Math.PI / 180;
            const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                      Math.cos(lat * Math.PI / 180) * Math.cos(info.lat * Math.PI / 180) *
                      Math.sin(dLon / 2) * Math.sin(dLon / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            const dist = 6371 * c;

            if (dist < minDistance) {
                minDistance = dist;
                closest = { city: cityName, name: info.name || cityName, distance: dist };
            }
        }
        return closest;
    }

    // City & GPS Handlers
    if (selectCity) {
        selectCity.addEventListener('change', () => {
            const city = selectCity.value;
            if (city === 'manual') return;

            if (city === 'GPS') {
                isGpsActive = true;
                if (btnDetectGps) {
                    btnDetectGps.classList.add('border-sky-400', 'bg-sky-500/20', 'text-white');
                    btnDetectGps.innerHTML = '<i class="ph-bold ph-crosshair text-sky-400"></i> <span class="hidden sm:inline">GPS Active</span>';
                }
                if (deviceGpsCoords) {
                    currentLat = deviceGpsCoords.lat;
                    currentLon = deviceGpsCoords.lon;
                    if (leafletMap) {
                        leafletMap.flyTo([currentLat, currentLon], 12, { duration: 1.0 });
                        updateUserCenterMarker(currentLat, currentLon, currentGpsLabel);
                    }
                    syncRealtimeStationData(currentCity, currentLat, currentLon, true);
                } else if (btnDetectGps) {
                    btnDetectGps.click();
                }
                return;
            }

            // Standard city selected
            isGpsActive = false;
            clearTimeout(gpsTimeoutId);
            if (btnDetectGps) {
                btnDetectGps.classList.remove('border-sky-400', 'bg-sky-500/20', 'text-white');
                btnDetectGps.innerHTML = '<i class="ph-bold ph-crosshair"></i> <span class="hidden sm:inline">GPS</span>';
            }

            currentCity = city;
            if (cityCoordinates[city]) {
                currentLat = cityCoordinates[city].lat;
                currentLon = cityCoordinates[city].lon;

                if (leafletMap) {
                    leafletMap.flyTo([currentLat, currentLon], 11, { duration: 1.0 });
                    updateUserCenterMarker(currentLat, currentLon, cityCoordinates[city].name || currentCity);
                }

                syncRealtimeStationData(currentCity, currentLat, currentLon, true);
            }
        });
    }

    if (btnDetectGps) {
        btnDetectGps.addEventListener('click', () => {
            if (!navigator.geolocation) {
                alert('Geolocation is not supported by your browser.');
                return;
            }

            clearTimeout(gpsTimeoutId);
            const originalBtn = btnDetectGps.innerHTML;
            btnDetectGps.innerHTML = '<i class="ph-bold ph-spinner animate-spin"></i> Locating...';

            navigator.geolocation.getCurrentPosition(
                async (pos) => {
                    isGpsActive = true;
                    currentLat = parseFloat(pos.coords.latitude.toFixed(4));
                    currentLon = parseFloat(pos.coords.longitude.toFixed(4));
                    deviceGpsCoords = { lat: currentLat, lon: currentLon };

                    // 1. Calculate closest metropolitan airshed (for baseline modeling)
                    const closest = findClosestCity(currentLat, currentLon);
                    currentCity = closest ? closest.city : 'Delhi';

                    // 2. Initial GPS label based on coordinates or proximity
                    currentGpsLabel = closest && closest.distance <= 80 ? `GPS: ${closest.name || closest.city}` : `GPS (${currentLat.toFixed(2)}°, ${currentLon.toFixed(2)}°)`;

                    // 3. Update the City dropdown (<select id="select-city">)
                    if (selectCity) {
                        let gpsOption = selectCity.querySelector('option[value="GPS"]');
                        if (!gpsOption) {
                            gpsOption = document.createElement('option');
                            gpsOption.value = 'GPS';
                            selectCity.insertBefore(gpsOption, selectCity.firstChild);
                        }
                        gpsOption.textContent = currentGpsLabel;
                        gpsOption.selected = true;
                        selectCity.value = 'GPS';
                    }

                    // 4. Highlight GPS button state
                    btnDetectGps.innerHTML = '<i class="ph-bold ph-check text-emerald-400"></i> <span class="hidden sm:inline">Located</span>';
                    btnDetectGps.classList.add('border-sky-400', 'bg-sky-500/20', 'text-white');
                    gpsTimeoutId = setTimeout(() => {
                        if (isGpsActive && selectCity && selectCity.value === 'GPS' && btnDetectGps) {
                            btnDetectGps.innerHTML = '<i class="ph-bold ph-crosshair text-sky-400"></i> <span class="hidden sm:inline">GPS Active</span>';
                        }
                    }, 2000);

                    // 5. Center map and drop marker
                    if (leafletMap) {
                        leafletMap.flyTo([currentLat, currentLon], 12, { duration: 1.0 });
                        updateUserCenterMarker(currentLat, currentLon, currentGpsLabel);
                    }

                    // 6. Launch reverse geocode refinement in parallel
                    resolveGpsLocality(currentLat, currentLon).then(locality => {
                        if (locality) {
                            currentGpsLabel = `GPS: ${locality}`;
                            if (selectCity) {
                                const opt = selectCity.querySelector('option[value="GPS"]');
                                if (opt) opt.textContent = currentGpsLabel;
                                if (isGpsActive) selectCity.value = 'GPS';
                            }
                            if (userCenterMarker && isGpsActive) {
                                updateUserCenterMarker(currentLat, currentLon, currentGpsLabel);
                            }
                        }
                    });

                    // 7. Synchronize real-time station telemetry and nearby sources
                    await syncRealtimeStationData(currentCity, currentLat, currentLon, true);

                    // 8. Ensure GPS mode selection is strictly preserved
                    if (isGpsActive && selectCity) {
                        selectCity.value = 'GPS';
                    }
                },
                (err) => {
                    console.warn('Geolocation error:', err);
                    isGpsActive = false;
                    clearTimeout(gpsTimeoutId);
                    if (btnDetectGps) {
                        btnDetectGps.classList.remove('border-sky-400', 'bg-sky-500/20', 'text-white');
                        btnDetectGps.innerHTML = '<i class="ph-bold ph-crosshair"></i> <span class="hidden sm:inline">GPS</span>';
                    }
                    alert('Could not retrieve GPS location. Please verify browser location permissions.');
                },
                { enableHighAccuracy: true, timeout: 8000 }
            );
        });
    }

    fetch('/api/cities')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.cities) cityCoordinates = data.cities;
        })
        .catch(err => console.warn('Cities error:', err));

    function updateSliderFill(slider) {
        if (!slider) return;
        const min = parseFloat(slider.min) || 0;
        const max = parseFloat(slider.max) || 100;
        const val = parseFloat(slider.value) || 0;
        const pct = Math.max(0, Math.min(100, ((val - min) / (max - min)) * 100));
        slider.style.background = `linear-gradient(to right, rgba(245, 158, 11, 0.75) 0%, rgba(245, 158, 11, 0.75) ${pct}%, rgba(255, 255, 255, 0.08) ${pct}%, rgba(255, 255, 255, 0.08) 100%)`;
    }

    function updateAllSliderFills() {
        document.querySelectorAll('.pollutant-slider').forEach(s => updateSliderFill(s));
    }

    const pollutantCards = document.querySelectorAll('.pollutant-card');
    pollutantCards.forEach(card => {
        const numInput = card.querySelector('.pollutant-number-input');
        const sliderInput = card.querySelector('.pollutant-slider');

        if (numInput && sliderInput) {
            updateSliderFill(sliderInput);
            sliderInput.addEventListener('input', () => {
                numInput.value = sliderInput.value;
                updateSliderFill(sliderInput);
                setManualTelemetryMode();
                triggerPredictionDebounced();
            });
            numInput.addEventListener('input', () => {
                sliderInput.value = numInput.value;
                updateSliderFill(sliderInput);
                setManualTelemetryMode();
                triggerPredictionDebounced();
            });
            numInput.addEventListener('change', () => {
                sliderInput.value = numInput.value;
                updateSliderFill(sliderInput);
                setManualTelemetryMode();
                triggerPredictionDebounced();
            });
        }
    });

    if (btnManualSync) {
        btnManualSync.addEventListener('click', () => {
            const icon = btnManualSync.querySelector('i');
            if (icon) icon.classList.add('animate-spin');
            requestPrediction().finally(() => {
                setTimeout(() => {
                    if (icon) icon.classList.remove('animate-spin');
                }, 400);
            });
        });
    }

    function triggerPredictionDebounced() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => requestPrediction(), 180);
    }

    function getFormData() {
        const data = {};
        const inputs = form.querySelectorAll('.pollutant-number-input');
        inputs.forEach(input => {
            data[input.name] = parseFloat(input.value) || 0;
        });
        return data;
    }

    // Prediction request
    async function requestPrediction() {
        const payload = getFormData();
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) return;
            const result = await response.json();
            if (result.success && result.report) {
                latestReport = result.report;
                updateUIWithReport(result.report);
            }
        } catch (error) {
            console.error('Prediction fetch error:', error);
        }
    }

    function updateUIWithReport(report) {
        animateAqiNumber(report.aqi);
        updateGauge(report.aqi, report.category_color);

        if (ambientGlow) ambientGlow.style.backgroundColor = `${report.category_color}18`;

        categoryNameEl.textContent = report.category;
        categoryNameEl.style.color = report.category_color;
        categorySummaryEl.textContent = report.summary;
        categoryBanner.style.borderColor = `${report.category_color}55`;
        categoryBanner.style.backgroundColor = `${report.category_color}15`;

        categoryIcon.style.color = report.category_color;
        categoryIcon.style.backgroundColor = `${report.category_color}25`;

        let iconClass = 'ph-shield-warning';
        const catLower = (report.category || '').toLowerCase();
        if (catLower.includes('good') || catLower.includes('satisfactory')) {
            iconClass = 'ph-shield-check';
        } else if (catLower.includes('moderate')) {
            iconClass = 'ph-shield-warning';
        } else if (catLower.includes('very poor')) {
            iconClass = 'ph-warning-octagon';
        } else if (catLower.includes('poor')) {
            iconClass = 'ph-warning';
        } else if (catLower.includes('severe')) {
            iconClass = 'ph-skull';
        }
        categoryIcon.innerHTML = `<i class="ph-bold ${iconClass}"></i>`;

        dominantNameEl.textContent = report.dominant_pollutant;
        dominantNameEl.style.color = report.category_color;

        healthAdvisoryText.textContent = report.health_advisory;
        sensitiveAdvisoryText.textContent = report.sensitive_advisory;

        renderSubIndices(report.sub_indices);

        if (report.pollutant_identification) renderPollutantIdentification(report.pollutant_identification);
        if (report.source_attribution) renderSourceAttribution(report.source_attribution);
    }

    function renderPollutantIdentification(pollutantId) {
        const primary = pollutantId.primary_driver;
        if (primary) {
            primarySymbolEl.textContent = primary.key;
            primaryFullnameEl.textContent = primary.name;
            primaryConcentrationEl.textContent = primary.concentration;
            primaryUnitEl.textContent = primary.unit;
            primaryRatioEl.textContent = `(${primary.exceedance_ratio}× NAAQS)`;
            primaryHealthEl.textContent = primary.health_impact;

            primaryBadgeEl.textContent = primary.status;
            primaryBadgeEl.style.color = primary.badge_color;
            primaryBadgeEl.style.backgroundColor = primary.badge_bg;
            primaryBadgeEl.style.borderColor = `${primary.badge_color}55`;
        }

        const count = pollutantId.total_exceeded || 0;
        exceededCountBadge.textContent = `${count} standard breach${count === 1 ? '' : 'es'}`;
        exceededCountBadge.className = count > 0 ? "text-amber-400 font-bold" : "text-emerald-400 font-bold";

        secondaryPollutantsList.innerHTML = '';
        const secondaries = pollutantId.secondary_drivers || [];
        if (secondaries.length === 0) {
            const emptyNotice = document.createElement('span');
            emptyNotice.className = 'text-[11px] text-slate-500 font-mono italic';
            emptyNotice.textContent = 'All secondary pollutants within safe threshold.';
            secondaryPollutantsList.appendChild(emptyNotice);
        } else {
            secondaries.forEach(sec => {
                const badge = document.createElement('span');
                badge.className = 'inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[10px] font-mono border transition';
                badge.style.color = sec.badge_color;
                badge.style.backgroundColor = sec.badge_bg;
                badge.style.borderColor = `${sec.badge_color}44`;
                badge.innerHTML = `<strong>${sec.key}</strong>: ${sec.concentration} ${sec.unit} <span class="opacity-75">(${sec.exceedance_ratio}×)</span>`;
                secondaryPollutantsList.appendChild(badge);
            });
        }
    }

    function renderSourceAttribution(sourceData) {
        if (!sourceData) return;

        const top = sourceData.dominant_source;
        if (top && dominantSourceNameEl) {
            dominantSourceNameEl.textContent = `${top.name} (${top.percentage}%)`;
        }

        sourceAttributionBars.innerHTML = '';
        const breakdown = sourceData.sources_breakdown || [];
        breakdown.forEach(src => {
            const row = document.createElement('div');
            row.className = 'flex flex-col gap-1';
            row.innerHTML = `
                <div class="flex items-center justify-between text-xs font-mono">
                    <span class="flex items-center gap-1.5 text-slate-300">
                        <i class="${src.icon}" style="color: ${src.color}"></i>
                        <span class="font-medium">${src.name}</span>
                    </span>
                    <span class="font-bold text-white font-mono">${src.percentage}%</span>
                </div>
                <div class="w-full h-2 bg-obsidian-950 rounded-full overflow-hidden border border-white/[0.06]">
                    <div class="h-full rounded-full transition-all duration-500" style="width: ${src.percentage}%; background-color: ${src.color};"></div>
                </div>
            `;
            sourceAttributionBars.appendChild(row);
        });

        if (sourceDiagnosticText) {
            sourceDiagnosticText.innerHTML = (sourceData.diagnostic_summary || '').replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>');
        }

        if (sourceInterventionsList) {
            sourceInterventionsList.innerHTML = '';
            const interventions = sourceData.interventions || [];
            interventions.forEach(item => {
                const li = document.createElement('li');
                li.className = 'leading-relaxed text-[11px] text-slate-300';
                li.textContent = item;
                sourceInterventionsList.appendChild(li);
            });
        }
    }

    function animateAqiNumber(target) {
        const start = currentDisplayedAqi;
        const duration = 300;
        const startTime = performance.now();

        function step(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const val = start + (target - start) * easeOut;

            aqiScoreEl.textContent = val.toFixed(1);

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                aqiScoreEl.textContent = target.toFixed(1);
                currentDisplayedAqi = target;
            }
        }
        requestAnimationFrame(step);
    }

    function updateGauge(aqi, color) {
        const capped = Math.min(Math.max(aqi, 0), 500);
        const percent = capped / 500;
        const offset = GAUGE_CIRCUMFERENCE * (1 - percent);
        gaugeCircle.style.strokeDashoffset = `${offset}`;
        gaugeCircle.setAttribute('stroke', color);
        gaugeCircle.style.filter = `drop-shadow(0 0 12px ${color}99)`;

        const spectrumDot = document.getElementById('spectrum-indicator-dot');
        if (spectrumDot) {
            const pct = Math.min(100, Math.max(0, (capped / 500) * 100));
            spectrumDot.style.left = `${pct}%`;
            spectrumDot.style.borderColor = color;
            spectrumDot.style.boxShadow = `0 0 10px ${color}bb`;
        }
    }

    function renderSubIndices(subIndices) {
        if (!subIndices) return;

        const entries = Object.entries(subIndices).sort((a, b) => b[1] - a[1]);
        breakdownBars.innerHTML = '';

        entries.forEach(([pol, subVal]) => {
            const pct = Math.min(100, Math.round((subVal / 500) * 100));
            const barColor = getBarColor(subVal);

            const card = document.createElement('div');
            card.className = 'inner-well p-3 flex flex-col justify-between gap-2 border border-white/[0.06] hover:border-white/20 transition';
            card.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="font-heading font-extrabold text-sm text-white">${pol}</span>
                    <span class="font-mono text-xs font-bold" style="color: ${barColor}">${subVal}</span>
                </div>
                <div class="w-full h-1.5 bg-obsidian-950 rounded-full overflow-hidden border border-white/[0.06]">
                    <div class="h-full rounded-full transition-all duration-500 shadow-sm" style="width: ${pct}%; background-color: ${barColor};"></div>
                </div>
                <div class="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>Sub-Index</span>
                    <span style="color: ${barColor}">${subVal <= 50 ? 'Good' : (subVal <= 100 ? 'Satisfactory' : (subVal <= 200 ? 'Moderate' : (subVal <= 300 ? 'Poor' : (subVal <= 400 ? 'Very Poor' : 'Severe'))))}</span>
                </div>
            `;
            breakdownBars.appendChild(card);
        });

        // 8th slot: CPCB Governing Max-Operator principle card to balance the 4x2 grid cleanly
        const ruleCard = document.createElement('div');
        ruleCard.className = 'inner-well p-3 flex flex-col justify-between gap-1.5 border border-dashed border-white/10 bg-white/[0.02] hover:border-white/20 transition';
        ruleCard.innerHTML = `
            <div class="flex items-center justify-between text-slate-400 text-xs font-mono">
                <span class="flex items-center gap-1.5 font-semibold text-slate-300">
                    <i class="ph-bold ph-scales text-amber-400"></i> Max Operator
                </span>
                <span class="text-amber-400 font-bold font-mono">CPCB NAQI</span>
            </div>
            <div class="text-[10px] text-slate-400 leading-snug">
                Overall AQI is mathematically governed by the highest active criteria sub-index.
            </div>
            <div class="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-1 border-t border-white/[0.05]">
                <span>NAQI Standard</span>
                <span class="text-emerald-400 font-semibold">Active Matrix</span>
            </div>
        `;
        breakdownBars.appendChild(ruleCard);
    }

    function getBarColor(subVal) {
        if (subVal <= 50) return '#10B981';
        if (subVal <= 100) return '#84CC16';
        if (subVal <= 200) return '#F59E0B';
        if (subVal <= 300) return '#F97316';
        if (subVal <= 400) return '#EF4444';
        return '#A855F7';
    }

    // Session verification & authentication status
    async function checkAuthStatus() {
        try {
            const res = await fetch('/api/auth/status');
            if (!res.ok) return;
            const data = await res.json();
            if (data.success && data.auth_enabled && !data.is_authenticated) {
                window.location.href = '/login';
            }
        } catch (e) {
            console.warn('Auth status check:', e);
        }
    }

    // Print & Export
    function populatePrintReport() {
        if (!latestReport) return;

        const elTime = document.getElementById('print-timestamp');
        if (elTime) elTime.textContent = new Date().toLocaleString();
        const elAqi = document.getElementById('print-aqi-score');
        if (elAqi) elAqi.textContent = latestReport.aqi;
        const elCat = document.getElementById('print-category');
        if (elCat) elCat.textContent = latestReport.category;
        const elDom = document.getElementById('print-dominant-pollutant');
        if (elDom) elDom.textContent = latestReport.dominant_pollutant;
        const elSum = document.getElementById('print-summary');
        if (elSum) elSum.textContent = latestReport.summary;
        const elHealth = document.getElementById('print-health-advisory');
        if (elHealth) elHealth.textContent = latestReport.health_advisory;
        const elSens = document.getElementById('print-sensitive-advisory');
        if (elSens) elSens.textContent = latestReport.sensitive_advisory;

        const polId = latestReport.pollutant_identification;
        if (polId && polId.primary_driver) {
            const elThreat = document.getElementById('print-primary-threat');
            const elImpact = document.getElementById('print-primary-impact');
            if (elThreat) elThreat.textContent = `${polId.primary_driver.name} (${polId.primary_driver.key}) - ${polId.primary_driver.status}`;
            if (elImpact) elImpact.textContent = polId.primary_driver.health_impact;
        }

        const srcData = latestReport.source_attribution;
        if (srcData && srcData.dominant_source) {
            const elTopSrc = document.getElementById('print-top-source');
            const elDiag = document.getElementById('print-source-diagnostic');
            if (elTopSrc) elTopSrc.textContent = `${srcData.dominant_source.name} (${srcData.dominant_source.percentage}%)`;
            if (elDiag) elDiag.textContent = (srcData.diagnostic_summary || '').replace(/\*\*/g, '');
        }

        const tableBody = document.getElementById('print-pollutant-table');
        if (tableBody && polId && polId.all_evaluations) {
            tableBody.innerHTML = '';
            polId.all_evaluations.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="p-2 border border-gray-300 font-bold">${item.key} (${item.name})</td>
                    <td class="p-2 border border-gray-300 font-mono">${item.concentration}</td>
                    <td class="p-2 border border-gray-300">${item.unit}</td>
                    <td class="p-2 border border-gray-300 font-mono">${item.standard_limit}</td>
                    <td class="p-2 border border-gray-300 font-semibold">${item.status}</td>
                    <td class="p-2 border border-gray-300 font-mono font-bold">${item.sub_index !== null ? item.sub_index : 'N/A'}</td>
                `;
                tableBody.appendChild(tr);
            });
        }

        const srcTableBody = document.getElementById('print-source-table');
        if (srcTableBody && srcData && srcData.sources_breakdown) {
            srcTableBody.innerHTML = '';
            srcData.sources_breakdown.forEach(s => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="p-2 border border-gray-300 font-bold">${s.name}</td>
                    <td class="p-2 border border-gray-300 font-mono font-bold">${s.percentage}%</td>
                    <td class="p-2 border border-gray-300">${s.description}</td>
                `;
                srcTableBody.appendChild(tr);
            });
        }

        const nearbyTableBody = document.getElementById('print-nearby-table');
        if (nearbyTableBody) {
            nearbyTableBody.innerHTML = '';
            const hotspots = (latestNearbyData && latestNearbyData.hotspots) ? latestNearbyData.hotspots : [];
            if (hotspots.length === 0) {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td colspan="5" class="p-3 text-center text-gray-500 italic">No major stationary point sources within monitoring perimeter.</td>`;
                nearbyTableBody.appendChild(tr);
            } else {
                hotspots.slice(0, 8).forEach(h => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td class="p-2 border border-gray-300 font-bold">${h.name}</td>
                        <td class="p-2 border border-gray-300">${h.category}</td>
                        <td class="p-2 border border-gray-300 font-mono font-bold">${h.distance_km} km</td>
                        <td class="p-2 border border-gray-300">${h.wind_alignment}</td>
                        <td class="p-2 border border-gray-300 font-mono">${(h.key_pollutants || []).join(', ')}</td>
                    `;
                    nearbyTableBody.appendChild(tr);
                });
            }
        }
    }

    if (btnDownloadPdf) {
        btnDownloadPdf.addEventListener('click', () => {
            populatePrintReport();
            window.print();
        });
    }

    // Enlarged Tactical Map Modal Handler
    const btnEnlargeMapFloating = document.getElementById('btn-enlarge-map-floating');
    const btnCloseEnlargedMap = document.getElementById('btn-close-enlarged-map');
    const modalBackdropDismiss = document.getElementById('modal-backdrop-dismiss');
    const enlargedMapModal = document.getElementById('enlarged-map-modal');
    const originalMapSlot = document.getElementById('original-map-slot');
    const modalMapSlot = document.getElementById('modal-map-slot');
    const mapExpandedPlaceholder = document.getElementById('map-expanded-placeholder');
    const mainAppWrapper = document.getElementById('main-app-wrapper');
    const btnRecenterMap = document.getElementById('btn-recenter-map');
    const modalThreatBadge = document.getElementById('modal-threat-badge');
    const modalDiagnosticSummary = document.getElementById('modal-diagnostic-summary');

    let isMapEnlarged = false;

    function openEnlargedMap() {
        if (isMapEnlarged || !enlargedMapModal || !modalMapSlot) return;
        isMapEnlarged = true;

        const sourcesMap = document.getElementById('sources-map');
        if (sourcesMap && modalMapSlot) {
            modalMapSlot.appendChild(sourcesMap);
            sourcesMap.style.height = '100%';
        }
        if (mapExpandedPlaceholder) mapExpandedPlaceholder.classList.remove('hidden');

        // Sync modal badge and diagnostic text with card
        const threatBadge = document.getElementById('nearby-threat-count');
        if (threatBadge && modalThreatBadge) modalThreatBadge.textContent = threatBadge.textContent;
        if (modalDiagnosticSummary) {
            if (latestNearbyData && latestNearbyData.hotspots && latestNearbyData.hotspots.length > 0) {
                const closest = latestNearbyData.hotspots[0];
                const dw = latestNearbyData.downwind_threat_count || 0;
                modalDiagnosticSummary.innerHTML = `Nearest: <strong class="text-white">${closest.name}</strong> (${closest.distance_km} km • ${closest.category})${dw > 0 ? ` • <span class="text-rose-400 font-semibold">${dw} downwind</span>` : ''}`;
            } else {
                modalDiagnosticSummary.textContent = 'Live airshed radar active • Click any source to inspect';
            }
        }

        // Apply blur to rest of website
        if (mainAppWrapper) {
            mainAppWrapper.classList.add('filter', 'blur-[8px]', 'pointer-events-none', 'select-none');
        }

        // Show modal with smooth transition
        enlargedMapModal.classList.remove('opacity-0', 'pointer-events-none');
        enlargedMapModal.classList.add('opacity-100');

        // Allow DOM reflow then trigger Leaflet resize
        setTimeout(() => {
            if (leafletMap) {
                leafletMap.invalidateSize();
                if (currentLat && currentLon) {
                    leafletMap.setView([currentLat, currentLon], 12);
                }
            }
        }, 120);
    }

    function closeEnlargedMap() {
        if (!isMapEnlarged || !enlargedMapModal) return;
        isMapEnlarged = false;

        const sourcesMap = document.getElementById('sources-map');
        if (sourcesMap && originalMapSlot) {
            originalMapSlot.insertBefore(sourcesMap, originalMapSlot.firstChild);
            sourcesMap.style.height = '';
        }
        if (mapExpandedPlaceholder) mapExpandedPlaceholder.classList.add('hidden');

        // Remove blur from rest of website
        if (mainAppWrapper) {
            mainAppWrapper.classList.remove('filter', 'blur-[8px]', 'pointer-events-none', 'select-none');
        }

        // Hide modal
        enlargedMapModal.classList.add('opacity-0', 'pointer-events-none');
        enlargedMapModal.classList.remove('opacity-100');

        // Restore embedded Leaflet view
        setTimeout(() => {
            if (leafletMap) {
                leafletMap.invalidateSize();
                if (currentLat && currentLon) {
                    leafletMap.setView([currentLat, currentLon], 11);
                }
            }
        }, 120);
    }

    if (btnEnlargeMapFloating) btnEnlargeMapFloating.addEventListener('click', openEnlargedMap);
    if (btnCloseEnlargedMap) btnCloseEnlargedMap.addEventListener('click', closeEnlargedMap);
    if (modalBackdropDismiss) modalBackdropDismiss.addEventListener('click', closeEnlargedMap);

    if (btnRecenterMap) {
        btnRecenterMap.addEventListener('click', () => {
            if (leafletMap && currentLat && currentLon) {
                leafletMap.setView([currentLat, currentLon], 12, { animate: true });
                if (modalDiagnosticSummary && latestNearbyData && latestNearbyData.hotspots && latestNearbyData.hotspots.length > 0) {
                    const closest = latestNearbyData.hotspots[0];
                    const dw = latestNearbyData.downwind_threat_count || 0;
                    modalDiagnosticSummary.innerHTML = `Nearest: <strong class="text-white">${closest.name}</strong> (${closest.distance_km} km • ${closest.category})${dw > 0 ? ` • <span class="text-rose-400 font-semibold">${dw} downwind</span>` : ''}`;
                }
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isMapEnlarged) {
            closeEnlargedMap();
        }
    });

    initMap();
    updateAllSliderFills();
    checkAuthStatus();
    // Automatically synchronize selected location with genuine live real-time station data on initial load
    syncRealtimeStationData(currentCity, currentLat, currentLon, true);
});

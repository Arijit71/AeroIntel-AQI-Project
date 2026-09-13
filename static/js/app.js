document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('aqi-form');
    const aqiScoreEl = document.getElementById('aqi-score');
    const gaugeCircle = document.getElementById('gauge-progress-circle');
    const categoryBanner = document.getElementById('category-banner');
    const categoryNameEl = document.getElementById('category-name');
    const categorySummaryEl = document.getElementById('category-summary');
    const categoryIcon = document.getElementById('category-icon');
    const dominantNameEl = document.getElementById('dominant-pollutant-name');
    const healthAdvisoryText = document.getElementById('health-advisory-text');
    const sensitiveAdvisoryText = document.getElementById('sensitive-advisory-text');
    const breakdownBars = document.getElementById('breakdown-bars');
    const ambientGlow = document.getElementById('ambient-glow-primary');

    const btnManualSync = document.getElementById('btn-manual-sync');
    const presetPills = document.querySelectorAll('.preset-pill');
    const btnDownloadPdf = document.getElementById('btn-download-pdf');
    const btnDownloadJson = document.getElementById('btn-download-json');
    const btnCopySummary = document.getElementById('btn-copy-summary');

    const GAUGE_CIRCUMFERENCE = 515.22;
    gaugeCircle.style.strokeDasharray = `${GAUGE_CIRCUMFERENCE}`;
    gaugeCircle.style.transition = 'stroke-dashoffset 0.7s ease-out, stroke 0.3s ease';

    let presetsData = {};
    let debounceTimer = null;
    let currentDisplayedAqi = 0;
    let latestReport = null;

    fetch('/api/presets')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.presets) {
                data.presets.forEach(p => {
                    presetsData[p.id] = p.values;
                });
            }
        })
        .catch(err => console.warn('Presets loading error:', err));

    const pollutantCards = document.querySelectorAll('.pollutant-card');
    pollutantCards.forEach(card => {
        const numInput = card.querySelector('.pollutant-number-input');
        const sliderInput = card.querySelector('.pollutant-slider');

        if (numInput && sliderInput) {
            sliderInput.addEventListener('input', () => {
                numInput.value = sliderInput.value;
                triggerPredictionDebounced();
            });

            numInput.addEventListener('input', () => {
                sliderInput.value = numInput.value;
                triggerPredictionDebounced();
            });
        }
    });

    presetPills.forEach(pill => {
        pill.addEventListener('click', () => {
            presetPills.forEach(p => {
                p.classList.remove('border-amber-500/80', 'bg-amber-500/10', 'text-white', 'shadow-[0_0_15px_rgba(245,158,11,0.15)]');
            });
            pill.classList.add('border-amber-500/80', 'bg-amber-500/10', 'text-white', 'shadow-[0_0_15px_rgba(245,158,11,0.15)]');

            applyPreset(pill.dataset.presetId);
        });
    });

    function applyPreset(presetId) {
        const values = presetsData[presetId];
        if (!values) return;

        Object.keys(values).forEach(pollutant => {
            const numInput = document.getElementById(`num-${pollutant}`);
            const sliderInput = document.getElementById(`slider-${pollutant}`);
            if (numInput) numInput.value = values[pollutant];
            if (sliderInput) sliderInput.value = values[pollutant];
        });

        requestPrediction();
    }

    if (btnManualSync) {
        btnManualSync.addEventListener('click', () => requestPrediction());
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

        if (ambientGlow) {
            ambientGlow.style.backgroundColor = `${report.category_color}18`;
        }

        categoryNameEl.textContent = report.category;
        categoryNameEl.style.color = report.category_color;
        categorySummaryEl.textContent = report.summary;
        categoryBanner.style.borderColor = `${report.category_color}55`;
        categoryBanner.style.backgroundColor = `${report.category_color}15`;

        categoryIcon.style.color = report.category_color;
        categoryIcon.style.backgroundColor = `${report.category_color}25`;

        dominantNameEl.textContent = report.dominant_pollutant;
        dominantNameEl.style.color = report.category_color;

        healthAdvisoryText.textContent = report.health_advisory;
        sensitiveAdvisoryText.textContent = report.sensitive_advisory;

        renderSubIndices(report.sub_indices);
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
    }

    function renderSubIndices(subIndices) {
        if (!subIndices) return;

        const entries = Object.entries(subIndices).sort((a, b) => b[1] - a[1]);
        breakdownBars.innerHTML = '';

        entries.forEach(([pol, subVal]) => {
            const pct = Math.min(100, Math.round((subVal / 500) * 100));
            const barColor = getBarColor(subVal);

            const row = document.createElement('div');
            row.className = 'flex items-center gap-2.5 text-xs font-mono';
            row.innerHTML = `
                <span class="w-12 text-slate-400 font-bold shrink-0">${pol}</span>
                <div class="flex-1 h-1.5 bg-dark-950 rounded-full overflow-hidden border border-slate-800/80">
                    <div class="h-full rounded-full transition-all duration-500" style="width: ${pct}%; background-color: ${barColor};"></div>
                </div>
                <span class="w-10 text-right font-semibold text-white shrink-0">${subVal}</span>
            `;
            breakdownBars.appendChild(row);
        });
    }

    function getBarColor(subVal) {
        if (subVal <= 50) return '#10B981';
        if (subVal <= 100) return '#84CC16';
        if (subVal <= 200) return '#F59E0B';
        if (subVal <= 300) return '#F97316';
        if (subVal <= 400) return '#EF4444';
        return '#A855F7';
    }

    function populatePrintReport() {
        if (!latestReport) return;

        document.getElementById('print-timestamp').textContent = new Date().toLocaleString();
        document.getElementById('print-aqi-score').textContent = latestReport.aqi;
        document.getElementById('print-category').textContent = latestReport.category;
        document.getElementById('print-dominant-pollutant').textContent = latestReport.dominant_pollutant;
        document.getElementById('print-summary').textContent = latestReport.summary;
        document.getElementById('print-health-advisory').textContent = latestReport.health_advisory;
        document.getElementById('print-sensitive-advisory').textContent = latestReport.sensitive_advisory;

        const tableBody = document.getElementById('print-pollutant-table');
        tableBody.innerHTML = '';

        const formData = getFormData();
        Object.entries(formData).forEach(([pol, concentration]) => {
            const sub = (latestReport.sub_indices && latestReport.sub_indices[pol]) ? latestReport.sub_indices[pol] : 'N/A';
            const unit = (pol === 'CO') ? 'mg/m³' : 'µg/m³';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="p-2 border border-gray-300 font-bold">${pol}</td>
                <td class="p-2 border border-gray-300">${concentration}</td>
                <td class="p-2 border border-gray-300">${unit}</td>
                <td class="p-2 border border-gray-300 font-mono font-bold">${sub}</td>
            `;
            tableBody.appendChild(tr);
        });
    }

    if (btnDownloadPdf) {
        btnDownloadPdf.addEventListener('click', () => {
            populatePrintReport();
            window.print();
        });
    }

    if (btnDownloadJson) {
        btnDownloadJson.addEventListener('click', () => {
            if (!latestReport) return;

            const exportPayload = {
                system: "AeroIntel City-Scale Air Quality Intelligence",
                timestamp: new Date().toISOString(),
                predicted_aqi: latestReport.aqi,
                category: latestReport.category,
                dominant_pollutant: latestReport.dominant_pollutant,
                pollutant_concentrations: getFormData(),
                sub_indices: latestReport.sub_indices,
                health_advisories: {
                    general: latestReport.health_advisory,
                    sensitive_groups: latestReport.sensitive_advisory
                }
            };

            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportPayload, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", `AeroIntel_AQI_Report_${Date.now()}.json`);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        });
    }

    if (btnCopySummary) {
        btnCopySummary.addEventListener('click', () => {
            if (!latestReport) return;

            const summaryText = `[AeroIntel AQI Intelligence Report]
AQI: ${latestReport.aqi} (${latestReport.category})
Dominant Contributor: ${latestReport.dominant_pollutant}
Health Impact: ${latestReport.health_advisory}
Sensitive Demographic Alert: ${latestReport.sensitive_advisory}
Timestamp: ${new Date().toLocaleString()}`;

            navigator.clipboard.writeText(summaryText).then(() => {
                const originalText = btnCopySummary.innerHTML;
                btnCopySummary.innerHTML = '<i class="ph-bold ph-check text-emerald-400"></i> Copied!';
                setTimeout(() => {
                    btnCopySummary.innerHTML = originalText;
                }, 1800);
            }).catch(err => {
                console.error('Clipboard copy failed:', err);
            });
        });
    }

    requestPrediction();
});

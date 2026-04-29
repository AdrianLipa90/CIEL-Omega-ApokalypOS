// Adam-Ciel¹³ Application JavaScript
class CielApplication {
    constructor() {
        this.charts = {};
        this.animationId = null;
        this.isPlaying = false;
        this.animationFrame = 0;
        this.data = this.initializeData();
        this.init();
    }

    initializeData() {
        return {
            cmb_spectrum: {
                l_values: [2, 10, 30, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
                D_l_LCDM: [8500, 7200, 6000, 5200, 4800, 6000, 3500, 2800, 2200, 1800, 1500, 1800, 1200, 1000],
                D_l_LPEG: [8650, 7350, 6100, 5250, 4820, 6020, 3510, 2810, 2210, 1805, 1502, 1803, 1201, 1000]
            },
            time_field: {
                x_coords: [0, 0.628, 1.257, 1.885, 2.513, 3.142, 3.770, 4.398, 5.027, 5.655, 6.283],
                y_coords: [0, 0.628, 1.257, 1.885, 2.513, 3.142, 3.770, 4.398, 5.027, 5.655, 6.283],
                tau_values: [-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5, 1.0, 0.5, 0, -0.5],
                rho_tau_values: [0.05, 0.08, 0.12, 0.15, 0.18, 0.20, 0.18, 0.15, 0.12, 0.08, 0.05]
            },
            harmonic_zones: {
                zones: ["Intentional", "Structural", "Acoustic"],
                l_ranges: ["< 30", "30-200", "> 200"],
                avg_changes: [4.75, 0.99, 0.00],
                descriptions: ["Dynamiczna topologia", "Koherencja galaktyczna", "Zachowana struktura rekombinacji"]
            }
        };
    }

    init() {
        this.setupTabNavigation();
        this.setupControlListeners();
        this.initializeCharts();
        this.updatePeakStatistics();
    }

    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.getAttribute('data-tab');
                
                // Remove active class from all tabs and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                button.classList.add('active');
                document.getElementById(tabId).classList.add('active');
                
                // Resize charts when tab becomes visible
                this.resizeChart(tabId);
            });
        });
    }

    setupControlListeners() {
        // CMB Spectrum controls
        const modulationAmplitude = document.getElementById('modulation-amplitude');
        const decayParameter = document.getElementById('decay-parameter');
        const sineFrequency = document.getElementById('sine-frequency');

        [modulationAmplitude, decayParameter, sineFrequency].forEach(control => {
            control?.addEventListener('input', () => {
                this.updateControlValue(control);
                this.updateCMBSpectrum();
            });
        });

        // Time field controls
        const coherenceLevel = document.getElementById('coherence-level');
        const colorScale = document.getElementById('color-scale');
        const animationSpeed = document.getElementById('animation-speed');
        const playPause = document.getElementById('play-pause');

        coherenceLevel?.addEventListener('input', () => {
            this.updateControlValue(coherenceLevel);
            this.updateTimeField();
        });

        colorScale?.addEventListener('change', () => {
            this.updateTimeField();
        });

        animationSpeed?.addEventListener('input', () => {
            this.updateControlValue(animationSpeed);
        });

        playPause?.addEventListener('click', () => {
            this.toggleAnimation();
        });

        // Fluid dynamics controls
        const equationState = document.getElementById('equation-state');
        
        equationState?.addEventListener('input', () => {
            this.updateControlValue(equationState);
            this.updateFluidProperties();
            this.updateFlowProfiles();
        });
    }

    updateControlValue(control) {
        const valueSpan = control.parentElement.querySelector('.control-value');
        if (valueSpan) {
            valueSpan.textContent = parseFloat(control.value).toFixed(2);
        }
    }

    initializeCharts() {
        this.createCMBChart();
        this.createTimeFieldChart();
        this.createFlowProfilesChart();
        this.createVectorFieldChart();
    }

    createCMBChart() {
        const ctx = document.getElementById('cmb-chart');
        if (!ctx) return;

        this.charts.cmb = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.data.cmb_spectrum.l_values,
                datasets: [
                    {
                        label: 'ΛCDM',
                        data: this.data.cmb_spectrum.D_l_LCDM,
                        borderColor: '#32A0DC',
                        backgroundColor: 'rgba(50, 160, 220, 0.1)',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'LPEG Modulowany',
                        data: this.calculateLPEGSpectrum(),
                        borderColor: '#FF5459',
                        backgroundColor: 'rgba(255, 84, 137, 0.1)',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Spektrum Mocy CMB: ΛCDM vs LPEG',
                        color: '#32A0DC',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#f5f5f5' }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Moment multipolowy l',
                            color: '#f5f5f5'
                        },
                        ticks: { color: '#f5f5f5' },
                        grid: { color: 'rgba(245, 245, 245, 0.1)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'D_l [μK²]',
                            color: '#f5f5f5'
                        },
                        ticks: { color: '#f5f5f5' },
                        grid: { color: 'rgba(245, 245, 245, 0.1)' }
                    }
                },
                elements: {
                    line: { tension: 0.1 }
                }
            }
        });

        // Add zone markers
        this.addZoneMarkers();
    }

    calculateLPEGSpectrum() {
        const amplitude = parseFloat(document.getElementById('modulation-amplitude')?.value || 0.1);
        const decay = parseFloat(document.getElementById('decay-parameter')?.value || 50);
        const frequency = parseFloat(document.getElementById('sine-frequency')?.value || 0.3);

        return this.data.cmb_spectrum.D_l_LCDM.map((value, index) => {
            const l = this.data.cmb_spectrum.l_values[index];
            const modulation = amplitude * Math.exp(-l / decay) * Math.sin(frequency * l);
            return value * (1 + modulation);
        });
    }

    addZoneMarkers() {
        // This would add vertical lines for harmonic zones
        // Implementation depends on Chart.js annotation plugin
    }

    createTimeFieldChart() {
        const ctx = document.getElementById('time-field-chart');
        if (!ctx) return;

        const scatterData = this.generateTimeFieldData();

        this.charts.timeField = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Pole Czasowe τ(x,y)',
                    data: scatterData,
                    backgroundColor: this.getTimeFieldColors(),
                    borderColor: '#32A0DC',
                    borderWidth: 1,
                    pointRadius: this.getTimeFieldSizes()
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Rozkład Przestrzenny Pola Czasowego',
                        color: '#32A0DC',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#f5f5f5' }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'x [rad]',
                            color: '#f5f5f5'
                        },
                        ticks: { color: '#f5f5f5' },
                        grid: { color: 'rgba(245, 245, 245, 0.1)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'y [rad]',
                            color: '#f5f5f5'
                        },
                        ticks: { color: '#f5f5f5' },
                        grid: { color: 'rgba(245, 245, 245, 0.1)' }
                    }
                }
            }
        });
    }

    generateTimeFieldData() {
        const data = [];
        const coherence = parseFloat(document.getElementById('coherence-level')?.value || 0.5);
        
        for (let i = 0; i < this.data.time_field.x_coords.length; i++) {
            for (let j = 0; j < this.data.time_field.y_coords.length; j++) {
                const tau = this.data.time_field.tau_values[i] * coherence;
                data.push({
                    x: this.data.time_field.x_coords[i],
                    y: this.data.time_field.y_coords[j],
                    tau: tau,
                    rho: this.data.time_field.rho_tau_values[j]
                });
            }
        }
        return data;
    }

    getTimeFieldColors() {
        const colorScale = document.getElementById('color-scale')?.value || 'viridis';
        const data = this.generateTimeFieldData();
        
        return data.map(point => {
            const normalized = (point.tau + 1.5) / 3; // Normalize to 0-1
            return this.getColorFromScale(normalized, colorScale);
        });
    }

    getTimeFieldSizes() {
        const data = this.generateTimeFieldData();
        return data.map(point => 3 + point.rho * 15); // Scale point size
    }

    getColorFromScale(normalized, scale) {
        const colors = {
            viridis: ['#440154', '#31688e', '#35b779', '#fde725'],
            plasma: ['#0d0887', '#7301a8', '#bd3786', '#f0f921'],
            coolwarm: ['#3b4cc0', '#7396d3', '#f1a142', '#b40426']
        };
        
        const palette = colors[scale] || colors.viridis;
        const index = Math.floor(normalized * (palette.length - 1));
        return palette[Math.max(0, Math.min(index, palette.length - 1))];
    }

    createFlowProfilesChart() {
        const ctx = document.getElementById('flow-profiles-chart');
        if (!ctx) return;

        const positions = this.data.time_field.x_coords;
        
        this.charts.flowProfiles = new Chart(ctx, {
            type: 'line',
            data: {
                labels: positions.map(x => x.toFixed(2)),
                datasets: [
                    {
                        label: 'τ poziomo',
                        data: this.data.time_field.tau_values,
                        borderColor: '#32A0DC',
                        backgroundColor: 'rgba(50, 160, 220, 0.1)',
                        borderWidth: 2,
                        borderDash: []
                    },
                    {
                        label: 'τ pionowo',
                        data: this.data.time_field.tau_values.map(v => v * 0.8),
                        borderColor: '#FF5459',
                        backgroundColor: 'rgba(255, 84, 137, 0.1)',
                        borderWidth: 2,
                        borderDash: []
                    },
                    {
                        label: 'ρτ poziomo',
                        data: this.data.time_field.rho_tau_values,
                        borderColor: '#32A0DC',
                        backgroundColor: 'rgba(50, 160, 220, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5]
                    },
                    {
                        label: 'ρτ pionowo',
                        data: this.data.time_field.rho_tau_values.map(v => v * 0.9),
                        borderColor: '#FF5459',
                        backgroundColor: 'rgba(255, 84, 137, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Profile Przepływu Płynu Czasu',
                        color: '#32A0DC',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        labels: { color: '#f5f5f5' }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Pozycja [rad]',
                            color: '#f5f5f5'
                        },
                        ticks: { color: '#f5f5f5' },
                        grid: { color: 'rgba(245, 245, 245, 0.1)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Wartość Pola',
                            color: '#f5f5f5'
                        },
                        ticks: { color: '#f5f5f5' },
                        grid: { color: 'rgba(245, 245, 245, 0.1)' }
                    }
                }
            }
        });
    }

    createVectorFieldChart() {
        const canvas = document.getElementById('vector-field-chart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        this.drawVectorField(ctx);
    }

    drawVectorField(ctx) {
        const width = ctx.canvas.width;
        const height = ctx.canvas.height;
        const gridSize = 20;
        
        ctx.clearRect(0, 0, width, height);
        ctx.strokeStyle = '#32A0DC';
        ctx.lineWidth = 2;

        for (let x = gridSize; x < width; x += gridSize * 2) {
            for (let y = gridSize; y < height; y += gridSize * 2) {
                // Calculate vector direction based on time field gradient
                const angle = (x + y) * 0.02;
                const magnitude = 10;
                const dx = Math.cos(angle) * magnitude;
                const dy = Math.sin(angle) * magnitude;

                // Draw arrow
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x + dx, y + dy);
                ctx.stroke();

                // Arrow head
                const headlen = 3;
                const headangle = Math.PI / 6;
                ctx.beginPath();
                ctx.moveTo(x + dx, y + dy);
                ctx.lineTo(x + dx - headlen * Math.cos(angle - headangle), y + dy - headlen * Math.sin(angle - headangle));
                ctx.moveTo(x + dx, y + dy);
                ctx.lineTo(x + dx - headlen * Math.cos(angle + headangle), y + dy - headlen * Math.sin(angle + headangle));
                ctx.stroke();
            }
        }
    }

    updateCMBSpectrum() {
        if (!this.charts.cmb) return;
        
        const newLPEGData = this.calculateLPEGSpectrum();
        this.charts.cmb.data.datasets[1].data = newLPEGData;
        this.charts.cmb.update();
        
        this.updatePeakStatistics();
    }

    updateTimeField() {
        if (!this.charts.timeField) return;
        
        const newData = this.generateTimeFieldData();
        this.charts.timeField.data.datasets[0].data = newData;
        this.charts.timeField.data.datasets[0].backgroundColor = this.getTimeFieldColors();
        this.charts.timeField.data.datasets[0].pointRadius = this.getTimeFieldSizes();
        this.charts.timeField.update();
        
        this.updateFieldStatistics();
    }

    updateFlowProfiles() {
        if (!this.charts.flowProfiles) return;
        
        const w = parseFloat(document.getElementById('equation-state')?.value || 0.33);
        
        // Modify flow profiles based on equation of state parameter
        const modifiedTau = this.data.time_field.tau_values.map(v => v * (1 + w));
        const modifiedRho = this.data.time_field.rho_tau_values.map(v => v * Math.sqrt(1 + w));
        
        this.charts.flowProfiles.data.datasets[0].data = modifiedTau;
        this.charts.flowProfiles.data.datasets[1].data = modifiedTau.map(v => v * 0.8);
        this.charts.flowProfiles.data.datasets[2].data = modifiedRho;
        this.charts.flowProfiles.data.datasets[3].data = modifiedRho.map(v => v * 0.9);
        
        this.charts.flowProfiles.update();
    }

    updateFluidProperties() {
        const w = parseFloat(document.getElementById('equation-state')?.value || 0.33);
        
        // Calculate fluid properties
        const avgRho = this.data.time_field.rho_tau_values.reduce((a, b) => a + b) / this.data.time_field.rho_tau_values.length;
        const timeDensity = avgRho * (1 + w);
        const timePressure = w * timeDensity;
        const soundSpeed = Math.sqrt(w);
        
        // Update display
        document.getElementById('time-density').textContent = `${timeDensity.toFixed(3)} jednostek`;
        document.getElementById('time-pressure').textContent = `${timePressure.toFixed(3)} jednostek`;
        document.getElementById('sound-speed').textContent = `${soundSpeed.toFixed(2)} c`;
    }

    updateFieldStatistics() {
        const coherence = parseFloat(document.getElementById('coherence-level')?.value || 0.5);
        const scaledTau = this.data.time_field.tau_values.map(v => v * coherence);
        
        const min = Math.min(...scaledTau);
        const max = Math.max(...scaledTau);
        const gradient = Math.sqrt(scaledTau.reduce((sum, v, i, arr) => {
            if (i < arr.length - 1) {
                return sum + Math.pow(arr[i + 1] - v, 2);
            }
            return sum;
        }, 0) / scaledTau.length);
        
        document.getElementById('field-min').textContent = min.toFixed(2);
        document.getElementById('field-max').textContent = max.toFixed(2);
        document.getElementById('gradient-mag').textContent = gradient.toFixed(2);
    }

    updatePeakStatistics() {
        const statsContainer = document.getElementById('peak-stats');
        if (!statsContainer) return;
        
        const lValues = this.data.cmb_spectrum.l_values;
        const lcdmData = this.data.cmb_spectrum.D_l_LCDM;
        const lpegData = this.calculateLPEGSpectrum();
        
        // Find peaks (local maxima)
        const peaks = [];
        for (let i = 1; i < lcdmData.length - 1; i++) {
            if (lcdmData[i] > lcdmData[i - 1] && lcdmData[i] > lcdmData[i + 1]) {
                const relativeChange = ((lpegData[i] - lcdmData[i]) / lcdmData[i] * 100);
                peaks.push({
                    l: lValues[i],
                    lcdm: lcdmData[i],
                    lpeg: lpegData[i],
                    change: relativeChange
                });
            }
        }
        
        statsContainer.innerHTML = peaks.map(peak => `
            <div class="stat-item">
                <strong>Pik l=${peak.l}</strong><br>
                ΛCDM: ${peak.lcdm.toFixed(0)} μK²<br>
                LPEG: ${peak.lpeg.toFixed(0)} μK²<br>
                Zmiana: ${peak.change.toFixed(2)}%
            </div>
        `).join('');
    }

    toggleAnimation() {
        const button = document.getElementById('play-pause');
        if (!button) return;
        
        if (this.isPlaying) {
            this.stopAnimation();
            button.textContent = '▶ Odtwórz';
        } else {
            this.startAnimation();
            button.textContent = '⏸ Pauza';
        }
        this.isPlaying = !this.isPlaying;
    }

    startAnimation() {
        const speed = parseFloat(document.getElementById('animation-speed')?.value || 1.0);
        
        const animate = () => {
            if (!this.isPlaying) return;
            
            this.animationFrame += 0.1 * speed;
            
            // Update time field with temporal evolution
            const phase = Math.sin(this.animationFrame);
            const coherence = parseFloat(document.getElementById('coherence-level')?.value || 0.5);
            
            // Temporarily modify tau values for animation
            const originalTau = [...this.data.time_field.tau_values];
            this.data.time_field.tau_values = originalTau.map(v => v * (1 + 0.2 * phase) * coherence);
            
            this.updateTimeField();
            
            // Restore original values
            this.data.time_field.tau_values = originalTau;
            
            this.animationId = requestAnimationFrame(animate);
        };
        
        animate();
    }

    stopAnimation() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    resizeChart(tabId) {
        setTimeout(() => {
            Object.values(this.charts).forEach(chart => {
                if (chart && chart.resize) {
                    chart.resize();
                }
            });
            
            if (tabId === 'fluid-dynamics') {
                const canvas = document.getElementById('vector-field-chart');
                if (canvas) {
                    canvas.width = canvas.offsetWidth;
                    canvas.height = canvas.offsetHeight;
                    this.drawVectorField(canvas.getContext('2d'));
                }
            }
        }, 100);
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cielApp = new CielApplication();
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.cielApp) {
        window.cielApp.resizeChart();
    }
});
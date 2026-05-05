// ================================================
// Kyiv Alert System - Modern Dashboard JS
// Згортаючі логи + адаптивність + плавні анімації
// ================================================

let audioEnabled = false;
let lastState = 'clear';
let stateStartTime = Date.now();
let localTestMode = false;

// ==================== ДОПОМІЖНІ ФУНКЦІЇ ====================

function formatTime(ms) {
    const total = Math.floor(ms / 1000);
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    const s = total % 60;
    return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
}

function stopAllLocalSounds() {
    ['snd-alarm', 'snd-cancel', 'snd-moment'].forEach(id => {
        const audio = document.getElementById(id);
        if (audio) {
            audio.pause();
            audio.currentTime = 0;
        }
    });
}

// ==================== АКТИВАЦІЯ ЗВУКУ ====================

function enableAudio() {
    if (audioEnabled) return;

    audioEnabled = true;
    const btn = document.getElementById('audio-status');
    btn.textContent = "✅ ЗВУК АКТИВОВАНО";
    btn.style.background = "linear-gradient(90deg, #2ecc71, #00f2ea)";
}

// ==================== МОДАЛЬНЕ ВІКНО ====================

function showTestModal() {
    document.getElementById('testModal').style.display = 'flex';
}

function hideTestModal() {
    document.getElementById('testModal').style.display = 'none';
}

// ==================== ЗГОРТАЮЧІ ЛОГИ ====================

function toggleLog(serviceId) {
    const container = document.getElementById(`log-container-${serviceId}`);
    if (container) {
        container.classList.toggle('open');
    }
}

// ==================== ОНОВЛЕННЯ ІНТЕРФЕЙСУ ====================

async function update() {
    try {
        const response = await fetch('/status');
        if (!response.ok) throw new Error('Network error');

        const data = await response.json();

        updateMainStatus(data);

        if (audioEnabled && !localTestMode) {
            handleAudioPlayback(data);
        }

        updateServiceCards(data);

    } catch (error) {
        console.warn('Не вдалося оновити статус:', error);
        document.getElementById('status-text').innerText = "ОФЛАЙН";
    }
}

function updateMainStatus(data) {
    const statusText = document.getElementById('status-text');
    const statusCircle = document.getElementById('status-circle');
    const durationEl = document.getElementById('status-duration');
    const serverTimeEl = document.getElementById('server-time');

    statusText.innerText = data.status_text || "СИНХРОНІЗАЦІЯ...";
    serverTimeEl.innerText = `Час сервера: ${data.server_time || '--:--:--'}`;
    durationEl.innerText = `Тривалість: ${formatTime(Date.now() - stateStartTime)}`;

    // Анімація круга
    if (data.is_alarm) {
        statusCircle.style.background = '#ff4d6d';
        statusCircle.style.boxShadow = '0 0 50px #ff4d6d';
    } else if (data.is_moment) {
        statusCircle.style.background = '#ffb703';
        statusCircle.style.boxShadow = '0 0 50px #ffb703';
    } else {
        statusCircle.style.background = '#00f2ea';
        statusCircle.style.boxShadow = '0 0 40px #00f2ea';
    }
}

function handleAudioPlayback(data) {
    const shouldMoment = data.is_moment;
    const shouldAlarm = data.is_alarm && !data.is_moment;

    if (shouldMoment && lastState !== 'moment') {
        stopAllLocalSounds();
        document.getElementById('snd-moment').play();
        lastState = 'moment';
        stateStartTime = Date.now();
    }
    else if (shouldAlarm && lastState !== 'alarm') {
        stopAllLocalSounds();
        document.getElementById('snd-alarm').play();
        lastState = 'alarm';
        stateStartTime = Date.now();
    }
    else if (!shouldMoment && !shouldAlarm && lastState !== 'clear') {
        stopAllLocalSounds();
        if (lastState === 'alarm') {
            document.getElementById('snd-cancel').play();
        }
        lastState = 'clear';
        stateStartTime = Date.now();
    }
}

function updateServiceCards(data) {
    const container = document.getElementById('services-container');

    const services = [
        { id: 'monitor',   icon: '📡', title: 'API МОНІТОРИНГ' },
        { id: 'player',    icon: '🔊', title: 'АУДІО ПЛЕЄР' },
        { id: 'scheduler', icon: '⏰', title: 'ПЛАНУВАЛЬНИК' }
    ];

    // Створюємо картки один раз
    if (container.children.length === 0) {
        container.innerHTML = '';

        services.forEach(svc => {
            const html = `
                <div class="service-card" id="card-${svc.id}">
                    <div class="service-header" onclick="toggleLog('${svc.id}')">
                        <div class="service-title">
                            <span class="indicator" id="ind-${svc.id}"></span>
                            ${svc.icon} ${svc.title}
                        </div>
                        <button id="btn-${svc.id}" 
                                class="toggle-btn off"
                                onclick="event.stopImmediatePropagation(); toggle('${svc.id}')">
                            УВІМК
                        </button>
                    </div>
                    <div class="log-container" id="log-container-${svc.id}">
                        <div id="log-${svc.id}" class="console">Очікування запуску...</div>
                    </div>
                </div>
            `;
            container.innerHTML += html;
        });
    }

    // Оновлюємо стан
    services.forEach(svc => {
        const isActive = data.scripts[svc.id] === 'ПРАЦЮЄ';

        // Індикатор
        const indicator = document.getElementById(`ind-${svc.id}`);
        if (indicator) {
            indicator.style.background = isActive ? '#00f2ea' : '#555';
        }

        // Кнопка
        const btn = document.getElementById(`btn-${svc.id}`);
        if (btn) {
            btn.textContent = isActive ? "ВИМК" : "УВІМК";
            btn.className = `toggle-btn ${isActive ? 'on' : 'off'}`;
        }

        // Логи
        const logEl = document.getElementById(`log-${svc.id}`);
        if (logEl && data.logs[svc.id]) {
            if (logEl.textContent !== data.logs[svc.id]) {
                logEl.textContent = data.logs[svc.id];
                logEl.scrollTop = logEl.scrollHeight;
            }
        }
    });
}

// ==================== КЕРУВАННЯ ====================

function toggle(name) {
    fetch('/toggle/' + name)
        .catch(err => console.error('Toggle error:', err));
}

function runLocalTest(type) {
    if (!audioEnabled) {
        alert("Спочатку активуйте звук на верхній кнопці!");
        return;
    }

    stopAllLocalSounds();
    hideTestModal();

    const audioMap = {
        'alarm': 'snd-alarm',
        'cancel': 'snd-cancel',
        'moment': 'snd-moment'
    };

    const audio = document.getElementById(audioMap[type]);
    if (audio) audio.play();
}

function runTest(action) {
    if (action === 'stop_all') stopAllLocalSounds();
    
    fetch('/manual/' + action)
        .then(() => update())
        .catch(err => console.error(err));

    hideTestModal();
}

function clearLogs() {
    if (confirm("Очистити всі журнали?")) {
        fetch('/clear_logs').then(() => update());
    }
}

// ==================== ІНІЦІАЛІЗАЦІЯ ====================

function init() {
    document.getElementById('audio-status').addEventListener('click', enableAudio);
    
    update();
    setInterval(update, 1400);   // оновлення кожні 1.4 секунди

    console.log('🚀 Kyiv Alert Dashboard — сучасна версія завантажена');
}

window.addEventListener('load', init);
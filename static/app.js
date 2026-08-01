let liveEventSource = null

function getTeamInitials(name) {
    if (!name) return '???';
    const words = name.trim().split(/\s+/);
    if (words.length >= 2) {
        return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.slice(0, 3).toUpperCase();
}

function getEventIcon(eventType) {
    switch (eventType) {
        case 'Goal':
        case 'GoalWithAssist':
        case 'PenaltyKickGoal':
            return '⚽';
        case 'ShotSave':
            return '🧤';
        case 'YellowCardFoul':
        case 'DoubleYellowCard':
            return '🟨';
        case 'RedCardFoul':
            return '🟥';
        case 'Foul':
            return '🟨';
        case 'KickoffEvent':
            return '🪙';
        case 'HalfTimeEvent':
            return '⏸️';
        case 'MatchEndEvent':
            return '🏁';
        case 'Substitution':
            return '🔄';
        case 'CornerKickEvent':
            return '🚩';
        case 'InjuryEvent':
            return '🚑';
        default:
            return '⏱️';
    }
}

function updateSetupPreviews() {
    const homeSelect = document.getElementById('home-team-select');
    const awaySelect = document.getElementById('away-team-select');
    const setupHomeName = document.getElementById('setup-home-name');
    const setupAwayName = document.getElementById('setup-away-name');
    const setupHomeBadge = document.getElementById('setup-home-badge');
    const setupAwayBadge = document.getElementById('setup-away-badge');

    if (homeSelect && setupHomeName && setupHomeBadge) {
        const name = homeSelect.value || 'Gospodarze';
        setupHomeName.textContent = name;
        setupHomeBadge.textContent = getTeamInitials(name);
    }
    if (awaySelect && setupAwayName && setupAwayBadge) {
        const name = awaySelect.value || 'Goście';
        setupAwayName.textContent = name;
        setupAwayBadge.textContent = getTeamInitials(name);
    }
}

async function loadMatchOptions() {
    try {
        const response = await fetch('/match/options');
        const data = await response.json();

        const homeSelect = document.getElementById('home-team-select');
        const awaySelect = document.getElementById('away-team-select');
        const homeFormSelect = document.getElementById('home-formation-select');
        const awayFormSelect = document.getElementById('away-formation-select');

        if (homeSelect && awaySelect && data.teams) {
            homeSelect.innerHTML = '';
            awaySelect.innerHTML = '';

            data.teams.forEach((team, idx) => {
                const optHome = document.createElement('option');
                optHome.value = team;
                optHome.textContent = team;
                homeSelect.appendChild(optHome);

                const optAway = document.createElement('option');
                optAway.value = team;
                optAway.textContent = team;
                awaySelect.appendChild(optAway);
            });

            if (data.teams.length >= 2) {
                homeSelect.selectedIndex = 0;
                awaySelect.selectedIndex = 1;
            }
        }

        if (homeFormSelect && awayFormSelect && data.formations) {
            homeFormSelect.innerHTML = '';
            awayFormSelect.innerHTML = '';

            data.formations.forEach(form => {
                const optHome = document.createElement('option');
                optHome.value = form;
                optHome.textContent = form;
                homeFormSelect.appendChild(optHome);

                const optAway = document.createElement('option');
                optAway.value = form;
                optAway.textContent = form;
                awayFormSelect.appendChild(optAway);
            });
        }

        updateSetupPreviews();
    } catch (err) {
        console.error('Failed to load match options:', err);
    }
}

async function startNewMatch() {
    const homeTeam = document.getElementById('home-team-select').value;
    const awayTeam = document.getElementById('away-team-select').value;
    const homeFormation = document.getElementById('home-formation-select').value;
    const awayFormation = document.getElementById('away-formation-select').value;

    if (homeTeam === awayTeam) {
        alert('Gospodarze i Goście muszą być różnymi drużynami!');
        return;
    }

    try {
        const response = await fetch('/match/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                home_team_name: homeTeam,
                away_team_name: awayTeam,
                home_formation: homeFormation,
                away_formation: awayFormation
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`Błąd: ${errData.detail || 'Nie udało się rozpocząć meczu'}`);
            return;
        }

        const data = await response.json();
        renderMatchData(data);
    } catch (err) {
        console.error('Failed to start new match:', err);
    }
    startLiveStream()
}

function renderMatchData(data) {
    const tickBtn = document.getElementById('tick-btn');
    const scoreBroad = document.getElementById('score-board');

    if (scoreBroad) {
        scoreBroad.textContent = `${data.home_team_name} ${data.home_score} - ${data.away_team_name} ${data.away_score} (${data.current_minute})`;
    }

    const homeNameEl = document.getElementById('home-team-name');
    const awayNameEl = document.getElementById('away-team-name');
    const homeBadgeEl = document.getElementById('home-team-badge');
    const awayBadgeEl = document.getElementById('away-team-badge');
    const homeScoreEl = document.getElementById('home-score');
    const awayScoreEl = document.getElementById('away-score');
    const currentMinuteEl = document.getElementById('current-minute');
    const statusBadgeText = document.getElementById('status-badge-text');
    const statusBadge = document.getElementById('status-badge');

    if (homeNameEl) homeNameEl.textContent = data.home_team_name;
    if (awayNameEl) awayNameEl.textContent = data.away_team_name;
    if (homeBadgeEl) homeBadgeEl.textContent = getTeamInitials(data.home_team_name);
    if (awayBadgeEl) awayBadgeEl.textContent = getTeamInitials(data.away_team_name);
    if (homeScoreEl) homeScoreEl.textContent = data.home_score;
    if (awayScoreEl) awayScoreEl.textContent = data.away_score;
    if (currentMinuteEl) currentMinuteEl.textContent = `${data.current_minute}'`;

    if (data.is_finished) {
        if (statusBadgeText) statusBadgeText.textContent = 'ZAKOŃCZONY';
        if (statusBadge) statusBadge.classList.add('finished');
        if (tickBtn) {
            tickBtn.disabled = true;
            tickBtn.innerHTML = '<div class="btn-tile-icon">🏁</div><div><div class="btn-tile-title">MECZ ZAKOŃCZONY</div><div class="btn-tile-sub">BRAK DALSZYCH AKCJI</div></div>';
        }
    } else {
        if (statusBadgeText) statusBadgeText.textContent = 'LIVE';
        if (statusBadge) statusBadge.classList.remove('finished');
        if (tickBtn) {
            tickBtn.disabled = false;
            tickBtn.innerHTML = '<div class="btn-tile-icon">▶</div><div><div class="btn-tile-title">KOLEJNA AKCJA</div><div class="btn-tile-sub">NACIŚNIJ ABY WYKONAĆ TICK</div></div>';
        }
    }

    const eventsContainer = document.getElementById('events-container');
    if (eventsContainer) {
        eventsContainer.innerHTML = '';
        
        const eventsCountEl = document.getElementById('events-count');
        if (eventsCountEl) eventsCountEl.textContent = `${data.events.length} ZDARZEŃ`;

        if (data.events.length === 0) {
            eventsContainer.innerHTML = '<div class="empty-events">Oczekiwanie na pierwszy gwizdek...</div>';
        } else {
            data.events.forEach(event => {
                const minute = Math.floor(event.second / 60);
                const row = document.createElement('div');
                row.className = `metro-event-row event-${event.event_type || 'default'}`;
                
                const timeEl = document.createElement('div');
                timeEl.className = 'metro-event-time';
                timeEl.textContent = `${minute}'`;

                const iconEl = document.createElement('div');
                iconEl.className = 'metro-event-icon';
                iconEl.textContent = getEventIcon(event.event_type);

                const descEl = document.createElement('div');
                descEl.className = 'metro-event-desc';
                descEl.textContent = event.description;

                row.appendChild(timeEl);
                row.appendChild(iconEl);
                row.appendChild(descEl);

                eventsContainer.appendChild(row);
            });
        }
    }
}

async function updateMatchState(url, userMethod = 'GET') {
    const tickBtn = document.getElementById('tick-btn');
    
    try {
        const response = await fetch(url, { method: userMethod });
        const data = await response.json();
        renderMatchData(data);

        // Sync selects with running match if options are loaded
        const homeSelect = document.getElementById('home-team-select');
        const awaySelect = document.getElementById('away-team-select');
        if (homeSelect && data.home_team_name && [...homeSelect.options].some(o => o.value === data.home_team_name)) {
            homeSelect.value = data.home_team_name;
        }
        if (awaySelect && data.away_team_name && [...awaySelect.options].some(o => o.value === data.away_team_name)) {
            awaySelect.value = data.away_team_name;
        }
        updateSetupPreviews();
    } catch (err) {
        if (tickBtn) tickBtn.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await loadMatchOptions();

    const homeSelect = document.getElementById('home-team-select');
    const awaySelect = document.getElementById('away-team-select');

    if (homeSelect) homeSelect.addEventListener('change', updateSetupPreviews);
    if (awaySelect) awaySelect.addEventListener('change', updateSetupPreviews);
    
    const startBtn = document.getElementById('start-match-btn');
    if (startBtn) {
        startBtn.addEventListener('click', startNewMatch);
    }

    const tickBtn = document.getElementById('tick-btn');
    if (tickBtn) {
        tickBtn.addEventListener('click', () => {
            updateMatchState('/match/tick', 'POST');
        });
    }

    updateMatchState('/match/status', 'GET');
});

function startLiveStream(){
    if (liveEventSource){
        liveEventSource.close()
    }
    const eventSource = new EventSource('/match/stream')

    eventSource.onmessage = function(event){
        const data = JSON.parse(event.data)
        renderMatchData(data)
        if (data.is_finished){
            eventSource.close()
        }
    }
    eventSource.onerror = function(err) {
        console.error("Błąd strumieniowania SSE:", err);
        eventSource.close();
    };
}
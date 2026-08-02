import { getTeamInitials, getEventIcon } from './helpers.js';
import { fetchPlayerStats } from './stats.js';

let liveEventSource = null;

export function switchView(viewName) {
    const setupView = document.getElementById('setup-view');
    const matchView = document.getElementById('match-view');
    const tabSetup = document.getElementById('nav-tab-setup');
    const tabMatch = document.getElementById('nav-tab-match');

    if (viewName === 'setup') {
        if (setupView) setupView.classList.remove('hidden');
        if (matchView) matchView.classList.add('hidden');
        if (tabSetup) tabSetup.classList.add('active');
        if (tabMatch) tabMatch.classList.remove('active');
    } else if (viewName === 'match') {
        if (setupView) setupView.classList.add('hidden');
        if (matchView) matchView.classList.remove('hidden');
        if (tabSetup) tabSetup.classList.remove('active');
        if (tabMatch) tabMatch.classList.add('active');
    }
}

export function renderMatchData(data) {
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
    } else {
        if (statusBadgeText) statusBadgeText.textContent = 'LIVE';
        if (statusBadge) statusBadge.classList.remove('finished');
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

            eventsContainer.scrollTop = eventsContainer.scrollHeight;
        }
    }
}

export async function updateMatchState(url, userMethod = 'GET') {
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
        await fetchPlayerStats();
    } catch (err) {
        console.error('Failed to update match state:', err);
    }
}

export function startLiveStream(){
    if (liveEventSource){
        liveEventSource.close();
    }
    const eventSource = new EventSource('/match/stream');
    liveEventSource = eventSource;

    eventSource.onmessage = function(event){
        const data = JSON.parse(event.data);
        renderMatchData(data);
        fetchPlayerStats();
        if (data.is_finished){
            eventSource.close();
        }
    };
    eventSource.onerror = function(err) {
        console.error("Błąd strumieniowania SSE:", err);
        eventSource.close();
    };
}

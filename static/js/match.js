import { getTeamInitials, getEventIcon } from './helpers.js';
import { fetchPlayerStats } from './stats.js';

let liveEventSource = null;

export function switchView(viewName) {
    const setupView = document.getElementById('setup-view');
    const matchView = document.getElementById('match-view');
    const leagueView = document.getElementById('league-view');

    const tabSetup = document.getElementById('nav-tab-setup');
    const tabMatch = document.getElementById('nav-tab-match');
    const tabLeague = document.getElementById('nav-tab-league');

    if (setupView) setupView.classList.toggle('hidden', viewName !== 'setup');
    if (matchView) matchView.classList.toggle('hidden', viewName !== 'match');
    if (leagueView) leagueView.classList.toggle('hidden', viewName !== 'league');

    if (tabSetup) tabSetup.classList.toggle('active', viewName === 'setup');
    if (tabMatch) tabMatch.classList.toggle('active', viewName === 'match');
    if (tabLeague) tabLeague.classList.toggle('active', viewName === 'league');
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

    if (data.home_team_stats && data.away_team_stats) {
        renderTeamMatchStats(data.home_team_stats, data.away_team_stats);
    }
}

export function renderTeamMatchStats(homeStats, awayStats) {
    if (!homeStats || !awayStats) return;

    const setStatRow = (key, homeVal, awayVal, isPercentage = false) => {
        const homeValEl = document.getElementById(`stat-home-${key}`);
        const awayValEl = document.getElementById(`stat-away-${key}`);
        const homeBarEl = document.getElementById(`bar-home-${key}`);
        const awayBarEl = document.getElementById(`bar-away-${key}`);

        if (homeValEl) homeValEl.textContent = isPercentage ? `${homeVal}%` : homeVal;
        if (awayValEl) awayValEl.textContent = isPercentage ? `${awayVal}%` : awayVal;

        let homePct = 50;
        let awayPct = 50;
        if (isPercentage) {
            homePct = homeVal;
            awayPct = awayVal;
        } else {
            const sum = (homeVal || 0) + (awayVal || 0);
            if (sum > 0) {
                homePct = Math.round((homeVal / sum) * 100);
                awayPct = 100 - homePct;
            }
        }

        if (homeBarEl) homeBarEl.style.width = `${homePct}%`;
        if (awayBarEl) awayBarEl.style.width = `${awayPct}%`;
    };

    setStatRow('possession', homeStats.possession_percentage ?? 50, awayStats.possession_percentage ?? 50, true);
    setStatRow('shots-target', homeStats.shots_on_target ?? 0, awayStats.shots_on_target ?? 0);
    setStatRow('shots-off', homeStats.shots_off_target ?? 0, awayStats.shots_off_target ?? 0);
    setStatRow('shots-total', homeStats.total_shots ?? 0, awayStats.total_shots ?? 0);
    setStatRow('fouls', homeStats.fouls ?? 0, awayStats.fouls ?? 0);
    setStatRow('passes', homeStats.passes ?? 0, awayStats.passes ?? 0);
    setStatRow('corners', homeStats.corners ?? 0, awayStats.corners ?? 0);
    setStatRow('saves', homeStats.saves ?? 0, awayStats.saves ?? 0);
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

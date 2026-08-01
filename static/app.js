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

async function updateMatchState(url, userMethod = 'GET') {
    const tickBtn = document.getElementById('tick-btn');
    
    try {
        const response = await fetch(url, { method: userMethod });
        const data = await response.json();

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
    } catch (err) {
        if (tickBtn) tickBtn.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const tickBtn = document.getElementById('tick-btn');
    if (tickBtn) {
        tickBtn.addEventListener('click', () => {
            updateMatchState('/match/tick', 'POST');
        });
    }
    updateMatchState('/match/status', 'GET');
});
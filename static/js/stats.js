import { getTeamInitials, getShortPosition, getPositionClass } from './helpers.js';

let currentStatsData = null;
let activeStatsTab = 'home';

export function getCurrentStatsData() {
    return currentStatsData;
}

export function getActiveStatsTab() {
    return activeStatsTab;
}

export function setActiveStatsTab(tab) {
    activeStatsTab = tab;
}

export async function fetchPlayerStats() {
    try {
        const response = await fetch('/match/stats');
        if (!response.ok) {
            currentStatsData = null;
            renderPlayerStats();
            return;
        }
        currentStatsData = await response.json();
        renderPlayerStats();
    } catch (err) {
        console.error('Failed to fetch player stats:', err);
        currentStatsData = null;
        renderPlayerStats();
    }
}

export function createPlayerStatCard(player, index, forceBench = false) {
    const card = document.createElement('div');

    const hasStarterProp = player.is_starter !== undefined;
    const isStarter = hasStarterProp ? player.is_starter : !forceBench;
    const isOnField = player.is_on_field !== undefined ? player.is_on_field : isStarter;

    let cardStatusClass = '';
    let statusText = '';
    let statusBadgeClass = '';

    if (player.has_red_card) {
        cardStatusClass = 'has-red';
        statusText = 'CZERWONA KARTKA';
        statusBadgeClass = 'red-card';
    } else if (player.is_injured) {
        cardStatusClass = 'is-injured';
        statusText = 'KONTUZJA';
        statusBadgeClass = 'injured';
    } else if (isStarter && isOnField) {
        cardStatusClass = 'is-starter';
        statusText = 'NA BOISKU';
        statusBadgeClass = 'on-field';
    } else if (isStarter && !isOnField) {
        cardStatusClass = 'subbed-off';
        statusText = 'ZMIENIONY';
        statusBadgeClass = 'sub-off';
    } else if (!isStarter && isOnField) {
        cardStatusClass = 'subbed-in';
        statusText = 'WEJŚCIE Z ŁAWKI';
        statusBadgeClass = 'sub-in';
    } else {
        cardStatusClass = 'is-bench';
        statusText = 'NA ŁAWCE';
        statusBadgeClass = 'bench';
    }

    card.className = `player-stat-card ${cardStatusClass}`;

    const mainRow = document.createElement('div');
    mainRow.className = 'player-card-main';

    const infoDiv = document.createElement('div');
    infoDiv.className = 'player-card-info';
    infoDiv.style.flexDirection = 'column';
    infoDiv.style.alignItems = 'flex-start';
    infoDiv.style.gap = '0.2rem';

    const shortPos = getShortPosition(player.position);
    const posClass = getPositionClass(player.position);

    const nameRow = document.createElement('div');
    nameRow.className = 'player-card-name-row';

    const posSpan = document.createElement('span');
    posSpan.className = `pos-badge ${posClass}`;
    posSpan.textContent = shortPos;

    const nameSpan = document.createElement('span');
    nameSpan.className = 'player-card-name';
    nameSpan.textContent = `${index + 1}. ${player.short_name || player.name || player.player_name || player.full_name || 'Zawodnik'}`;

    nameRow.appendChild(posSpan);
    nameRow.appendChild(nameSpan);

    const statusBadgeSpan = document.createElement('span');
    statusBadgeSpan.className = `player-status-badge ${statusBadgeClass}`;
    statusBadgeSpan.textContent = statusText;

    infoDiv.appendChild(nameRow);
    infoDiv.appendChild(statusBadgeSpan);

    const pillsDiv = document.createElement('div');
    pillsDiv.className = 'player-stat-pills';

    // Goal pill
    const goalPill = document.createElement('span');
    goalPill.className = `stat-pill goals ${player.goals > 0 ? 'active' : ''}`;
    goalPill.textContent = `⚽ ${player.goals || 0}`;
    pillsDiv.appendChild(goalPill);

    // Assist pill
    const assistPill = document.createElement('span');
    assistPill.className = `stat-pill assists ${player.assists > 0 ? 'active' : ''}`;
    assistPill.textContent = `🅰️ ${player.assists || 0}`;
    pillsDiv.appendChild(assistPill);

    // Yellow Card pill
    const yellowPill = document.createElement('span');
    yellowPill.className = `stat-pill yellow ${player.yellow_cards > 0 ? 'active' : ''}`;
    yellowPill.textContent = `🟨 ${player.yellow_cards || 0}`;
    pillsDiv.appendChild(yellowPill);

    // Red Card pill
    if (player.has_red_card) {
        const redPill = document.createElement('span');
        redPill.className = 'stat-pill red active';
        redPill.textContent = `🟥`;
        pillsDiv.appendChild(redPill);
    }

    // Rating pill
    const ratingVal = player.rating !== undefined ? Number(player.rating).toFixed(1) : '6.0';
    const ratingNum = parseFloat(ratingVal);
    let ratingClass = 'medium';
    if (ratingNum >= 7.0) ratingClass = 'high';
    else if (ratingNum < 6.0) ratingClass = 'low';

    const ratingPill = document.createElement('span');
    ratingPill.className = `stat-pill rating ${ratingClass}`;
    ratingPill.textContent = `⭐ ${ratingVal}`;
    pillsDiv.appendChild(ratingPill);

    mainRow.appendChild(infoDiv);
    mainRow.appendChild(pillsDiv);

    // Stamina block
    const staminaDiv = document.createElement('div');
    staminaDiv.className = 'stamina-block';

    const staminaPct = Math.max(0, Math.min(100, Math.round((player.current_stamina ?? 1.0) * 100)));

    const trackDiv = document.createElement('div');
    trackDiv.className = 'stamina-track';

    const fillDiv = document.createElement('div');
    let staminaClass = 'high';
    if (staminaPct < 35) staminaClass = 'low';
    else if (staminaPct < 70) staminaClass = 'medium';

    fillDiv.className = `stamina-fill ${staminaClass}`;
    fillDiv.style.width = `${staminaPct}%`;
    trackDiv.appendChild(fillDiv);

    const staminaText = document.createElement('span');
    staminaText.className = 'stamina-text';
    staminaText.textContent = `⚡ ${staminaPct}%`;

    staminaDiv.appendChild(trackDiv);
    staminaDiv.appendChild(staminaText);

    card.appendChild(mainRow);
    card.appendChild(staminaDiv);

    return card;
}

export function renderPlayerStats() {
    const container = document.getElementById('stats-players-list');
    const homeNameEl = document.getElementById('stats-home-name');
    const awayNameEl = document.getElementById('stats-away-name');
    const homeBadgeEl = document.getElementById('stats-home-badge');
    const awayBadgeEl = document.getElementById('stats-away-badge');
    const homeTab = document.getElementById('tab-home-stats');
    const awayTab = document.getElementById('tab-away-stats');
    const motmEl = document.getElementById('stats-motm-card');
    const motmNameEl = document.getElementById('stats-motm-name');
    const motmPosEl = document.getElementById('stats-motm-pos');
    const motmRatingEl = document.getElementById('stats-motm-rating');
    const teamAvgEl = document.getElementById('stats-team-avg-rating');

    if (!container) return;

    if (!currentStatsData) {
        container.innerHTML = '<div class="empty-stats">Rozpocznij mecz, aby zobaczyć statystyki zawodników</div>';
        if (homeNameEl) homeNameEl.textContent = 'GOSPODARZE';
        if (awayNameEl) awayNameEl.textContent = 'GOŚCIE';
        if (homeBadgeEl) homeBadgeEl.textContent = '---';
        if (awayBadgeEl) awayBadgeEl.textContent = '---';
        if (motmNameEl) motmNameEl.textContent = '---';
        if (motmRatingEl) motmRatingEl.textContent = '⭐ 6.0';
        if (teamAvgEl) teamAvgEl.textContent = '⭐ 6.0';
        return;
    }

    const homeTeamName = currentStatsData.home_team_name || 'Gospodarze';
    const awayTeamName = currentStatsData.away_team_name || 'Goście';

    if (homeNameEl) homeNameEl.textContent = homeTeamName;
    if (awayNameEl) awayNameEl.textContent = awayTeamName;
    if (homeBadgeEl) homeBadgeEl.textContent = getTeamInitials(homeTeamName);
    if (awayBadgeEl) awayBadgeEl.textContent = getTeamInitials(awayTeamName);

    if (homeTab && awayTab) {
        if (activeStatsTab === 'home') {
            homeTab.classList.add('active');
            awayTab.classList.remove('active');
        } else {
            awayTab.classList.add('active');
            homeTab.classList.remove('active');
        }
    }

    const allPlayers = [
        ...(currentStatsData.home_players || []),
        ...(currentStatsData.away_players || [])
    ];

    // Calculate MOTM (Man of the Match)
    let motm = currentStatsData.man_of_the_match;
    if (!motm && allPlayers.length > 0) {
        const played = allPlayers.filter(p => p.is_starter || p.is_on_field);
        const candidates = played.length > 0 ? played : allPlayers;
        motm = candidates.reduce((best, p) => {
            if (!best) return p;
            const pRating = p.rating ?? 6.0;
            const bestRating = best.rating ?? 6.0;
            if (pRating > bestRating) return p;
            if (pRating === bestRating && (p.goals || 0) > (best.goals || 0)) return p;
            return best;
        }, null);
    }

    if (motm && motmNameEl) {
        motmNameEl.textContent = motm.short_name || motm.name || motm.full_name || '---';
        if (motmPosEl) {
            const shortPos = getShortPosition(motm.position);
            const posClass = getPositionClass(motm.position);
            motmPosEl.className = `pos-badge ${posClass}`;
            motmPosEl.textContent = shortPos;
        }
        if (motmRatingEl) {
            const rVal = motm.rating !== undefined ? Number(motm.rating).toFixed(1) : '6.0';
            const rNum = parseFloat(rVal);
            let rClass = 'medium';
            if (rNum >= 7.0) rClass = 'high';
            else if (rNum < 6.0) rClass = 'low';
            motmRatingEl.className = `stat-pill rating ${rClass}`;
            motmRatingEl.textContent = `⭐ ${rVal}`;
        }
    }

    const players = activeStatsTab === 'home' ? (currentStatsData.home_players || []) : (currentStatsData.away_players || []);

    // Calculate Team Average Rating for active tab
    if (teamAvgEl && players.length > 0) {
        const playedTeam = players.filter(p => p.is_starter || p.is_on_field);
        const activeGroup = playedTeam.length > 0 ? playedTeam : players;
        const avg = activeGroup.reduce((sum, p) => sum + (p.rating ?? 6.0), 0) / activeGroup.length;
        const avgStr = avg.toFixed(1);
        const avgNum = parseFloat(avgStr);
        let avgClass = 'medium';
        if (avgNum >= 7.0) avgClass = 'high';
        else if (avgNum < 6.0) avgClass = 'low';
        teamAvgEl.className = `stat-pill rating ${avgClass}`;
        teamAvgEl.textContent = `⭐ ${avgStr}`;
    }

    if (players.length === 0) {
        container.innerHTML = '<div class="empty-stats">Brak danych zawodników dla wybranej drużyny</div>';
        return;
    }

    container.innerHTML = '';

    const hasStarterAttr = players.some(p => p.is_starter !== undefined);

    let starters = [];
    let bench = [];

    if (hasStarterAttr) {
        starters = players.filter(p => p.is_starter);
        bench = players.filter(p => !p.is_starter);
    } else {
        starters = players.slice(0, 11);
        bench = players.slice(11);
    }

    // Starting 11 Header
    const startersHeader = document.createElement('div');
    startersHeader.className = 'stats-section-header starter';
    startersHeader.innerHTML = `<span>⚽ SKŁAD GŁÓWNY (WYJŚCIOWA 11)</span> <span class="section-count-badge">${starters.length}</span>`;
    container.appendChild(startersHeader);

    // Starting 11 players
    starters.forEach((player, i) => {
        container.appendChild(createPlayerStatCard(player, i, false));
    });

    // Bench Header
    if (bench.length > 0) {
        const benchHeader = document.createElement('div');
        benchHeader.className = 'stats-section-header bench';
        benchHeader.innerHTML = `<span>🪑 ŁAWKA REZERWOWYCH</span> <span class="section-count-badge">${bench.length}</span>`;
        container.appendChild(benchHeader);

        bench.forEach((player, i) => {
            container.appendChild(createPlayerStatCard(player, i + starters.length, true));
        });
    }
}

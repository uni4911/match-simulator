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

function createPlayerStatCard(player, index) {
    const card = document.createElement('div');
    card.className = `player-stat-card ${player.has_red_card ? 'has-red' : ''}`;

    const mainRow = document.createElement('div');
    mainRow.className = 'player-card-main';

    const infoDiv = document.createElement('div');
    infoDiv.className = 'player-card-info';
    infoDiv.style.flexDirection = 'column';
    infoDiv.style.alignItems = 'flex-start';
    infoDiv.style.gap = '0.15rem';

    const nameSpan = document.createElement('span');
    nameSpan.className = 'player-card-name';
    nameSpan.textContent = `${index + 1}. ${player.name || 'Zawodnik'}`;

    const posSpan = document.createElement('span');
    const shortPos = getShortPosition(player.position);
    const posClass = getPositionClass(player.position);
    posSpan.className = `pos-badge ${posClass}`;
    posSpan.textContent = shortPos;

    const nameRow = document.createElement('div');
    nameRow.className = 'player-card-name-row';
    nameRow.appendChild(posSpan);
    nameRow.appendChild(nameSpan);

    infoDiv.appendChild(nameRow);


    const pillsDiv = document.createElement('div');
    pillsDiv.className = 'player-stat-pills';

    // Goal pill
    const goalPill = document.createElement('span');
    goalPill.className = `stat-pill goals ${player.goals > 0 ? 'active' : ''}`;
    goalPill.textContent = `⚽ ${player.goals}`;
    pillsDiv.appendChild(goalPill);

    // Assist pill
    const assistPill = document.createElement('span');
    assistPill.className = `stat-pill assists ${player.assists > 0 ? 'active' : ''}`;
    assistPill.textContent = `🅰️ ${player.assists}`;
    pillsDiv.appendChild(assistPill);

    // Yellow Card pill
    const yellowPill = document.createElement('span');
    yellowPill.className = `stat-pill yellow ${player.yellow_cards > 0 ? 'active' : ''}`;
    yellowPill.textContent = `🟨 ${player.yellow_cards}`;
    pillsDiv.appendChild(yellowPill);

    // Red Card pill
    if (player.has_red_card) {
        const redPill = document.createElement('span');
        redPill.className = 'stat-pill red active';
        redPill.textContent = `🟥`;
        pillsDiv.appendChild(redPill);
    }

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

    if (!container) return;

    if (!currentStatsData) {
        container.innerHTML = '<div class="empty-stats">Rozpocznij mecz, aby zobaczyć statystyki zawodników</div>';
        if (homeNameEl) homeNameEl.textContent = 'GOSPODARZE';
        if (awayNameEl) awayNameEl.textContent = 'GOŚCIE';
        if (homeBadgeEl) homeBadgeEl.textContent = '---';
        if (awayBadgeEl) awayBadgeEl.textContent = '---';
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

    const players = activeStatsTab === 'home' ? (currentStatsData.home_players || []) : (currentStatsData.away_players || []);

    if (players.length === 0) {
        container.innerHTML = '<div class="empty-stats">Brak danych zawodników dla wybranej drużyny</div>';
        return;
    }

    container.innerHTML = '';

    // Starting 11 Header
    const startersHeader = document.createElement('div');
    startersHeader.className = 'stats-section-header';
    startersHeader.textContent = `SKŁAD GŁÓWNY (${Math.min(11, players.length)})`;
    container.appendChild(startersHeader);

    // Starting 11 players
    const starters = players.slice(0, 11);
    starters.forEach((player, i) => {
        container.appendChild(createPlayerStatCard(player, i));
    });

    // Bench Header
    if (players.length > 11) {
        const benchHeader = document.createElement('div');
        benchHeader.className = 'stats-section-header bench';
        benchHeader.textContent = `REZERWOWI (${players.length - 11})`;
        container.appendChild(benchHeader);

        const bench = players.slice(11);
        bench.forEach((player, i) => {
            container.appendChild(createPlayerStatCard(player, i + 11));
        });
    }
}

import { getTeamInitials, getShortPosition, getPositionClass } from './helpers.js';
import { renderMatchData, switchView, startLiveStream } from './match.js';
import { fetchPlayerStats } from './stats.js';

let currentLeagueData = null;
let currentFilter = 'all'; // 'all', 'pending', 'finished'
let currentSelectedRound = 1;
let isSimulatingAll = false;

export async function initLeagueView() {
    await loadLeagueTeamOptions();
    await fetchLeagueTable();
}

export async function loadLeagueTeamOptions() {
    const container = document.getElementById('league-team-checkboxes');
    if (!container) return;

    try {
        const response = await fetch('/match/options');
        const data = await response.json();

        if (data.teams && data.teams.length > 0) {
            container.innerHTML = '';
            data.teams.forEach((teamName) => {
                const label = document.createElement('label');
                label.className = 'team-checkbox-card';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.name = 'league-team-select';
                checkbox.value = teamName;
                checkbox.checked = true;

                const badge = document.createElement('span');
                badge.className = 'team-checkbox-badge';
                badge.textContent = getTeamInitials(teamName);

                const text = document.createElement('span');
                text.className = 'team-checkbox-name';
                text.textContent = teamName;

                label.appendChild(checkbox);
                label.appendChild(badge);
                label.appendChild(text);

                container.appendChild(label);
            });
        }
    } catch (err) {
        console.error('Błąd podczas ładowania drużyn do ligi:', err);
    }
}

export async function fetchLeagueTable() {
    try {
        const response = await fetch('/league/table');
        if (!response.ok) {
            showLeagueCreationView();
            return;
        }

        const data = await response.json();
        currentLeagueData = data;
        
        // Auto select first round with unplayed matches if not set
        autoSelectActiveRound(data);
        renderLeagueView(data);
    } catch (err) {
        console.error('Błąd podczas pobierania stanu ligi:', err);
        showLeagueCreationView();
    }
}

function autoSelectActiveRound(data) {
    if (!data || !data.fixtures || data.fixtures.length === 0) return;
    
    // Find earliest round that has at least one unfinished match
    const pendingFixture = data.fixtures.find(f => !f.is_finished);
    if (pendingFixture) {
        currentSelectedRound = pendingFixture.round_number || 1;
    } else {
        currentSelectedRound = 1;
    }
}

export function showLeagueCreationView() {
    const creationContainer = document.getElementById('league-creation-container');
    const activeContainer = document.getElementById('league-active-container');

    if (creationContainer) creationContainer.classList.remove('hidden');
    if (activeContainer) activeContainer.classList.add('hidden');
}

export function showLeagueActiveView() {
    const creationContainer = document.getElementById('league-creation-container');
    const activeContainer = document.getElementById('league-active-container');

    if (creationContainer) creationContainer.classList.add('hidden');
    if (activeContainer) activeContainer.classList.remove('hidden');
}

export async function createNewLeague() {
    const nameInput = document.getElementById('league-name-input');
    const doubleRoundCheckbox = document.getElementById('league-double-round-checkbox');
    const checkboxes = document.querySelectorAll('input[name="league-team-select"]:checked');

    const leagueName = nameInput ? nameInput.value.trim() || 'Moja liga' : 'Moja liga';
    const doubleRound = doubleRoundCheckbox ? doubleRoundCheckbox.checked : false;
    const selectedTeams = Array.from(checkboxes).map(cb => cb.value);

    if (selectedTeams.length < 2) {
        alert('Musisz wybrać co najmniej 2 drużyny, aby utworzyć ligę!');
        return;
    }

    try {
        const response = await fetch('/league/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                league_name: leagueName,
                league_teams: selectedTeams,
                double_round: doubleRound
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`Błąd tworzenia ligi: ${errData.detail || 'Nieznany błąd'}`);
            return;
        }

        const data = await response.json();
        currentLeagueData = data;
        currentSelectedRound = 1;
        renderLeagueView(data);
    } catch (err) {
        console.error('Błąd podczas tworzenia ligi:', err);
        alert('Wystąpił błąd podczas połączenia z serwerem.');
    }
}

export function renderLeagueView(data) {
    if (!data) return;
    showLeagueActiveView();

    // League Header & Progress
    const titleEl = document.getElementById('active-league-name');
    const progressTextEl = document.getElementById('league-progress-text');
    const progressBarEl = document.getElementById('league-progress-bar');
    const teamsCountBadge = document.getElementById('league-teams-count-badge');

    if (titleEl) titleEl.textContent = data.name;
    if (teamsCountBadge) teamsCountBadge.textContent = `${data.teams.length} DRUŻYN`;

    const totalFixtures = data.fixtures ? data.fixtures.length : 0;
    const finishedFixtures = data.fixtures ? data.fixtures.filter(f => f.is_finished).length : 0;
    const progressPercent = totalFixtures > 0 ? Math.round((finishedFixtures / totalFixtures) * 100) : 0;

    if (progressTextEl) {
        progressTextEl.textContent = `${finishedFixtures} z ${totalFixtures} meczów rozegranych (${progressPercent}%)`;
    }
    if (progressBarEl) {
        progressBarEl.style.width = `${progressPercent}%`;
    }

    // Calculate Total Rounds
    let maxRound = 1;
    if (data.fixtures && data.fixtures.length > 0) {
        maxRound = Math.max(...data.fixtures.map(f => f.round_number || 1));
    }

    // Clamp currentSelectedRound
    if (currentSelectedRound < 1) currentSelectedRound = 1;
    if (currentSelectedRound > maxRound) currentSelectedRound = maxRound;

    // Update Round Navigator UI
    updateRoundNavigatorUI(data.fixtures, maxRound);

    // Render Table
    renderLeagueTable(data.table);

    // Render Fixtures for currentSelectedRound
    renderFixturesList(data.fixtures);


    // Render Player Season Stats
    renderLeaguePlayerStats(data.player_stats);
}




function updateRoundNavigatorUI(fixtures, totalRounds) {
    const roundSelect = document.getElementById('round-select-dropdown');
    const prevBtn = document.getElementById('prev-round-btn');
    const nextBtn = document.getElementById('next-round-btn');

    if (roundSelect) {
        roundSelect.innerHTML = '';
        for (let r = 1; r <= totalRounds; r++) {
            const roundFixtures = fixtures ? fixtures.filter(f => (f.round_number || 1) === r) : [];
            const finishedCount = roundFixtures.filter(f => f.is_finished).length;
            const totalCount = roundFixtures.length;

            const option = document.createElement('option');
            option.value = r;
            option.textContent = `KOLEJKA ${r} (${finishedCount}/${totalCount} rozegranych)`;
            if (r === currentSelectedRound) {
                option.selected = true;
            }
            roundSelect.appendChild(option);
        }
    }

    if (prevBtn) {
        prevBtn.disabled = currentSelectedRound <= 1;
    }
    if (nextBtn) {
        nextBtn.disabled = currentSelectedRound >= totalRounds;
    }
}

export function changeRound(delta) {
    currentSelectedRound += delta;
    if (currentLeagueData) {
        renderLeagueView(currentLeagueData);
    }
}

export function selectRound(roundNum) {
    currentSelectedRound = parseInt(roundNum, 10);
    if (currentLeagueData) {
        renderLeagueView(currentLeagueData);
    }
}

function renderLeagueTable(tableData) {
    const tbody = document.getElementById('league-table-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!tableData || tableData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="empty-table-msg">Brak danych w tabeli</td></tr>';
        return;
    }

    const sorted = [...tableData].sort((a, b) => {
        if (b.points !== a.points) return b.points - a.points;
        if (b.goal_difference !== a.goal_difference) return b.goal_difference - a.goal_difference;
        return b.goals_scored - a.goals_scored;
    });

    sorted.forEach((team, index) => {
        const rank = index + 1;
        const tr = document.createElement('tr');

        let rankClass = '';
        let rankBadge = `${rank}`;
        if (rank === 1) {
            rankClass = 'gold-rank';
            rankBadge = '🥇';
        } else if (rank === 2) {
            rankClass = 'silver-rank';
            rankBadge = '🥈';
        } else if (rank === 3) {
            rankClass = 'bronze-rank';
            rankBadge = '🥉';
        }

        tr.className = `table-row ${rankClass}`;

        tr.innerHTML = `
            <td class="text-center font-bold rank-cell">${rankBadge}</td>
            <td class="team-name-cell">
                <span class="table-team-badge">${getTeamInitials(team.team_name)}</span>
                <span class="table-team-text">${team.team_name}</span>
            </td>
            <td class="text-center">${team.matches_played}</td>
            <td class="text-center text-green font-semibold">${team.wins}</td>
            <td class="text-center text-gold">${team.draws}</td>
            <td class="text-center text-red">${team.loses}</td>
            <td class="text-center">${team.goals_scored}</td>
            <td class="text-center">${team.goals_conceded}</td>
            <td class="text-center ${team.goal_difference > 0 ? 'text-green' : team.goal_difference < 0 ? 'text-red' : ''}">
                ${team.goal_difference > 0 ? '+' : ''}${team.goal_difference}
            </td>
            <td class="text-center highlight-col font-bold points-cell">${team.points}</td>
        `;

        tbody.appendChild(tr);
    });
}

export function setFixturesFilter(filter) {
    currentFilter = filter;

    const allBtn = document.getElementById('filter-fixtures-all');
    const pendingBtn = document.getElementById('filter-fixtures-pending');
    const finishedBtn = document.getElementById('filter-fixtures-finished');

    if (allBtn) allBtn.classList.toggle('active', filter === 'all');
    if (pendingBtn) pendingBtn.classList.toggle('active', filter === 'pending');
    if (finishedBtn) finishedBtn.classList.toggle('active', filter === 'finished');

    if (currentLeagueData && currentLeagueData.fixtures) {
        renderFixturesList(currentLeagueData.fixtures);
    }
}

function renderFixturesList(fixtures) {
    const listContainer = document.getElementById('league-fixtures-list');
    if (!listContainer) return;

    listContainer.innerHTML = '';

    if (!fixtures || fixtures.length === 0) {
        listContainer.innerHTML = '<div class="empty-events">Brak meczów w terminarzu.</div>';
        return;
    }

    // Filter by currentSelectedRound first
    const roundFixtures = fixtures.map((f, originalIndex) => ({ ...f, originalIndex }))
        .filter(f => (f.round_number || 1) === currentSelectedRound);

    if (roundFixtures.length === 0) {
        listContainer.innerHTML = `<div class="empty-events">Brak meczów w Kolejce ${currentSelectedRound}.</div>`;
        return;
    }

    const filtered = roundFixtures.filter(f => {
        if (currentFilter === 'pending') return !f.is_finished;
        if (currentFilter === 'finished') return f.is_finished;
        return true;
    });

    if (filtered.length === 0) {
        listContainer.innerHTML = `<div class="empty-events">Brak meczów w kategorii "${currentFilter === 'pending' ? 'Do rozegrania' : 'Zakończone'}" w Kolejce ${currentSelectedRound}.</div>`;
        return;
    }

    filtered.forEach((fixture) => {
        const card = document.createElement('div');
        card.className = `fixture-card ${fixture.is_finished ? 'finished' : 'pending'}`;

        const homeInitials = getTeamInitials(fixture.home_team_name);
        const awayInitials = getTeamInitials(fixture.away_team_name);

        const scoreText = fixture.is_finished ? `${fixture.home_score} - ${fixture.away_score}` : 'vs';

        card.innerHTML = `
            <div class="fixture-header-row">
                <span class="fixture-number">Kolejka ${fixture.round_number} • Mecz #${fixture.originalIndex + 1}</span>
                <span class="fixture-status-badge ${fixture.is_finished ? 'status-finished' : 'status-pending'}">
                    ${fixture.is_finished ? 'ZAKOŃCZONY' : 'DO ROZEGRANIA'}
                </span>
            </div>

            <div class="fixture-teams-row">
                <div class="fixture-team home">
                    <span class="fixture-team-badge home">${homeInitials}</span>
                    <span class="fixture-team-name">${fixture.home_team_name}</span>
                </div>

                <div class="fixture-score-badge ${fixture.is_finished ? 'has-score' : ''}">
                    ${scoreText}
                </div>

                <div class="fixture-team away">
                    <span class="fixture-team-name">${fixture.away_team_name}</span>
                    <span class="fixture-team-badge away">${awayInitials}</span>
                </div>
            </div>
        `;

        if (!fixture.is_finished) {
            const footer = document.createElement('div');
            footer.className = 'fixture-footer-row';

            const watchLiveBtn = document.createElement('button');
            watchLiveBtn.type = 'button';
            watchLiveBtn.className = 'metro-btn-sm live-match-btn';
            watchLiveBtn.innerHTML = '🔴 OGLĄDAJ NA ŻYWO';
            watchLiveBtn.onclick = () => watchLeagueMatchLive(fixture.originalIndex);

            const playBtn = document.createElement('button');
            playBtn.type = 'button';
            playBtn.className = 'metro-btn-sm play-match-btn';
            playBtn.innerHTML = '⚡ SYMULUJ SZYBKO';
            playBtn.onclick = () => playSingleLeagueMatch(fixture.originalIndex);

            footer.appendChild(watchLiveBtn);
            footer.appendChild(playBtn);
            card.appendChild(footer);
        }

        listContainer.appendChild(card);
    });
}

export async function watchLeagueMatchLive(matchIndex) {
    try {
        const response = await fetch('/league/match/live_start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ match_index: matchIndex })
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`Błąd uruchamiania transmisji na żywo: ${errData.detail || 'Nie można połączyć z meczem'}`);
            return;
        }

        const data = await response.json();
        renderMatchData(data);
        await fetchPlayerStats();
        switchView('match');
        startLiveStream();
    } catch (err) {
        console.error('Błąd transmisji na żywo:', err);
    }
}

export async function playSingleLeagueMatch(matchIndex) {
    try {
        const response = await fetch('/league/match/status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ match_index: matchIndex })
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`Błąd rozegrania meczu: ${errData.detail || 'Nie udało się symulować meczu'}`);
            return;
        }

        const data = await response.json();
        currentLeagueData = data;
        renderLeagueView(data);
    } catch (err) {
        console.error('Błąd podczas symulacji meczu:', err);
    }
}

export async function playCurrentRoundMatches() {
    if (!currentLeagueData || !currentLeagueData.fixtures) return;

    const targetRound = currentSelectedRound;
    const unplayedCount = currentLeagueData.fixtures.filter(
        f => (f.round_number || 1) === targetRound && !f.is_finished
    ).length;

    if (unplayedCount === 0) {
        alert(`Wszystkie mecze w Kolejce ${targetRound} zostały już rozegrane!`);
        return;
    }

    const simBtn = document.getElementById('sim-current-round-btn');
    if (simBtn) {
        simBtn.disabled = true;
        simBtn.innerHTML = '⚡ SYMULOWANIE...';
    }

    while (currentLeagueData && currentLeagueData.fixtures) {
        const nextIndex = currentLeagueData.fixtures.findIndex(
            f => (f.round_number || 1) === targetRound && !f.is_finished
        );

        if (nextIndex === -1) break;

        await playSingleLeagueMatch(nextIndex);
        await new Promise(res => setTimeout(res, 80));
    }

    if (simBtn) {
        simBtn.disabled = false;
        simBtn.innerHTML = '⚡ Symuluj kolejkę';
    }
}

export async function playAllLeagueMatches() {
    if (!currentLeagueData || !currentLeagueData.fixtures) return;

    const unplayedCount = currentLeagueData.fixtures.filter(f => !f.is_finished).length;
    if (unplayedCount === 0) {
        alert('Wszystkie mecze w tej lidze zostały już rozegrane!');
        return;
    }

    const simBtn = document.getElementById('sim-all-matches-btn');
    if (simBtn) {
        simBtn.disabled = true;
        simBtn.innerHTML = '⚡ SYMULOWANIE...';
    }

    isSimulatingAll = true;

    while (isSimulatingAll && currentLeagueData) {
        const nextIndex = currentLeagueData.fixtures.findIndex(f => !f.is_finished);
        if (nextIndex === -1) break;

        await playSingleLeagueMatch(nextIndex);
        await new Promise(res => setTimeout(res, 80));
    }

    isSimulatingAll = false;

    if (simBtn) {
        simBtn.disabled = false;
        simBtn.innerHTML = '<span class="btn-icon">⚡</span> SYMULUJ CAŁY SEZON';
    }
}

export function selectAllTeams(select = true) {
    const checkboxes = document.querySelectorAll('input[name="league-team-select"]');
    checkboxes.forEach(cb => cb.checked = select);
}

/* ==========================================================================
   PLAYER SEASON STATS & MODAL RENDERERS
   ========================================================================== */

let currentModalCategory = 'goals';
let currentModalSearch = '';
let currentLeaguePlayerStats = [];

export function renderLeaguePlayerStats(playerStats) {
    currentLeaguePlayerStats = playerStats || [];
    const container = document.getElementById('league-player-stats-grid');
    if (!container) return;

    if (!playerStats || playerStats.length === 0) {
        container.innerHTML = '<div class="empty-events" style="grid-column: 1 / -1; text-align: center;">Brak statystyk zawodników w bieżącym sezonie. Rozegraj mecze, aby zobaczyć wyniki!</div>';
        return;
    }

    // 1. Top Scorers (Bramki)
    const topScorers = [...playerStats]
        .sort((a, b) => b.goals - a.goals || b.assists - a.assists)
        .slice(0, 5);

    // 2. Top Assists (Asysty)
    const topAssists = [...playerStats]
        .sort((a, b) => b.assists - a.assists || b.goals - a.goals)
        .slice(0, 5);

    // 3. Most Cards (Kartki)
    const mostCards = [...playerStats]
        .sort((a, b) => (b.yellow_cards + b.red_cards * 2) - (a.yellow_cards + a.red_cards * 2))
        .slice(0, 5);

    // 4. Clean Sheets (Czyste Konta)
    const cleanSheets = [...playerStats]
        .filter(p => p.position === 'GOALKEEPER')
        .sort((a, b) => b.clean_sheets - a.clean_sheets)
        .slice(0, 5);

    container.innerHTML = `
        ${createCategoryCard('⚽ NAJLEPSI STRZELCY', topScorers, p => `${p.goals} gol(i)`, 'goals')}
        ${createCategoryCard('🅰️ NAJLEPSI ASYSTENCI', topAssists, p => `${p.assists} asyst`, 'assists')}
        ${createCategoryCard('🟨 NAJWIĘCEJ KARTEK', mostCards, p => `${p.yellow_cards}🟨 ${p.red_cards}🟥`, 'cards')}
        ${createCategoryCard('🧤 CZYSTE KONTA', cleanSheets, p => `${p.clean_sheets} mecz(e)`, 'cleansheets')}
    `;

    container.querySelectorAll('.category-open-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const cat = btn.getAttribute('data-category');
            openPlayerStatsModal(cat || 'goals');
        });
    });
}

function createCategoryCard(title, players, statFormatter, categoryKey) {
    const rowsHtml = players.map((p, idx) => {
        const rank = idx + 1;
        const rankBadge = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `${rank}.`;
        const isTop = rank <= 3;
        return `
            <div class="stat-player-item ${isTop ? 'rank-top' : ''}">
                <div class="stat-player-left">
                    <span class="stat-player-rank">${rankBadge}</span>
                    <div class="stat-player-info">
                        <span class="stat-player-name">${p.player_name}</span>
                        <span class="stat-player-pos">${getShortPosition(p.position)}</span>
                    </div>
                </div>
                <span class="stat-player-val">${statFormatter(p)}</span>
            </div>
        `;
    }).join('');

    return `
        <div class="league-stat-card">
            <div class="stat-card-header">
                <div class="stat-card-title">${title}</div>
            </div>
            <div class="stat-card-body">
                ${rowsHtml || '<div class="empty-stats">Brak danych</div>'}
            </div>
            <div class="stat-card-footer">
                <button type="button" class="stat-card-footer-btn category-open-btn" data-category="${categoryKey}">
                    Pokaż pełną listę →
                </button>
            </div>
        </div>
    `;
}


export function openPlayerStatsModal(category = 'goals') {
    currentModalCategory = category;
    currentModalSearch = '';

    const modal = document.getElementById('player-stats-modal');
    const searchInput = document.getElementById('modal-player-search');
    if (searchInput) searchInput.value = '';

    document.querySelectorAll('.modal-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-category') === category);
    });

    if (modal) modal.classList.remove('hidden');
    renderModalTable();
}

export function closePlayerStatsModal() {
    const modal = document.getElementById('player-stats-modal');
    if (modal) modal.classList.add('hidden');
}

export function setModalCategory(category) {
    currentModalCategory = category;
    document.querySelectorAll('.modal-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-category') === category);
    });
    renderModalTable();
}

export function setModalSearch(query) {
    currentModalSearch = query;
    renderModalTable();
}

export function renderModalTable() {
    const tbody = document.getElementById('modal-player-stats-tbody');
    if (!tbody) return;

    let players = [...currentLeaguePlayerStats];

    if (currentModalSearch.trim() !== '') {
        const query = currentModalSearch.toLowerCase().trim();
        players = players.filter(p => p.player_name.toLowerCase().includes(query) || p.position.toLowerCase().includes(query));
    }

    if (currentModalCategory === 'goals') {
        players.sort((a, b) => b.goals - a.goals || b.assists - a.assists);
    } else if (currentModalCategory === 'assists') {
        players.sort((a, b) => b.assists - a.assists || b.goals - a.goals);
    } else if (currentModalCategory === 'cards') {
        players.sort((a, b) => (b.yellow_cards + b.red_cards * 2) - (a.yellow_cards + a.red_cards * 2));
    } else if (currentModalCategory === 'cleansheets') {
        players = players.filter(p => p.position === 'GOALKEEPER').sort((a, b) => b.clean_sheets - a.clean_sheets);
    } else if (currentModalCategory === 'all') {
        players.sort((a, b) => a.player_name.localeCompare(b.player_name));
    }

    if (players.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty-table-msg">Brak zawodników spełniających kryteria.</td></tr>';
        return;
    }

    tbody.innerHTML = players.map((p, idx) => {
        const rank = idx + 1;
        const rankBadge = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `${rank}`;
        return `
            <tr class="table-row">
                <td class="text-center font-bold rank-cell">${rankBadge}</td>
                <td class="font-semibold">${p.player_name}</td>
                <td class="text-center text-sub font-semibold">${getShortPosition(p.position)}</td>
                <td class="text-center">${p.matches_played}</td>
                <td class="text-center highlight-col font-bold points-cell">${p.goals}</td>
                <td class="text-center text-green font-semibold">${p.assists}</td>
                <td class="text-center">${p.yellow_cards} 🟨 / ${p.red_cards} 🟥</td>
                <td class="text-center text-gold font-bold">${p.clean_sheets}</td>
                <td class="text-center text-sub">${p.passes}</td>
            </tr>
        `;
    }).join('');
}



window.openPlayerStatsModal = openPlayerStatsModal;


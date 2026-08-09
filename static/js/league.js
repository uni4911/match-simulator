import { getTeamInitials, getShortPosition, getPositionClass, getEventIcon } from './helpers.js';
import { renderMatchData, switchView, startLiveStream } from './match.js';
import { fetchPlayerStats, createPlayerStatCard } from './stats.js';

let currentLeagueData = null;
let currentFilter = 'all'; // 'all', 'pending', 'finished'
let currentSelectedRound = 1;
let isSimulatingAll = false;
let stopSeasonAfterRound = null;

let allLeagueTeamsDetailed = [];
let selectedTeamNames = new Set();
let collapsedLeagues = new Set();
let teamSearchQuery = '';
let teamLeagueFilter = 'ALL';
let teamViewMode = 'grouped';
let teamShowOnlySelected = false;
let isTeamEventsBound = false;

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

        if (data.teams_detailed && data.teams_detailed.length > 0) {
            allLeagueTeamsDetailed = data.teams_detailed;
        } else if (data.teams && data.teams.length > 0) {
            allLeagueTeamsDetailed = data.teams.map(t => ({ name: t, league: 'Inne' }));
        } else {
            allLeagueTeamsDetailed = [];
        }

        // Teams are NOT selected by default. User must search and pick teams.

        populateLeagueFilterDropdown(data.leagues);
        bindTeamSelectionEvents();
        renderLeagueTeamSelection();
    } catch (err) {
        console.error('Błąd podczas ładowania drużyn do ligi:', err);
    }
}

function populateLeagueFilterDropdown(leaguesList) {
    const selectEl = document.getElementById('league-filter-select');
    if (!selectEl) return;

    const counts = {};
    allLeagueTeamsDetailed.forEach(t => {
        counts[t.league] = (counts[t.league] || 0) + 1;
    });

    const sortedLeagues = leaguesList && leaguesList.length > 0
        ? leaguesList
        : Object.keys(counts).sort();

    selectEl.innerHTML = '';

    const allOpt = document.createElement('option');
    allOpt.value = 'ALL';
    allOpt.textContent = `Wszystkie ligi (${allLeagueTeamsDetailed.length})`;
    selectEl.appendChild(allOpt);

    sortedLeagues.forEach(lg => {
        const cnt = counts[lg] || 0;
        if (cnt > 0) {
            const opt = document.createElement('option');
            opt.value = lg;
            opt.textContent = `${lg} (${cnt})`;
            selectEl.appendChild(opt);
        }
    });

    selectEl.value = teamLeagueFilter;
}

let searchDebounceTimer = null;

function bindTeamSelectionEvents() {
    if (isTeamEventsBound) return;
    isTeamEventsBound = true;

    const searchInput = document.getElementById('league-team-search');
    const clearBtn = document.getElementById('clear-search-btn');
    const filterSelect = document.getElementById('league-filter-select');
    const groupSelect = document.getElementById('league-group-select');
    const showOnlySelectedCheckbox = document.getElementById('show-only-selected-checkbox');

    const selectVisibleBtn = document.getElementById('select-visible-teams-btn');
    const deselectVisibleBtn = document.getElementById('deselect-visible-teams-btn');
    const selectAllBtn = document.getElementById('select-all-teams-btn');
    const deselectAllBtn = document.getElementById('deselect-all-teams-btn');
    const clearSelectedBtn = document.getElementById('clear-selected-teams-btn');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchDebounceTimer);
            const val = e.target.value.trim().toLowerCase();
            if (clearBtn) {
                if (val.length > 0) clearBtn.classList.remove('hidden');
                else clearBtn.classList.add('hidden');
            }
            searchDebounceTimer = setTimeout(() => {
                teamSearchQuery = val;
                renderLeagueTeamSelection();
            }, 120);
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (searchInput) searchInput.value = '';
            teamSearchQuery = '';
            clearBtn.classList.add('hidden');
            renderLeagueTeamSelection();
        });
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', (e) => {
            teamLeagueFilter = e.target.value;
            renderLeagueTeamSelection();
        });
    }

    if (groupSelect) {
        groupSelect.addEventListener('change', (e) => {
            teamViewMode = e.target.value;
            renderLeagueTeamSelection();
        });
    }

    if (showOnlySelectedCheckbox) {
        showOnlySelectedCheckbox.addEventListener('change', (e) => {
            teamShowOnlySelected = e.target.checked;
            renderLeagueTeamSelection();
        });
    }

    if (selectVisibleBtn) {
        selectVisibleBtn.addEventListener('click', () => {
            const visibleTeams = getCurrentlyFilteredTeams();
            visibleTeams.forEach(t => selectedTeamNames.add(t.name));
            renderLeagueTeamSelection();
        });
    }

    if (deselectVisibleBtn) {
        deselectVisibleBtn.addEventListener('click', () => {
            const visibleTeams = getCurrentlyFilteredTeams();
            visibleTeams.forEach(t => selectedTeamNames.delete(t.name));
            renderLeagueTeamSelection();
        });
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => selectAllTeams(true));
    }

    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', () => selectAllTeams(false));
    }

    if (clearSelectedBtn) {
        clearSelectedBtn.addEventListener('click', () => {
            selectedTeamNames.clear();
            renderLeagueTeamSelection();
        });
    }
}

function getCurrentlyFilteredTeams() {
    return allLeagueTeamsDetailed.filter(team => {
        if (teamLeagueFilter !== 'ALL' && team.league !== teamLeagueFilter) {
            return false;
        }

        if (teamShowOnlySelected && !selectedTeamNames.has(team.name)) {
            return false;
        }

        if (teamSearchQuery) {
            const nameMatch = team.name.toLowerCase().includes(teamSearchQuery);
            const leagueMatch = team.league.toLowerCase().includes(teamSearchQuery);
            if (!nameMatch && !leagueMatch) return false;
        }

        return true;
    });
}

export function selectAllTeams(select = true) {
    if (select) {
        allLeagueTeamsDetailed.forEach(t => selectedTeamNames.add(t.name));
    } else {
        selectedTeamNames.clear();
    }
    renderLeagueTeamSelection();
}

export function renderSelectedTeamsList() {
    const listContainer = document.getElementById('selected-teams-list');
    const countEl = document.getElementById('selected-teams-count');
    const clearBtn = document.getElementById('clear-selected-teams-btn');

    if (countEl) {
        countEl.textContent = selectedTeamNames.size;
    }

    if (clearBtn) {
        if (selectedTeamNames.size > 0) {
            clearBtn.classList.remove('hidden');
        } else {
            clearBtn.classList.add('hidden');
        }
    }

    if (!listContainer) return;

    if (selectedTeamNames.size === 0) {
        listContainer.innerHTML = '<div class="selected-teams-empty">Nie wybrano jeszcze żadnej drużyny. Wyszukaj drużyny poniżej i dodaj je do ligi.</div>';
        return;
    }

    listContainer.innerHTML = '';
    const fragment = document.createDocumentFragment();

    const teamMap = new Map();
    allLeagueTeamsDetailed.forEach(t => teamMap.set(t.name, t));

    Array.from(selectedTeamNames).forEach(teamName => {
        const teamObj = teamMap.get(teamName) || { name: teamName, league: 'Inne' };

        const chip = document.createElement('div');
        chip.className = 'selected-team-chip';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'chip-team-name';
        nameSpan.textContent = teamObj.name;

        const leagueSpan = document.createElement('span');
        leagueSpan.className = 'chip-league';
        leagueSpan.textContent = teamObj.league;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'chip-remove';
        removeBtn.title = `Usuń ${teamObj.name} z ligi`;
        removeBtn.textContent = '✕';
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            selectedTeamNames.delete(teamName);
            renderLeagueTeamSelection();
        });

        chip.appendChild(nameSpan);
        chip.appendChild(leagueSpan);
        chip.appendChild(removeBtn);
        fragment.appendChild(chip);
    });

    listContainer.appendChild(fragment);
}

function updateSelectionCounters() {
    renderSelectedTeamsList();

    const selectedCountNum = document.getElementById('selected-count-number');
    const countBadge = document.getElementById('league-teams-count-badge');
    const totalSelected = selectedTeamNames.size;
    const totalAvailable = allLeagueTeamsDetailed.length;

    if (selectedCountNum) selectedCountNum.textContent = totalSelected;
    if (countBadge) {
        countBadge.textContent = `${totalSelected} WYBRANYCH Z ${totalAvailable}`;
        if (totalSelected >= 2) {
            countBadge.className = 'tile-badge-info';
        } else {
            countBadge.className = 'tile-badge-warning';
        }
    }
}

export function renderLeagueTeamSelection() {
    const container = document.getElementById('league-team-checkboxes');
    if (!container) return;

    updateSelectionCounters();

    const isSearching = Boolean(teamSearchQuery.trim().length > 0);
    const hasFilter = teamLeagueFilter !== 'ALL' || teamShowOnlySelected;

    if (!isSearching && !hasFilter) {
        container.innerHTML = `
            <div class="search-prompt-box">
                <span class="search-prompt-icon">🔍</span>
                <div class="search-prompt-title">Wyszukaj drużyny do ligi</div>
                <div class="search-prompt-desc">Wpisz nazwę drużyny lub ligi w polu wyszukiwania powyżej (np. <em>Real</em>, <em>Premier League</em>), aby wyświetlić dostępne zespoły.</div>
            </div>
        `;
        return;
    }

    const filteredTeams = getCurrentlyFilteredTeams();
    const fragment = document.createDocumentFragment();

    if (filteredTeams.length === 0) {
        container.innerHTML = `<div class="no-teams-found">Brak drużyn spełniających kryteria wyszukiwania.</div>`;
        return;
    }

    if (teamViewMode === 'grouped') {
        const grouped = {};
        filteredTeams.forEach(t => {
            if (!grouped[t.league]) grouped[t.league] = [];
            grouped[t.league].push(t);
        });

        const sortedLeagues = Object.keys(grouped).sort();
        const isFiltering = Boolean(teamSearchQuery || teamLeagueFilter !== 'ALL' || teamShowOnlySelected);

        sortedLeagues.forEach(leagueName => {
            const teamsInLeague = grouped[leagueName];
            const isCollapsed = isFiltering ? collapsedLeagues.has(leagueName) : (collapsedLeagues.size === 0 ? true : collapsedLeagues.has(leagueName));

            const selectedInLeague = teamsInLeague.filter(t => selectedTeamNames.has(t.name)).length;

            const block = document.createElement('div');
            block.className = 'league-group-block';

            const header = document.createElement('div');
            header.className = 'league-group-header';

            const titleBlock = document.createElement('div');
            titleBlock.className = 'league-group-title';

            const countEl = document.createElement('span');
            countEl.className = 'league-group-count';
            countEl.textContent = `${selectedInLeague} / ${teamsInLeague.length} wybranych`;

            titleBlock.innerHTML = `<span>🏆 ${leagueName}</span>`;
            titleBlock.appendChild(countEl);

            const actionsBlock = document.createElement('div');
            actionsBlock.className = 'league-group-actions';

            const selectLeagueBtn = document.createElement('button');
            selectLeagueBtn.type = 'button';
            selectLeagueBtn.className = 'metro-btn-sm primary-sm';
            selectLeagueBtn.textContent = 'Zaznacz ligę';
            selectLeagueBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                teamsInLeague.forEach(t => selectedTeamNames.add(t.name));
                renderLeagueTeamSelection();
            });

            const deselectLeagueBtn = document.createElement('button');
            deselectLeagueBtn.type = 'button';
            deselectLeagueBtn.className = 'metro-btn-sm';
            deselectLeagueBtn.textContent = 'Odznacz ligę';
            deselectLeagueBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                teamsInLeague.forEach(t => selectedTeamNames.delete(t.name));
                renderLeagueTeamSelection();
            });

            const toggleIcon = document.createElement('span');
            toggleIcon.style.fontSize = '0.8rem';
            toggleIcon.style.color = '#8a99ad';
            toggleIcon.textContent = isCollapsed ? '▼' : '▲';

            actionsBlock.appendChild(selectLeagueBtn);
            actionsBlock.appendChild(deselectLeagueBtn);
            actionsBlock.appendChild(toggleIcon);

            header.appendChild(titleBlock);
            header.appendChild(actionsBlock);

            const body = document.createElement('div');
            body.className = `league-group-body ${isCollapsed ? 'collapsed' : ''}`;

            const grid = document.createElement('div');
            grid.className = 'league-teams-grid';

            header.addEventListener('click', () => {
                const nowCollapsed = !body.classList.contains('collapsed');
                if (nowCollapsed) {
                    body.classList.add('collapsed');
                    toggleIcon.textContent = '▼';
                    collapsedLeagues.add(leagueName);
                } else {
                    body.classList.remove('collapsed');
                    toggleIcon.textContent = '▲';
                    collapsedLeagues.delete(leagueName);
                    if (grid.children.length === 0) {
                        teamsInLeague.sort((a, b) => a.name.localeCompare(b.name)).forEach(team => {
                            const card = createTeamCheckboxCard(team, countEl, teamsInLeague);
                            grid.appendChild(card);
                        });
                    }
                }
            });

            if (!isCollapsed) {
                teamsInLeague.sort((a, b) => a.name.localeCompare(b.name)).forEach(team => {
                    const card = createTeamCheckboxCard(team, countEl, teamsInLeague);
                    grid.appendChild(card);
                });
            }

            body.appendChild(grid);
            block.appendChild(header);
            block.appendChild(body);
            fragment.appendChild(block);
        });
    } else {
        const grid = document.createElement('div');
        grid.className = 'league-teams-grid';

        filteredTeams.sort((a, b) => a.name.localeCompare(b.name)).forEach(team => {
            const card = createTeamCheckboxCard(team, null, null, true);
            grid.appendChild(card);
        });

        fragment.appendChild(grid);
    }

    container.innerHTML = '';
    container.appendChild(fragment);
}

function createTeamCheckboxCard(team, leagueGroupCountEl = null, teamsInLeague = null, showSubLeague = false) {
    const isChecked = selectedTeamNames.has(team.name);

    const label = document.createElement('label');
    label.className = `team-checkbox-card ${isChecked ? 'selected' : ''}`;

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.name = 'league-team-select';
    checkbox.value = team.name;
    checkbox.checked = isChecked;

    checkbox.addEventListener('change', (e) => {
        if (e.target.checked) {
            selectedTeamNames.add(team.name);
            label.classList.add('selected');
        } else {
            selectedTeamNames.delete(team.name);
            label.classList.remove('selected');
        }
        updateSelectionCounters();
        if (leagueGroupCountEl && teamsInLeague) {
            const selCount = teamsInLeague.filter(t => selectedTeamNames.has(t.name)).length;
            leagueGroupCountEl.textContent = `${selCount} / ${teamsInLeague.length} wybranych`;
        }
    });

    const badge = document.createElement('span');
    badge.className = 'team-checkbox-badge';
    badge.textContent = getTeamInitials(team.name);

    const text = document.createElement('span');
    text.className = 'team-checkbox-name';
    text.textContent = team.name;

    label.appendChild(checkbox);
    label.appendChild(badge);
    label.appendChild(text);

    if (showSubLeague && team.league) {
        const sub = document.createElement('span');
        sub.className = 'team-checkbox-league-sub';
        sub.textContent = team.league;
        label.appendChild(sub);
    }

    return label;
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

    const leagueName = nameInput ? nameInput.value.trim() || 'Moja liga' : 'Moja liga';
    const doubleRound = doubleRoundCheckbox ? doubleRoundCheckbox.checked : false;
    const selectedTeams = Array.from(selectedTeamNames);

    if (selectedTeams.length < 2) {
        alert('Musisz wybrać co najmniej 2 drużyny, aby utworzyć ligę!');
        return;
    }

    if (selectedTeams.length > 64) {
        alert('Maksymalna liczba drużyn w jednej lidze to 64! Odznacz część drużyn (np. przefiltruj wg konkretnej ligi), aby utworzyć rozgrywki.');
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
    renderModalTable();
}

let currentLeagueSubTab = 'table';

export function switchLeagueSubTab(tabName) {
    currentLeagueSubTab = tabName;
    const tableTabBtn = document.getElementById('league-subtab-table');
    const statsTabBtn = document.getElementById('league-subtab-stats');
    const tableView = document.getElementById('league-panel-table');
    const statsView = document.getElementById('league-panel-stats');

    if (tableTabBtn) tableTabBtn.classList.toggle('active', tabName === 'table');
    if (statsTabBtn) statsTabBtn.classList.toggle('active', tabName === 'stats');

    if (tableView) tableView.classList.toggle('hidden', tabName !== 'table');
    if (statsView) statsView.classList.toggle('hidden', tabName !== 'stats');

    if (tabName === 'stats') {
        if (currentLeagueData && currentLeagueData.player_stats) {
            renderLeaguePlayerStats(currentLeagueData.player_stats);
        }
        renderModalTable();
    }
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

function renderFormBadges(recentResults) {
    if (!recentResults || recentResults.length === 0) {
        return '<div class="form-badges-container"><span class="form-badge-empty-text">—</span></div>';
    }

    const badgesHtml = recentResults.map(res => {
        const r = String(res).toUpperCase();
        if (r === 'W' || r === 'Z') {
            return '<span class="form-badge form-badge-win" title="Wygrana (Win)">W</span>';
        } else if (r === 'D' || r === 'R') {
            return '<span class="form-badge form-badge-draw" title="Remis (Draw)">R</span>';
        } else if (r === 'L' || r === 'P') {
            return '<span class="form-badge form-badge-loss" title="Porażka (Loss)">P</span>';
        }
        return `<span class="form-badge form-badge-draw" title="${res}">${res}</span>`;
    }).join('');

    return `<div class="form-badges-container">${badgesHtml}</div>`;
}

function renderLeagueTable(tableData) {
    const tbody = document.getElementById('league-table-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!tableData || tableData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" class="empty-table-msg">Brak danych w tabeli</td></tr>';
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

        const formHtml = renderFormBadges(team.form || team.recent_results);

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
            <td class="text-center form-cell">${formHtml}</td>
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
        } else {
            const footer = document.createElement('div');
            footer.className = 'fixture-footer-row';

            const statsBtn = document.createElement('button');
            statsBtn.type = 'button';
            statsBtn.className = 'metro-btn-sm match-stats-btn';
            statsBtn.style.width = '100%';
            statsBtn.style.background = 'var(--metro-blue)';
            statsBtn.style.borderColor = 'var(--metro-accent-blue)';
            statsBtn.style.fontWeight = '700';
            statsBtn.innerHTML = '📊 STATYSTYKI MECZU';
            statsBtn.onclick = () => openMatchDetailsModal(fixture);

            footer.appendChild(statsBtn);
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

    let targetRound = currentSelectedRound;
    let unplayedCount = currentLeagueData.fixtures.filter(
        f => (f.round_number || 1) === targetRound && !f.is_finished
    ).length;

    // If current round is already finished, try moving to the next unplayed round
    if (unplayedCount === 0) {
        const nextPending = currentLeagueData.fixtures.find(f => !f.is_finished);
        if (nextPending) {
            targetRound = nextPending.round_number || 1;
            currentSelectedRound = targetRound;
            renderLeagueView(currentLeagueData);
            unplayedCount = currentLeagueData.fixtures.filter(
                f => (f.round_number || 1) === targetRound && !f.is_finished
            ).length;
        } else {
            alert(`Wszystkie mecze w Kolejce ${targetRound} (oraz w całej lidze) zostały już rozegrane!`);
            return;
        }
    }

    const simBtn = document.getElementById('sim-current-round-btn');
    if (simBtn) {
        simBtn.disabled = true;
        simBtn.innerHTML = '<span class="btn-icon">⚡</span> SYMULOWANIE...';
    }

    while (currentLeagueData && currentLeagueData.fixtures) {
        const nextIndex = currentLeagueData.fixtures.findIndex(
            f => (f.round_number || 1) === targetRound && !f.is_finished
        );

        if (nextIndex === -1) break;

        await playSingleLeagueMatch(nextIndex);
        await new Promise(res => setTimeout(res, 80));
    }

    // Automatically move to next round if available
    if (currentLeagueData && currentLeagueData.fixtures && currentLeagueData.fixtures.length > 0) {
        const maxRound = Math.max(...currentLeagueData.fixtures.map(f => f.round_number || 1));
        if (targetRound < maxRound) {
            currentSelectedRound = targetRound + 1;
            renderLeagueView(currentLeagueData);
        }
    }

    if (simBtn) {
        simBtn.disabled = false;
        simBtn.innerHTML = '<span class="btn-icon">⚡</span> SYMULUJ KOLEJKĘ';
    }
}

export function requestStopLeagueSimulation() {
    if (!isSimulatingAll) return;

    stopSeasonAfterRound = currentSelectedRound;

    const stopBtn = document.getElementById('stop-sim-all-btn');
    if (stopBtn) {
        stopBtn.disabled = true;
        stopBtn.innerHTML = `<span class="btn-icon">⏳</span> DOKAŃCZANIE KOLEJKI ${stopSeasonAfterRound}...`;
    }

    const simAllBtn = document.getElementById('sim-all-matches-btn');
    if (simAllBtn) {
        simAllBtn.innerHTML = `<span class="btn-icon">⏳</span> ZATRZYMYWANIE...`;
    }
}

export async function playAllLeagueMatches() {
    if (!currentLeagueData || !currentLeagueData.fixtures) return;

    const unplayedCount = currentLeagueData.fixtures.filter(f => !f.is_finished).length;
    if (unplayedCount === 0) {
        alert('Wszystkie mecze w tej lidze zostały już rozegrane!');
        return;
    }

    const simAllBtn = document.getElementById('sim-all-matches-btn');
    const simRoundBtn = document.getElementById('sim-current-round-btn');
    const stopBtn = document.getElementById('stop-sim-all-btn');

    if (simAllBtn) {
        simAllBtn.disabled = true;
        simAllBtn.innerHTML = '<span class="btn-icon">⚡</span> SYMULOWANIE...';
    }

    if (simRoundBtn) {
        simRoundBtn.disabled = true;
    }

    if (stopBtn) {
        stopBtn.classList.remove('hidden');
        stopBtn.disabled = false;
        stopBtn.innerHTML = '<span class="btn-icon">⏹</span> ZATRZYMAJ PO KOLEJCE';
    }

    isSimulatingAll = true;
    stopSeasonAfterRound = null;

    while (isSimulatingAll && currentLeagueData) {
        const nextIndex = currentLeagueData.fixtures.findIndex(f => !f.is_finished);
        if (nextIndex === -1) break;

        const nextRound = currentLeagueData.fixtures[nextIndex].round_number || 1;

        // If stop was requested for a specific round and we reached a fixture in a future round, stop now!
        if (stopSeasonAfterRound !== null && nextRound > stopSeasonAfterRound) {
            break;
        }

        if (currentSelectedRound !== nextRound) {
            currentSelectedRound = nextRound;
        }

        await playSingleLeagueMatch(nextIndex);
        await new Promise(res => setTimeout(res, 80));

        // If stop was requested and no unplayed matches remain in stopSeasonAfterRound, break!
        if (stopSeasonAfterRound !== null) {
            const remainingInRound = currentLeagueData.fixtures.filter(
                f => (f.round_number || 1) === stopSeasonAfterRound && !f.is_finished
            ).length;
            if (remainingInRound === 0) {
                break;
            }
        }
    }

    // Auto-advance to next round if available
    if (currentLeagueData && currentLeagueData.fixtures && currentLeagueData.fixtures.length > 0) {
        const maxRound = Math.max(...currentLeagueData.fixtures.map(f => f.round_number || 1));
        if (currentSelectedRound < maxRound) {
            const nextPending = currentLeagueData.fixtures.find(f => !f.is_finished);
            if (nextPending && nextPending.round_number) {
                currentSelectedRound = nextPending.round_number;
            } else if (currentSelectedRound < maxRound) {
                currentSelectedRound = currentSelectedRound + 1;
            }
            renderLeagueView(currentLeagueData);
        }
    }

    isSimulatingAll = false;
    stopSeasonAfterRound = null;

    if (stopBtn) {
        stopBtn.classList.add('hidden');
        stopBtn.disabled = false;
        stopBtn.innerHTML = '<span class="btn-icon">⏹</span> ZATRZYMAJ PO KOLEJCE';
    }

    if (simAllBtn) {
        simAllBtn.disabled = false;
        simAllBtn.innerHTML = '<span class="btn-icon">⚡</span> SYMULUJ CAŁY SEZON';
    }

    if (simRoundBtn) {
        simRoundBtn.disabled = false;
        simRoundBtn.innerHTML = '<span class="btn-icon">⚡</span> SYMULUJ KOLEJKĘ';
    }
}


/* ==========================================================================
   PLAYER SEASON STATS & MODAL RENDERERS
   ========================================================================== */

let currentModalCategory = 'goals';
let currentModalSearch = '';
let currentLeaguePlayerStats = [];
let modalSortKey = 'goals'; // 'rank', 'name', 'position', 'matches', 'goals', 'assists', 'cards', 'cleansheets', 'passes'
let modalSortDir = 'desc';  // 'desc' | 'asc'

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
        .sort((a, b) => b.goals - a.goals || b.assists - a.assists || a.player_name.localeCompare(b.player_name))
        .slice(0, 5);

    // 2. Top Assists (Asysty)
    const topAssists = [...playerStats]
        .sort((a, b) => b.assists - a.assists || b.goals - a.goals || a.player_name.localeCompare(b.player_name))
        .slice(0, 5);

    // 3. Top Ratings (Średnia ocen - gracze z >5 meczami)
    let ratingPool = playerStats.filter(p => p.matches_played > 5);
    const hasMin5 = ratingPool.length > 0;
    if (!hasMin5) {
        ratingPool = playerStats.filter(p => p.matches_played > 0);
    }
    const topRatings = [...ratingPool]
        .sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0) || (b.motm_awards || 0) - (a.motm_awards || 0) || a.player_name.localeCompare(b.player_name))
        .slice(0, 5);

    // 4. Top MOTM Awards (Zawodnik meczu)
    const topMotm = [...playerStats]
        .filter(p => (p.motm_awards || 0) > 0)
        .sort((a, b) => (b.motm_awards || 0) - (a.motm_awards || 0) || (b.average_rating || 0) - (a.average_rating || 0) || a.player_name.localeCompare(b.player_name))
        .slice(0, 5);

    // 5. Most Cards (Kartki)
    const mostCards = [...playerStats]
        .sort((a, b) => (b.yellow_cards + b.red_cards * 2) - (a.yellow_cards + a.red_cards * 2) || a.player_name.localeCompare(b.player_name))
        .slice(0, 5);

    // 6. Clean Sheets (Czyste Konta)
    const cleanSheets = [...playerStats]
        .filter(p => p.position === 'GOALKEEPER')
        .sort((a, b) => b.clean_sheets - a.clean_sheets || a.player_name.localeCompare(b.player_name))
        .slice(0, 5);

    const ratingCardTitle = hasMin5 ? '⭐ ŚREDNIA OCEN (>5 meczów)' : '⭐ ŚREDNIA OCEN';

    container.innerHTML = `
        ${createCategoryCard('⚽ NAJLEPSI STRZELCY', topScorers, p => `${p.goals} gol(i)`, 'goals')}
        ${createCategoryCard('🅰️ NAJLEPSI ASYSTENCI', topAssists, p => `${p.assists} asyst`, 'assists')}
        ${createCategoryCard(ratingCardTitle, topRatings, p => `⭐ ${(p.average_rating || 0).toFixed(2)}`, 'rating')}
        ${createCategoryCard('👑 ZAWODNIK MECZU', topMotm, p => `${p.motm_awards || 0}x 👑`, 'motm')}
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
                        <span class="stat-player-name">${p.short_name || p.player_name || p.name || p.full_name}</span>
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

function updateModalTabButtons() {
    document.querySelectorAll('.modal-tab-btn').forEach(btn => {
        const cat = btn.getAttribute('data-category');
        btn.classList.toggle('active', cat === currentModalCategory);
    });
}

export async function openPlayerStatsModal(category = 'goals') {
    currentModalCategory = category;
    currentModalSearch = '';

    if (category === 'goals') {
        modalSortKey = 'goals';
        modalSortDir = 'desc';
    } else if (category === 'assists') {
        modalSortKey = 'assists';
        modalSortDir = 'desc';
    } else if (category === 'rating') {
        modalSortKey = 'rating';
        modalSortDir = 'desc';
    } else if (category === 'motm') {
        modalSortKey = 'motm';
        modalSortDir = 'desc';
    } else if (category === 'cards') {
        modalSortKey = 'cards';
        modalSortDir = 'desc';
    } else if (category === 'cleansheets') {
        modalSortKey = 'cleansheets';
        modalSortDir = 'desc';
    } else if (category === 'all') {
        modalSortKey = 'name';
        modalSortDir = 'asc';
    }

    switchLeagueSubTab('stats');

    const searchInput = document.getElementById('modal-player-search');
    if (searchInput) searchInput.value = '';

    updateModalTabButtons();

    if (!currentLeaguePlayerStats || currentLeaguePlayerStats.length === 0) {
        try {
            const resp = await fetch('/league/player-stats');
            if (resp.ok) {
                currentLeaguePlayerStats = await resp.json();
            }
        } catch (e) {
            console.error('Failed to fetch league player stats:', e);
        }
    }

    renderModalTable();

    const fullStatsSection = document.getElementById('league-player-full-stats-section');
    if (fullStatsSection) {
        fullStatsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

export function closePlayerStatsModal() {
    const modal = document.getElementById('player-stats-modal');
    if (modal) modal.classList.add('hidden');
}

export function setModalCategory(category) {
    currentModalCategory = category;
    if (category === 'goals') {
        modalSortKey = 'goals';
        modalSortDir = 'desc';
    } else if (category === 'assists') {
        modalSortKey = 'assists';
        modalSortDir = 'desc';
    } else if (category === 'rating') {
        modalSortKey = 'rating';
        modalSortDir = 'desc';
    } else if (category === 'motm') {
        modalSortKey = 'motm';
        modalSortDir = 'desc';
    } else if (category === 'cards') {
        modalSortKey = 'cards';
        modalSortDir = 'desc';
    } else if (category === 'cleansheets') {
        modalSortKey = 'cleansheets';
        modalSortDir = 'desc';
    } else if (category === 'all') {
        modalSortKey = 'name';
        modalSortDir = 'asc';
    }
    updateModalTabButtons();
    renderModalTable();
}

export function toggleModalSort(sortKey) {
    if (modalSortKey === sortKey) {
        modalSortDir = modalSortDir === 'desc' ? 'asc' : 'desc';
    } else {
        modalSortKey = sortKey;
        modalSortDir = (sortKey === 'name' || sortKey === 'position' || sortKey === 'rank') ? 'asc' : 'desc';
    }

    if (['goals', 'assists', 'rating', 'motm', 'cards', 'cleansheets'].includes(sortKey)) {
        currentModalCategory = sortKey;
    } else {
        currentModalCategory = 'all';
    }
    updateModalTabButtons();
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
        players = players.filter(p => {
            const nameVal = p.short_name || p.player_name || p.name || p.full_name || '';
            return (nameVal && nameVal.toLowerCase().includes(query)) || 
                   (p.position && p.position.toLowerCase().includes(query));
        });
    }

    if (currentModalCategory === 'cleansheets') {
        players = players.filter(p => p.position === 'GOALKEEPER');
    } else if (currentModalCategory === 'rating') {
        if (players.some(p => p.matches_played > 5)) {
            players = players.filter(p => p.matches_played > 5);
        }
    }

    players.sort((a, b) => {
        let cmp = 0;
        const getPName = (x) => x.short_name || x.player_name || x.name || x.full_name || '';
        if (modalSortKey === 'goals') {
            cmp = (b.goals - a.goals) || (b.assists - a.assists) || getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'assists') {
            cmp = (b.assists - a.assists) || (b.goals - a.goals) || getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'rating') {
            cmp = ((b.average_rating || 0) - (a.average_rating || 0)) || ((b.motm_awards || 0) - (a.motm_awards || 0)) || getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'motm') {
            cmp = ((b.motm_awards || 0) - (a.motm_awards || 0)) || ((b.average_rating || 0) - (a.average_rating || 0)) || getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'cards') {
            const pointsA = (a.yellow_cards || 0) + (a.red_cards || 0) * 2;
            const pointsB = (b.yellow_cards || 0) + (b.red_cards || 0) * 2;
            cmp = (pointsB - pointsA) || (b.red_cards - a.red_cards) || getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'cleansheets') {
            cmp = (b.clean_sheets - a.clean_sheets) || (b.matches_played - a.matches_played) || getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'passes') {
            cmp = (b.passes - a.passes) || (b.assists - a.assists) || getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'matches') {
            cmp = (b.matches_played - a.matches_played) || (b.goals - a.goals) || getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'name') {
            cmp = getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'position') {
            cmp = a.position.localeCompare(b.position) || getPName(a).localeCompare(getPName(b));
        } else if (modalSortKey === 'rank') {
            cmp = 0;
        }

        if (['name', 'position', 'rank'].includes(modalSortKey)) {
            return modalSortDir === 'desc' ? -cmp : cmp;
        } else {
            return modalSortDir === 'asc' ? -cmp : cmp;
        }
    });

    const sortHeaders = document.querySelectorAll('#modal-player-stats-thead-row .sortable-header');
    const headerTitles = {
        'rank': '#',
        'name': 'ZAWODNIK',
        'position': 'POZYCJA',
        'matches': 'MECZE',
        'goals': 'BRAMKI',
        'assists': 'ASYSTY',
        'rating': 'ŚR. OCENA',
        'motm': 'MOTM (👑)',
        'cards': 'KARTKI (🟨/🟥)',
        'cleansheets': 'CZYSTE KONTA',
        'passes': 'PODANIA'
    };

    sortHeaders.forEach(th => {
        const key = th.getAttribute('data-sort');
        const isSorted = key === modalSortKey;
        th.classList.toggle('highlight-col', isSorted);
        
        const arrow = isSorted ? (modalSortDir === 'desc' ? ' ▼' : ' ▲') : '';
        const baseTitle = headerTitles[key] || th.textContent.replace(/[▼▲]/g, '').trim();
        th.textContent = baseTitle + arrow;
    });

    if (players.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" class="empty-table-msg">Brak zawodników spełniających kryteria.</td></tr>';
        return;
    }

    tbody.innerHTML = players.map((p, idx) => {
        const rank = idx + 1;
        const rankBadge = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `${rank}`;

        const isRank = modalSortKey === 'rank';
        const isName = modalSortKey === 'name';
        const isPos = modalSortKey === 'position';
        const isMatches = modalSortKey === 'matches';
        const isGoals = modalSortKey === 'goals';
        const isAssists = modalSortKey === 'assists';
        const isRating = modalSortKey === 'rating';
        const isMotm = modalSortKey === 'motm';
        const isCards = modalSortKey === 'cards';
        const isClean = modalSortKey === 'cleansheets';
        const isPasses = modalSortKey === 'passes';

        const avgVal = (p.average_rating || 0).toFixed(2);
        const avgNum = parseFloat(avgVal);
        let ratingBadgeClass = 'medium';
        if (avgNum >= 7.0) ratingBadgeClass = 'high';
        else if (avgNum > 0 && avgNum < 6.0) ratingBadgeClass = 'low';

        return `
            <tr class="table-row">
                <td class="text-center font-bold rank-cell ${isRank ? 'highlight-col' : ''}">${rankBadge}</td>
                <td class="font-semibold ${isName ? 'highlight-col' : ''}">${p.short_name || p.player_name || p.name || p.full_name}</td>
                <td class="text-center text-sub font-semibold ${isPos ? 'highlight-col' : ''}">${getShortPosition(p.position)}</td>
                <td class="text-center ${isMatches ? 'highlight-col font-bold' : ''}">${p.matches_played}</td>
                <td class="text-center ${isGoals ? 'highlight-col font-bold points-cell' : ''}">${p.goals}</td>
                <td class="text-center ${isAssists ? 'highlight-col font-bold points-cell' : 'text-green font-semibold'}">${p.assists}</td>
                <td class="text-center ${isRating ? 'highlight-col font-bold' : ''}"><span class="stat-pill rating ${ratingBadgeClass}" style="display:inline-flex;">⭐ ${avgVal}</span></td>
                <td class="text-center ${isMotm ? 'highlight-col font-bold text-gold' : ''}">${p.motm_awards > 0 ? `${p.motm_awards} 👑` : '-'}</td>
                <td class="text-center ${isCards ? 'highlight-col font-bold' : ''}">${p.yellow_cards} 🟨 / ${p.red_cards} 🟥</td>
                <td class="text-center ${isClean ? 'highlight-col font-bold points-cell' : 'text-gold font-bold'}">${p.clean_sheets}</td>
                <td class="text-center ${isPasses ? 'highlight-col font-bold' : 'text-sub'}">${p.passes}</td>
            </tr>
        `;
    }).join('');
}

export function openMatchDetailsModal(fixture) {
    const modal = document.getElementById('match-details-modal');
    if (!modal) return;

    const homeNameEl = document.getElementById('md-home-name');
    const awayNameEl = document.getElementById('md-away-name');
    const homeBadgeEl = document.getElementById('md-home-badge');
    const awayBadgeEl = document.getElementById('md-away-badge');
    const scoreEl = document.getElementById('md-score');
    const statusEl = document.getElementById('md-status');

    if (homeNameEl) homeNameEl.textContent = fixture.home_team_name;
    if (awayNameEl) awayNameEl.textContent = fixture.away_team_name;
    if (homeBadgeEl) homeBadgeEl.textContent = getTeamInitials(fixture.home_team_name);
    if (awayBadgeEl) awayBadgeEl.textContent = getTeamInitials(fixture.away_team_name);
    if (scoreEl) scoreEl.textContent = `${fixture.home_score} : ${fixture.away_score}`;
    if (statusEl) statusEl.textContent = fixture.is_finished ? 'ZAKOŃCZONY' : 'DO ROZEGRANIA';

    // Render team stats
    const statsGrid = document.getElementById('md-team-stats-grid');
    if (statsGrid) {
        const homeStats = fixture.home_team_stats || {
            possession_percentage: 50, shots_on_target: fixture.home_score, shots_off_target: 2, total_shots: fixture.home_score + 2, fouls: 5, passes: 300, corners: 4, saves: 3
        };
        const awayStats = fixture.away_team_stats || {
            possession_percentage: 50, shots_on_target: fixture.away_score, shots_off_target: 3, total_shots: fixture.away_score + 3, fouls: 6, passes: 290, corners: 3, saves: 2
        };

        const createStatRow = (title, homeVal, awayVal, isPct = false) => {
            let hPct = 50, aPct = 50;
            if (isPct) {
                hPct = homeVal;
                aPct = awayVal;
            } else {
                const sum = (homeVal || 0) + (awayVal || 0);
                if (sum > 0) {
                    hPct = Math.round((homeVal / sum) * 100);
                    aPct = 100 - hPct;
                }
            }
            return `
                <div class="team-stat-row">
                    <div class="stat-team-val home">${isPct ? homeVal + '%' : homeVal}</div>
                    <div class="stat-center">
                        <span class="stat-title">${title}</span>
                        <div class="dual-bar">
                            <div class="dual-bar-fill home" style="width: ${hPct}%;"></div>
                            <div class="dual-bar-fill away" style="width: ${aPct}%;"></div>
                        </div>
                    </div>
                    <div class="stat-team-val away">${isPct ? awayVal + '%' : awayVal}</div>
                </div>
            `;
        };

        statsGrid.innerHTML = `
            ${createStatRow('POSIADANIE PIŁKI', homeStats.possession_percentage ?? 50, awayStats.possession_percentage ?? 50, true)}
            ${createStatRow('STRZAŁY CELNE', homeStats.shots_on_target ?? 0, awayStats.shots_on_target ?? 0)}
            ${createStatRow('STRZAŁY NIECELNE', homeStats.shots_off_target ?? 0, awayStats.shots_off_target ?? 0)}
            ${createStatRow('STRZAŁY OGÓŁEM', homeStats.total_shots ?? 0, awayStats.total_shots ?? 0)}
            ${createStatRow('FAULE', homeStats.fouls ?? 0, awayStats.fouls ?? 0)}
            ${createStatRow('PODANIA', homeStats.passes ?? 0, awayStats.passes ?? 0)}
            ${createStatRow('RZUTY ROŻNE', homeStats.corners ?? 0, awayStats.corners ?? 0)}
            ${createStatRow('INTERWENCJE BRAMKARZY', homeStats.saves ?? 0, awayStats.saves ?? 0)}
            ${createStatRow('ŚREDNIA OCENA DRUŻYNY', Number(homeStats.average_rating ?? 6.0).toFixed(1), Number(awayStats.average_rating ?? 6.0).toFixed(1))}
        `;
    }

    // Render events
    const eventsContainer = document.getElementById('md-events-list');
    if (eventsContainer) {
        eventsContainer.innerHTML = '';
        const events = fixture.events || [];
        if (events.length === 0) {
            eventsContainer.innerHTML = '<div class="empty-events">Brak zarejestrowanych zdarzeń w tym meczu.</div>';
        } else {
            events.forEach(event => {
                const minute = Math.floor((event.second || 0) / 60);
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

    // Render Home & Away players list
    const renderPlayersInContainer = (containerId, players, title) => {
        const c = document.getElementById(containerId);
        if (!c) return;
        c.innerHTML = '';
        if (!players || players.length === 0) {
            c.innerHTML = `<div class="empty-stats">Brak szczegółowych danych zawodników drużyny ${title}</div>`;
            return;
        }

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
        c.appendChild(startersHeader);

        starters.forEach((p, idx) => {
            c.appendChild(createPlayerStatCard(p, idx, false));
        });

        // Bench Header
        if (bench.length > 0) {
            const benchHeader = document.createElement('div');
            benchHeader.className = 'stats-section-header bench';
            benchHeader.innerHTML = `<span>🪑 ŁAWKA REZERWOWYCH</span> <span class="section-count-badge">${bench.length}</span>`;
            c.appendChild(benchHeader);

            bench.forEach((p, idx) => {
                c.appendChild(createPlayerStatCard(p, idx + starters.length, true));
            });
        }
    };

    renderPlayersInContainer('md-home-players-list', fixture.home_players, fixture.home_team_name);
    renderPlayersInContainer('md-away-players-list', fixture.away_players, fixture.away_team_name);

    switchMatchDetailsTab('stats');

    modal.classList.remove('hidden');
}

export function closeMatchDetailsModal() {
    const modal = document.getElementById('match-details-modal');
    if (modal) modal.classList.add('hidden');
}

export function switchMatchDetailsTab(tabName) {
    const panels = {
        'stats': 'md-panel-stats',
        'events': 'md-panel-events',
        'players': 'md-panel-players',
        'away-players': 'md-panel-away-players'
    };
    const buttons = {
        'stats': 'btn-md-tab-stats',
        'events': 'btn-md-tab-events',
        'players': 'btn-md-tab-players',
        'away-players': 'btn-md-tab-away-players'
    };

    Object.keys(panels).forEach(key => {
        const panel = document.getElementById(panels[key]);
        const btn = document.getElementById(buttons[key]);
        if (panel) panel.classList.toggle('hidden', key !== tabName);
        if (btn) btn.classList.toggle('active', key === tabName);
    });
}

window.openPlayerStatsModal = openPlayerStatsModal;
window.openMatchDetailsModal = openMatchDetailsModal;



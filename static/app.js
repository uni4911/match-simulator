import { loadMatchOptions, updateSetupPreviews, startNewMatch } from './js/setup.js';
import { fetchPlayerStats, renderPlayerStats, setActiveStatsTab } from './js/stats.js';
import { updateMatchState, switchView } from './js/match.js';
import { 
    initLeagueView, 
    createNewLeague, 
    showLeagueCreationView, 
    playAllLeagueMatches, 
    playCurrentRoundMatches,
    changeRound,
    selectRound,
    setFixturesFilter,
    selectAllTeams 
} from './js/league.js';

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

    // Navigation tab switches
    const tabSetup = document.getElementById('nav-tab-setup');
    const tabMatch = document.getElementById('nav-tab-match');
    const tabLeague = document.getElementById('nav-tab-league');

    if (tabSetup) {
        tabSetup.addEventListener('click', () => switchView('setup'));
    }
    if (tabMatch) {
        tabMatch.addEventListener('click', () => switchView('match'));
    }
    if (tabLeague) {
        tabLeague.addEventListener('click', () => switchView('league'));
    }

    // League event listeners
    const createLeagueBtn = document.getElementById('create-league-btn');
    if (createLeagueBtn) {
        createLeagueBtn.addEventListener('click', createNewLeague);
    }

    const resetLeagueBtn = document.getElementById('reset-league-btn');
    if (resetLeagueBtn) {
        resetLeagueBtn.addEventListener('click', showLeagueCreationView);
    }

    const simCurrentRoundBtn = document.getElementById('sim-current-round-btn');
    if (simCurrentRoundBtn) {
        simCurrentRoundBtn.addEventListener('click', playCurrentRoundMatches);
    }

    const prevRoundBtn = document.getElementById('prev-round-btn');
    if (prevRoundBtn) {
        prevRoundBtn.addEventListener('click', () => changeRound(-1));
    }

    const nextRoundBtn = document.getElementById('next-round-btn');
    if (nextRoundBtn) {
        nextRoundBtn.addEventListener('click', () => changeRound(1));
    }

    const roundSelectDropdown = document.getElementById('round-select-dropdown');
    if (roundSelectDropdown) {
        roundSelectDropdown.addEventListener('change', (e) => selectRound(e.target.value));
    }

    const simAllBtn = document.getElementById('sim-all-matches-btn');
    if (simAllBtn) {
        simAllBtn.addEventListener('click', playAllLeagueMatches);
    }

    const selectAllBtn = document.getElementById('select-all-teams-btn');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => selectAllTeams(true));
    }

    const deselectAllBtn = document.getElementById('deselect-all-teams-btn');
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', () => selectAllTeams(false));
    }

    // Fixture filter buttons
    const filterAllBtn = document.getElementById('filter-fixtures-all');
    const filterPendingBtn = document.getElementById('filter-fixtures-pending');
    const filterFinishedBtn = document.getElementById('filter-fixtures-finished');

    if (filterAllBtn) filterAllBtn.addEventListener('click', () => setFixturesFilter('all'));
    if (filterPendingBtn) filterPendingBtn.addEventListener('click', () => setFixturesFilter('pending'));
    if (filterFinishedBtn) filterFinishedBtn.addEventListener('click', () => setFixturesFilter('finished'));

    // Stats team tab switches (Gospodarze / Goście)
    const homeTab = document.getElementById('tab-home-stats');
    const awayTab = document.getElementById('tab-away-stats');
    if (homeTab) {
        homeTab.onclick = (e) => {
            e.preventDefault();
            setActiveStatsTab('home');
            renderPlayerStats();
        };
    }
    if (awayTab) {
        awayTab.onclick = (e) => {
            e.preventDefault();
            setActiveStatsTab('away');
            renderPlayerStats();
        };
    }

    // Refresh stats button
    const refreshBtn = document.getElementById('refresh-stats-btn');
    if (refreshBtn) {
        refreshBtn.onclick = (e) => {
            e.preventDefault();
            fetchPlayerStats();
        };
    }

    await updateMatchState('/match/status', 'GET');
    await fetchPlayerStats();
    await initLeagueView();
});
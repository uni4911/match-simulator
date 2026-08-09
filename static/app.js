import { loadMatchOptions, updateSetupPreviews, startNewMatch } from './js/setup.js';
import { fetchPlayerStats, renderPlayerStats, setActiveStatsTab } from './js/stats.js';
import { updateMatchState, switchView } from './js/match.js';
import { 
    initLeagueView, 
    createNewLeague, 
    showLeagueCreationView, 
    playAllLeagueMatches, 
    playCurrentRoundMatches,
    requestStopLeagueSimulation,
    changeRound,
    selectRound,
    setFixturesFilter,
    selectAllTeams,
    switchLeagueSubTab,
    openPlayerStatsModal,
    closePlayerStatsModal,
    setModalCategory,
    toggleModalSort,
    setModalSearch,
    closeMatchDetailsModal,
    switchMatchDetailsTab,
    openMatchByIndex
} from './js/league.js';
import { 
    openPlayerProfile, 
    initPlayerProfileView,
    switchPlayerProfileTab 
} from './js/player-profile.js';

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

    // Setup section toggle in Match view
    const toggleSetupBtn = document.getElementById('toggle-setup-btn');
    const matchSetupBox = document.getElementById('match-setup-box');
    const toggleSetupIcon = document.getElementById('toggle-setup-icon');
    const toggleSetupText = document.getElementById('toggle-setup-text');

    if (toggleSetupBtn && matchSetupBox) {
        toggleSetupBtn.addEventListener('click', () => {
            const isCollapsed = matchSetupBox.classList.toggle('collapsed');
            if (toggleSetupIcon) toggleSetupIcon.textContent = isCollapsed ? '🔽' : '🔼';
            if (toggleSetupText) toggleSetupText.textContent = isCollapsed ? 'Rozwiń konfigurację' : 'Zwiń';
        });
    }

    // Navigation switches (Sidebar & Home Cards)
    const tabHome = document.getElementById('nav-tab-home');
    const tabMatch = document.getElementById('nav-tab-match');
    const tabLeague = document.getElementById('nav-tab-league');
    const sidebarBrandBtn = document.getElementById('sidebar-brand-btn');
    const mobileLogoBtn = document.getElementById('mobile-logo-btn');
    const mobileToggleBtn = document.getElementById('mobile-menu-toggle-btn');
    const appSidebar = document.getElementById('app-sidebar');

    const homeCardMatch = document.getElementById('home-card-match');
    const homeCardLeague = document.getElementById('home-card-league');

    if (tabHome) tabHome.addEventListener('click', () => switchView('home'));
    if (sidebarBrandBtn) sidebarBrandBtn.addEventListener('click', () => switchView('home'));
    if (mobileLogoBtn) mobileLogoBtn.addEventListener('click', () => switchView('home'));

    if (tabMatch) tabMatch.addEventListener('click', () => switchView('match'));
    if (tabLeague) tabLeague.addEventListener('click', () => switchView('league'));

    if (homeCardMatch) {
        homeCardMatch.addEventListener('click', () => switchView('match'));
        homeCardMatch.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); switchView('match'); }
        });
    }
    if (homeCardLeague) {
        homeCardLeague.addEventListener('click', () => switchView('league'));
        homeCardLeague.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); switchView('league'); }
        });
    }

    if (mobileToggleBtn && appSidebar) {
        mobileToggleBtn.addEventListener('click', () => {
            appSidebar.classList.toggle('mobile-open');
        });
    }

    // League sub-tab switches (Tabela i Terminarz vs Statystyki Zawodników)
    const leagueSubTabTable = document.getElementById('league-subtab-table');
    const leagueSubTabStats = document.getElementById('league-subtab-stats');
    const leagueSubTabPlayer = document.getElementById('league-subtab-player');

    if (leagueSubTabTable) {
        leagueSubTabTable.addEventListener('click', () => switchLeagueSubTab('table'));
    }
    if (leagueSubTabStats) {
        leagueSubTabStats.addEventListener('click', () => switchLeagueSubTab('stats'));
    }
    if (leagueSubTabPlayer) {
        leagueSubTabPlayer.addEventListener('click', () => switchLeagueSubTab('player'));
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

    const stopSimAllBtn = document.getElementById('stop-sim-all-btn');
    if (stopSimAllBtn) {
        stopSimAllBtn.addEventListener('click', requestStopLeagueSimulation);
    }

    const selectAllBtn = document.getElementById('select-all-teams-btn');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => selectAllTeams(true));
    }

    const deselectAllBtn = document.getElementById('deselect-all-teams-btn');
    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', () => selectAllTeams(false));
    }


    const filterAllBtn = document.getElementById('filter-fixtures-all');
    const filterPendingBtn = document.getElementById('filter-fixtures-pending');
    const filterFinishedBtn = document.getElementById('filter-fixtures-finished');

    if (filterAllBtn) filterAllBtn.addEventListener('click', () => setFixturesFilter('all'));
    if (filterPendingBtn) filterPendingBtn.addEventListener('click', () => setFixturesFilter('pending'));
    if (filterFinishedBtn) filterFinishedBtn.addEventListener('click', () => setFixturesFilter('finished'));

    
    const showAllStatsBtn = document.getElementById('show-all-player-stats-btn');
    if (showAllStatsBtn) {
        showAllStatsBtn.addEventListener('click', () => openPlayerStatsModal('goals'));
    }

    const closeModalBtn = document.getElementById('close-player-stats-modal-btn');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closePlayerStatsModal);
    }

    const playerStatsModal = document.getElementById('player-stats-modal');
    if (playerStatsModal) {
        playerStatsModal.addEventListener('click', (e) => {
            if (e.target === playerStatsModal) closePlayerStatsModal();
        });
    }

    const modalCategoryTabs = document.getElementById('modal-category-tabs');
    if (modalCategoryTabs) {
        modalCategoryTabs.addEventListener('click', (e) => {
            const btn = e.target.closest('.modal-tab-btn');
            if (btn) {
                const cat = btn.getAttribute('data-category');
                if (cat) setModalCategory(cat);
            }
        });
    }

    const searchInput = document.getElementById('modal-player-search');
    if (searchInput) {
        let searchTimeout = null;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                setModalSearch(e.target.value.trim());
            }, 200);
        });
    }

    const closeMdModalBtn = document.getElementById('close-match-details-modal-btn');
    if (closeMdModalBtn) {
        closeMdModalBtn.addEventListener('click', closeMatchDetailsModal);
    }

    const matchDetailsModal = document.getElementById('match-details-modal');
    if (matchDetailsModal) {
        matchDetailsModal.addEventListener('click', (e) => {
            if (e.target === matchDetailsModal) closeMatchDetailsModal();
        });
    }

    const btnMdStats = document.getElementById('btn-md-tab-stats');
    const btnMdEvents = document.getElementById('btn-md-tab-events');
    const btnMdPlayers = document.getElementById('btn-md-tab-players');
    const btnMdAwayPlayers = document.getElementById('btn-md-tab-away-players');

    if (btnMdStats) btnMdStats.addEventListener('click', () => switchMatchDetailsTab('stats'));
    if (btnMdEvents) btnMdEvents.addEventListener('click', () => switchMatchDetailsTab('events'));
    if (btnMdPlayers) btnMdPlayers.addEventListener('click', () => switchMatchDetailsTab('players'));
    if (btnMdAwayPlayers) btnMdAwayPlayers.addEventListener('click', () => switchMatchDetailsTab('away-players'));

    // Initialize Player Profile dedicated view
    initPlayerProfileView();


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
import { loadMatchOptions, updateSetupPreviews, startNewMatch } from './js/setup.js';
import { fetchPlayerStats, renderPlayerStats, setActiveStatsTab } from './js/stats.js';
import { updateMatchState, switchView } from './js/match.js';

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
    if (tabSetup) {
        tabSetup.addEventListener('click', () => switchView('setup'));
    }
    if (tabMatch) {
        tabMatch.addEventListener('click', () => switchView('match'));
    }

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
});
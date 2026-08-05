import { getTeamInitials } from './helpers.js';
import { getCurrentStatsData, fetchPlayerStats } from './stats.js';
import { renderMatchData, switchView, startLiveStream } from './match.js';

export function updateSetupPreviews() {
    const homeSelect = document.getElementById('home-team-select');
    const awaySelect = document.getElementById('away-team-select');
    const setupHomeName = document.getElementById('setup-home-name');
    const setupAwayName = document.getElementById('setup-away-name');
    const setupHomeBadge = document.getElementById('setup-home-badge');
    const setupAwayBadge = document.getElementById('setup-away-badge');

    const statsHomeName = document.getElementById('stats-home-name');
    const statsAwayName = document.getElementById('stats-away-name');
    const statsHomeBadge = document.getElementById('stats-home-badge');
    const statsAwayBadge = document.getElementById('stats-away-badge');

    const currentStatsData = getCurrentStatsData();

    if (homeSelect) {
        const name = homeSelect.value || 'Gospodarze';
        if (setupHomeName) setupHomeName.textContent = name;
        if (setupHomeBadge) setupHomeBadge.textContent = getTeamInitials(name);
        if (!currentStatsData && statsHomeName) statsHomeName.textContent = name;
        if (!currentStatsData && statsHomeBadge) statsHomeBadge.textContent = getTeamInitials(name);
    }
    if (awaySelect) {
        const name = awaySelect.value || 'Goście';
        if (setupAwayName) setupAwayName.textContent = name;
        if (setupAwayBadge) setupAwayBadge.textContent = getTeamInitials(name);
        if (!currentStatsData && statsAwayName) statsAwayName.textContent = name;
        if (!currentStatsData && statsAwayBadge) statsAwayBadge.textContent = getTeamInitials(name);
    }
}

export async function loadMatchOptions() {
    try {
        const response = await fetch('/match/options');
        const data = await response.json();

        const homeSelect = document.getElementById('home-team-select');
        const awaySelect = document.getElementById('away-team-select');
        const homeFormSelect = document.getElementById('home-formation-select');
        const awayFormSelect = document.getElementById('away-formation-select');

        if (homeSelect && awaySelect && (data.teams_detailed || data.teams)) {
            homeSelect.innerHTML = '';
            awaySelect.innerHTML = '';

            if (data.teams_detailed && data.teams_detailed.length > 0) {
                const grouped = {};
                data.teams_detailed.forEach(t => {
                    const lg = t.league || 'Inne';
                    if (!grouped[lg]) grouped[lg] = [];
                    grouped[lg].push(t.name);
                });

                Object.keys(grouped).sort().forEach(leagueName => {
                    const groupHome = document.createElement('optgroup');
                    groupHome.label = leagueName;
                    const groupAway = document.createElement('optgroup');
                    groupAway.label = leagueName;

                    grouped[leagueName].sort((a, b) => a.localeCompare(b)).forEach(teamName => {
                        const optHome = document.createElement('option');
                        optHome.value = teamName;
                        optHome.textContent = teamName;
                        groupHome.appendChild(optHome);

                        const optAway = document.createElement('option');
                        optAway.value = teamName;
                        optAway.textContent = teamName;
                        groupAway.appendChild(optAway);
                    });

                    homeSelect.appendChild(groupHome);
                    awaySelect.appendChild(groupAway);
                });
            } else {
                data.teams.forEach((team) => {
                    const optHome = document.createElement('option');
                    optHome.value = team;
                    optHome.textContent = team;
                    homeSelect.appendChild(optHome);

                    const optAway = document.createElement('option');
                    optAway.value = team;
                    optAway.textContent = team;
                    awaySelect.appendChild(optAway);
                });
            }

            if (data.teams && data.teams.length >= 2) {
                homeSelect.selectedIndex = 0;
                awaySelect.selectedIndex = 1;
            }
        }

        if (homeFormSelect && awayFormSelect && data.formations) {
            homeFormSelect.innerHTML = '';
            awayFormSelect.innerHTML = '';

            data.formations.forEach(form => {
                const optHome = document.createElement('option');
                optHome.value = form;
                optHome.textContent = form;
                homeFormSelect.appendChild(optHome);

                const optAway = document.createElement('option');
                optAway.value = form;
                optAway.textContent = form;
                awayFormSelect.appendChild(optAway);
            });
        }

        updateSetupPreviews();
    } catch (err) {
        console.error('Failed to load match options:', err);
    }
}

export async function startNewMatch() {
    const homeTeam = document.getElementById('home-team-select').value;
    const awayTeam = document.getElementById('away-team-select').value;
    const homeFormation = document.getElementById('home-formation-select').value;
    const awayFormation = document.getElementById('away-formation-select').value;

    if (homeTeam === awayTeam) {
        alert('Gospodarze i Goście muszą być różnymi drużynami!');
        return;
    }

    try {
        const response = await fetch('/match/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                home_team_name: homeTeam,
                away_team_name: awayTeam,
                home_formation: homeFormation,
                away_formation: awayFormation
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            alert(`Błąd: ${errData.detail || 'Nie udało się rozpocząć meczu'}`);
            return;
        }

        const data = await response.json();
        renderMatchData(data);
        await fetchPlayerStats();
        switchView('match');
    } catch (err) {
        console.error('Failed to start new match:', err);
    }
    startLiveStream();
}

import { getTeamInitials, getShortPosition, getPositionClass, getCountryFlag } from './helpers.js';
import { openPlayerProfile } from './player-profile.js';

let currentTotwRound = 1;
let currentTotwFormation = '4-3-3';
let currentTotsFormation = '4-3-3';
let cachedTotwData = null;
let cachedTotsData = null;

// Formation coordinates mapping (% top, % left)
const FORMATION_COORDINATES = {
    '4-3-3': {
        'GK': { top: 88, left: 50 },
        'LB': { top: 72, left: 14 },
        'LCB': { top: 74, left: 38 },
        'RCB': { top: 74, left: 62 },
        'RB': { top: 72, left: 86 },
        'LCM': { top: 46, left: 24 },
        'CDM': { top: 55, left: 50 },
        'CCM': { top: 55, left: 50 },
        'RCM': { top: 46, left: 76 },
        'LW': { top: 20, left: 16 },
        'ST': { top: 15, left: 50 },
        'RW': { top: 20, left: 84 }
    },
    '4-4-2': {
        'GK': { top: 88, left: 50 },
        'LB': { top: 72, left: 14 },
        'LCB': { top: 74, left: 38 },
        'RCB': { top: 74, left: 62 },
        'RB': { top: 72, left: 86 },
        'LM': { top: 46, left: 14 },
        'LCM': { top: 48, left: 38 },
        'RCM': { top: 48, left: 62 },
        'RM': { top: 46, left: 86 },
        'LST': { top: 18, left: 36 },
        'RST': { top: 18, left: 64 }
    },
    '4-2-3-1': {
        'GK': { top: 88, left: 50 },
        'LB': { top: 74, left: 14 },
        'LCB': { top: 76, left: 38 },
        'RCB': { top: 76, left: 62 },
        'RB': { top: 74, left: 86 },
        'LDM': { top: 58, left: 36 },
        'RDM': { top: 58, left: 64 },
        'LAM': { top: 36, left: 18 },
        'CAM': { top: 34, left: 50 },
        'RAM': { top: 36, left: 82 },
        'ST': { top: 15, left: 50 }
    },
    '3-5-2': {
        'GK': { top: 88, left: 50 },
        'LCB': { top: 74, left: 24 },
        'CCB': { top: 76, left: 50 },
        'RCB': { top: 74, left: 76 },
        'LWB': { top: 50, left: 12 },
        'LDM': { top: 56, left: 34 },
        'CDM': { top: 56, left: 34 },
        'LCM': { top: 56, left: 34 },
        'CAM': { top: 38, left: 50 },
        'RCM': { top: 54, left: 66 },
        'RWB': { top: 50, left: 88 },
        'LST': { top: 18, left: 36 },
        'RST': { top: 18, left: 64 }
    },
    '3-4-3': {
        'GK': { top: 88, left: 50 },
        'LCB': { top: 74, left: 24 },
        'CCB': { top: 76, left: 50 },
        'RCB': { top: 74, left: 76 },
        'LM': { top: 48, left: 14 },
        'LDM': { top: 52, left: 38 },
        'CDM': { top: 52, left: 38 },
        'LCM': { top: 52, left: 38 },
        'RCM': { top: 50, left: 62 },
        'RM': { top: 48, left: 86 },
        'LW': { top: 20, left: 18 },
        'ST': { top: 15, left: 50 },
        'RW': { top: 20, left: 82 }
    }
};

export function getTotwRound() {
    return currentTotwRound;
}

export function setTotwRound(roundNum) {
    currentTotwRound = parseInt(roundNum, 10);
}

// Fetch and render Team of the Week
export async function loadTeamOfTheWeek(roundNumber = null, formation = null) {
    if (roundNumber !== null) currentTotwRound = roundNumber;
    if (formation !== null) currentTotwFormation = formation;

    const roundParam = currentTotwRound ? `&round_number=${currentTotwRound}` : '';
    const formParam = currentTotwFormation ? `&formation=${encodeURIComponent(currentTotwFormation)}` : '';

    try {
        const response = await fetch(`/league/team-of-the-week?${roundParam}${formParam}`);
        if (!response.ok) {
            console.error('Błąd podczas pobierania Jedenastki Kolejki');
            return;
        }
        const data = await response.json();
        cachedTotwData = data;
        currentTotwRound = data.round_number || currentTotwRound;
        renderTeamOfTheWeekUI(data);
    } catch (err) {
        console.error('Błąd sieci podczas pobierania TOTW:', err);
    }
}

// Fetch and render Team of the Season
export async function loadTeamOfTheSeason(formation = null) {
    if (formation !== null) currentTotsFormation = formation;
    const formParam = currentTotsFormation ? `?formation=${encodeURIComponent(currentTotsFormation)}` : '';

    try {
        const response = await fetch(`/league/team-of-the-season${formParam}`);
        if (!response.ok) {
            console.error('Błąd podczas pobierania Jedenastki Sezonu');
            return;
        }
        const data = await response.json();
        cachedTotsData = data;
        renderTeamOfTheSeasonUI(data);
    } catch (err) {
        console.error('Błąd sieci podczas pobierania TOTS:', err);
    }
}

// Render Team of the Week UI
export function renderTeamOfTheWeekUI(data) {
    if (!data) return;

    // Header updates
    const roundBadge = document.getElementById('totw-round-badge');
    const statusBadge = document.getElementById('totw-status-badge');
    const prevBtn = document.getElementById('totw-prev-round-btn');
    const nextBtn = document.getElementById('totw-next-round-btn');
    const roundSelect = document.getElementById('totw-round-select');
    const formationSelect = document.getElementById('totw-formation-select');

    if (roundBadge) {
        roundBadge.textContent = `KOLEJKA ${data.round_number} Z ${data.total_rounds}`;
    }

    if (statusBadge) {
        if (data.is_round_finished) {
            statusBadge.className = 'totw-status-pill finished';
            statusBadge.textContent = `ROZEGRANA (${data.matches_played_in_round}/${data.total_matches_in_round})`;
        } else if (data.matches_played_in_round > 0) {
            statusBadge.className = 'totw-status-pill in-progress';
            statusBadge.textContent = `W TRAKCIE (${data.matches_played_in_round}/${data.total_matches_in_round})`;
        } else {
            statusBadge.className = 'totw-status-pill pending';
            statusBadge.textContent = `NIEROZEGRANA (0/${data.total_matches_in_round})`;
        }
    }

    if (prevBtn) prevBtn.disabled = data.round_number <= 1;
    if (nextBtn) nextBtn.disabled = data.round_number >= data.total_rounds;

    // Round select dropdown
    if (roundSelect && data.total_rounds > 0) {
        roundSelect.innerHTML = '';
        for (let r = 1; r <= data.total_rounds; r++) {
            const opt = document.createElement('option');
            opt.value = r;
            opt.textContent = `KOLEJKA ${r}`;
            if (r === data.round_number) opt.selected = true;
            roundSelect.appendChild(opt);
        }
    }

    if (formationSelect && data.formation) {
        formationSelect.value = data.formation;
    }

    // Sync formation pills active state
    const totwPills = document.querySelectorAll('#totw-formation-pills .formation-pill-btn');
    totwPills.forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-formation') === data.formation);
    });

    // Top summary stats
    const avgRatingEl = document.getElementById('totw-avg-rating');
    const totalGoalsEl = document.getElementById('totw-total-goals');
    const totalAssistsEl = document.getElementById('totw-total-assists');

    const startingXI = data.starting_xi || [];
    const totalGoals = startingXI.reduce((sum, p) => sum + (p.goals || 0), 0);
    const totalAssists = startingXI.reduce((sum, p) => sum + (p.assists || 0), 0);

    if (avgRatingEl) avgRatingEl.textContent = (data.average_rating || 0).toFixed(2);
    if (totalGoalsEl) totalGoalsEl.textContent = totalGoals;
    if (totalAssistsEl) totalAssistsEl.textContent = totalAssists;

    // Pitch starting XI
    renderPitchPlayers('totw-pitch-players-layer', startingXI, data.formation, false);

    // MVP Card
    renderMvpCard('totw-mvp-card-container', data.mvp, false);

    // Honors
    renderHonorsList('totw-honors-list', data, false);

    // Bench
    renderBenchList('totw-bench-list', data.bench || [], false);
}

// Render Team of the Season UI
export function renderTeamOfTheSeasonUI(data) {
    if (!data) return;

    // Header updates
    const leagueBadge = document.getElementById('tots-league-badge');
    const statusBadge = document.getElementById('tots-status-badge');
    const formationSelect = document.getElementById('tots-formation-select');

    if (leagueBadge) {
        leagueBadge.textContent = `${data.league_name || 'LIGA'} • ${data.rounds_played}/${data.total_rounds} KOLEJEK`;
    }

    if (statusBadge) {
        if (data.is_season_finished) {
            statusBadge.className = 'tots-status-pill finished';
            statusBadge.textContent = '🏆 SEZON ZAKOŃCZONY';
        } else {
            statusBadge.className = 'tots-status-pill in-progress';
            statusBadge.textContent = `W TRAKCIE (${data.rounds_played}/${data.total_rounds} KOLEJEK)`;
        }
    }

    if (formationSelect && data.formation) {
        formationSelect.value = data.formation;
    }

    // Sync formation pills active state
    const totsPills = document.querySelectorAll('#tots-formation-pills .formation-pill-btn');
    totsPills.forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-formation') === data.formation);
    });

    if (formationSelect && data.formation) {
        formationSelect.value = data.formation;
    }

    // Top summary stats
    const avgRatingEl = document.getElementById('tots-avg-rating');
    const totalGoalsEl = document.getElementById('tots-total-goals');
    const totalAssistsEl = document.getElementById('tots-total-assists');

    const startingXI = data.starting_xi || [];
    const totalGoals = startingXI.reduce((sum, p) => sum + (p.goals || 0), 0);
    const totalAssists = startingXI.reduce((sum, p) => sum + (p.assists || 0), 0);

    if (avgRatingEl) avgRatingEl.textContent = (data.average_rating || 0).toFixed(2);
    if (totalGoalsEl) totalGoalsEl.textContent = totalGoals;
    if (totalAssistsEl) totalAssistsEl.textContent = totalAssists;

    // Pitch starting XI
    renderPitchPlayers('tots-pitch-players-layer', startingXI, data.formation, true);

    // MVP Card
    renderMvpCard('tots-mvp-card-container', data.mvp, true);

    // Awards / Honors
    renderHonorsList('tots-awards-list', data, true);

    // Bench
    renderBenchList('tots-bench-list', data.bench || [], true);
}

// Render tactical pitch player cards
function renderPitchPlayers(containerId, players, formation = '4-3-3', isTots = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    if (!players || players.length === 0) {
        container.innerHTML = `
            <div class="pitch-empty-state ${isTots ? 'tots-empty-state' : ''}">
                <span class="pitch-empty-icon">${isTots ? '🏆' : '⚽'}</span>
                <p class="pitch-empty-text">${isTots ? 'Brak rozegranych meczów w sezonie.' : 'Brak rozegranych meczów w tej kolejce.'}</p>
                <span class="pitch-empty-sub">Rozegraj mecze ligowe, aby wyłonić najlepszą jedenastkę.</span>
            </div>
        `;
        return;
    }

    const formCoords = FORMATION_COORDINATES[formation] || FORMATION_COORDINATES['4-3-3'];

    players.forEach((player) => {
        const slotId = player.slot_id || 'SLOT';
        const coords = formCoords[slotId] || { top: 50, left: 50 };

        const node = document.createElement('div');
        node.className = `pitch-player-node ${isTots ? 'tots-card' : ''} ${player.is_mvp ? 'is-mvp' : ''}`;
        node.style.top = `${coords.top}%`;
        node.style.left = `${coords.left}%`;
        node.setAttribute('data-slot', slotId);

        // Click handler to open player profile
        node.addEventListener('click', () => {
            const pName = player.short_name || player.player_name || player.full_name;
            const tName = player.team_name || '';
            if (window.openPlayerProfile) {
                window.openPlayerProfile(pName, tName);
            }
        });

        const shortPos = player.slot_position || getShortPosition(player.position);
        const posClass = getPositionClass(player.position);
        const teamInitials = getTeamInitials(player.team_name);
        const ratingVal = (player.rating || 6.0).toFixed(1);

        let ratingColorClass = 'rating-good';
        if (player.rating >= 8.5) ratingColorClass = 'rating-elite';
        else if (player.rating >= 7.5) ratingColorClass = 'rating-great';
        else if (player.rating < 6.0) ratingColorClass = 'rating-low';

        // Secondary stats tag
        let statSnippet = '';
        if (player.goals > 0 && player.assists > 0) {
            statSnippet = `⚽${player.goals} 🅰️${player.assists}`;
        } else if (player.goals > 0) {
            statSnippet = `⚽ ${player.goals}`;
        } else if (player.assists > 0) {
            statSnippet = `🅰️ ${player.assists}`;
        } else if (player.clean_sheet && (shortPos === 'GK' || ['LB', 'CB', 'RB', 'LWB', 'RWB'].includes(shortPos))) {
            statSnippet = `🧤 Czyste K.`;
        } else if (isTots && player.matches_played > 1) {
            statSnippet = `M: ${player.matches_played}`;
        }

        node.innerHTML = `
            ${player.is_mvp ? '<div class="pitch-mvp-crown" title="Najlepszy zawodnik">👑 MVP</div>' : ''}
            <div class="pitch-card-inner">
                <div class="pitch-card-top-row">
                    <span class="pitch-pos-badge ${posClass}">${shortPos}</span>
                    <span class="pitch-rating-badge ${ratingColorClass}">⭐ ${ratingVal}</span>
                </div>
                <div class="pitch-avatar-circle">
                    <span class="pitch-team-badge" title="${player.team_name}">${teamInitials}</span>
                </div>
                <div class="pitch-player-name" title="${player.full_name || player.player_name}">${player.short_name || player.player_name}</div>
                <div class="pitch-team-name">${player.team_name}</div>
                ${statSnippet ? `<div class="pitch-stat-snippet">${statSnippet}</div>` : ''}
            </div>
        `;

        container.appendChild(node);
    });
}

// Render MVP Card
function renderMvpCard(containerId, mvp, isTots = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!mvp) {
        container.innerHTML = `
            <div class="tile-header">
                <div class="tile-header-title">
                    <span class="header-icon">${isTots ? '👑' : '⭐'}</span> ${isTots ? 'ZAWODNIK SEZONU (MVP)' : 'ZAWODNIK KOLEJKI (MVP)'}
                </div>
            </div>
            <div class="mvp-placeholder ${isTots ? 'tots-empty-text' : ''}">
                <span>Brak danych MVP</span>
            </div>
        `;
        return;
    }

    const flag = getCountryFlag(mvp.nationality);
    const shortPos = getShortPosition(mvp.position);
    const posClass = getPositionClass(mvp.position);
    const teamInitials = getTeamInitials(mvp.team_name);
    const ratingVal = (mvp.rating || 6.0).toFixed(2);

    container.innerHTML = `
        <div class="tile-header">
            <div class="tile-header-title">
                <span class="header-icon">${isTots ? '🏆' : '⭐'}</span> ${isTots ? 'ZAWODNIK SEZONU (MVP)' : 'ZAWODNIK KOLEJKI (MVP)'}
            </div>
            <span class="${isTots ? 'tile-badge-tots' : 'tile-badge-info'}">⭐ NAJLEPSZY</span>
        </div>

        <div class="mvp-card-body ${isTots ? 'tots-theme-card' : ''}">
            <div class="mvp-card-header">
                <div class="mvp-avatar-large">
                    <span class="mvp-avatar-team">${teamInitials}</span>
                    <span class="mvp-avatar-pos ${posClass}">${shortPos}</span>
                </div>
                <div class="mvp-player-meta">
                    <div class="mvp-title-row">
                        <span class="mvp-flag">${flag}</span>
                        <h3 class="mvp-name">${mvp.full_name || mvp.player_name}</h3>
                    </div>
                    <div class="mvp-team-text">🏟️ ${mvp.team_name}</div>
                    <div class="mvp-sub-meta">Wiek: ${mvp.age} • OVR: ${mvp.overall}</div>
                </div>
                <div class="mvp-score-box">
                    <span class="mvp-score-label">ŚR. OCENA</span>
                    <span class="mvp-score-val">⭐ ${ratingVal}</span>
                </div>
            </div>

            <div class="mvp-stats-grid">
                <div class="mvp-stat-item">
                    <span class="mvp-stat-icon">⚽</span>
                    <span class="mvp-stat-val">${mvp.goals}</span>
                    <span class="mvp-stat-lbl">Gole</span>
                </div>
                <div class="mvp-stat-item">
                    <span class="mvp-stat-icon">🅰️</span>
                    <span class="mvp-stat-val">${mvp.assists}</span>
                    <span class="mvp-stat-lbl">Asysty</span>
                </div>
                <div class="mvp-stat-item">
                    <span class="mvp-stat-icon">🦶</span>
                    <span class="mvp-stat-val">${mvp.passes}</span>
                    <span class="mvp-stat-lbl">Podania</span>
                </div>
                <div class="mvp-stat-item">
                    <span class="mvp-stat-icon">${isTots ? '📅' : '⏱️'}</span>
                    <span class="mvp-stat-val">${isTots ? mvp.matches_played : (mvp.minutes_played + "'")}</span>
                    <span class="mvp-stat-lbl">${isTots ? 'Mecze' : 'Minuty'}</span>
                </div>
            </div>

            <button type="button" class="metro-btn primary mvp-profile-btn" id="${containerId}-profile-btn">
                <span>👤 ZOBACZ PROFIL ZAWODNIKA</span>
            </button>
        </div>
    `;

    const btn = document.getElementById(`${containerId}-profile-btn`);
    if (btn) {
        btn.addEventListener('click', () => {
            const pName = mvp.short_name || mvp.player_name || mvp.full_name;
            const tName = mvp.team_name || '';
            if (window.openPlayerProfile) {
                window.openPlayerProfile(pName, tName);
            }
        });
    }
}

// Render Honors / Awards List
function renderHonorsList(containerId, data, isTots = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    const items = [];

    if (isTots) {
        // Season Awards
        if (data.best_team_name) {
            items.push({
                icon: '🏆',
                title: 'Mistrz / Lider Ligi',
                name: data.best_team_name,
                meta: '1. miejsce w tabeli',
                type: 'team'
            });
        }
        if (data.top_scorer) {
            items.push({
                icon: '⚽',
                title: 'Król Strzelców',
                name: data.top_scorer.short_name || data.top_scorer.player_name,
                team: data.top_scorer.team_name,
                meta: `${data.top_scorer.goals} goli w sezonie`,
                player: data.top_scorer
            });
        }
        if (data.top_assister) {
            items.push({
                icon: '🅰️',
                title: 'Król Asyst',
                name: data.top_assister.short_name || data.top_assister.player_name,
                team: data.top_assister.team_name,
                meta: `${data.top_assister.assists} asyst w sezonie`,
                player: data.top_assister
            });
        }
        if (data.top_goalkeeper) {
            items.push({
                icon: '🧤',
                title: 'Złota Rękawica',
                name: data.top_goalkeeper.short_name || data.top_goalkeeper.player_name,
                team: data.top_goalkeeper.team_name,
                meta: `${data.top_goalkeeper.clean_sheets} czystych kont (śr. ${data.top_goalkeeper.rating.toFixed(2)})`,
                player: data.top_goalkeeper
            });
        }
    } else {
        // Round Honors
        if (data.best_team_name) {
            items.push({
                icon: '🛡️',
                title: 'Drużyna Kolejki',
                name: data.best_team_name,
                meta: 'Najwyższa śr. ocen w kolejce',
                type: 'team'
            });
        }
        if (data.top_scorer) {
            items.push({
                icon: '⚽',
                title: 'Strzelec Kolejki',
                name: data.top_scorer.short_name || data.top_scorer.player_name,
                team: data.top_scorer.team_name,
                meta: `${data.top_scorer.goals} ${data.top_scorer.goals === 1 ? 'gol' : 'gole'} w meczu`,
                player: data.top_scorer
            });
        }
        if (data.top_assister) {
            items.push({
                icon: '🅰️',
                title: 'Asystent Kolejki',
                name: data.top_assister.short_name || data.top_assister.player_name,
                team: data.top_assister.team_name,
                meta: `${data.top_assister.assists} ${data.top_assister.assists === 1 ? 'asysta' : 'asysty'} w meczu`,
                player: data.top_assister
            });
        }
        if (data.top_goalkeeper) {
            items.push({
                icon: '🧤',
                title: 'Bramkarz Kolejki',
                name: data.top_goalkeeper.short_name || data.top_goalkeeper.player_name,
                team: data.top_goalkeeper.team_name,
                meta: `Ocena ⭐ ${data.top_goalkeeper.rating.toFixed(2)}`,
                player: data.top_goalkeeper
            });
        }
    }

    if (items.length === 0) {
        container.innerHTML = `<div class="honors-empty ${isTots ? 'tots-empty-text' : ''}">Brak rozegranych meczów do przyznania wyróżnień.</div>`;
        return;
    }

    items.forEach((item) => {
        const card = document.createElement('div');
        card.className = `honor-item-card ${isTots ? 'tots-honor-card' : ''} ${item.player ? 'clickable-player-card' : ''}`;

        if (item.player) {
            card.addEventListener('click', () => {
                const pName = item.player.short_name || item.player.player_name || item.player.full_name;
                const tName = item.player.team_name || '';
                if (window.openPlayerProfile) {
                    window.openPlayerProfile(pName, tName);
                }
            });
        }

        card.innerHTML = `
            <div class="honor-icon">${item.icon}</div>
            <div class="honor-details">
                <span class="honor-label">${item.title}</span>
                <span class="honor-name">${item.name}</span>
                ${item.team ? `<span class="honor-team">${item.team}</span>` : ''}
                <span class="honor-meta">${item.meta}</span>
            </div>
        `;
        container.appendChild(card);
    });
}

// Render Bench / Substitutes
function renderBenchList(containerId, benchPlayers, isTots = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = '';

    if (!benchPlayers || benchPlayers.length === 0) {
        container.innerHTML = `<div class="bench-empty ${isTots ? 'tots-empty-text' : ''}">Brak zawodników na ławce rezerwowych.</div>`;
        return;
    }

    benchPlayers.forEach((player, idx) => {
        const item = document.createElement('div');
        item.className = `bench-player-row clickable-player-card ${isTots ? 'tots-bench-row' : ''}`;

        item.addEventListener('click', () => {
            const pName = player.short_name || player.player_name || player.full_name;
            const tName = player.team_name || '';
            if (window.openPlayerProfile) {
                window.openPlayerProfile(pName, tName);
            }
        });

        const shortPos = player.slot_position || getShortPosition(player.position);
        const posClass = getPositionClass(player.position);
        const teamInitials = getTeamInitials(player.team_name);
        const ratingVal = (player.rating || 6.0).toFixed(1);

        item.innerHTML = `
            <span class="bench-index">${idx + 1}</span>
            <span class="pos-badge ${posClass}">${shortPos}</span>
            <span class="bench-team-tag">${teamInitials}</span>
            <div class="bench-player-info">
                <span class="bench-player-name">${player.short_name || player.player_name}</span>
                <span class="bench-club-name">${player.team_name}</span>
            </div>
            <div class="bench-stat-pills">
                ${player.goals > 0 ? `<span class="mini-pill goals">⚽ ${player.goals}</span>` : ''}
                ${player.assists > 0 ? `<span class="mini-pill assists">🅰️ ${player.assists}</span>` : ''}
                <span class="bench-rating-badge">⭐ ${ratingVal}</span>
            </div>
        `;

        container.appendChild(item);
    });
}

// Initialize event listeners for TOTW & TOTS
export function initTotwEventListeners() {
    // TOTW Round navigation
    const prevBtn = document.getElementById('totw-prev-round-btn');
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentTotwRound > 1) {
                currentTotwRound--;
                loadTeamOfTheWeek(currentTotwRound, currentTotwFormation);
            }
        });
    }

    const nextBtn = document.getElementById('totw-next-round-btn');
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            const maxR = cachedTotwData ? cachedTotwData.total_rounds : 999;
            if (currentTotwRound < maxR) {
                currentTotwRound++;
                loadTeamOfTheWeek(currentTotwRound, currentTotwFormation);
            }
        });
    }

    const roundSelect = document.getElementById('totw-round-select');
    if (roundSelect) {
        roundSelect.addEventListener('change', (e) => {
            currentTotwRound = parseInt(e.target.value, 10);
            loadTeamOfTheWeek(currentTotwRound, currentTotwFormation);
        });
    }

    // TOTW Formation select
    const totwFormSelect = document.getElementById('totw-formation-select');
    if (totwFormSelect) {
        totwFormSelect.addEventListener('change', (e) => {
            currentTotwFormation = e.target.value;
            loadTeamOfTheWeek(currentTotwRound, currentTotwFormation);
        });
    }

    // TOTW Formation pill buttons
    const totwPills = document.querySelectorAll('#totw-formation-pills .formation-pill-btn');
    totwPills.forEach(btn => {
        btn.addEventListener('click', () => {
            const form = btn.getAttribute('data-formation');
            if (form) {
                currentTotwFormation = form;
                loadTeamOfTheWeek(currentTotwRound, currentTotwFormation);
            }
        });
    });

    // TOTS Formation select
    const totsFormSelect = document.getElementById('tots-formation-select');
    if (totsFormSelect) {
        totsFormSelect.addEventListener('change', (e) => {
            currentTotsFormation = e.target.value;
            loadTeamOfTheSeason(currentTotsFormation);
        });
    }

    // TOTS Formation pill buttons
    const totsPills = document.querySelectorAll('#tots-formation-pills .formation-pill-btn');
    totsPills.forEach(btn => {
        btn.addEventListener('click', () => {
            const form = btn.getAttribute('data-formation');
            if (form) {
                currentTotsFormation = form;
                loadTeamOfTheSeason(currentTotsFormation);
            }
        });
    });
}

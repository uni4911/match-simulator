import { getTeamInitials, getShortPosition, getPositionClass, getFullPositionName, getNationalityBadge, getAttributeLabel, getAttributeTier } from './helpers.js';
import { switchView } from './match.js';
import { switchLeagueSubTab, getPreviousLeagueSubTab, getCurrentLeagueData } from './league.js';

let currentPlayerProfileData = null;
let activeProfileTab = 'overview';
let allTeamsAndPlayersCache = null;

export async function openPlayerProfile(playerName, teamName = '') {
    if (!playerName) return;

    // Clean rank numbers if passed e.g. "1. Vinicius Jr"
    let cleanName = String(playerName).trim();
    if (/^\d+\.\s*/.test(cleanName)) {
        cleanName = cleanName.replace(/^\d+\.\s*/, '');
    }

    // Switch to League view and activate the player subtab inside the league
    switchView('league');
    switchLeagueSubTab('player');

    // Update league subtab label and back button text
    const playerSubtabLabel = document.getElementById('league-subtab-player-label');
    if (playerSubtabLabel) {
        playerSubtabLabel.textContent = `PROFIL: ${cleanName}`;
    }

    updateBackButtonLabel();

    // Show loading state
    renderProfileLoading(cleanName, teamName);

    try {
        const queryParams = new URLSearchParams({ name: cleanName });
        if (teamName) queryParams.append('team', teamName);

        const response = await fetch(`/player/profile?${queryParams.toString()}`);
        if (!response.ok) {
            throw new Error(`Błąd ładowania profilu: ${response.statusText}`);
        }

        currentPlayerProfileData = await response.json();
        renderPlayerProfile(currentPlayerProfileData);

        // Populate and sync quick selector within the league
        ensurePlayerSwitcherLoaded(currentPlayerProfileData.team_name, currentPlayerProfileData.full_name || currentPlayerProfileData.short_name);
    } catch (err) {
        console.error('Błąd pobierania profilu gracza:', err);
        renderProfileError(cleanName, err.message);
    }
}

function updateBackButtonLabel() {
    const backBtnText = document.getElementById('player-back-text');
    if (!backBtnText) return;

    const prev = getPreviousLeagueSubTab();
    if (prev === 'stats') {
        backBtnText.textContent = 'Wróć do statystyk';
    } else {
        backBtnText.textContent = 'Wróć do tabeli';
    }
}

export function switchPlayerProfileTab(tabName) {
    activeProfileTab = tabName;
    const tabs = {
        'overview': 'pp-panel-overview',
        'matches': 'pp-panel-matches',
        'stats': 'pp-panel-stats',
        'all': 'pp-panel-all'
    };
    const buttons = {
        'overview': 'pp-tab-overview-btn',
        'matches': 'pp-tab-matches-btn',
        'stats': 'pp-tab-stats-btn',
        'all': 'pp-tab-all-btn'
    };

    Object.keys(tabs).forEach(key => {
        const panel = document.getElementById(tabs[key]);
        const btn = document.getElementById(buttons[key]);
        if (panel) panel.classList.toggle('hidden', key !== tabName);
        if (btn) btn.classList.toggle('active', key === tabName);
    });
}

function renderProfileLoading(name, team) {
    const banner = document.getElementById('pp-header-banner');
    const body = document.getElementById('pp-content-body');
    if (banner) {
        banner.innerHTML = `
            <div class="pp-loading-state">
                <div class="pp-loading-spinner"></div>
                <div class="pp-loading-text">Ładowanie pełnego profilu zawodnika <strong>${name}</strong>...</div>
            </div>
        `;
    }
    if (body) body.classList.add('pp-body-loading');
}

function renderProfileError(name, errorMsg) {
    const banner = document.getElementById('pp-header-banner');
    if (banner) {
        banner.innerHTML = `
            <div class="pp-error-state">
                <div class="pp-error-icon">⚠️</div>
                <div class="pp-error-title">Nie udało się załadować profilu zawodnika</div>
                <div class="pp-error-desc">${errorMsg}</div>
                <button type="button" class="metro-btn-sm" id="pp-error-back-btn">Powrót</button>
            </div>
        `;
        const btn = document.getElementById('pp-error-back-btn');
        if (btn) {
            btn.onclick = () => switchView(lastVisitedView || 'home');
        }
    }
}

export function renderPlayerProfile(data) {
    const body = document.getElementById('pp-content-body');
    if (body) body.classList.remove('pp-body-loading');

    const shortPos = getShortPosition(data.position);
    const posClass = getPositionClass(data.position);
    const fullPosName = getFullPositionName(data.position);
    const nat = getNationalityBadge(data.nationality);
    const teamBadge = getTeamInitials(data.team_name);
    const seasonStats = data.season_stats || {};
    const matchHistory = data.match_history || [];

    // Header Banner
    const bannerEl = document.getElementById('pp-header-banner');
    if (bannerEl) {
        const ovrVal = data.overall || 50;
        let ovrColorClass = 'ovr-tier-good';
        if (ovrVal >= 88) ovrColorClass = 'ovr-tier-elite';
        else if (ovrVal >= 80) ovrColorClass = 'ovr-tier-great';
        else if (ovrVal < 70) ovrColorClass = 'ovr-tier-avg';

        bannerEl.innerHTML = `
            <div class="pp-banner-inner">
                <div class="pp-avatar-col">
                    <div class="pp-avatar-badge ${posClass}">
                        <span class="pp-avatar-initials">${getTeamInitials(data.short_name || data.player_name)}</span>
                        <span class="pp-pos-floating ${posClass}">${shortPos}</span>
                    </div>
                </div>

                <div class="pp-info-col">
                    <div class="pp-team-pill">
                        <span class="pp-team-mini-badge">${teamBadge}</span>
                        <span class="pp-team-name-text">${data.team_name}</span>
                    </div>

                    <h2 class="pp-player-name" title="${data.full_name || data.player_name}">
                        ${data.short_name || data.player_name}
                    </h2>
                    ${data.full_name && data.full_name !== (data.short_name || data.player_name) ? `
                        <div class="pp-player-fullname">${data.full_name}</div>
                    ` : ''}

                    <div class="pp-meta-row">
                        <div class="pp-meta-chip">
                            <span class="meta-label">Pozycja:</span>
                            <span class="pos-badge ${posClass}" style="padding: 2px 6px;">${shortPos}</span>
                            <span class="meta-val font-semibold">${fullPosName}</span>
                        </div>

                        <div class="pp-meta-chip">
                            <span class="meta-label">Kraj:</span>
                            <span class="meta-flag">${nat.flag}</span>
                            <span class="meta-val">${nat.name}</span>
                        </div>

                        <div class="pp-meta-chip">
                            <span class="meta-label">Wiek:</span>
                            <span class="meta-val font-semibold">${data.age} lat</span>
                        </div>

                        <div class="pp-meta-chip">
                            <span class="meta-label">Wzrost:</span>
                            <span class="meta-val font-semibold">${data.height} cm</span>
                        </div>
                    </div>
                </div>

                <div class="pp-rating-col">
                    <div class="pp-ovr-card ${ovrColorClass}">
                        <span class="pp-ovr-label">OVERALL</span>
                        <span class="pp-ovr-number">${ovrVal}</span>
                        <span class="pp-ovr-stars">★ ★ ★ ★ ★</span>
                    </div>

                    <div class="pp-status-mini-group">
                        <div class="pp-stamina-mini" title="Kondycja gracza">
                            <span>⚡</span>
                            <div class="mini-bar-track">
                                <div class="mini-bar-fill" style="width: ${Math.round((data.fitness || 1.0) * 100)}%;"></div>
                            </div>
                            <span>${Math.round((data.fitness || 1.0) * 100)}%</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Update Match count badge on tab button
    const matchCountBadge = document.getElementById('pp-matches-count-badge');
    if (matchCountBadge) {
        matchCountBadge.textContent = matchHistory.length;
    }

    // 1. Overview Panel (KPIs + Attributes)
    renderOverviewPanel(data, seasonStats);

    // 2. Match History Panel
    renderMatchHistoryPanel(data, matchHistory);

    // 3. Detailed Season Stats Panel
    renderDetailedStatsPanel(data, seasonStats);

    // 4. All Stats Comprehensive Matrix Panel
    renderAllStatsPanel(data, seasonStats);

    // Switch to active tab
    switchPlayerProfileTab(activeProfileTab);
}

function renderOverviewPanel(data, stats) {
    const kpiGrid = document.getElementById('pp-overview-kpi-grid');
    const attrGrid = document.getElementById('pp-attributes-grid');

    if (kpiGrid) {
        const matchesPlayed = stats.matches_played || 0;
        const minutesPlayed = stats.minutes_played || 0;
        const goals = stats.goals || 0;
        const assists = stats.assists || 0;
        const avgRating = stats.average_rating ? Number(stats.average_rating).toFixed(2) : '0.00';
        const motm = stats.motm_awards || 0;
        const avgMinPerMatch = matchesPlayed > 0 ? Math.round(minutesPlayed / matchesPlayed) : 0;

        let ratingClass = 'medium';
        const rNum = parseFloat(avgRating);
        if (rNum >= 7.0) ratingClass = 'high';
        else if (rNum > 0 && rNum < 6.0) ratingClass = 'low';

        const ovrVal = data.overall || 50;

        kpiGrid.innerHTML = `
            <div class="pp-kpi-card pp-kpi-ovr-highlight">
                <div class="pp-kpi-icon">🌟</div>
                <div class="pp-kpi-info">
                    <span class="pp-kpi-val gold-text font-bold" style="font-size: 1.5rem;">${ovrVal}</span>
                    <span class="pp-kpi-title">Ocena Ogólna (OVR)</span>
                </div>
            </div>

            <div class="pp-kpi-card">
                <div class="pp-kpi-icon">🏟️</div>
                <div class="pp-kpi-info">
                    <span class="pp-kpi-val">${matchesPlayed}</span>
                    <span class="pp-kpi-title">Mecze w sezonie</span>
                </div>
            </div>

            <div class="pp-kpi-card">
                <div class="pp-kpi-icon">⚽</div>
                <div class="pp-kpi-info">
                    <span class="pp-kpi-val ${goals > 0 ? 'highlight-text' : ''}">${goals}</span>
                    <span class="pp-kpi-title">Bramki</span>
                </div>
            </div>

            <div class="pp-kpi-card">
                <div class="pp-kpi-icon">🅰️</div>
                <div class="pp-kpi-info">
                    <span class="pp-kpi-val ${assists > 0 ? 'highlight-text' : ''}">${assists}</span>
                    <span class="pp-kpi-title">Asysty</span>
                </div>
            </div>

            <div class="pp-kpi-card">
                <div class="pp-kpi-icon">⭐</div>
                <div class="pp-kpi-info">
                    <span class="pp-kpi-val stat-pill rating ${ratingClass}" style="display:inline-flex;">${avgRating}</span>
                    <span class="pp-kpi-title">Śr. ocena meczowa</span>
                </div>
            </div>

            <div class="pp-kpi-card">
                <div class="pp-kpi-icon">👑</div>
                <div class="pp-kpi-info">
                    <span class="pp-kpi-val ${motm > 0 ? 'gold-text' : ''}">${motm}</span>
                    <span class="pp-kpi-title">Gracz meczu (MOTM)</span>
                </div>
            </div>
        `;
    }

    if (attrGrid) {
        const attributes = data.attributes || {};
        const attrKeys = Object.keys(attributes);

        if (attrKeys.length === 0) {
            attrGrid.innerHTML = '<div class="empty-stats">Brak szczegółowych atrybutów dla tego zawodnika.</div>';
            return;
        }

        attrGrid.innerHTML = attrKeys.map(key => {
            const val = attributes[key] || 50;
            const label = getAttributeLabel(key);
            const tier = getAttributeTier(val);
            const pct = Math.max(0, Math.min(100, val));

            return `
                <div class="pp-attr-item">
                    <div class="pp-attr-header">
                        <span class="pp-attr-label">${label}</span>
                        <div class="pp-attr-right">
                            <span class="pp-attr-tier ${tier.className}">${tier.label}</span>
                            <span class="pp-attr-val">${val}</span>
                        </div>
                    </div>
                    <div class="pp-attr-track">
                        <div class="pp-attr-fill ${tier.className}" style="width: ${pct}%;"></div>
                    </div>
                </div>
            `;
        }).join('');
    }
}

function renderMatchHistoryPanel(data, matchHistory) {
    const listContainer = document.getElementById('pp-matches-list');
    const summaryEl = document.getElementById('pp-matches-summary');

    if (summaryEl) {
        const finishedMatches = matchHistory.filter(m => m.is_finished);
        const playedMatches = matchHistory.filter(m => m.played_in_match);
        const wins = matchHistory.filter(m => m.is_finished && m.result === 'W').length;
        const draws = matchHistory.filter(m => m.is_finished && m.result === 'D').length;
        const losses = matchHistory.filter(m => m.is_finished && m.result === 'L').length;
        const totalGoals = matchHistory.reduce((sum, m) => sum + (m.goals || 0), 0);
        const totalAssists = matchHistory.reduce((sum, m) => sum + (m.assists || 0), 0);

        summaryEl.innerHTML = `
            <div class="pp-summary-item">
                <span class="summary-num">${matchHistory.length}</span>
                <span class="summary-lbl">Wszystkie mecze</span>
            </div>
            <div class="pp-summary-item">
                <span class="summary-num">${playedMatches.length}</span>
                <span class="summary-lbl">Występy na boisku</span>
            </div>
            <div class="pp-summary-item">
                <span class="summary-num form-record">
                    <span class="w-val">${wins}W</span> - <span class="d-val">${draws}R</span> - <span class="l-val">${losses}P</span>
                </span>
                <span class="summary-lbl">Bilans drużyny</span>
            </div>
            <div class="pp-summary-item">
                <span class="summary-num highlight-text">${totalGoals} ⚽ / ${totalAssists} 🅰️</span>
                <span class="summary-lbl">Bramki i Asysty</span>
            </div>
        `;
    }

    if (!listContainer) return;

    if (!matchHistory || matchHistory.length === 0) {
        listContainer.innerHTML = '<div class="empty-events" style="text-align: center; padding: 2rem;">Brak rozegranych meczów w historii zawodnika w tym sezonie.</div>';
        return;
    }

    listContainer.innerHTML = matchHistory.map((m, idx) => {
        const isFin = m.is_finished;
        const isHome = m.is_home;
        const oppName = m.opponent_name || (isHome ? m.away_team_name : m.home_team_name);
        const oppBadge = getTeamInitials(oppName);
        const scoreStr = isFin ? `${m.home_score} : ${m.away_score}` : 'vs';

        let resultBadgeClass = 'res-pending';
        let resultText = 'DO ROZEGRANIA';
        if (isFin) {
            if (m.result === 'W') {
                resultBadgeClass = 'res-win';
                resultText = 'ZWYCIĘSTWO';
            } else if (m.result === 'D') {
                resultBadgeClass = 'res-draw';
                resultText = 'REMIS';
            } else {
                resultBadgeClass = 'res-loss';
                resultText = 'PORAŻKA';
            }
        }

        let roleBadge = '';
        if (m.played_in_match) {
            if (m.is_starter && !m.was_subbed_off) {
                roleBadge = '<span class="role-badge starter">Wyjściowa 11 (90\')</span>';
            } else if (m.is_starter && m.was_subbed_off) {
                roleBadge = `<span class="role-badge sub-off">Zmieniony (${m.minutes_played}\')</span>`;
            } else if (m.was_subbed_in) {
                roleBadge = `<span class="role-badge sub-in">Wejście z ławki (${m.minutes_played}\')</span>`;
            } else {
                roleBadge = `<span class="role-badge on-field">Grał (${m.minutes_played}\')</span>`;
            }
        } else if (isFin) {
            roleBadge = '<span class="role-badge bench">Na ławce / Poza kadrą (0\')</span>';
        } else {
            roleBadge = '<span class="role-badge pending">Zaplanowany</span>';
        }

        const ratingVal = m.rating !== undefined ? Number(m.rating).toFixed(1) : '6.0';
        const ratingNum = parseFloat(ratingVal);
        let ratingClass = 'medium';
        if (ratingNum >= 7.0) ratingClass = 'high';
        else if (ratingNum < 6.0 && ratingNum > 0) ratingClass = 'low';

        return `
            <div class="pp-match-card ${isFin ? 'finished' : 'pending'} ${m.is_motm ? 'is-motm-match' : ''}" data-fixture-index="${m.fixture_index !== undefined && m.fixture_index !== null ? m.fixture_index : ''}">
                <div class="pp-match-left">
                    <div class="pp-match-round">Kolejka ${m.round_number}</div>
                    <div class="pp-match-opp">
                        <span class="pp-match-home-tag">${isHome ? '(D)' : '(W)'}</span>
                        <span class="team-mini-badge">${oppBadge}</span>
                        <span class="opp-name-text">${oppName}</span>
                    </div>
                </div>

                <div class="pp-match-score-block">
                    <div class="pp-match-score">${scoreStr}</div>
                    <span class="pp-result-badge ${resultBadgeClass}">${resultText}</span>
                </div>

                <div class="pp-match-role-block">
                    ${roleBadge}
                    ${m.is_motm ? '<span class="motm-badge-gold">👑 MOTM</span>' : ''}
                    ${m.is_injured ? '<span class="injured-badge-red">🚑 Kontuzja</span>' : ''}
                </div>

                <div class="pp-match-stats-block">
                    ${isFin && m.played_in_match ? `
                        <div class="pp-match-pills">
                            <span class="stat-pill rating ${ratingClass}">⭐ ${ratingVal}</span>
                            <span class="stat-pill minutes">⏱️ ${m.minutes_played}'</span>
                            ${m.goals > 0 ? `<span class="stat-pill goals active">⚽ ${m.goals}</span>` : ''}
                            ${m.assists > 0 ? `<span class="stat-pill assists active">🅰️ ${m.assists}</span>` : ''}
                            ${m.passes > 0 ? `<span class="stat-pill passes">👟 ${m.passes}</span>` : ''}
                            ${m.yellow_cards > 0 ? `<span class="stat-pill yellow active">🟨 ${m.yellow_cards}</span>` : ''}
                            ${m.has_red_card ? `<span class="stat-pill red active">🟥</span>` : ''}
                        </div>
                    ` : (isFin ? `
                        <span class="text-sub italic">Brak występów</span>
                    ` : `
                        <span class="text-sub">Mecz nieodbyty</span>
                    `)}
                </div>

                ${m.fixture_index !== undefined && m.fixture_index !== null && isFin ? `
                    <button type="button" class="pp-match-details-btn" data-fixture-index="${m.fixture_index}" title="Zobacz szczegóły tego meczu">
                        Szczegóły ➔
                    </button>
                ` : '<div style="width: 24px;"></div>'}
            </div>
        `;
    }).join('');

    // Add click listeners to fixture detail buttons inside match history
    listContainer.querySelectorAll('.pp-match-details-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const fixIdx = parseInt(btn.getAttribute('data-fixture-index'), 10);
            if (!isNaN(fixIdx) && window.openMatchByIndex) {
                window.openMatchByIndex(fixIdx);
            }
        });
    });
}

function renderDetailedStatsPanel(data, stats) {
    const container = document.getElementById('pp-stats-detail-grid');
    if (!container) return;

    const mPlayed = stats.matches_played || 0;
    const mTotal = stats.minutes_played || 0;
    const goals = stats.goals || 0;
    const assists = stats.assists || 0;
    const passes = stats.passes || 0;
    const yellows = stats.yellow_cards || 0;
    const reds = stats.red_cards || 0;
    const cleanSheets = stats.clean_sheets || 0;
    const motm = stats.motm_awards || 0;
    const avgRating = stats.average_rating ? Number(stats.average_rating).toFixed(2) : '0.00';

    const gPer90 = mTotal > 0 ? ((goals / mTotal) * 90).toFixed(2) : '0.00';
    const aPer90 = mTotal > 0 ? ((assists / mTotal) * 90).toFixed(2) : '0.00';
    const gaTotal = goals + assists;
    const gaPer90 = mTotal > 0 ? ((gaTotal / mTotal) * 90).toFixed(2) : '0.00';
    const passesPerMatch = mPlayed > 0 ? (passes / mPlayed).toFixed(1) : '0.0';
    const avgMinPerMatch = mPlayed > 0 ? Math.round(mTotal / mPlayed) : 0;
    const discPoints = yellows + (reds * 3);

    container.innerHTML = `
        <div class="pp-stat-group-box">
            <div class="pp-group-header">
                <span class="group-icon">⚽</span> OFENSYWA I KREACJA
            </div>
            <div class="pp-stat-rows-list">
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Zdobyte bramki</span>
                    <span class="stat-row-val font-bold highlight-text">${goals}</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Zanotowane asysty</span>
                    <span class="stat-row-val font-bold highlight-text">${assists}</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Klasyfikacja kanadyjska (G + A)</span>
                    <span class="stat-row-val font-bold">${gaTotal}</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Bramki na 90 minut</span>
                    <span class="stat-row-val">${gPer90}</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Asysty na 90 minut</span>
                    <span class="stat-row-val">${aPer90}</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Udział bramkowy na 90 min</span>
                    <span class="stat-row-val font-bold">${gaPer90}</span>
                </div>
            </div>
        </div>

        <div class="pp-stat-group-box">
            <div class="pp-group-header">
                <span class="group-icon">⏱️</span> CZAS GRY I WYSTĘPY
            </div>
            <div class="pp-stat-rows-list">
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Rozegrane spotkania</span>
                    <span class="stat-row-val font-bold">${mPlayed}</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Łączny czas gry</span>
                    <span class="stat-row-val font-bold">${mTotal} minut</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Średnio minut na mecz</span>
                    <span class="stat-row-val">${avgMinPerMatch}' / mecz</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Kondycja fizyczna</span>
                    <span class="stat-row-val">${Math.round((data.fitness || 1.0) * 100)}%</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Mnożnik formy meczowej</span>
                    <span class="stat-row-val font-bold">${(data.form || 1.0).toFixed(2)}x</span>
                </div>
            </div>
        </div>

        <div class="pp-stat-group-box">
            <div class="pp-group-header">
                <span class="group-icon">🌟</span> WPŁYW NA MECZ & WYRÓŻNIENIA
            </div>
            <div class="pp-stat-rows-list">
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Średnia ocena meczowa</span>
                    <span class="stat-row-val font-bold">⭐ ${avgRating}</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Tytuły Gracza Meczu (MOTM)</span>
                    <span class="stat-row-val font-bold gold-text">${motm}x 👑</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Wykonane podania ogółem</span>
                    <span class="stat-row-val">${passes}</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Średnio podań na mecz</span>
                    <span class="stat-row-val">${passesPerMatch}</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Czyste konta (Clean sheets)</span>
                    <span class="stat-row-val font-bold">${cleanSheets}</span>
                </div>
            </div>
        </div>

        <div class="pp-stat-group-box">
            <div class="pp-group-header">
                <span class="group-icon">🟨</span> DYSCYPLINA I KARTKI
            </div>
            <div class="pp-stat-rows-list">
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Żółte kartki</span>
                    <span class="stat-row-val font-bold">${yellows} 🟨</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Czerwone kartki</span>
                    <span class="stat-row-val font-bold ${reds > 0 ? 'red-text' : ''}">${reds} 🟥</span>
                </div>
                <div class="pp-stat-row-item">
                    <span class="stat-row-label">Punkty dyscyplinarne</span>
                    <span class="stat-row-val">${discPoints} pkt</span>
                </div>
            </div>
        </div>
    `;
}

function renderAllStatsPanel(data, stats) {
    const container = document.getElementById('pp-all-stats-table-container');
    if (!container) return;

    const nat = getNationalityBadge(data.nationality);
    const fullPos = getFullPositionName(data.position);
    const isGK = data.is_goalkeeper || String(data.position).includes('GOALKEEPER');

    const mPlayed = stats.matches_played || 0;
    const mTotal = stats.minutes_played || 0;
    const goals = stats.goals || 0;
    const assists = stats.assists || 0;
    const passes = stats.passes || 0;
    const avgRating = stats.average_rating ? Number(stats.average_rating).toFixed(2) : '0.00';
    const motm = stats.motm_awards || 0;
    const yellows = stats.yellow_cards || 0;
    const reds = stats.red_cards || 0;
    const cleanSheets = stats.clean_sheets || 0;
    const avgMinPerMatch = mPlayed > 0 ? Math.round(mTotal / mPlayed) : 0;
    const gaPer90 = mTotal > 0 ? ((goals + assists) / (mTotal / 90)).toFixed(2) : '0.00';
    const goalsPer90 = mTotal > 0 ? (goals / (mTotal / 90)).toFixed(2) : '0.00';
    const assistsPer90 = mTotal > 0 ? (assists / (mTotal / 90)).toFixed(2) : '0.00';
    const passesPerMatch = mPlayed > 0 ? (passes / mPlayed).toFixed(1) : '0.0';

    const attrs = data.attributes || {};

    let attrRowsHtml = '';
    Object.entries(attrs).forEach(([key, val]) => {
        const label = getAttributeLabel(key);
        const tier = getAttributeTier(val);
        attrRowsHtml += `
            <tr>
                <td class="stat-matrix-name">${label}</td>
                <td class="stat-matrix-cat">Atrybut (${isGK ? 'Bramkarski' : 'Piłkarski'})</td>
                <td class="stat-matrix-val font-bold tier-${tier.class}">${val} / 99</td>
                <td class="stat-matrix-bar-cell">
                    <div class="matrix-bar-track">
                        <div class="matrix-bar-fill fill-${tier.class}" style="width: ${Math.min(100, Math.max(0, val))}%;"></div>
                    </div>
                </td>
                <td class="stat-matrix-tier"><span class="attr-tier-tag ${tier.class}">${tier.label}</span></td>
            </tr>
        `;
    });

    container.innerHTML = `
        <div class="all-stats-wrapper">
            <div class="all-stats-header-info">
                <div class="info-title">📋 KOMPLETNA TABELA DANYCH I STATYSTYK ZAWODNIKA</div>
                <div class="info-subtitle">Zestawienie wszystkich atrybutów, parametrów fizycznych oraz wskaźników meczowych i sezonowych.</div>
            </div>

            <div class="metro-table-wrapper" style="overflow-x: auto; margin-top: 1rem;">
                <table class="metro-table all-stats-matrix-table">
                    <thead>
                        <tr>
                            <th style="width: 25%;">Parametr / Statystyka</th>
                            <th style="width: 20%;">Kategoria</th>
                            <th style="width: 15%;">Wartość</th>
                            <th style="width: 25%;">Wskaźnik Graficzny</th>
                            <th style="width: 15%;">Poziom / Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- General Info -->
                        <tr class="matrix-group-row"><td colspan="5">👤 DANE PODSTAWOWE I BIOMETRYCZNE</td></tr>
                        <tr>
                            <td class="stat-matrix-name">Imię i nazwisko</td>
                            <td class="stat-matrix-cat">Identyfikacja</td>
                            <td class="stat-matrix-val font-bold" colspan="3">${data.full_name || data.player_name}</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Klub / Drużyna</td>
                            <td class="stat-matrix-cat">Klub</td>
                            <td class="stat-matrix-val font-bold" colspan="3">${data.team_name}</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Narodowość / Kraj</td>
                            <td class="stat-matrix-cat">Pochodzenie</td>
                            <td class="stat-matrix-val font-bold">${nat.flag} ${nat.name}</td>
                            <td colspan="2" class="text-muted">Baza danych FIFA / Scraper</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Pozycja na boisku</td>
                            <td class="stat-matrix-cat">Rola taktyczna</td>
                            <td class="stat-matrix-val font-bold">${fullPos} (${getShortPosition(data.position)})</td>
                            <td colspan="2"><span class="pos-badge ${getPositionClass(data.position)}">${getShortPosition(data.position)}</span></td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Ocena Ogólna (OVERALL)</td>
                            <td class="stat-matrix-cat">Ranking ogólny</td>
                            <td class="stat-matrix-val font-bold gold-text" style="font-size: 1.15rem;">⭐ ${data.overall || 50}</td>
                            <td class="stat-matrix-bar-cell">
                                <div class="matrix-bar-track">
                                    <div class="matrix-bar-fill fill-elite" style="width: ${Math.min(100, Math.max(0, data.overall || 50))}%;"></div>
                                </div>
                            </td>
                            <td><span class="attr-tier-tag ${data.overall >= 85 ? 'elite' : data.overall >= 78 ? 'great' : 'good'}">OVR ${data.overall}</span></td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Wiek zawodnika</td>
                            <td class="stat-matrix-cat">Biometria</td>
                            <td class="stat-matrix-val font-bold">${data.age} lat</td>
                            <td colspan="2">Urodzony ok. ${new Date().getFullYear() - data.age}</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Wzrost</td>
                            <td class="stat-matrix-cat">Biometria</td>
                            <td class="stat-matrix-val font-bold">${data.height} cm</td>
                            <td colspan="2">${data.height >= 190 ? 'Wysoki (przewaga w powietrzu)' : data.height >= 180 ? 'Średni wzrost' : 'Niski (wysoka zwinność)'}</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Kondycja fizyczna (Fitness)</td>
                            <td class="stat-matrix-cat">Stan fizyczny</td>
                            <td class="stat-matrix-val font-bold">${Math.round((data.fitness || 1.0) * 100)}%</td>
                            <td class="stat-matrix-bar-cell">
                                <div class="matrix-bar-track">
                                    <div class="matrix-bar-fill fill-good" style="width: ${Math.round((data.fitness || 1.0) * 100)}%;"></div>
                                </div>
                            </td>
                            <td>${data.fitness >= 0.85 ? '🟢 Pełna świeżość' : data.fitness >= 0.6 ? '🟡 Zmęczenie' : '🔴 Wyczerpanie'}</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Wskaźnik formy meczowej</td>
                            <td class="stat-matrix-cat">Forma</td>
                            <td class="stat-matrix-val font-bold">${(data.form || 1.0).toFixed(2)}x</td>
                            <td colspan="2">${data.form >= 1.1 ? '🔥 Znakomita dyspozycja' : data.form >= 0.95 ? '⚡ Normalna dyspozycja' : '❄️ Spadek formy'}</td>
                        </tr>

                        <!-- Attributes Group -->
                        <tr class="matrix-group-row"><td colspan="5">⚡ OFICJALNE ATRYBUTY I UMIEJĘTNOŚCI ZAWODNIKA</td></tr>
                        ${attrRowsHtml}

                        <!-- Performance Group -->
                        <tr class="matrix-group-row"><td colspan="5">📊 STATYSTYKI WYSTĘPÓW I OSIĄGNIĘĆ</td></tr>
                        <tr>
                            <td class="stat-matrix-name">Rozegrane mecze</td>
                            <td class="stat-matrix-cat">Występy</td>
                            <td class="stat-matrix-val font-bold">${mPlayed}</td>
                            <td colspan="2">${mPlayed} spotkań</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Minuty na boisku</td>
                            <td class="stat-matrix-cat">Czas gry</td>
                            <td class="stat-matrix-val font-bold">${mTotal}'</td>
                            <td colspan="2">Średnio ${avgMinPerMatch}' / mecz</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Strzelone bramki</td>
                            <td class="stat-matrix-cat">Ofensywa</td>
                            <td class="stat-matrix-val font-bold ${goals > 0 ? 'gold-text' : ''}">⚽ ${goals}</td>
                            <td colspan="2">${goalsPer90} goli / 90 min</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Asysty bramkowe</td>
                            <td class="stat-matrix-cat">Kreacja</td>
                            <td class="stat-matrix-val font-bold">🅰️ ${assists}</td>
                            <td colspan="2">${assistsPer90} asyst / 90 min</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Klasyfikacja Kanadyjska (Gole + Asysty)</td>
                            <td class="stat-matrix-cat">Wpływ ofensywny</td>
                            <td class="stat-matrix-val font-bold gold-text">${goals + assists} pkt</td>
                            <td colspan="2">${gaPer90} G+A / 90 min</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Średnia ocena meczowa</td>
                            <td class="stat-matrix-cat">Jakość gry</td>
                            <td class="stat-matrix-val font-bold">⭐ ${avgRating}</td>
                            <td colspan="2">${Number(avgRating) >= 7.0 ? 'Klasa światowa' : Number(avgRating) >= 6.5 ? 'Solidna' : 'Przeciętna'}</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Tytuły Gracza Meczu (MOTM)</td>
                            <td class="stat-matrix-cat">Wyróżnienia</td>
                            <td class="stat-matrix-val font-bold gold-text">👑 ${motm}</td>
                            <td colspan="2">${motm > 0 ? `Najlepszy na boisku ${motm}x` : 'Brak wyróżnień'}</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Podania ogółem</td>
                            <td class="stat-matrix-cat">Rozegranie</td>
                            <td class="stat-matrix-val">${passes}</td>
                            <td colspan="2">${passesPerMatch} podań / mecz</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Czyste konta (Clean sheets)</td>
                            <td class="stat-matrix-cat">Defensywa</td>
                            <td class="stat-matrix-val font-bold">${cleanSheets}</td>
                            <td colspan="2">${cleanSheets} meczów bez straty bramki</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Żółte kartki</td>
                            <td class="stat-matrix-cat">Dyscyplina</td>
                            <td class="stat-matrix-val font-bold">🟨 ${yellows}</td>
                            <td colspan="2">${yellows} napomnień</td>
                        </tr>
                        <tr>
                            <td class="stat-matrix-name">Czerwone kartki</td>
                            <td class="stat-matrix-cat">Dyscyplina</td>
                            <td class="stat-matrix-val font-bold ${reds > 0 ? 'red-text' : ''}">🟥 ${reds}</td>
                            <td colspan="2">${reds > 0 ? 'Wykluczenie z gry' : 'Czyste konto'}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

export async function ensurePlayerSwitcherLoaded(selectedTeam = '', selectedPlayer = '') {
    const teamSelect = document.getElementById('pv-team-select');
    const playerSelect = document.getElementById('pv-player-select');
    if (!teamSelect || !playerSelect) return;

    try {
        if (!allTeamsAndPlayersCache) {
            const response = await fetch('/teams');
            if (response.ok) {
                allTeamsAndPlayersCache = await response.json();
            }
        }

        const leagueData = getCurrentLeagueData();
        const leagueTeams = leagueData && leagueData.teams ? leagueData.teams : null;

        if (allTeamsAndPlayersCache) {
            const allTeams = Object.keys(allTeamsAndPlayersCache).sort();
            const teams = leagueTeams ? leagueTeams.filter(t => allTeams.includes(t)).sort() : allTeams;
            
            // Populate teams if empty or if list changed
            teamSelect.innerHTML = '<option value="">Wszystkie drużyny ligi</option>';
            teams.forEach(tName => {
                const opt = document.createElement('option');
                opt.value = tName;
                opt.textContent = tName;
                teamSelect.appendChild(opt);
            });

            if (selectedTeam && [...teamSelect.options].some(o => o.value === selectedTeam)) {
                teamSelect.value = selectedTeam;
            }

            populatePlayerDropdown(teamSelect.value, selectedPlayer);
        }
    } catch (err) {
        console.error('Błąd ładowania listy drużyn dla profilu:', err);
    }
}

function populatePlayerDropdown(filterTeam = '', selectedPlayer = '') {
    const playerSelect = document.getElementById('pv-player-select');
    if (!playerSelect || !allTeamsAndPlayersCache) return;

    playerSelect.innerHTML = '<option value="">Wybierz gracza...</option>';

    const leagueData = getCurrentLeagueData();
    const leagueTeams = leagueData && leagueData.teams ? leagueData.teams : null;

    let playerOptions = [];
    if (filterTeam && allTeamsAndPlayersCache[filterTeam]) {
        playerOptions = allTeamsAndPlayersCache[filterTeam].map(p => ({
            name: p.short_name || p.full_name || p.name,
            team: filterTeam,
            pos: getShortPosition(p.position),
            ovr: p.overall || p._overall || ''
        }));
    } else {
        Object.entries(allTeamsAndPlayersCache).forEach(([tName, players]) => {
            if (!leagueTeams || leagueTeams.includes(tName)) {
                players.forEach(p => {
                    playerOptions.push({
                        name: p.short_name || p.full_name || p.name,
                        team: tName,
                        pos: getShortPosition(p.position),
                        ovr: p.overall || p._overall || ''
                    });
                });
            }
        });
    }

    playerOptions.sort((a, b) => a.name.localeCompare(b.name));

    playerOptions.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.name;
        opt.dataset.team = p.team;
        const ovrStr = p.ovr ? ` [${p.ovr}]` : '';
        opt.textContent = `${p.name} (${p.pos})${ovrStr} - ${p.team}`;
        if (selectedPlayer && (p.name.toLowerCase() === selectedPlayer.toLowerCase())) {
            opt.selected = true;
        }
        playerSelect.appendChild(opt);
    });
}

export function initPlayerProfileView() {
    // Back Button: returns to previous league subtab (table or stats)
    const backBtn = document.getElementById('player-back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            switchLeagueSubTab(getPreviousLeagueSubTab() || 'table');
        });
    }

    // League subtab player button click
    const leagueSubtabPlayer = document.getElementById('league-subtab-player');
    if (leagueSubtabPlayer) {
        leagueSubtabPlayer.addEventListener('click', () => {
            switchLeagueSubTab('player');
        });
    }

    // Tab buttons inside player profile
    const btnOverview = document.getElementById('pp-tab-overview-btn');
    const btnMatches = document.getElementById('pp-tab-matches-btn');
    const btnStats = document.getElementById('pp-tab-stats-btn');
    const btnAll = document.getElementById('pp-tab-all-btn');

    if (btnOverview) btnOverview.addEventListener('click', () => switchPlayerProfileTab('overview'));
    if (btnMatches) btnMatches.addEventListener('click', () => switchPlayerProfileTab('matches'));
    if (btnStats) btnStats.addEventListener('click', () => switchPlayerProfileTab('stats'));
    if (btnAll) btnAll.addEventListener('click', () => switchPlayerProfileTab('all'));

    // Quick Switcher: Team Select
    const teamSelect = document.getElementById('pv-team-select');
    if (teamSelect) {
        teamSelect.addEventListener('change', () => {
            populatePlayerDropdown(teamSelect.value);
        });
    }

    // Quick Switcher: Player Select
    const playerSelect = document.getElementById('pv-player-select');
    if (playerSelect) {
        playerSelect.addEventListener('change', () => {
            const selectedOpt = playerSelect.selectedOptions[0];
            if (selectedOpt && selectedOpt.value) {
                const teamName = selectedOpt.dataset.team || '';
                openPlayerProfile(selectedOpt.value, teamName);
            }
        });
    }

    // Quick Switcher: Search Input
    const searchInput = document.getElementById('pv-player-search');
    if (searchInput) {
        let debounceTimer = null;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = searchInput.value.trim().toLowerCase();
                if (!query) return;
                const playerSelect = document.getElementById('pv-player-select');
                if (playerSelect) {
                    for (let i = 1; i < playerSelect.options.length; i++) {
                        const opt = playerSelect.options[i];
                        if (opt.text.toLowerCase().includes(query)) {
                            playerSelect.selectedIndex = i;
                            const teamName = opt.dataset.team || '';
                            openPlayerProfile(opt.value, teamName);
                            break;
                        }
                    }
                }
            }, 400);
        });
    }
}

window.openPlayerProfile = openPlayerProfile;
window.initPlayerProfileView = initPlayerProfileView;
window.switchPlayerProfileTab = switchPlayerProfileTab;

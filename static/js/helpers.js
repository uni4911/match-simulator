export function getTeamInitials(name) {
    if (!name) return '???';
    const words = name.trim().split(/\s+/);
    if (words.length >= 2) {
        return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.slice(0, 3).toUpperCase();
}

export function getShortPosition(pos) {
    if (!pos) return 'FLD';
    const uppercase = String(pos).toUpperCase().trim();
    
    const fifaMap = {
        'GOALKEEPER': 'GK',
        'GK': 'GK',
        'LEFT_BACK': 'LB',
        'LB': 'LB',
        'CENTRE_BACK': 'CB',
        'CENTER_BACK': 'CB',
        'CB': 'CB',
        'RIGHT_BACK': 'RB',
        'RB': 'RB',
        'LEFT_WING_BACK': 'LWB',
        'LWB': 'LWB',
        'RIGHT_WING_BACK': 'RWB',
        'RWB': 'RWB',
        'CENTRAL_DEFENSIVE_MIDFIELDER': 'CDM',
        'CDM': 'CDM',
        'CENTRAL_MIDFIELDER': 'CM',
        'CM': 'CM',
        'CENTRAL_ATTACKING_MIDFIELDER': 'CAM',
        'CAM': 'CAM',
        'LEFT_MIDFIELDER': 'LM',
        'LM': 'LM',
        'RIGHT_MIDFIELDER': 'RM',
        'RM': 'RM',
        'LEFT_WING': 'LW',
        'LW': 'LW',
        'RIGHT_WING': 'RW',
        'RW': 'RW',
        'CENTRAL_FORWARD': 'CF',
        'CF': 'CF',
        'STRIKER': 'ST',
        'ST': 'ST'
    };

    if (fifaMap[uppercase]) return fifaMap[uppercase];
    return uppercase.slice(0, 3);
}

export function getPositionClass(pos) {
    const code = getShortPosition(pos);
    if (code === 'GK') return 'pos-gk';
    if (['LB', 'CB', 'RB', 'LWB', 'RWB'].includes(code)) return 'pos-def';
    if (['CDM', 'CM', 'CAM', 'LM', 'RM'].includes(code)) return 'pos-mid';
    if (['LW', 'RW', 'CF', 'ST'].includes(code)) return 'pos-fwd';
    return 'pos-fld';
}

export function getEventIcon(eventType) {
    switch (eventType) {
        case 'Goal':
        case 'GoalWithAssist':
        case 'PenaltyKickGoal':
        case 'LongShotGoal':
            return '⚽';
        case 'ShotSave':
            return '🧤';
        case 'LongShotEvent':
            return '🚀';
        case 'WingPlayEvent':
            return '⚡';
        case 'BuildUpEvent':
            return '🦶';
        case 'InterceptionEvent':
            return '🛡️';
        case 'YellowCardFoul':
        case 'DoubleYellowCard':
            return '🟨';
        case 'RedCardFoul':
            return '🟥';
        case 'Foul':
            return '🟨';
        case 'KickoffEvent':
            return '🪙';
        case 'HalfTimeEvent':
            return '⏸️';
        case 'MatchEndEvent':
            return '🏁';
        case 'Substitution':
            return '🔄';
        case 'CornerKickEvent':
            return '🚩';
        case 'InjuryEvent':
            return '🚑';
        default:
            return '⏱️';
    }
}


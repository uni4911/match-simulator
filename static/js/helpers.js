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

export function getFullPositionName(pos) {
    if (!pos) return 'Zawodnik';
    const code = getShortPosition(pos);
    const names = {
        'GK': 'Bramkarz',
        'LB': 'Lewy Obrońca',
        'CB': 'Środkowy Obrońca',
        'RB': 'Prawy Obrońca',
        'LWB': 'Lewy Wahadłowy',
        'RWB': 'Prawy Wahadłowy',
        'CDM': 'Defensywny Pomocnik',
        'CM': 'Środkowy Pomocnik',
        'CAM': 'Ofensywny Pomocnik',
        'LM': 'Lewy Pomocnik',
        'RM': 'Prawy Pomocnik',
        'LW': 'Lewy Skrzydłowy',
        'RW': 'Prawy Skrzydłowy',
        'CF': 'Cofnięty Napastnik',
        'ST': 'Środkowy Napastnik'
    };
    return names[code] || String(pos).replace(/_/g, ' ');
}

const NATIONALITY_FLAG_MAP = {
    'Afghanistan': { flag: '🇦🇫', name: 'Afganistan' },
    'Albania': { flag: '🇦🇱', name: 'Albania' },
    'Algeria': { flag: '🇩🇿', name: 'Algieria' },
    'American Samoa': { flag: '🇦🇸', name: 'Samoa Amerykańskie' },
    'Andorra': { flag: '🇦🇩', name: 'Andora' },
    'Andora': { flag: '🇦🇩', name: 'Andora' },
    'Angola': { flag: '🇦🇴', name: 'Angola' },
    'Anguilla': { flag: '🇦🇮', name: 'Anguilla' },
    'Antigua and Barbuda': { flag: '🇦🇬', name: 'Antigua i Barbuda' },
    'Argentina': { flag: '🇦🇷', name: 'Argentyna' },
    'Argentyna': { flag: '🇦🇷', name: 'Argentyna' },
    'Armenia': { flag: '🇦🇲', name: 'Armenia' },
    'Aruba': { flag: '🇦🇼', name: 'Aruba' },
    'Australia': { flag: '🇦🇺', name: 'Australia' },
    'Austria': { flag: '🇦🇹', name: 'Austria' },
    'Azerbaijan': { flag: '🇦🇿', name: 'Azerbejdżan' },
    'Bahamas': { flag: '🇧🇸', name: 'Bahamy' },
    'Bahrain': { flag: '🇧🇭', name: 'Bahrajn' },
    'Bangladesh': { flag: '🇧🇩', name: 'Bangladesz' },
    'Barbados': { flag: '🇧🇧', name: 'Barbados' },
    'Belarus': { flag: '🇧🇾', name: 'Białoruś' },
    'Belgium': { flag: '🇧🇪', name: 'Belgia' },
    'Belgia': { flag: '🇧🇪', name: 'Belgia' },
    'Belize': { flag: '🇧🇿', name: 'Belize' },
    'Benin': { flag: '🇧🇯', name: 'Benin' },
    'Bermuda': { flag: '🇧🇲', name: 'Bermudy' },
    'Bhutan': { flag: '🇧🇹', name: 'Bhutan' },
    'Bolivia': { flag: '🇧🇴', name: 'Boliwia' },
    'Bosnia and Herzegovina': { flag: '🇧🇦', name: 'Bośnia i Hercegowina' },
    'Bośnia i Hercegowina': { flag: '🇧🇦', name: 'Bośnia i Hercegowina' },
    'Bośnia i Herc.': { flag: '🇧🇦', name: 'Bośnia i Hercegowina' },
    'Botswana': { flag: '🇧🇼', name: 'Botswana' },
    'Brazil': { flag: '🇧🇷', name: 'Brazylia' },
    'Brazylia': { flag: '🇧🇷', name: 'Brazylia' },
    'British Virgin Islands': { flag: '🇻🇬', name: 'Brytyjskie Wyspy Dziewicze' },
    'Brunei Darussalam': { flag: '🇧🇳', name: 'Brunei' },
    'Bulgaria': { flag: '🇧🇬', name: 'Bułgaria' },
    'Bułgaria': { flag: '🇧🇬', name: 'Bułgaria' },
    'Burkina Faso': { flag: '🇧🇫', name: 'Burkina Faso' },
    'Burundi': { flag: '🇧🇮', name: 'Burundi' },
    'Cabo Verde': { flag: '🇨🇻', name: 'Wyspy Zielonego Przylądka' },
    'W-y Ziel. Przylądka': { flag: '🇨🇻', name: 'Wyspy Zielonego Przylądka' },
    'Wyspy Zielonego Przylądka': { flag: '🇨🇻', name: 'Wyspy Zielonego Przylądka' },
    'Cambodia': { flag: '🇰🇭', name: 'Kambodża' },
    'Cameroon': { flag: '🇨🇲', name: 'Kamerun' },
    'Kamerun': { flag: '🇨🇲', name: 'Kamerun' },
    'Canada': { flag: '🇨🇦', name: 'Kanada' },
    'Kanada': { flag: '🇨🇦', name: 'Kanada' },
    'Cayman Islands': { flag: '🇰🇾', name: 'Kajmany' },
    'Central African Republic': { flag: '🇨🇫', name: 'Rep. Środkowoafrykańska' },
    'Rep. Środkowoafryk.': { flag: '🇨🇫', name: 'Rep. Środkowoafrykańska' },
    'Chad': { flag: '🇹🇩', name: 'Czad' },
    'Chile': { flag: '🇨🇱', name: 'Chile' },
    'China PR': { flag: '🇨🇳', name: 'Chiny' },
    'Chinese Taipei': { flag: '🇹🇼', name: 'Tajwan' },
    'Colombia': { flag: '🇨🇴', name: 'Kolumbia' },
    'Kolumbia': { flag: '🇨🇴', name: 'Kolumbia' },
    'Comoros': { flag: '🇰🇲', name: 'Komory' },
    'Congo': { flag: '🇨🇬', name: 'Kongo' },
    'Congo DR': { flag: '🇨🇩', name: 'DR Kongo' },
    'Demokr. Rep. Konga': { flag: '🇨🇩', name: 'DR Kongo' },
    'Cook Islands': { flag: '🇨🇰', name: 'Wyspy Cooka' },
    'Costa Rica': { flag: '🇨🇷', name: 'Kostaryka' },
    'Croatia': { flag: '🇭🇷', name: 'Chorwacja' },
    'Chorwacja': { flag: '🇭🇷', name: 'Chorwacja' },
    'Cuba': { flag: '🇨🇺', name: 'Kuba' },
    'Curaçao': { flag: '🇨🇼', name: 'Curaçao' },
    'Curacao': { flag: '🇨🇼', name: 'Curaçao' },
    'Cyprus': { flag: '🇨🇾', name: 'Cypr' },
    'Czechia': { flag: '🇨🇿', name: 'Czechy' },
    'Czech Republic': { flag: '🇨🇿', name: 'Czechy' },
    'Czechy': { flag: '🇨🇿', name: 'Czechy' },
    'Côte d\'Ivoire': { flag: '🇨🇮', name: 'WKS' },
    'Ivory Coast': { flag: '🇨🇮', name: 'WKS' },
    'Wybrzeże Kości Słoniowej': { flag: '🇨🇮', name: 'WKS' },
    'Denmark': { flag: '🇩🇰', name: 'Dania' },
    'Dania': { flag: '🇩🇰', name: 'Dania' },
    'Djibouti': { flag: '🇩🇯', name: 'Dżibuti' },
    'Dominica': { flag: '🇩🇲', name: 'Dominika' },
    'Dominican Republic': { flag: '🇩🇴', name: 'Dominikana' },
    'DPR Korea': { flag: '🇰🇵', name: 'Korea Północna' },
    'Ecuador': { flag: '🇪🇨', name: 'Ekwador' },
    'Egypt': { flag: '🇪🇬', name: 'Egipt' },
    'Egipt': { flag: '🇪🇬', name: 'Egipt' },
    'El Salvador': { flag: '🇸🇻', name: 'Salwador' },
    'England': { flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', name: 'Anglia' },
    'Anglia': { flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', name: 'Anglia' },
    'Equatorial Guinea': { flag: '🇬🇶', name: 'Gwinea Równikowa' },
    'Eritrea': { flag: '🇪🇷', name: 'Erytrea' },
    'Estonia': { flag: '🇪🇪', name: 'Estonia' },
    'Eswatini': { flag: '🇸🇿', name: 'Eswatini' },
    'Ethiopia': { flag: '🇪🇹', name: 'Etiopia' },
    'Faroe Islands': { flag: '🇫🇴', name: 'Wyspy Owcze' },
    'Fiji': { flag: '🇫🇯', name: 'Fidżi' },
    'Finland': { flag: '🇫🇮', name: 'Finlandia' },
    'Finlandia': { flag: '🇫🇮', name: 'Finlandia' },
    'France': { flag: '🇫🇷', name: 'Francja' },
    'Francja': { flag: '🇫🇷', name: 'Francja' },
    'French Guiana': { flag: '🇬🇫', name: 'Gujana Francuska' },
    'Gabon': { flag: '🇬🇦', name: 'Gabon' },
    'Gambia': { flag: '🇬🇲', name: 'Gambia' },
    'Georgia': { flag: '🇬🇪', name: 'Gruzja Gruzja' },
    'Germany': { flag: '🇩🇪', name: 'Niemcy' },
    'Niemcy': { flag: '🇩🇪', name: 'Niemcy' },
    'Ghana': { flag: '🇬🇭', name: 'Ghana' },
    'Gibraltar': { flag: '🇬🇮', name: 'Gibraltar' },
    'Greece': { flag: '🇬🇷', name: 'Grecja' },
    'Grecja': { flag: '🇬🇷', name: 'Grecja' },
    'Grenada': { flag: '🇬🇩', name: 'Grenada' },
    'Guadeloupe': { flag: '🇬🇵', name: 'Gwadelupa' },
    'Guam': { flag: '🇬🇺', name: 'Guam' },
    'Guatemala': { flag: '🇬🇹', name: 'Gwatemala' },
    'Guernsey': { flag: '🇬🇬', name: 'Guernsey' },
    'Guinea': { flag: '🇬🇳', name: 'Gwinea' },
    'Guinea-Bissau': { flag: '🇬🇼', name: 'Gwinea Bissau' },
    'Guyana': { flag: '🇬🇾', name: 'Gujana' },
    'Haiti': { flag: '🇭🇹', name: 'Haiti' },
    'Honduras': { flag: '🇭🇳', name: 'Honduras' },
    'Hong Kong': { flag: '🇭🇰', name: 'Hongkong' },
    'Hungary': { flag: '🇭🇺', name: 'Węgry' },
    'Węgry': { flag: '🇭🇺', name: 'Węgry' },
    'Iceland': { flag: '🇮🇸', name: 'Islandia' },
    'India': { flag: '🇮🇳', name: 'Indie' },
    'Indonesia': { flag: '🇮🇩', name: 'Indonezja' },
    'Iran': { flag: '🇮🇷', name: 'Iran' },
    'Iraq': { flag: '🇮🇶', name: 'Irak' },
    'Israel': { flag: '🇮🇱', name: 'Izrael' },
    'Italy': { flag: '🇮🇹', name: 'Włochy' },
    'Włochy': { flag: '🇮🇹', name: 'Włochy' },
    'Jamaica': { flag: '🇯🇲', name: 'Jamajka' },
    'Japan': { flag: '🇯🇵', name: 'Japonia' },
    'Japonia': { flag: '🇯🇵', name: 'Japonia' },
    'Jersey': { flag: '🇯🇪', name: 'Jersey' },
    'Jordan': { flag: '🇯🇴', name: 'Jordania' },
    'Kazakhstan': { flag: '🇰🇿', name: 'Kazachstan' },
    'Kenya': { flag: '🇰🇪', name: 'Kenia' },
    'Kosovo': { flag: '🇽🇰', name: 'Kosowo' },
    'Kuwait': { flag: '🇰🇼', name: 'Kuwejt' },
    'Kyrgyz Republic': { flag: '🇰🇬', name: 'Kirgistan' },
    'Laos': { flag: '🇱🇦', name: 'Laos' },
    'Latvia': { flag: '🇱🇻', name: 'Łotwa' },
    'Lebanon': { flag: '🇱🇧', name: 'Liban' },
    'Lesotho': { flag: '🇱🇸', name: 'Lesotho' },
    'Liberia': { flag: '🇱🇷', name: 'Liberia' },
    'Libya': { flag: '🇱🇾', name: 'Libia' },
    'Liechtenstein': { flag: '🇱🇮', name: 'Liechtenstein' },
    'Lithuania': { flag: '🇱🇹', name: 'Litwa' },
    'Luxembourg': { flag: '🇱🇺', name: 'Luksemburg' },
    'Macau': { flag: '🇲🇴', name: 'Makau' },
    'Madagascar': { flag: '🇲🇬', name: 'Madagaskar' },
    'Malawi': { flag: '🇲🇼', name: 'Malawi' },
    'Malaysia': { flag: '🇲🇾', name: 'Malezja' },
    'Maldives': { flag: '🇲🇻', name: 'Malediwy' },
    'Mali': { flag: '🇲🇱', name: 'Mali' },
    'Malta': { flag: '🇲🇹', name: 'Malta' },
    'Martinique': { flag: '🇲🇶', name: 'Martynika' },
    'Mauritania': { flag: '🇲🇷', name: 'Mauretania' },
    'Mauritius': { flag: '🇲🇺', name: 'Mauritius' },
    'Mexico': { flag: '🇲🇽', name: 'Meksyk' },
    'Meksyk': { flag: '🇲🇽', name: 'Meksyk' },
    'Moldova': { flag: '🇲🇩', name: 'Mołdawia' },
    'Mongolia': { flag: '🇲🇳', name: 'Mongolia' },
    'Montenegro': { flag: '🇲🇪', name: 'Czarnogóra' },
    'Montserrat': { flag: '🇲🇸', name: 'Montserrat' },
    'Morocco': { flag: '🇲🇦', name: 'Maroko' },
    'Maroko': { flag: '🇲🇦', name: 'Maroko' },
    'Mozambique': { flag: '🇲🇿', name: 'Mozambik' },
    'Myanmar': { flag: '🇲🇲', name: 'Mjanma' },
    'Namibia': { flag: '🇳🇦', name: 'Namibia' },
    'Nepal': { flag: '🇳🇵', name: 'Nepal' },
    'Netherlands': { flag: '🇳🇱', name: 'Holandia' },
    'Holandia': { flag: '🇳🇱', name: 'Holandia' },
    'New Caledonia': { flag: '🇳🇨', name: 'Nowa Kaledonia' },
    'New Zealand': { flag: '🇳🇿', name: 'Nowa Zelandia' },
    'Nicaragua': { flag: '🇳🇮', name: 'Nikaragua' },
    'Niger': { flag: '🇳🇪', name: 'Niger' },
    'Nigeria': { flag: '🇳🇬', name: 'Nigeria' },
    'North Macedonia': { flag: '🇲🇰', name: 'Macedonia Płn.' },
    'Northern Ireland': { flag: '🏴󠁧󠁢󠁮󠁩󠁲󠁿', name: 'Irlandia Płn.' },
    'Norway': { flag: '🇳🇴', name: 'Norwegia' },
    'Norwegia': { flag: '🇳🇴', name: 'Norwegia' },
    'Oman': { flag: '🇴🇲', name: 'Oman' },
    'Pakistan': { flag: '🇵🇰', name: 'Pakistan' },
    'Palestine': { flag: '🇵🇸', name: 'Palestyna' },
    'Panama': { flag: '🇵🇦', name: 'Panama' },
    'Papua New Guinea': { flag: '🇵🇬', name: 'Papua-Nowa Gwinea' },
    'Paraguay': { flag: '🇵🇾', name: 'Paragwaj' },
    'Peru': { flag: '🇵🇪', name: 'Peru' },
    'Philippines': { flag: '🇵🇭', name: 'Filipiny' },
    'Poland': { flag: '🇵🇱', name: 'Polska' },
    'Polska': { flag: '🇵🇱', name: 'Polska' },
    'Portugal': { flag: '🇵🇹', name: 'Portugalia' },
    'Portugalia': { flag: '🇵🇹', name: 'Portugalia' },
    'Puerto Rico': { flag: '🇵🇷', name: 'Portoryko' },
    'Qatar': { flag: '🇶🇦', name: 'Katar' },
    'Republic of Ireland': { flag: '🇮🇪', name: 'Irlandia' },
    'Irlandia': { flag: '🇮🇪', name: 'Irlandia' },
    'Republic of Korea': { flag: '🇰🇷', name: 'Korea Południowa' },
    'South Korea': { flag: '🇰🇷', name: 'Korea Płd.' },
    'Romania': { flag: '🇷🇴', name: 'Rumunia' },
    'Russia': { flag: '🇷🇺', name: 'Rosja' },
    'Rosja': { flag: '🇷🇺', name: 'Rosja' },
    'Rwanda': { flag: '🇷🇼', name: 'Rwanda' },
    'Saint Kitts and Nevis': { flag: '🇰🇳', name: 'Saint Kitts i Nevis' },
    'Saint Lucia': { flag: '🇱🇨', name: 'Saint Lucia' },
    'Saint Vincent and the Grenadines': { flag: '🇻🇨', name: 'St. Vincent i Grenadyny' },
    'St Vincent i Grenad.': { flag: '🇻🇨', name: 'St. Vincent i Grenadyny' },
    'Samoa': { flag: '🇼🇸', name: 'Samoa' },
    'San Marino': { flag: '🇸🇲', name: 'San Marino' },
    'São Tomé and Príncipe': { flag: '🇸🇹', name: 'Wyspy Św. Tomasza' },
    'Saudi Arabia': { flag: '🇸🇦', name: 'Arabia Saudyjska' },
    'Scotland': { flag: '🏴󠁧󠁢󠁳󠁣󠁴󠁿', name: 'Szkocja' },
    'Szkocja': { flag: '🏴󠁧󠁢󠁳󠁣󠁴󠁿', name: 'Szkocja' },
    'Senegal': { flag: '🇸🇳', name: 'Senegal' },
    'Serbia': { flag: '🇷🇸', name: 'Serbia' },
    'Seychelles': { flag: '🇸🇨', name: 'Seszele' },
    'Sierra Leone': { flag: '🇸🇱', name: 'Sierra Leone' },
    'Singapore': { flag: '🇸🇬', name: 'Singapur' },
    'Slovakia': { flag: '🇸🇰', name: 'Słowacja' },
    'Słowacja': { flag: '🇸🇰', name: 'Słowacja' },
    'Slovenia': { flag: '🇸🇮', name: 'Słowenia' },
    'Słowenia': { flag: '🇸🇮', name: 'Słowenia' },
    'Solomon Islands': { flag: '🇸🇧', name: 'Wyspy Salomona' },
    'Somalia': { flag: '🇸🇴', name: 'Somalia' },
    'South Africa': { flag: '🇿🇦', name: 'RPA' },
    'RPA': { flag: '🇿🇦', name: 'RPA' },
    'South Sudan': { flag: '🇸🇸', name: 'Sudan Płd.' },
    'Spain': { flag: '🇪🇸', name: 'Hiszpania' },
    'Hiszpania': { flag: '🇪🇸', name: 'Hiszpania' },
    'Sri Lanka': { flag: '🇱🇰', name: 'Sri Lanka' },
    'Sudan': { flag: '🇸🇩', name: 'Sudan' },
    'Suriname': { flag: '🇸🇷', name: 'Surinam' },
    'Sweden': { flag: '🇸🇪', name: 'Szwecja' },
    'Szwecja': { flag: '🇸🇪', name: 'Szwecja' },
    'Switzerland': { flag: '🇨🇭', name: 'Szwajcaria' },
    'Szwajcaria': { flag: '🇨🇭', name: 'Szwajcaria' },
    'Syria': { flag: '🇸🇾', name: 'Syria' },
    'Tahiti': { flag: '🇵🇫', name: 'Tahiti' },
    'Tajikistan': { flag: '🇹🇯', name: 'Tadżykistan' },
    'Tanzania': { flag: '🇹🇿', name: 'Tanzania' },
    'Thailand': { flag: '🇹🇭', name: 'Tajlandia' },
    'Timor-Leste': { flag: '🇹🇱', name: 'Timor Wschodni' },
    'Togo': { flag: '🇹🇬', name: 'Togo' },
    'Tonga': { flag: '🇹🇴', name: 'Tonga' },
    'Trinidad and Tobago': { flag: '🇹🇹', name: 'Trynidad i Tobago' },
    'Tunisia': { flag: '🇹🇳', name: 'Tunezja' },
    'Turkey': { flag: '🇹🇷', name: 'Turcja' },
    'Turcja': { flag: '🇹🇷', name: 'Turcja' },
    'Turkmenistan': { flag: '🇹🇲', name: 'Turkmenistan' },
    'Turks and Caicos Islands': { flag: '🇹🇨', name: 'Turks i Caicos' },
    'US Virgin Islands': { flag: '🇻🇮', name: 'Wyspy Dziewicze USA' },
    'Uganda': { flag: '🇺🇬', name: 'Uganda' },
    'Ukraine': { flag: '🇺🇦', name: 'Ukraina' },
    'Ukraina': { flag: '🇺🇦', name: 'Ukraina' },
    'United Arab Emirates': { flag: '🇦🇪', name: 'ZEA' },
    'ZEA': { flag: '🇦🇪', name: 'ZEA' },
    'United States': { flag: '🇺🇸', name: 'USA' },
    'USA': { flag: '🇺🇸', name: 'USA' },
    'Uruguay': { flag: '🇺🇾', name: 'Urugwaj' },
    'Urugwaj': { flag: '🇺🇾', name: 'Urugwaj' },
    'Uzbekistan': { flag: '🇺🇿', name: 'Uzbekistan' },
    'Vanuatu': { flag: '🇻🇺', name: 'Vanuatu' },
    'Venezuela': { flag: '🇻🇪', name: 'Wenezuela' },
    'Vietnam': { flag: '🇻🇳', name: 'Wietnam' },
    'Wales': { flag: '🏴󠁧󠁢󠁷󠁬󠁳󠁿', name: 'Walia' },
    'Walia': { flag: '🏴󠁧󠁢󠁷󠁬󠁳󠁿', name: 'Walia' },
    'Yemen': { flag: '🇾🇪', name: 'Jemen' },
    'Zambia': { flag: '🇿🇲', name: 'Zambia' },
    'Zimbabwe': { flag: '🇿🇼', name: 'Zimbabwe' }
};

export function getNationalityBadge(nat) {
    if (!nat) return { flag: '🌐', name: 'Nieznana' };
    const n = String(nat).trim();
    if (NATIONALITY_FLAG_MAP[n]) {
        return NATIONALITY_FLAG_MAP[n];
    }
    const clean = n.replace(/_/g, ' ');
    if (NATIONALITY_FLAG_MAP[clean]) {
        return NATIONALITY_FLAG_MAP[clean];
    }
    return { flag: '🌍', name: n };
}

export function getCountryFlag(nat) {
    return getNationalityBadge(nat).flag;
}

export function getAttributeLabel(key) {
    const labels = {
        'pace': 'Tempo (PAC)',
        'shooting': 'Strzały (SHO)',
        'passing': 'Podania (PAS)',
        'dribbling': 'Drybling (DRI)',
        'defending': 'Obrona (DEF)',
        'physical': 'Fizyczność (PHY)',
        'heading': 'Gra Głową (HEA)',
        'diving': 'Parady (DIV)',
        'handling': 'Chwyt (HAN)',
        'kicking': 'Wykopy (KIC)',
        'reflexes': 'Refleks (REF)',
        'speed': 'Szybkość (SPD)',
        'positioning': 'Ustawianie (POS)',
        'goalkeeping_score': 'Ogólna Obrona (GK)'
    };
    return labels[key] || key.toUpperCase();
}

export function getAttributeTier(val) {
    const num = Number(val) || 0;
    if (num >= 88) return { label: 'Elitarny', className: 'tier-elite' };
    if (num >= 78) return { label: 'Świetny', className: 'tier-great' };
    if (num >= 68) return { label: 'Dobry', className: 'tier-good' };
    return { label: 'Solidny', className: 'tier-avg' };
}



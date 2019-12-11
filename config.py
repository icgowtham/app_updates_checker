"""Configuration file."""
BASE_PLAY_STORE_URL = 'https://play.google.com/store/apps/details?id={id}'
BASE_APP_STORE_URL = 'http://itunes.apple.com/{cc}/app/{id}?mt=8'

APP_STORE_COUNTRY_CODES = {'in', 'us'}
DATA_STORE = 'data/apps_last_updated.json'
COUNT_TRACKER = 'data/updates_counter.json'

APPS_TO_ID_MAP = {
    'youtube': {
        'play_store': 'com.google.android.youtube&hl=en_IN',
        'app_store': 'id544007664'
    },
    'facebook': {
        'play_store': 'com.facebook.katana&hl=en_IN',
        'app_store': 'id284882215'
    },
    'instagram': {
        'play_store': 'com.instagram.android&hl=en_IN',
        'app_store': 'id389801252'
    },
    'whatsapp': {
        'play_store': 'com.whatsapp&hl=en_IN',
        'app_store': 'id310633997'
    },
    'skype': {
        'play_store': 'com.skype.raider&hl=en_IN',
        'app_store': 'id304878510'
    },
    'google-maps': {
        'play_store': 'com.google.android.apps.maps&hl=en_IN',
        'app_store': 'id585027354'
    },
    'gmail': {
        'play_store': 'com.google.android.gm&hl=en_IN',
        'app_store': 'id422689480'
    },
    'netflix': {
        'play_store': 'com.netflix.mediaclient&hl=en_IN',
        'app_store': 'id363590051'
    },
    'amazon-prime-music': {
        'play_store': 'com.amazon.mp3&hl=en_IN',
        'app_store': 'id510855668'
    },
    'amazon-prime-video': {
        'play_store': 'com.amazon.avod.thirdpartyclient&hl=en_IN',
        'app_store': 'id545519333'
    },
    'tiktok': {
        'play_store': 'com.zhiliaoapp.musically',
        'app_store': 'id835599320'
    },
    'twitter': {
        'play_store': 'com.twitter.android&hl=en_IN',
        'app_store': 'id333903271'
    },
    'amazon': {
        'play_store': 'com.amazon.avod.thirdpartyclient&hl=en_IN',
        'app_store': 'id545519333'
    },
    'pubg': {
        'play_store': 'com.tencent.ig&hl=en_IN',
        'app_store': 'id1330123889'
    },
}

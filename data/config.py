from environs import Env

env = Env()

env.read_env()

BOT_TOKEN = env.str('BOT_TOKEN')
CRYPTO_PAY_TOKEN = env.str('CRYPTO_PAY_TOKEN')

photo_1 = 'AgACAgIAAxkBAAEBiyljquz5De27FfbiYU3AE7Z2KQGidgACTcIxG0RiWUn6y87G5Z1FtgEAAwIAA3kAAywE'

ADMINS_ID = [5371593117, 5683905582]
GROUP_ID = '@Advanced_Info'

sub_tariffs = {
    '🌎 VINTED': {
        24: (2.5, 150),
        72: (5, 300),
        168: (10, 600),
        360: (20, 1190),
        744: (40, 2220)
    },
    '🇪🇺 WALLAPOP': {
        24: (2.5, 150),
        72: (5, 300),
        168: (10, 600),
        360: (20, 1190),
        744: (40, 2220)
    },
    '🇭🇺 JOFOGAS': {
        24: (2.5, 150),
        72: (5, 300),
        168: (10, 600),
        360: (20, 1190),
        744: (40, 2220)
    }
}

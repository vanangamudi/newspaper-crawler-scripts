import config

import logging
logging.basicConfig(format=config.CONFIG.FORMAT_STRING)
log = logging.getLogger(__name__)
log.setLevel(config.CONFIG.LOGLEVEL)



class AliasBase:
    MONTHS = [
        'january'
        , 'february'
        , 'march'
        , 'april'
        , 'may'
        , 'june'
        , 'july'
        , 'august'
        , 'september'
        , 'october'
        , 'november'
        , 'december'
    ]

    def __init__(self):
        self.ALIASES = dict([ (v, k) for k, v in  enumerate(['00'] + self.MONTHS)])
    
    def __getitem__(self, key):
        if type(key) == str:
            try:
                return '{:02d}'.format(self.ALIASES[key])
            except:
                log.exception('==========')
                return '{:02d}'.format(self.ALIASES['SPECIAL'])
        else: #type(key) == int:
            return self.MONTHS[key]
        
class GregorianMonthInTamilAlias(AliasBase):
    MONTHS = [
        'ஜனவரி'
        ,'பிப்ரவரி'
        ,'மார்ச்'
        ,'ஏப்ரல்'
        ,'மே'
        ,'ஜூன்'
        ,'ஜூலை'
        ,'ஆகஸ்ட்'
        ,'செப்டம்பர்'
        ,'அக்டோபர்'
        ,'நவம்பர்'
        ,'டிசம்பர்'
    ]

    
class GregorianMonthInEnglishShort(AliasBase):
    MONTHS = [
        'jan'
        , 'feb'
        , 'mar'
        , 'apr'
        , 'may'
        , 'jun'
        , 'jul'
        , 'aug'
        , 'sep'
        , 'oct'
        , 'nov'
        , 'dec'
    ]

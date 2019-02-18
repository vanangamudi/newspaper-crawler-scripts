
class AliasBase:
    MONTHS = ['SPECIAL'
              , 'january'
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
        self.ALIASES = dict([ (v, k) for k, v in  enumerate(self.MONTHS)])
    
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
    MONTHS = ['SPECIAL'
              ,'ஜனவரி'
              ,'பிப்ரவரி'
              ,'மார்ச்'
              ,'ஏப்ரல்'
              ,'மே'
              ,'ஜூன்'
              ,'ஜூலை'
              ,'ஆகஸ்ட'
              ,'செப்டம்பர்'
              ,'அக்டோபர்'
              ,'நவம்பர்'
              ,'டிசம்பர்'
    ]

    
class GregorianMonthInEnglishShort(AliasBase):
    MONTHS = ['SPECIAL'
              , 'jan'
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

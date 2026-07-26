# core/db_router.py

class SegnalazioniRouter:
    def db_for_read(self, model, **hints):
        # ✅ Aggiungi 'rifiuti' oltre a 'core'
        if model._meta.app_label in ['core', 'rifiuti']:
            return 'segnalazioni_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ['core', 'rifiuti']:
            return 'segnalazioni_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._state.db == obj2._state.db:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ['core', 'rifiuti']:
            return db == 'segnalazioni_db'
        return db == 'default'


#class SegnalazioniRouter:
#    """
#    Un router per indirizzare le operazioni di database sulle segnalazioni.
#    """
#
#    def db_for_read(self, model, **hints):
#        """ Indica quale DB usare per le letture """
#        if model._meta.app_label == 'core':
#            return 'segnalazioni_db'
#        return 'default'
#
#    def db_for_write(self, model, **hints):
#        """ Indica quale DB usare per le scritture """
#        if model._meta.app_label == 'core':
#            return 'segnalazioni_db'
#        return 'default'
#
#    def allow_relation(self, obj1, obj2, **hints):
#        """ Permette relazioni solo all'interno dello stesso DB """
#        if obj1._state.db == obj2._state.db:
#            return True
#        return None
#
#    def allow_migrate(self, db, app_label, model_name=None, **hints):
#        """ Gestisce le migrazioni: evita che le tabelle delle segnalazioni finiscano nel DB sbagliato """
#        if app_label == 'core':
#            return db == 'segnalazioni_db'
#        return db == 'default'
#

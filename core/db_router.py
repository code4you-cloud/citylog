# core/db_router.py
class SegnalazioniRouter:
    def db_for_read(self, model, **hints):
        # Tutte le app che devono andare sul database legacy
        legacy_apps = ['core', 'rifiuti', 'testers']

        if model._meta.app_label in legacy_apps:
            return 'segnalazioni_db'
        return 'default'

    def db_for_write(self, model, **hints):
        legacy_apps = ['core', 'rifiuti', 'testers', 'report']

        if model._meta.app_label in legacy_apps:
            return 'segnalazioni_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Permetti relazioni se sono nello stesso database
        if obj1._state.db == obj2._state.db:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Le migrazioni delle app legacy vanno su segnalazioni_db
        legacy_apps = ['core', 'rifiuti', 'testers']

        if app_label in legacy_apps:
            return db == 'segnalazioni_db'
        # Per le altre app (Django di sistema) vanno su default
        return db == 'default'

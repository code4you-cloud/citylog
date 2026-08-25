# core/db_router.py
# core/db_router.py
class SegnalazioniRouter:
    legacy_apps = ['core', 'rifiuti', 'testers', 'report', 'stripe_payments']  # 👈 AGGIUNGI

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.legacy_apps:
            return 'segnalazioni_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.legacy_apps:
            return 'segnalazioni_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Permetti relazioni tra report e Users (core)
        if obj1._meta.app_label == 'report' and obj2._meta.app_label == 'core':
            return True
        if obj2._meta.app_label == 'report' and obj1._meta.app_label == 'core':
            return True

        if obj1._state.db == obj2._state.db:
            return True
        return None

    def allow_relation_(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'stripe_payments' and obj2._meta.app_label == 'auth':
            return True
        if obj2._meta.app_label == 'stripe_payments' and obj1._meta.app_label == 'auth':
            return True
        if obj1._state.db == obj2._state.db:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # 👈 USA LA STESSA LISTA
        if app_label in self.legacy_apps:
            return db == 'segnalazioni_db'
        return db == 'default'

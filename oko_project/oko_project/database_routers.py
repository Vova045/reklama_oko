class DatabaseRouter:
    def db_for_read(self, model, **hints):
        """Указываем, из какой базы данных читать"""
        if model._meta.app_label == 'my_app':  # Замените 'my_app' на имя вашего приложения
            return 'sqlite'  # SQLite для чтения
        return 'default'  # MySQL для чтения по умолчанию

    def db_for_write(self, model, **hints):
        """Указываем, в какую базу данных писать"""
        if model._meta.app_label == 'my_app':  # Замените 'my_app' на имя вашего приложения
            return 'sqlite'  # SQLite для записи
        return 'default'  # MySQL для записи по умолчанию

    def allow_relation(self, obj1, obj2, **hints):
        """Разрешаем связи между объектами из разных баз данных"""
        db_list = ('default', 'sqlite')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Определяем, куда применять миграции"""
        if app_label == 'my_app':  # Замените 'my_app' на имя вашего приложения
            return db == 'sqlite'
        return db == 'default'

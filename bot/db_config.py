databaseUrl = ''


class db_postgres_url_parsing:

    @staticmethod
    def db_url_parsing(self, url):
        global databaseUrl
        databaseUrl = url
        databaseUrl = databaseUrl[11:]  # getting rid of the postgres part

        engine = 'django.db.backends.postgresql'
        user = self.assist_function(databaseUrl, ':')
        password = self.assist_function(databaseUrl, '@')
        hostname = self.assist_function(databaseUrl, ":")
        port = self.assist_function(databaseUrl, "/")
        database_name = databaseUrl
        database = {
            'ENGINE': engine,
            'HOST': hostname,
            'USER': user,
            'NAME': database_name,
            'PASSWORD': password,
            'PORT': port
        }
        return database

    #  assist function to take care of the part
    @classmethod
    def assist_function(cls, url, checker):
        counter = 0
        variable = ''
        for eachChar in url:
            counter += 1
            if eachChar != checker:
                variable += eachChar
            else:
                break
        global databaseUrl
        databaseUrl = url[counter:]
        return variable

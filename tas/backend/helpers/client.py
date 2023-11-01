import cherrypy


def get_client_ip():
    if 'X-Forwarded-For' in cherrypy.request.headers:  # needs to be used in case haproxy is used in front of TAS
        return cherrypy.request.headers['X-Forwarded-For']
    else:
        return cherrypy.request.remote.ip

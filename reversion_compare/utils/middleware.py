"""
Print the query log to standard out.

Useful for optimizing database calls.

Insipired by the method at: <http://www.djangosnippets.org/snippets/344/>
"""

class QueryLogMiddleware:

    def process_response(self, request, response):
        from django.conf import settings
        from django.db import connection

        if settings.DEBUG:
            queries = {}
            for query in connection.queries:
                sql = query["sql"]
                queries.setdefault(sql, 0)
                queries[sql] += 1
            duplicates = sum([count - 1 for count in list(queries.values())])
            print("------------------------------------------------------")
            print("Total Queries:     %s" % len(queries))
            print("Duplicate Queries: %s" % duplicates)
            print()
            for query, count in list(queries.items()):
                print("%s x %s" % (count, query))
            print("------------------------------------------------------")
        return response


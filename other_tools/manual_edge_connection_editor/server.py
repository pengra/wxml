import http.server
import socketserver
import networkx

PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler


try:
    nx_path = sys.argv[1]
except:
    nx_path = "../../dnx/WA.dnx"

dnx_file = networkx.read_gpickle(nx_path)
# REQUIREMENTS:
# input box to highlight selected precinct with rid
# show the selected precinct (rid) connections
# ability to add and remove

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()

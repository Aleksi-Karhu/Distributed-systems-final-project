import sys
import requests
import multiprocessing
from xmlrpc.server import SimpleXMLRPCServer

# Sources:
# https://www.mediawiki.org/wiki/API:Info
# https://docs.python.org/3/library/multiprocessing.html#managers
# https://github.com/rklabs/WikiRacer/blob/master/wikiracer.py
# https://github.com/stong1108/WikiRacer/blob/master/wikiracer_threaded.py
# https://www.kite.com/python/answers/how-to-check-if-a-list-contains-a-substring-in-python
# https://stackoverflow.com/questions/5188792/how-to-check-a-string-for-specific-characters


# Define variable for the wikipedia API 
WIKIURL = "https://fi.wikipedia.org/w/api.php"


# Function for fetching all links inside of a page
def getLinks(link):
    try:
        # Create session for request
        S = requests.Session()

        # Create list to store links in
        linkList = []

        # Define parameters for query, set the number of links fetched to max
        PARAMS = {
            "action": "query",
            "format": "json",
            "titles": link,
            "prop": "links",
            "pllimit": "max"
        }

        # Make request
        R = S.get(url=WIKIURL, params=PARAMS)

        # Store data in json format
        DATA = R.json()

        # Navigate the json structure to access the page/link titles
        PAGES = DATA["query"]["pages"]


        if (len(PAGES) == 1):
            for k, v in PAGES.items():
                for l in v["links"]:
                    # Filter out all special links that inlude ":" for example Category: 
                    # Works with both Finnish and English wikipedia pages
                    if (l["title"].find(":") == -1):
                    
                        # Append the links to the list
                        linkList.append(l["title"])        
        
            # Return ready list
            print(len(linkList))
            return linkList
    except Exception as e:
        return linkList


# Function that checks that the links provided by the user are valid
def checkLink(link): 
    try:
        # Create session for request
        S = requests.Session()

        # Define parameters for query, set the number of links fetched to 1
        # Makes sure that:
        # 1) the page exists
        # 2) the page has atleast 1 valid link from which to navigate from 
        PARAMS = {
            "action": "query",
            "format": "json",
            "titles": link,
            "prop": "links",
            "pllimit": "1"
        }

        # Make request
        R = S.get(url=WIKIURL, params=PARAMS)

        # Store data in json format
        DATA = R.json()

        # Navigate the json structure to access the page/link titles
        PAGES = DATA["query"]["pages"]     
        for k, v in PAGES.items():
            for l in v["links"]:

                # Checks that if there is a valid link
                if len(l) != 2:        
                    return False
                else:
                    return True
    except Exception as e:
        print(e)
        return False


# Function that checks that is a link the ending page 
def addToPath(path, node, link, target): 
    try:  
        # Checks if the link is the ending page
        if(link == target):  

            # If yes return the full path
            return path[node] + [link]

        # Checks if the link is the current page that the program is inspecting
        if (link != node): 

            # Otherwise we check if the element is already queued and all reoccuring nodes are dismissed
            if (link not in path): 
                # Create a new branch for the tree and append the link to it
                path[link] = path[node] + [link] 
                return link
            
    except Exception as e:
        print(e)


# Function that oraganizes the crawling of the wikipedia pages
def crawlPage(start, end):
    try:  
        # Dictionary for maintaining the path and branches      
        path = multiprocessing.Manager().dict()

        # Sets the starting link as the root
        path[start] = [start]

        # Lists for maintaining the links of a page and the master queue for the bfs algorithm
        pageLinks = []
        linkQueue = []

        # Set the starting link as the first item
        linkQueue.append(start)
        while True:

            # Delete the first item of the queue and set it to a variable
            node = linkQueue.pop(0)          

            # Call a function to receive the links for that page
            pageLinks = getLinks(node)   

            # Check if there are links in the page
            processCount = len(pageLinks)
            if (processCount == 0):

                # If not then queue the next item and get its links
                node = linkQueue.pop(0)
                pageLinks = getLinks(node)           
                processCount = len(pageLinks)
            else:

                # Otherwise create a new pool of workers(Threads)
                # Max number of workers is the number of links on a page
                # In reality this is limited by the number of threads in the servers CPU. In my case 32. The theoretical maximum is 500 (limit of links from API)
                # On a actual server the performance is increased as number of CPUs is higher
                pool = multiprocessing.pool.ThreadPool(processes=processCount) 

                # For every link sets a worker to call the addToPath function 
                results = [pool.apply(addToPath, args=(path, node, link, end)) for link in pageLinks]  

                # Terminates the workers  
                pool.terminate()

                # Checks that is there a list object in the processed links 
                for r in results:
                    if type(r) == list: 

                        # If yes then returns the path to the client
                        return r
                    else:

                        # Otherwise queues the links to the bfs master queue
                        linkQueue.append(r)
                    
        print("No path found.")

    except Exception as e:
        print(e)
    

if __name__ == "__main__":

    # Creating server
    server = SimpleXMLRPCServer(("localhost", 8000))

    # Registering functions for the client to use
    server.register_function(checkLink)
    server.register_function(crawlPage)

    # Run server
    try:
        print("Server listening...")
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
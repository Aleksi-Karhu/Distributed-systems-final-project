import xmlrpc.client
import time

# Sources:
# https://www.mediawiki.org/wiki/API:Info
# https://docs.python.org/3/library/multiprocessing.html#managers
# https://github.com/rklabs/WikiRacer/blob/master/wikiracer.py
# https://github.com/stong1108/WikiRacer/blob/master/wikiracer_threaded.py
# https://www.kite.com/python/answers/how-to-check-if-a-list-contains-a-substring-in-python
# https://stackoverflow.com/questions/5188792/how-to-check-a-string-for-specific-characters

#Define localhost as the proxy
proxy = xmlrpc.client.ServerProxy("http://localhost:8000")

#Main function of the client
def main():
    try:
        print("Welcome to the Wikipedia game!")     

        # Prompts the user for a starting page
        while True:
            start = input("Enter starting page: ")

            # Checks for empty strings
            # Calls the server to check the validity of the link
            if (start.strip() == "" or proxy.checkLink(start) != True):
                print("Invalid link. Please provide a correct Wikipedia page")
            else: 
                break

        # Same for the ending page
        while True:
            end = input("Enter ending page: ")
            if (end.strip() == "" or proxy.checkLink(end) != True):
                print("Invalid link. Please provide a correct Wikipedia page")
            else: 
                break

        print("\nSearching for the shortest path...")

        # Gets the timestamp for the start of the query
        startTime = time.time()    

        # Calls the server and starts the wikicrawler
        path = proxy.crawlPage(start, end)

        # Gets the timestamp for the end of the query and the total time
        endTime = time.time()
        searchTime = endTime - startTime

        # Prints the results and path
        print("\nResult found!\n")
        print("Path:")
        for result in path:
            print(result)
        print(f"\nTime for the search took {round(searchTime, 1)} seconds\n")

    except Exception as e:
        print("An error occured!")


if __name__ == "__main__":
    main()
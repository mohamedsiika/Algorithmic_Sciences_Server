import socket
import threading
import timeit
import pytest
from datetime import datetime

class Server:

    def __init__(self):
        """
        Server initialization: the server is running on the local host and port 5050
        """
        self.port = 5050
        self.cache=None
        self.IP=socket.gethostbyname(socket.gethostname()) #gets the ip server
        self.ADDR=('localhost',self.port)
        self.server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  #tcp server socket
        self.server.bind(self.ADDR)  # binding the server
        self.Reread=None
        self.filepath=''
        self.read_file_path() # read file path from the config file
        self.read_reread_query() # read the reread_on_query flag from the config file
        self.file=open(self.filepath)
        self.preprocessing() #caching the text file
        print("server is starting on IP {} and port {}".format(self.ADDR[0],self.ADDR[1]))
    def read_file_path(self):
        """
        Reading the file path found in the config file by searching on the keyword 'linuxpath'
        :return: a string contains the file path
        """
        try:
            self.config = open('config.txt')   # open configuration file
        except IOError:
            print("Error : can't find Configuration file")

        while self.filepath=='':
            line=self.config.readline().split('=') #split each line by the '=' sign
            if line[0]=='linuxpath':
                self.filepath=line[1].replace('\n','')
        return self.filepath

    def read_reread_query(self):
        """
        Reading the Reread on query flag from the config file by searching on the REREAD_ON_QUERY kewyword
        :return: boolean which is the state of the flag
        """

        try:
            self.config = open('config.txt')
        except IOError:
            print("Error : can't find Configuration file")

        while True:
            line=self.config.readline().split('=')
            if line[0]=='REREAD_ON_QUERY':
                self.Reread=bool(int(line[1].replace('\n','')))
                break
        return self.Reread



    def query(self,msg,conn):
        """
         Searching for the text that the server received from the client in the text file we have,
         there are two cases
         1-Reread==True: so we will do a linear search to find that query
         2-Reread==False: we will check if the line in the cached dictionary
        :param msg: the query the user searching for
        :param conn: the connection established between the user and the server
        """

        self.read_reread_query()

        if self.Reread:   # first case
            self.file = open(self.filepath)
            lines=self.file.readlines()

            if msg in lines:
                conn.send("STRING EXISTS\n".encode()) #responds to the client

            else:
                conn.send("STRING NOT FOUND\n".encode()) # responds to the client
        else: # second case

           try:
                temp=self.cache[msg]  #check if the text in the cache dictionary
                conn.send("STRING EXISTS\n".encode()) #responds to the client
           except:
                conn.send("STRING NOT FOUND\n".encode()) #reponds to the client


    def handle_client(self,conn,addr):
        """
         here we receive the query from the client and decode it then we benchmark the speed of the response to the client
         then show the Debug message

        :param conn: connection established with the client
        :param addr: address of the client
        """
        msg=str(conn.recv(1024).decode()) #receive the query

        start_time=timeit.default_timer() #start time of the search method
        self.query(msg+'\n',conn)
        elapsed_time=timeit.default_timer()-start_time  #calculate the elapsed time to respond to the client

        log={"query":msg,"user_IP":addr[0],"start_time":datetime.fromtimestamp(start_time),"execution_time":elapsed_time}
        print("DEBUG",log)   # Debug message

        conn.close()

    def start(self):
        """
        start the server and wait for clients to connect on different threads

        """
        self.server.listen()
        while True:
            conn,addr=self.server.accept() #connection opened
            thread=threading.Thread(target=self.handle_client,args=(conn,addr)) #open thread for the client and execute the function handle client
            thread.start()

    def preprocessing(self):
        """
        caching the lines of the text file in a dictionary to be easier in searching for the query inside it
        :return:the dictionary
        """
        self.cache=dict.fromkeys(self.file.readlines(),1)
        return self.cache


class Testing(Server):
    """
    Testing class to check if the functions of the server class is working correctly
    """
    def test_preprocessing(self):
        assert len(self.preprocessing())==len(self.file.readlines())

    def test_read_file_path(self):
        assert self.read_file_path()=='root/200k.txt'

    def test_reread_on_query(self):
           assert self.read_reread_query()==True


if __name__ == "__main__":
    server=Server()
    server.start()

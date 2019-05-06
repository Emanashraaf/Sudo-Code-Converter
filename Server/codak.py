import pytesseract
import cv2
from PIL import Image
import matplotlib as plt
import numpy as np
import socket
import os
from _thread import *


# Extract text from image
#please check your path of tesseract.exe on your machine 
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
tessdata_dir_config = r'--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata"'

"""this function to extract text from the input image ,
   after resizing it and connvert it to grayscale ,
   then threshold it using binary thresholding and otsu ,
   then extract the text using tesseract """

def extract_text(img):
    img = cv2.resize(img,(1000,1000))
    img = np.array(img,np.uint8)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    val,binary = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(Image.fromarray(binary),lang='eng',config=tessdata_dir_config)
    
    #sudo.txt file will have the code from the input image
    f = open("sudo.txt","w+")
    f.write(text)
    f.close()
 
# Convert Sudo Code

# dictionaries to convert inputes to its equivalents in python 

key_word={"Display":"print","Promot":"input()","print":"print"}
string_operations={"add":"+","sub":"-","mul":"*","div":"/","mod":"%" ,"equal" : "=" , "greater_than" : ">" ,"less_than" : "<","greater_than_or_equal" : ">=",
                   "less_than_or_equal" : "=<" ,"not_equal":"!="}
operations = ["+" , "-" , "*" , "/"] 
key=["number","string","to","do"]

key_word={"Display":"print","Promot":"input()","print":"print"}
string_operations={"add":"+","sub":"-","mul":"*","div":"/","mod":"%" ,"equal" : "=" , "greater_than" : ">" ,"less_than" : "<","greater_than_or_equal" : ">=",
                   "less_than_or_equal" : "=<" ,"not_equal":"!="}
operations = ["+" , "-" , "*" , "/"] 
key=["number","string","to","do"]

# compiler function to python code
""" arguments -->
    input_ : this is the input file of sudocode resulted from preprocessing stage
    result : the output file which contains python code will be appear to the user and comiled
    exec_file : this file contains the code will send to the client from server in the background
    """
def compile_sudo (input_ , result, exec_file):
    indent = 0
    text = input_.readline().rstrip('\n')
    while text:        
        text_list = text.split()
        if ((text_list[0]) == ("endfor")) or ((text_list[0]) == ("endif")) :
            indent = indent - 1
            text = input_.readline().rstrip('\n')
            continue

        if ((text_list[0]) == ("else")) or ((text_list[0]) == ("elseif")) :
            indent = indent - 1
        
        #this is because the indents python take instead of brackets
        result.write("   " * indent)
        exec_file.write("   " * indent)
        print("   " * indent ,end = "")
 
        #Display use to print strings 
        if text_list[0] == "Display" :
            str1 = ' '.join(text_list[1:])
            print(key_word[text_list[0]],'("',str1,'")')
            result.write("%s ( '"'%s'"') \r\n" %(key_word[text_list[0]],str1))
            exec_file.write("f = open('out.txt','w+')\r\n")
            exec_file.write("   " * indent)
            exec_file.write("%s ('"'%s'"' , file = f ) \r\n" %(key_word[text_list[0]],str1))
            exec_file.write("   " * indent)
            exec_file.write("f.close()\r\n")
            exec_file.write("   " * indent)
            exec_file.write("f = open('out.txt','r+')\r\n")
            exec_file.write("   " * indent)
            exec_file.write("s = f.readline().rstrip('\\n ')\r\n")
            exec_file.write("   " * indent)
            exec_file.write("print(s)\r\n")
            exec_file.write("   " * indent)
            exec_file.write("c.send(bytes(s,'utf8'))\r\n")
            exec_file.write("   " * indent)
            exec_file.write("print(bytes(s,'utf8'))\r\n")
            exec_file.write("   " * indent)
            exec_file.write("ack=c.recv(1024)\r\n")
            exec_file.write("   " * indent)
            exec_file.write("f.truncate(0)\r\n")
            exec_file.write("   " * indent)
            exec_file.write("f.close()\r\n")
            
        #promot use to take input from user
        elif text_list[0] == "Promot" :
            result.write('print("Please Enter your input:")\r\n')
            exec_file.write("c.send(bytes('Please Enter your input:','utf8'))\r\n")
            exec_file.write("c.send(bytes('input','utf8'))\r\n")
            exec_file.write("ack=c.recv(1024)\r\n")
            exec_file.write("user_input=c.recv(1024).decode()\r\n")

            temp= key_word[text_list[0]]
            #this if when the user input interger number
            if(key[0] in text_list):

                text = input_.readline().rstrip('\n')
                text_list = text.split(" ")
                if text_list[0] == "Save" :
                    str1 = text_list[-1]
                    print(str1,"=int(",temp,")")
                    result.write("%s =int( %s )\r\n" %(str1,temp))
                    exec_file.write("%s =int( user_input )\r\n" %(str1))
                    
            #this if when the user input string
            else :
                if text_list[0] == "Save" :
                    str1 = text_list[-1]
                    print(str1,"=",temp)
                    result.write("%s = %s \r\n "%(str1,temp))
                    exec_file.write("%s = user_input \r\n "%(str1))

        #print use to print the output to the user in ui             
        elif text_list[0] == "print" :
            str1 = ' '.join(text_list[1:])
            print(key_word[text_list[0]],'(',str1,')')
            result.write("%s ( %s )\r\n"%(key_word[text_list[0]],str1))
            exec_file.write("f = open('out.txt','w+')\r\n")
            exec_file.write("   " * indent)
            exec_file.write("%s (%s  , file = f ) \r\n" %(key_word[text_list[0]],str1.lstrip()))
            exec_file.write("   " * indent)
            exec_file.write("f.close()\r\n")
            exec_file.write("   " * indent)
            exec_file.write("f = open('out.txt','r+')\r\n")
            exec_file.write("   " * indent)
            exec_file.write("s = f.readline().rstrip('\\n ')\r\n")
            exec_file.write("   " * indent)
            exec_file.write("print(s)\r\n")
            exec_file.write("   " * indent)
            exec_file.write("c.send(bytes(s,'utf8'))\r\n")
            exec_file.write("   " * indent)
            exec_file.write("print(bytes(s,'utf8'))\r\n")
            exec_file.write("   " * indent)
            exec_file.write("ack=c.recv(1024)\r\n")
            exec_file.write("   " * indent)
            exec_file.write("f.truncate(0)\r\n")
            exec_file.write("   " * indent)
            exec_file.write("f.close()\r\n")
        
        #the operation dictionary for equation statments
        elif([i for i in operations if i in text_list]):
            temp=' '.join(text_list)
            print(temp)
            result.write("%s\r\n"%(temp))
            exec_file.write("%s\r\n"%(temp))
        
        #initialize use to initialize lists with fixed size 100
        elif text_list[0] == "initialize" :
            print(text_list[1] , "= [0]*100")
            result.write("%s = [0]*100 \r\n"%(text_list[1]))
            exec_file.write("%s = [0]*100 \r\n"%(text_list[1]))

        #set use to initialize variables      
        elif text_list[0] == "set" :
            item = text_list.index(next(i for i in key if i in text_list))
            if(text_list[item]=="to"):
                print(numbers[text_list[item+1]])
                result.write("%s = %s \r\n"%(text_list[1] ,numbers[text_list[item+1]] ))
                exec_file.write("%s = %s\r\n"%(text_list[1] ,numbers[text_list[item+1]] ))

        #for loop in format of "for i in range(x,y):"
        elif text_list[0] == "for" :
            indent =  indent + 1    #increase the indent counter after for statement
            iterator = text_list[1]
            item = text_list.index(next(i for i in key if i in text_list))
            if(text_list[item]=="to"):
                print("for" , iterator ,"in range(",text_list[item-1],',',int(text_list[item+1])+1,'):')
                result.write("for %s in range (%s,%d) :\r\n" %( iterator ,(text_list[item-1]),(int(text_list[item+1])+1)))
                exec_file.write("for %s in range (%s,%d) :\r\n" %( iterator ,(text_list[item-1]),(int(text_list[item+1])+1)))
                
        #this is for if condition and support nested ifs inside it
        elif ((text_list[0]) == ("if")) or ((text_list[0]) == ("elseif")) or ((text_list[0]) == ("elif")) or ((text_list[0]) == ("while")) :
            
            indent =  indent + 1    #increase the indent counter after for statement
            #execlude to and is from input sudo statement
            if "is" in text_list:
                text_list.remove("is")
            if "to" in text_list:
                text_list.remove("to")
            # this to handle if the user want to write math operators in english words 
            if([i for i in string_operations if i in text_list]):
                item = next(i for i in text_list if i in string_operations)
                if item == "equal" :
                    text_list[text_list.index(item)] = string_operations[item]+string_operations[item]
                else :
                    text_list[text_list.index(item)] = string_operations[item]
            elif ("=" in text_list):
                text_list[text_list.index("=")] = "=="

            if(text_list[0]) == ("elseif"):
                text_list[0] = "elif"
            temp = ' '.join(text_list)
            print(' '.join(text_list) , ":")
            result.write("%s :\r\n"%(temp))
            exec_file.write("%s :\r\n"%(temp))  

        elif text_list[0] == "else" :
            print ("else :")
            result.write("else :\r\n")
            exec_file.write("else :\r\n")
            indent =  indent + 1
        
        #reading new line in input file
        text = input_.readline().rstrip('\n')
        
        #handling the case if there is multi empty lines between our code because of the tesseract output
        if(len(text) == 0):
            text = input_.readline().rstrip('\n')

    
    exec_file.write("c.send(bytes('end','utf8'))\r\n") 
    # close files and return result file to execute
    result.close()
    exec_file.close()
    return result


#Conversion Process

def threaded(c,addr):
    # Recieve image from client
    with open('input.jpg', 'wb') as img:
        data = c.recv(1024)
        while data != b'done':
            print(data)
            img.write(data)
            data = c.recv(1024)
    print ('image is recieved!')

    # Extract text from image
    img = cv2.imread('input.jpg')
    extract_text(img)

    # Convert sudo code
    input_file = open("sudo.txt" , "r+")
    output_file = open("result.txt" , "w+")
    exec_file = open("exec.txt" , "w+")
    print('Start compilation')
    compile_sudo(input_file,  output_file , exec_file)

    # Send output to client
    print("Beginning File Transfer")
    f = open("result.txt", 'rb')
    c.send(f.read(4096))
    f.close()
    print("Transfer Complete")

    # Execute Code
    run = c.recv(1024)
    if (run== b'run'):
        exec(open(exec_file.name).read())

    #close socket
    c.close()
    

# Main Function

def Main():
    # Create a Server Socket
    server = socket.socket()
    host= socket.gethostbyname(socket.gethostname()) 
    port = 12346
    server.bind((host, port))
    print(host)
    # Wait for client connection
    server.listen()
    while True:
        print ('Server is waiting..')
        client, addr = server.accept()
        
        print ('Got connection from', addr)

        # Start new thread
        start_new_thread(threaded, (client,addr,))

    server.close()

Main() 

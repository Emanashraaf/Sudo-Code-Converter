import socket
import pytesseract
import cv2
from PIL import Image
import matplotlib as plt
import os
from _thread import *
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
tessdata_dir_config = r'--tessdata-dir "C:\\Program Files\\Tesseract-OCR\\tessdata"'

# Extract text from image
def extract_text(img):
    img = cv2.resize(img,(1000,1000))
    img = np.array(img,np.uint8)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    val,binary = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(binary)
    print(text)
    f = open("sudo.txt","w+")
    f.write(text)
    f.close()

key_word={"Display":"print","Promot":"input()","print":"print"}
string_operations={"add":"+","sub":"-","mul":"*","div":"/","mod":"%" ,"equal" : "=" , "greater_than" : ">" ,"less_than" : "<","greater_than_or_equal" : ">=",
                   "less_than_or_equal" : "=<" ,"not_equal":"!="}
operations = ["+" , "-" , "*" , "/"] 
key=["number","string","to","do"]
numbers ={"zero":0 , "one":1 ,"two":2 , "three":3 ,"four":4 ,"five":5 ,"six":6 ,"seven":7 ,
          "eight":8 ,"nine":9 ,"ten":10}

def compile_sudo (input_ , result,exec_file):
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
                
        result.write("   " * indent)
        print("   " * indent ,end = "")
        
        if text_list[0] == "Display" :
            str1 = ' '.join(text_list[1:])
            print(key_word[text_list[0]],'("',str1,'")')
            result.write("%s ( '"'%s'"' )\r\n" %(key_word[text_list[0]],str1))
        elif text_list[0] == "Promot" :
            exec_file.write("c.send('input')")
            temp= key_word[text_list[0]]
            if(key[0] in text_list):

                text = input_.readline().rstrip('\n')
                text_list = text.split(" ")
                if text_list[0] == "Save" :
                    str1 = text_list[-1]
                    print(str1,"=int(",temp,")")
                    result.write("%s =int( %s )\r\n" %(str1,temp))
            else:
                if text_list[0] == "Save" :
                    str1 = text_list[-1]
                    print(str1,"=",temp)
                    result.write("%s = %s \r\n "%(str1,temp))

        elif text_list[0] == "print" :
            str1 = ' '.join(text_list[1:])
            print(key_word[text_list[0]],'(',str1,')')
            result.write("%s ( %s )\r\n"%(key_word[text_list[0]],str1))

        elif([i for i in operations if i in text_list]):
            temp=' '.join(text_list)
            print(temp)
            result.write("%s\r\n"%(temp))

        elif text_list[0] == "initialize" :
            print(text_list[1] , "= []")
            result.write("%s = []\r\n"%(text_list[1]))

        elif text_list[0] == "set" :
            item = text_list.index(next(i for i in key if i in text_list))
            if(text_list[item]=="to"):
                print(numbers[text_list[item+1]])
                result.write("%s = %s\r\n"%(text_list[1] ,numbers[text_list[item+1]] ))
                    


        elif text_list[0] == "for" :
            indent =  indent + 1
            iterator = text_list[1]
            item = text_list.index(next(i for i in key if i in text_list))
            if(text_list[item]=="to"):
                print("for" , iterator ,"in range(",text_list[item-1],',',int(text_list[item+1])+1,'):')
                result.write("for %s in range (%s,%d) :\r\n" %( iterator ,(text_list[item-1]),(int(text_list[item+1])+1)))


        elif ((text_list[0]) == ("if")) or ((text_list[0]) == ("elseif")) or ((text_list[0]) == ("elif")) or ((text_list[0]) == ("while")) :
            indent =  indent + 1
            if "is" in text_list:
                text_list.remove("is")
            if "to" in text_list:
                text_list.remove("to")
            if([i for i in string_operations if i in text_list]):
                item = next(i for i in text_list if i in string_operations)
                if item == "=" :
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
            
                
        elif text_list[0] == "else" :
            print ("else :")
            result.write("else :\r\n")
            indent =  indent + 1
                
        text = input_.readline().rstrip('\n')

        if(len(text)==0):
            text = input_.readline().rstrip('\n')
            
    result.close()
    return result

def threaded(c,addr):
    # Recieve image from client
    with open('tst.jpg', 'wb') as img:
        data = c.recv(1024)
        while data != b'done':
            print(data)
            img.write(data)
            data = c.recv(1024)
    print ('image is recieved!')

    # Extract text from image
    img = cv2.imread('tst1.jpg')
    extract_text(img)

    # Convert sudo code
    input_file = open("sudo.txt" , "r+")
    output_file = open("result.txt" , "w+")
    exec_file = open("exec.txt" , "w+")
    print('start compilation')
    compile_sudo(input_file,  output_file , exec_file)

    # Send output to client
    print("Beginning File Transfer")
    f = open("result.txt", 'rb')
    c.send(f.read(4096))
    f.close()
    print("Transfer Complete")
    

def Main():
    # Create a Server Socket
    server = socket.socket()
    host= socket.gethostbyname(socket.gethostname()) 
    port = 12345
    server.bind((host, port))

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

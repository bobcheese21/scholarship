# %%
import PyPDF2 as ppy
from addClass import main as ac
from addStudent import main as ass
from addStudClass import main as asc
import pandas as pd
import textract
import pymysql

# %%
pdf = ppy.PdfFileReader("./Transcript for Robi.pdf")
pdf2 = ppy.PdfFileReader("UWUnofficialTranscript.pdf")
text = textract.process("UWUnofficialTranscript.pdf")
otherPDF = text.decode("utf-8")


# %%
data = getClasses(pdf2)
studentID = data['studentID']
data = data['data']
print(data)
print(studentID)

# %%
def commitData(data, studentID):
    classes=data
#     studentID = data['studentID']
#     if (studentID == userID):     
    row = data.loc[0]
    classesBatch = []
    for i in range(len(data)):
        row = data.loc[i]
        classesBatch.append((row['Department'], row['ClassNum'], row['ClassTitle']))
    ac.main(classesBatch)
    
    row = data.loc[0]
    studClassBatch = []
    for i in range(len(data)):
        row = data.loc[i]
        studClassBatch.append((studentID, row['Quarter'], row['ClassNum'], row['Department'], row['ClassTitle'], row['Year']))
    asc.main(studClassBatch)

    

# %%
def mergePages(pages):
    breaks = []
    total = []
    # Look for the word 'Page' on each page 
    # assumptions: there is only one occurance
    # no valuable data preceds the occurance of 'Page'
    curQtr = ""
    studentNumber = ""
    for i in range(pages.getNumPages()):
        page = pages.getPage(i)
        parsed = page.extractText().split('\n')
        studentNumber = parsed[8]
        for i,x in enumerate(parsed):
            if "Page" in x:
                breaks = i
            if 'CURRENTLY ENROLLED' in x:
                curQtr = x.split('(')[1].split(')')[0].replace('QUARTER, ', "")        
        useful = parsed[breaks + 1: ]
        total.extend(useful)
    return {'total': total, 'curQtr': curQtr.strip(), 'studentID': studentNumber}

# %%
def getClasses(pdf):
    information = mergePages(pdf)
    parsed = information['total']
    curQtr = information['curQtr']
    studentID = information['studentID']
    durations = pd.DataFrame(columns = ['Quarter', 'Year', 'StatusWhile', 'index'])
    count = 0
    for i, x in enumerate(parsed):
        if 'AUTUMN' in x or 'WINTER' in x or 'SPRING' in x and 'D E S T R O Y' not in x:
            row = {'Quarter': x.split()[0], 'Year': x.split()[1], 'StatusWhile' : x.split()[2], 'index': i}
    #         y = x.split()
            durations = durations.append(row, ignore_index=True)
            count = count +1

    classes = pd.DataFrame(columns = ['Quarter', 'Department', 'ClassNum', 'ClassTitle', 'Grade'])
    for i in durations.iloc:
        ind = i['index'] + 1
        cur = parsed[ind]
        while 'QTR' not in cur and 'EARNED' not in cur and 'D E S T R O Y' not in cur and ind < len(parsed):
            if 'GEN ST' in cur:
                cur = cur.replace('GEN ST' ,"GEN")
            curSplit = cur.split()
            desc = ""
            grade =  curSplit[-1]
            for j in range(2, len(curSplit) - 2):
                desc = desc + " " + curSplit[j]
            if curQtr == str(i['Quarter'] + " " +i['Year']):
                desc = ""
                for j in range(2, len(curSplit) - 1):
                    desc = desc + " " + curSplit[j]
                grade = "IP"
            row = {'Quarter': i['Quarter'].strip(), 'Year': i['Year'].strip(), 'Grade': grade.strip(), 'Department': curSplit[0].strip(), 'ClassNum': curSplit[1].strip(), 'ClassTitle' : desc.strip() }
            classes = classes.append(row, ignore_index=True)
            ind = ind + 1
            cur = parsed[ind]
            
    return {'data': classes, 'studentID': studentID}

# %%
commitData(data, studentID)

# %%

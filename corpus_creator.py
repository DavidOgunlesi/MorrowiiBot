from util.Database import DB as db

##load text file as lines of text into array of strings
def loadTextFile(filename):
    file = open(filename, "r", encoding='utf-8')
    # utf-8
    lines = file.readlines()
    file.close()
    return lines

data = loadTextFile("database/source/morrowii.txt")

morrowiiDB = db(data)

morrowiiDB.Save("Morrowii", "database/data")
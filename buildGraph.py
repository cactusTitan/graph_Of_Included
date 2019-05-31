# https://www.flourish.org/cinclude2dot/

import os
import re
import random
import colorsys

# вид кавычек для подключаемых библиотек
quotetypes = "both" # "quote", "angle"
    # "both": include <file> & include "file"
    #"angle": include <file>
    #"quote": include "file"

# папка проекта, для которого требуется построить граф
src = os.getcwd() #"C:\\Users\\tv111\\Desktop\\work\\Практика\\project_graph\\Keyboard Handler 07.03.2018"

# путь к graphViz
graphvizSrc = 'C:\\"Program Files (x86)"\\Graphviz2.38\\bin\\dot.exe'

# множество программ, которые не надо включать в граф 
exclude = {}

# слияние одноимённых файлов
merge = "file" # "module" "directory"
    #"file" : в граф все файлы входят со своим расширением
    #"module" : файлы с одним названием и одной группой расширений {'.cpp', '.c','.cxx', '.C'} и {'.h', '.hpp', '.hxx'} считаются одинаковыми (.c или .h)
    #"directory" : файлы с одним названием и разными расширениями считаются одинаковыми

# очистка временных файлов
clearFiles = False

# файлы, которые мы рассматриваем на предмет подключаемых библиотек (только програмный код)
code = {'.cpp', '.h', '.c','.cxx', '.C', '.hpp', '.hxx'}

# вершины с фиксированным цветом - папки и отдельные файлы
fixedColors = {"base_color" : "cyan",
               "" : "slateblue",
               "Keyboard Handler 07.03.2018" : "lawngreen",
               "Debug": "purple",
               "Interface" : "gold",
               "Kernel" : "peachpuff",
               "Keyboard" : "dodgerblue",
               "Library" : "chocolate",
               "Win32" : "olive",
               "Release" : "springgreen"}

# форма вершин в зависимости от расширения
# box, polygon, ellipse, oval, circle, point, egg, triangle, plaintext, plain, diamond,
# trapezium, parallelogram, house, pentagon, hexagon, septagon, octagon, doublecircle,
# doubleoctagon, tripleoctagon, invtriangle, invtrapezium, invhouse, Mdiamond, Msquare,
# Mcircle, rect, rectangle, square, star, none
fixedShapes = {".c" : "\"rectangle\"",
               ".C" : "\"rectangle\"",
               ".cpp" : "\"rectangle\"",
               ".cxx": "\"rectangle\"",
               ".h" : "\"diamond\"",
               ".hpp" : "\"diamond\"",
               ".hxx" : "\"diamond\"",}

# выбор сулчайного (не тёмного) цвета для закраски вершин
def randomizeColor():
    return str('#%02X%02X%02X' % (random.randint(64, 255),
                                  random.randint(64, 255),
                                  random.randint(64, 255)))

#проверка того, что файл является кодом
def isCode(name):
    if (name in exclude):
        return False
    result = re.findall(r'\.\w+$', name)
    if (result == []):
        return False
    else:
        return (result[0] in code)

# раскрашивание вершин
def getColor(name):
    if (fixedColors.get(name) == None):
        return randomizeColor()
    else:
        return fixedColors.get(name)

# в зависимости от типа .c .h изменяем форму вершины
def shapeVertex(name):
    s = "["
    typeOfCode = re.findall(r'\.\w+$', name)[0]
    if (fixedShapes.get(typeOfCode) != None):
        s += "shape=" + fixedShapes.get(typeOfCode)
    if (fixedColors.get(name) != None):
        s += ", " + "fillcolor=\"" + getColor(name) + "\""
    s += "];\n"
    return s

# избавляемся от прямых и обратных слэшей, оставляем только последий файл 
def tidyPath(code):
    if (merge == "directory"):
        code = (re.split(r'\.\w+$', line))[0]
    if (merge == "module"):
        if (re.findall(r'\.\w+$', name)[0] in {'.cpp', '.c','.cxx', '.C'}):
            code = (re.split(r'\.\w+$', line))[0] + '.c'
        elif (re.findall(r'\.\w+$', name)[0] in {'.h', '.hpp', '.hxx'}):
            (re.split(r'\.\w+$', line))[0] + '.h'
    result = re.findall(r'[/\\]([^/\\]+)$',code)
    if (result == []):
        return code
    else:
        return result[0]

# ищем подключаемые библиотеки 
def findInclude(line):
    included = ""
    if ((quotetypes == "both") or (quotetypes == "quote")):
        result = re.findall(r'#include[ ]*"(.+)"',line)
        if (result != []):
            included = result[0]
    if ((quotetypes == "both") or (quotetypes == "angle")):
        result = re.findall(r'#include[ ]*<(.+)>',line)
        if (result != []):
            included = result[0]
    return included

# записываем какие библиотеки подключаются каким файлом
def writeGraph(code, way, vertexes, edges):
    f = open(way + code, 'r')
    edges.write("\"" + tidyPath(code) + "\" -> { ")   
    for line in f:
        included = findInclude(line)
        if (included != ""):
            edges.write("\"" + tidyPath(included) + "\" ")
    edges.write("};\n")
    f.close()

# обход всех подпапок
def walkFiles(adress, way, vertexes, edges):
    global n
    n += 1
    way = way + adress + '\\'
    cat = os.listdir(way)
    vertexes.write("subgraph cluster_" + str(n) + " {\n")
    vertexes.write("node [style=\"filled\", " +
                   "shape=\"box\", " +
                   "fillcolor=\"" + getColor(adress) + "\"];\n")
    vertexes.write("label = \"" + adress + "\";\n")
    for obj in cat:
        if (os.path.isdir(way + obj)):    #обход подпапок
            walkFiles(obj, way, vertexes, edges)
        else:
            if (isCode(obj)):
                vertexes.write("\""+obj+"\""+shapeVertex(tidyPath(obj)))
                writeGraph(obj, way, vertexes, edges)
    vertexes.write("}\n")

# отдельно записываем рёбра и вершины
vertexes = open("vertexes.txt", "w")
edges  = open("edges.txt", "w")
outfile = open("includesgraph.gv", "w")
n = 0
vertexes.write("digraph G{\n")
vertexes.write("node [style=\"filled\", " +
                   "fillcolor=\"" + getColor("base_color") + "\"];\n")

walkFiles('', src, vertexes, edges)
vertexes.close()
edges.close()
for line in open("vertexes.txt"):
    outfile.write(line)
for line in open("edges.txt"):
    outfile.write(line)
    
outfile.write("}")
outfile.close()
vertexes.close()
edges.close()
if (clearFiles):
    os.remove("vertexes.txt")
    os.remove("edges.txt")
os.system(graphvizSrc +' -Tpng -oincludeGraph.png includesgraph.gv')
if (clearFiles):
    os.remove("includesgraph.gv")

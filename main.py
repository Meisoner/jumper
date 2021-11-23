from sqlite3 import connect as sqc
from random import randrange as rr
from PIL import Image as img, ImageDraw as draw
from PyQt5.QtCore import QTimer as T, Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit

# Константы снизу МОЖНО редактировать!
# Цвета, которые можно вводить в cparser.
COLOURS = {'blue': (0, 0, 255, 255), 'green': (0, 255, 0, 255), 'red': (255, 0, 0, 255),
                       'purple': (255, 0, 255, 255), 'white': (255, 255, 255, 255),
                       'black': (0, 0, 0, 255), 'yellow': (255, 255, 0, 255), 'cyan': (0, 255, 255, 255)}
# Разные уровни сложности.
DIFFICULTIES = {'1': ('Легко', 'green'), '2': ('Средне', 'yellow'), '3': ('Сложно', 'red')}


# Проверяет, существует ли файл.
def exist(path):
    try:
        with open(path):
            return True
    except Exception:
        return False


# Функция для cparser для перевода цвета из шестнадцатеричной системы счисления.
def fromhex(hex):
    hexsymb = [str(i) for i in range(10)] + list('abcdef')
    hexdict = {hexsymb[i]: i for i in range(16)}
    result = 0
    for i in range(len(hex)):
        result += hexdict[hex[i]] * 16 ** (len(hex) - i - 1)
    return result


# Функция для перевода цветового кортежа в шестнадцатеричную систему счисления.
def tohexcol(col):
    res = '#'
    hexsymb = [str(i) for i in range(10)] + list('ABCDEF')
    for i in col[:3]:
        res += hexsymb[(i // 16) % 16] + hexsymb[i % 16]
    return res


# Функция для перевода цвета из практически любого типа в четырёхканальный кортеж.
def cparser(col):
    global COLOURS
    colour = col.lower()
    out = []
    c = str(colour).lower()
    for i in '()#':
        c = c.replace(i, '')
    if c in COLOURS.keys():
        return COLOURS[c]
    if len(c.split(',')) == 3:
        return tuple([int(i) for i in c.split(',')] + [255])
    if len(c) == 6:
        for i in range(3):
            out += [fromhex(c[2 * i] + c[2 * i + 1])]
        return (tuple(out + [255]))
    if len(c) == 9:
        for i in range(3):
            out += [int(c[3 * i:3 * i + 3])]
        return (tuple(out + [255]))


# Функция генератора.
def gen():
    height = 0
    sp, lsp, bsp = 0, 0, False
    res = []
    for i in range(rr(20, 100)):
        if rr(4) == 0 and lsp >= 3:
            if rr(2) == 0 and height > 0:
                height -= 1
            elif height < 10:
                height += 1
            if lsp != 3:
                lsp = 3
        elif rr(5) == 0 and sp < 3 and lsp >= 5:
                bsp = True
        if bsp:
            nxt = 'B' * height + 'S'
            bsp = False
            lsp = 0
        else:
            nxt = 'B' * height
            lsp += 1
        if nxt:
            res += [nxt]
        else:
            res += ['-']
    return ' '.join(res)


# Функция для создания картинок для разных объектов, описанных в level.l.
def imgenerator(shape, colour, sx, sy, depth, rot):
    col = cparser(colour)
    col1 = tohexcol(col[:3])[1:]
    for i in '(), ':
        col1 = col1.replace(i, '')
    name = shape.upper() + '_' + str(sx) + '_' + str(sy) + \
           '_' + col1 + '_' + str(depth) + '_' + str(rot) + '.png'
    if exist(name):
        return name
    res = img.new('RGBA', (sx, sy), (0, 0, 0, 0))
    drawer = draw.Draw(res)
    if shape == 'b' or shape == 'rect':
        drawer.rectangle(((0, 0), (sx - 1, sy - 1)), col)
        if shape == 'b':
            drawer.rectangle(((depth, depth), (sx - depth - 1, sy - depth - 1)), (0, 0, 0, 0))
    if shape == 'p' or shape == 'circ':
        drawer.ellipse(((0, 0), (sx - 1, sy - 1)), col)
        if shape == 'p':
            drawer.ellipse(((depth, depth), (sx - depth - 1, sy - depth - 1)), (0, 0, 0, 0))
    if shape == 'tri':
        if sx % 2 == 0:
            drawer.polygon(((0, sy - 1), ((sx - 1) // 2, 0),
                            (sx // 2, 0), (sx - 1, sy - 1)), col)
        else:
            drawer.polygon(((0, sy - 1), ((sx - 1) // 2, 0),
                            (sx - 1, sy - 1)), col)
    if shape == 's':
        for i in range(depth):
            drawer.line(((0, sy - i - 1), (sx - 1, sy - i - 1)), col)
            drawer.line(((i, sy - depth - 1), ((sx - 1) // 2, i)), col)
            drawer.line(((sx - i - 1, sy - depth - 1), (sx // 2, i)), col)
    if rot:
        res = res.rotate(rot)
    res.save(name)
    return name


# Функция для разделения строки на объекты, состоящие из буквы и его нумерации (0 не может присутствовать в нумерации)
# (A0BC1DE34 -> A, 0, B, C1, D, E34).
def div(string):
    res = []
    nums = [str(i) for i in range(1, 10)]
    for i in string:
        if i in nums:
            res[-1] += i
        else:
            res += [i]
    return res


# Функция для реализации циклов в уровнях 'B 2(2(-) S)' -> ['B', '-', '-', 'S', '-', '-', 'S']
def cyclesplit(string):
    res, hasbracket = [''], 0
    for i in string:
        hasbracket += int(i == '(') - int(i == ')')
        if i == ' ' and res[-1].replace(' ', '') and not hasbracket:
            res += ['']
        else:
            res[-1] += i
        if res[-1]:
            if res[-1][-1] == ')' and not hasbracket:
                tempstring = cyclesplit(
                    (int(res[-1].split('(')[0]) * ('('.join(res[-1].split('(')[1:])[:-1] + ' ')).strip())
                res = res[:-1]
                res += tempstring
    return [i.replace(' ', '') for i in res]


# Все игровые объекты описываются этим классом, в который включено много удобных методов.
class GameObject(QLabel):
    def __init__(self, parent, pic, sizex, sizey, phys, isblock):
        super().__init__(parent)
        self.phys = phys
        self.isblock = isblock
        self.resize(sizex, sizey)
        self.size = (sizex, sizey)
        self.parent = parent
        if pic:
            self.setPixmap(QPixmap(pic))

    def hasPhysics(self):
        return self.phys

    def canStandOn(self):
        return self.isblock

    # Проверяет, не врезался ли игрок в объект.
    def smashed(self):
        if not self.hasPhysics():
            return False
        if self.canStandOn():
            return self.x() < 750 and self.x() + self.size[0] > 700 and self.parent.player.y() + 50 > self.y() \
                   and self.parent.player.y() < self.y() + self.size[1]
        else:
            return self.x() < 750 and self.x() + self.size[0] > 720 and self.parent.player.y() + 50 > self.y() \
                   and self.parent.player.y() < self.y() + self.size[1]

    # Проверяет, не стоит ли игрок на объекте.
    def standingOn(self):
        if not self.canStandOn() or not self.hasPhysics():
            return False
        return self.x() < 750 and self.x() + self.size[0] > 700 and self.y() == self.parent.player.y() + 50

    def getSize(self):
        return self.size


# Этим методом описываются объекты, реагирующие на игрока.
class GameTrigger(GameObject):
    def __init__(self, parent, action):
        super().__init__(parent, '', 1, 1, False, False)
        self.action = action

    def smashed(self):
        if self.action and self.x() == 700:
            acttype = self.action.split('_')[0]
            if len(self.action.split('_')) > 1:
                actparams = self.action.split('_')[1:]
                actparams += ['' for _ in range(3 - len(actparams))]
            else:
                actparams = ['' for _ in range(3)]
            if acttype == 'setcol':
                if actparams[0]:
                    self.parent.bgcol(actparams[0])
                else:
                    self.parent.bgcol(self.parent.stcol)
            elif acttype == 'jump' and actparams[0]:
                self.parent.up = int(actparams[0])
            elif acttype == 'tpy':
                if actparams[0]:
                    self.parent.player.move(self.parent.player.x(), 600 - abs(int(actparams[0])) * 10)
                else:
                    self.parent.player.move(self.parent.player.x(), 600)
            elif acttype == 'setmode' and actparams[0]:
                self.parent.mode = int(actparams[0])
                if self.parent.player.y() % 10 != 0:
                    self.parent.player.move(self.parent.player.x(), self.parent.player.y() - 5)
            elif acttype == 'move' and actparams[0] and actparams[1] and actparams[2]:
                if (int(actparams[1].split(',')[0]) * 10) % int(actparams[2]) == 0 and \
                        (int(actparams[1].split(',')[1]) * 10) % int(actparams[2]) == 0:
                    for i in self.parent.findobj(actparams[0]):
                        self.parent.movements += [[i, (int(actparams[1].split(',')[0]) * 10) // int(actparams[2]),
                                                   (int(actparams[1].split(',')[1]) * 10) // int(actparams[2]),
                                                   int(actparams[2])]]
            elif acttype == 'move' and actparams[0] and actparams[1]:
                for i in self.parent.findobj(actparams[0]):
                    self.parent.movements += [[i, int(actparams[1].split(',')[0]), int(actparams[1].split(',')[1]), 10]]
        return False

    def getSize(self):
        return 0, 0


class Game(QWidget):
    def __init__(self, parent=None, lvlname='', lvlcont=''):
        super().__init__()
        self.parent = parent
        self.lvlname = lvlname
        self.lvlcont = lvlcont
        self.start()

    def start(self):
        self.setWindowIcon(QIcon(imgenerator('b', 'blue', 100, 100, 30, 45)))
        self.setGeometry(350, 200, 1200, 650)
        self.setFixedSize(1200, 650)
        self.setWindowTitle(':)')
        self.bg = QLabel(self)
        self.bg.resize(1200, 650)
        self.stcol = 'white'
        self.bgcol(self.stcol)
        self.title = QLabel('JUMPER', self)
        self.title.setFont(QFont('Arial', 30))
        self.launch = QPushButton('Начать', self)
        self.launch.setFont(QFont('Arial', 20))
        self.title.resize(1200, 50)
        self.title.setAlignment(Qt.AlignCenter)
        self.launch.move(450, 120)
        self.launch.resize(300, 100)
        self.launch.clicked.connect(self.lvl)
        self.clicked = False
        self.generator = QPushButton('Генератор', self)
        self.generator.resize(300, 50)
        self.generator.move(450, 240)
        self.generator.setFont(QFont('Arial', 20))
        self.generator.clicked.connect(self.genlvl)
        self.history = QPushButton('Уровни', self)
        self.history.setFont(QFont('Arial', 20))
        self.history.resize(300, 50)
        self.history.move(450, 310)
        self.submit = QPushButton('Сохранить', self)
        self.submit.setFont(QFont('Arial', 20))
        self.submit.resize(300, 50)
        self.submit.move(450, 380)
        if self.parent:
            self.generator.hide()
            self.history.hide()
            self.submit.move(450, 240)
        self.submit.clicked.connect(self.levelsave)
        self.submit.hide()
        self.history.clicked.connect(self.levelhist)
        self.wait = 0
        numdict = dict()
        self.objdict = dict()
        if not exist('level.l'):
            with open('level.l', 'w'):
                pass
        if self.lvlcont:
            self.textcont = self.lvlcont
        else:
            with open('level.l') as f:
                self.textcont = f.read()
        self.lcont0 = self.textcont.split('\n')
        if not exist('levels_db.sqlite'):
            self.db = sqc('levels_db.sqlite')
            self.dbc = self.db.cursor()
            self.dbc.execute('''CREATE TABLE IF NOT EXISTS levels(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                attempts INTEGER,
                difficulty TEXT);''')
            self.dbc.execute('''CREATE TABLE IF NOT EXISTS contents(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT);''')
        else:
            if not self.parent:
                self.db = sqc('levels_db.sqlite')
                self.dbc = self.db.cursor()
            else:
                self.dbc = self.parent.dbc
        self.lcont = cyclesplit(self.lcont0[0])
        self.lcont0 = self.lcont0[1:]
        self.customs = dict()
        self.standarts = {'shape': 'b', 'colour': 'black', 'width': '5', 'height': '5', 'depth': '2',
                          'rotation': '0', 'hasphysics': True, 'triggeraction': ''}
        for i in self.lcont0:
            if not i:
                continue
            key, params = i.split()[0], i.split()[1:]
            self.customs[key] = dict()
            for j in range(len(params) // 2):
                if params[2 * j + 1] == 'true':
                    self.customs[key][params[2 * j]] = True
                elif params[2 * j + 1] == 'false':
                    self.customs[key][params[2 * j]] = False
                else:
                    self.customs[key][params[2 * j]] = params[2 * j + 1]
            if 'from' in self.customs[key].keys():
                for j in self.customs[self.customs[key]['from']].keys():
                    if j not in self.customs[key].keys():
                        self.customs[key][j] = self.customs[self.customs[key]['from']][j]
            for j in self.standarts.keys():
                if j not in self.customs[key].keys():
                    self.customs[key][j] = self.standarts[j]
            if 'isblock' not in self.customs[key].keys():
                self.customs[key]['isblock'] = self.customs[key]['shape'] in ['b', 'rect']
        self.dmode = False
        if self.lcont:
            if self.lcont[0] == 'D':
                self.dmode = True
                self.lcont = self.lcont[1:]
                self.dmlb = QLabel('Demonstration: ON', self)
                self.dmlb.resize(150, 20)
                self.dmlb.setFont(QFont('Arial', 10))
        self.objects = []
        self.up = 0
        self.delayed_end = 0
        while self.lcont:
            self.objects += [[]]
            for i in div(self.lcont[0]):
                obj = 0
                if i == 'S':
                    obj = GameObject(self, imgenerator('s', 'black', 50, 50, 2, 0), 50, 50, True, False)
                    self.objects[-1] += [obj]
                    self.objects[-1][-1].move(0, 0)
                    self.objects[-1][-1].hide()
                elif i == 'B':
                    obj = GameObject(self, imgenerator('b', 'black', 50, 50, 2, 0), 50, 50, True, True)
                    self.objects[-1] += [obj]
                    self.objects[-1][-1].move(0, 0)
                    self.objects[-1][-1].hide()
                elif i == '0':
                    obj = 0
                    self.objects[-1] += [0]
                elif i in self.customs.keys():
                    inf = self.customs[i]
                    if inf['shape'] != 'trig':
                        obj = GameObject(self, imgenerator(inf['shape'], inf['colour'],
                                                           int(inf['width']) * 10,
                                                           int(inf['height']) * 10, int(inf['depth']),
                                                           int(inf['rotation'])), int(inf['width']) * 10,
                                         int(inf['height']) * 10, inf['hasphysics'],
                                         inf['isblock'])
                        self.objects[-1] += [obj]
                    else:
                        obj = GameTrigger(self, inf['triggeraction'])
                        self.objects[-1] += [obj]
                    self.objects[-1][-1].move(0, 0)
                    self.objects[-1][-1].hide()
                if obj:
                    if i in numdict.keys():
                        numdict[i] += 1
                    else:
                        numdict[i] = 1
                    self.objdict[i + 'N' + str(numdict[i])] = obj
            self.lcont = self.lcont[1:]
        if 'BG' in self.customs.keys():
            if 'colour' in self.customs['BG'].keys():
                self.stcol = self.customs['BG']['colour']
                self.bgcol(self.stcol)
        self.attprov = QLabel('Attempts: 0', self)
        self.attprov.resize(200, 100)
        self.attprov.move(650, 350)
        self.attprov.setFont(QFont('Arial', 20))
        self.attprov.hide()
        self.t = T(self)
        self.t.timeout.connect(self.frame)
        self.player = GameObject(self, imgenerator('p', 'black', 50, 50, 2, 0), 50, 50, False, False)
        self.player.move(700, 600)
        self.player.hide()
        self.opened = []
        if self.lvlcont:
            self.lvl()

    def resetVars(self):
        self.spp = []
        self.ctr = -1
        self.toexit = 15
        self.delayed_end = 0
        self.up = 0
        self.mode = 0
        self.movements = []

    # Метод для запуска игры.
    def lvl(self):
        self.resetVars()
        self.title.hide()
        self.launch.hide()
        self.history.hide()
        self.submit.hide()
        self.generator.hide()
        if self.lvlname:
            self.dbc.execute('''UPDATE levels SET attempts = attempts + 1
                WHERE name = "''' + self.lvlname + '"')
            self.att = list(self.dbc.execute('''SELECT attempts FROM levels
                WHERE name = "''' + self.lvlname + '"'))[0][0]
        else:
            self.att = 1
        self.attprov.setText('Attempts: ' + str(self.att))
        if not self.dmode:
            self.attprov.show()
        self.player.show()
        self.t.start(20)

    def mousePressEvent(self, event):
        self.clicked = True

    def mouseReleaseEvent(self, event):
        self.clicked = False

    # Метод для начала новой игры после проигрыша.
    def new(self):
        self.resetVars()
        self.player.move(700, 600)
        for i in self.objects:
            for j in i:
                if j:
                    j.hide()
                    j.move(0, 0)
        if not self.dmode:
            self.att += 1
            self.attprov.setText('Attempts: ' + str(self.att))
            self.attprov.show()
            self.attprov.move(650, 350)
        self.bgcol(self.stcol)

    # Метод для смены цвета фона.
    def bgcol(self, colour):
        self.bg.setStyleSheet('background-color: ' + tohexcol(cparser(colour)) + ';')

    # Метод для поиска объектов по их описанию.
    def findobj(self, description):
        if description in self.objdict.keys():
            if not self.objdict[description].isHidden():
                return [self.objdict[description]]
            else:
                return []
        else:
            res = []
            for i in self.objdict.keys():
                if div(i)[0] == description and not self.objdict[i].isHidden():
                    res += [self.objdict[i]]
            return res

    def levelsave(self):
        self.second = Submitter(self.textcont, str(self.att), self.dbc)
        self.opened += [self.second]
        self.second.show()
    
    def levelhist(self):
        self.third = Levelhistory(self, self.dbc)
        self.third.show()
        self.hide()

    def genlvl(self):
        self.game2 = Game(self, lvlcont=gen())
        self.game2.show()
        self.hide()

    # Действия, которые выполняются каждый кадр (50 раз в секунду).
    def frame(self):
        if self.ctr % 5 == 0 and len(self.objects) > self.ctr // 5:
            self.spp += [self.objects[self.ctr // 5]]
            t = 0
            for i in range(len(self.spp[-1])):
                if self.spp[-1][i]:
                    t += self.spp[-1][i].getSize()[1]
                    self.spp[-1][i].move(1200, 650 - t)
                    self.spp[-1][i].show()
                else:
                    t += 50
        elif self.ctr % 5 == 0:
            self.toexit -= 1
        for i in self.spp:
            if not i:
                continue
            for j in i:
                if j:
                    if j.x() > -1 * j.getSize()[0]:
                        j.move(j.x() - 10, j.y())
                    else:
                        j.hide()
        for i in self.movements:
            if i[1] > 0:
                i[0].move(i[0].x() + i[3], i[0].y())
                i[1] -= 1
            elif i[1] < 0:
                i[0].move(i[0].x() - i[3], i[0].y())
                i[1] += 1
            if i[2] > 0:
                i[0].move(i[0].x(), i[0].y() - i[3])
                i[2] -= 1
            elif i[2] < 0:
                i[0].move(i[0].x(), i[0].y() + i[3])
                i[2] += 1
        if self.delayed_end == 1:
            # Разделил на две части для оптимизации.
            if self.player.y() == 600:
                self.toexit = 3
                self.delayed_end = 2
        if self.ctr < 5:
            self.clicked = False
        if self.clicked:
            if self.mode == 1:
                self.clicked = False
            if not (self.up or self.mode):
                self.up = 10
            if self.mode and self.up <= 0:
                self.up = 5
        if self.wait:
            self.wait -= 1
        if self.up > 0:
            if self.player.y() > 0:
                self.player.move(self.player.x(), self.player.y() - 10 - 5 * (1 - abs(self.mode - 1)))
            self.up -= 1
            if not self.up:
                self.up = -10
                self.wait = 3
                if self.mode == 2:
                    self.wait = 1
        if self.up < 0 and not self.wait:
            if self.player.y() == 600:
                self.up = 0
            else:
                self.player.move(self.player.x(), self.player.y() + 10 - 5 * (1 - abs(self.mode - 1)))
                self.up += 1
        self.onBlock = False
        for i in self.spp:
            for j in i:
                if j:
                    if j.smashed():
                        if not self.dmode:
                            if self.lvlname:
                                self.dbc.execute('''UPDATE levels SET attempts = attempts + 1
                                    WHERE name = "''' + self.lvlname + '"')
                            self.new()
                    elif j.standingOn() and self.up < 0:
                        self.up = 0
                    if j.standingOn():
                        self.onBlock = True
        if self.attprov.x() > -200:
            self.attprov.move(self.attprov.x() - 10, 350)
        else:
            self.attprov.hide()
        if self.player.y() < 600 and not self.up and not self.onBlock:
            self.up = -5
        self.ctr += 1
        if self.toexit <= 0:
            if self.player.y() == 600 and self.delayed_end != 1:
                self.t.stop()
                self.new()
                self.att -= 1
                self.player.hide()
                if self.dmode:
                    self.title.setText('Демонстрация завершена.')
                else:
                    self.title.setText('Уровень пройден!')
                    if not self.lvlname:
                        self.submit.show()
                self.attprov.hide()
                self.launch.setText('Заново')
                self.title.show()
                self.launch.show()
                if not self.parent:
                    self.history.show()
                    self.generator.show()
            else:
                if not self.delayed_end:
                    self.delayed_end = 1

    def closeEvent(self, event):
        if self.parent:
            self.parent.show()
            if self.lvlname:
                self.parent.lvls = list(self.dbc.execute('''SELECT * FROM levels'''))
                self.parent.loadcontent()
        else:
            self.db.commit()
            self.db.close()
        self.t.stop()
        for i in self.opened:
            i.hide()


# Форма для сохранения уровней.
class Submitter(QWidget):
    def __init__(self, content, attempts, dbcursor):
        super().__init__()
        self.content = content
        self.atts = attempts
        self.dbc = dbcursor
        self.start()

    def start(self):
        global DIFFICULTIES
        self.setGeometry(650, 500, 500, 300)
        self.setFixedSize(500, 300)
        self.setWindowIcon(QIcon(imgenerator('b', 'red', 100, 100, 30, 45)))
        self.setWindowTitle('Сохранить')
        self.namelb = QLabel('Имя:', self)
        self.namelb.resize(50, 30)
        self.namerq = QLineEdit(self)
        self.namerq.move(50, 0)
        self.namerq.resize(200, 30)
        self.attempts = QLabel('Попытки: ' + self.atts, self)
        self.attempts.resize(200, 30)
        self.attempts.move(0, 30)
        self.attempts.setFont(QFont('Arial', 15))
        self.namelb.setFont(QFont('Arial', 15))
        self.difflb = QLabel('Сложность:', self)
        self.difflb.resize(100, 30)
        self.difflb.move(0, 60)
        self.difflb.setFont(QFont('Arial', 15))
        self.buttons = [QPushButton(i, self) for i in DIFFICULTIES.keys()]
        for i in range(len(self.buttons)):
            self.buttons[i].resize(40, 40)
            self.buttons[i].move(110 + i * 50, 60)
            self.buttons[i].clicked.connect(self.send)
        self.notification = QLabel(self)
        self.notification.resize(500, 40)
        self.notification.move(0, 260)

    def send(self):
        if not self.namerq.text():
            self.notification.setText('Введите имя уровня!')
            return
        if list(self.dbc.execute('''SELECT * FROM levels
                                    WHERE name = "''' + self.namerq.text().replace('"', '\'\'') + '"')):
            self.notification.setText('Уровень с таким именем уже существует!')
            return
        self.dbc.execute(f'''INSERT INTO levels(name, attempts, difficulty)
            VALUES("{self.namerq.text()}", {self.atts}, {self.sender().text()})''')
        self.dbc.execute(f'''INSERT INTO contents(content)
            VALUES("{self.content}")''')
        self.hide()


class Levelhistory(QWidget):
    def __init__(self, parent, dbcursor):
        global DIFFICULTIES
        super().__init__()
        self.parent = parent
        self.dbc = dbcursor
        self.lvls = list(self.dbc.execute('''SELECT * FROM levels'''))
        self.start()
    
    def start(self):
        self.setGeometry(350, 200, 1200, 650)
        self.setFixedSize(1200, 650)
        self.setWindowIcon(QIcon(imgenerator('b', 'green', 100, 100, 30, 45)))
        self.setWindowTitle('Список уровней')
        self.bg = QLabel(self)
        self.bg.resize(1200, 650)
        self.title = QLabel(self)
        self.title.resize(1200, 50)
        self.title.setFont(QFont('Arial', 25))
        self.title.setAlignment(Qt.AlignCenter)
        if self.lvls:
            self.inf = QLabel(self)
            self.inf.resize(1000, 200)
            self.inf.setFont(QFont('Arial', 20))
            self.inf.move(50, 50)
            self.buttonright = QLabel(self)
            self.buttonright.resize(30, 30)
            self.buttonright.setPixmap(QPixmap(imgenerator('tri', 'black', 30, 30, 2, 270)))
            self.buttonright.move(1170, 310)
            self.buttonleft = QLabel(self)
            self.buttonleft.resize(30, 30)
            self.buttonleft.setPixmap(QPixmap(imgenerator('tri', 'black', 30, 30, 2, 90)))
            self.buttonleft.move(0, 310)
            self.br = QPushButton(self)
            self.br.setStyleSheet('background-color:transparent; border:0;')
            self.br.resize(30, 30)
            self.br.move(1170, 310)
            self.bl = QPushButton(self)
            self.bl.setStyleSheet('background-color:transparent; border:0;')
            self.bl.resize(30, 30)
            self.bl.move(0, 310)
            self.bl.clicked.connect(self.prev)
            self.br.clicked.connect(self.nxt)
            self.play = QPushButton('Играть', self)
            self.play.resize(300, 50)
            self.play.move(450, 400)
            self.play.setFont(QFont('Arial', 25))
            self.play.clicked.connect(self.lvllaunch)
            self.current = 1
            self.prev()
        else:
            self.title.setText('Нет сохранённых уровней!')
            self.bgcol('white')

    def loadcontent(self):
        global DIFFICULTIES
        self.title.setText(str(self.current + 1) + '. ' + self.lvls[self.current][1])
        diff = DIFFICULTIES[self.lvls[self.current][3]]
        self.bgcol(diff[1])
        self.inf.setText(f'''Попытки: {self.lvls[self.current][2]}\nСложность: {diff[0]}''')

    def prev(self):
        if self.current > 0:
            self.current -= 1
            self.loadcontent()

    def nxt(self):
        if self.current + 1 < len(self.lvls):
            self.current += 1
            self.loadcontent()

    def bgcol(self, colour):
        self.bg.setStyleSheet('background-color: ' + tohexcol(cparser(colour)) + ';')

    def lvllaunch(self):
        content = list(self.dbc.execute('''SELECT content FROM contents
            WHERE id = ''' + str(self.lvls[self.current][0])))[0][0]
        self.game = Game(self, self.lvls[self.current][1], content)
        self.game.show()
        self.hide()

    def closeEvent(self, event):
        self.parent.show()


if __name__ == '__main__':
    a = QApplication([]), Game()
    a[1].show(), a[0].exec()

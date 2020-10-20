import csv
import datetime

def stringf_time(ts = None):
    return datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def writelog(filename,infostring,ledgerstring):

    file = open(filename, mode='a')
    file.write(infostring)
    file.write(ledgerstring)
    file.close()


def read_items_file(filename=None):
    file = open(filename, mode='r', newline='')
    reader = csv.reader(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    #one row
    for row in reader:items = row

    return items

def display_info(curtime=None, buy=None, sell=None, bought=None, sold=None):
    
    time_str = stringf_time(curtime)
    bar = "\n------------------------------------\n"
    sd = "\nBUY:\n\n"
    for i,p in buy.items():

        g,c,p = str(buy[i][0]), buy[i][1], buy[i][2]
        sd += i + ' @ ' + g + 'g ' + "{:1.3f}".format(c) + ' -> ' + "{:1.3f}".format(p[0]) + '\n'

    sd += "\nSELL\n\n"

    for i,p in sell.items():
        g,c,p = str(sell[i][0]), sell[i][1], sell[i][2]
        s = i + ' @ ' + g + 'g ' + "{:1.3f}".format(c) + ' -> ' + "{:1.3f}".format(p[0])
        sd +=i + ' @ ' + g + 'g ' + "{:1.3f}".format(c) + ' -> ' + "{:1.3f}".format(p[0]) + '\n'
    
    ib = ''
    for i in bought:
        ib += i + ', '
    ib += '\n'

    ss=''
    for i in sold:
        ss += i + ', '
    ss += '\n'

    booker_trades_str ='\nBooker bought: ' + ib + 'Booker sold: ' + ss

    disp =  bar + time_str  + bar + sd + bar + booker_trades_str

    print(disp)
    return disp
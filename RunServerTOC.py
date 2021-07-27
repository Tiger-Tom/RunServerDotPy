#Config
amount = 3 #0 shows headers, 1 shows headers & sub headers, etc. max=3,min=0
#Main
def pad0s(num, padAmount=1, padOn='left', autoRound=True): #Pads the number with the specified amount of zeroes (pad0s(1, 2) = 001 , pad0s(1, 2, 'right') = 100 (useful for decimals))
    if autoRound:
        num = round(num)
    if num == 0:
        return '0'*(padAmount+1)
    padding = ''
    while num < 10**padAmount:
        padding += '0'
        padAmount -= 1
    if padOn == 'right':
        return str(num)+padding
    return padding+str(num)
def toc():
    print ('"-" = header, "=" = sub-header, "~" = sub-sub-header, "+" = sub-sub-sub-header')
    rs = open('RunServer.py').readlines()
    am0unt = len(str(len(rs)))-1
    last = ''
    midChar = '├'
    lineChar = '─'
    print ('\n>'+pad0s(0, am0unt)+' ┌╢START OF FILE')
    for i in range(len(rs)):
        fI = pad0s(i+1, am0unt)
        dt = (' '+midChar+''+rs[i][1:4].replace(' ', lineChar)+' '.join(rs[i][4:].split(' '))).rstrip()
        if rs[i].startswith('#    '):
            if amount > 2:
                print ('+'+fI+dt)
        elif rs[i].startswith('#   '):
            if amount > 1:
                print ('~'+fI+dt)
        elif rs[i].startswith('#  '):
            if amount > 0:
                print ('='+fI+dt)
        elif rs[i].startswith('# '):
            print ('-'+fI+dt)
        last = dt.count(lineChar)
    print ('>'+pad0s(len(rs), am0unt)+' └╢END OF FILE\n')
while True:
    inp = input('Press enter for TOC with amount of '+str(amount)+', or enter an amount to change to and run with >')
    print ('\n'*49)
    try:
        amount = int(inp)
    except ValueError:
        pass
    toc()
